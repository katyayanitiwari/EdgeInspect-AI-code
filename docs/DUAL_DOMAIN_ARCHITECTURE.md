# EdgeInspect-AI dual-domain architecture

## Product concept

One inspection application with two explicit modes:

- **Steel mode:** the existing NEU-DET YOLOv8n model (EXP-002, 320 × 320).
- **PCB mode:** a separate PCB-trained model. This model is not present in the uploaded project yet and must not be represented as already trained.

The models are separate because the visual domains and defect labels are different. A single detector trained only on NEU-DET cannot be described as a PCB detector.

## Current model status

| Domain | Dataset | Classes | Model status |
|---|---|---|---|
| Steel | NEU-DET | crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches | Trained: `experiments/EXP-002/weights/best.pt` |
| PCB | DeepPCB proposed first benchmark | open, short, mousebite, spur, copper, pin-hole | Not yet downloaded, prepared, or trained |

DeepPCB is a bare-board surface/trace-defect dataset. It does not establish component-missing, component-misalignment, or solder-joint detection. Those require a separate component-level dataset and camera validation.

## Heterogeneous hardware roles

- **Kria KV260:** Arm/Linux host, camera/video ingestion, model inference, post-processing, dashboard/API, and Llama + ExecuTorch if supported on the actual software image.
- **Renesas RA6E2:** low-bandwidth inspection control, LEDs, buzzer, trigger, acknowledgements, and optional actuator control via a safe driver stage.
- **Laptop:** development/training and, during the first remote-camera demo, webcam capture. If the laptop webcam is streamed to KV260, inference still executes on KV260, but the camera itself is not physically attached to the board.

## System flow

```text
Laptop webcam or USB UVC camera
        |
        v
Local video transport / camera input
        |
        v
Kria KV260 (Arm Linux)
   |                         |
   | mode=steel              | mode=pcb
   v                         v
NEU-DET YOLOv8n          PCB-specific detector
   |                         |
   +------------+------------+
                v
        Domain-specific validation
                v
        Severity / decision logic
                v
     Llama-family advisor on-device
             via ExecuTorch
                v
        Dashboard + SQLite log
                |
          UART result message
                v
        Renesas RA6E2 controller
       LEDs / buzzer / inspection I/O
```

## Build order

1. Keep the existing steel model and laptop dashboard stable.
2. Prepare and train a separate PCB model from a documented dataset.
3. Add an explicit mode selector and independent model/rule configuration.
4. Bring up KV260 Linux and run steel inference on its CPU first.
5. Add PCB inference on KV260 after the PCB checkpoint is validated.
6. Evaluate any FPGA/DPU acceleration path for each model independently.
7. Deploy the Llama-family advisor with ExecuTorch on the KV260 Arm CPU, subject to runtime support and challenge acceptance.
8. Add the Renesas UART controller after confirming the exact RA6E2 board and UART pins.
9. Run offline, latency, memory, power, and robustness tests on the physical setup.

## Competition compliance note

The current PS5 challenge page describes Arm-based Linux/Android devices as eligible hardware, requires a Llama-family advisory model deployed on-device using ExecuTorch, and treats Hailo as optional. It describes Hailo vision inference and Llama/ExecuTorch as separate pipelines when Hailo is used. Get written organiser confirmation that the exact KV260 configuration is acceptable before relying on it as the team's competition platform.
