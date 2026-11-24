# AMD Kria KV260 deployment track

**Start here:** complete [`README_FIRST_BOOT.md`](README_FIRST_BOOT.md) and run [`collect_system_info.sh`](collect_system_info.sh) before installing packages or attempting inference. K0 collects the real KV260 OS/Python/ARM64 environment so we can choose compatible runtimes safely.

## Role in EdgeInspect-AI

Use KV260 as the Arm-based Linux edge computer and FPGA-capable platform. The current steel `best.pt` is a laptop PyTorch checkpoint. A small KV260 CPU smoke deployment has been completed and recorded in [`kv260_cpu_smoke_summary.json`](kv260_cpu_smoke_summary.json); it is not an accuracy benchmark. FPGA/DPU inference has not been performed. Do not label the checkpoint FPGA-accelerated until a compatible compiled accelerator model actually runs on this board.

The Windows laptop remains the development/control computer. Windows can prepare files and connect to the board over Ethernet/SSH; the application itself runs on Linux on KV260. The Renesas RA6E2 is a separate microcontroller used for low-bandwidth status/control, not for running the vision model.

## What the kit includes and what it does not

AMD documents the KV260 kit as including the K26 SOM, carrier card, and integrated thermal solution. The kit does **not** include the power supply, SD card, camera, display, or other peripherals. The official recommended input is 12 V, 3 A with a 5.5 mm OD / 2.5 mm ID centre-positive barrel connector. Verify the label and polarity of your adapter before connecting it.

- Official kit contents: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/What-s-in-the-Box
- Power requirements: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Powering-the-Starter-Kit-and-Power-Budgets
- Product details: https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details

## First bring-up checklist

1. Inspect the board and identify the carrier-card revision (1.0 or 2.0).
2. Confirm a correct 12 V / 3 A centre-positive supply before applying power.
3. Prepare a supported KV260 SD-card boot image using AMD's current getting-started instructions. The board boots via QSPI firmware and hands off to the SD-card operating-system image.
4. Connect Ethernet to the same LAN as the development laptop.
5. Boot Linux and record the exact image, kernel, Python, architecture, and available storage.
6. Capture these outputs and keep them with the project:

```bash
uname -a
uname -m
cat /etc/os-release
python3 --version
free -h
df -h
lscpu
```

7. Do not install the full laptop `requirements.txt` blindly on KV260. The current `ultralytics`/PyTorch wheel stack must be checked against the board OS, Python version, and aarch64 package availability first. Send the generated system report before choosing package versions.

## Deployment sequence

### Milestone K1 — CPU-only functional test

- Transfer the selected checkpoint and a small, known test-image set to KV260.
- Confirm Python and inference runtime availability.
- Run a single-image inference and compare class IDs, boxes, and confidence with the laptop result.
- Record cold-start time, warm inference latency, peak RAM, and input resolution.
- Only then build a camera-stream pipeline.

### Milestone K2 — Camera input

The laptop's built-in webcam cannot be electrically connected to KV260. For the initial demo, capture frames on the laptop and transmit them over the local network to KV260, where inference runs. This proves inference on KV260, but is not a fully standalone camera-to-board system. A USB UVC camera connected directly to a KV260 USB port is a later standalone option; validate the specific camera and driver.

### Milestone K3 — FPGA acceleration (separate experiment)

Investigate the AMD-supported Vitis AI / DPU route only after the CPU baseline is reproducible. Do not assume the newest Vitis AI release targets KV260: the current Vitis AI 5.1/6.2 documentation is not by itself proof that a KV260 image, DPU, compiler and runtime are a compatible set. AMD's older Vitis AI 3.0 documentation explicitly lists KV260 with DPUCZDX8G; the 3.5 release notes tie that release to Vivado/PetaLinux 2023.1. Any accelerator experiment must select a matching board image, DPU platform, compiler and runtime from one verified release line before export/quantization. See the vendor references below. Keep CPU inference as the required first deployment milestone and fallback. Report only measured accelerator results.

Official references:

- [AMD KV260 software getting started](https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Software-Getting-Started)
- [AMD Vitis AI 3.0 runtime: DPUCZDX8G and KV260](https://docs.amd.com/r/3.0-English/ug1414-vitis-ai/Vitis-AI-Runtime)
- [AMD Vitis AI releases: 3.5 compatibility notes](https://github.com/Xilinx/Vitis-AI/releases)
- [AMD current Vitis AI developer guide](https://vitisai.docs.amd.com/en/5.1/)

## Required benchmark record

| Metric | Laptop baseline | KV260 CPU | KV260 FPGA/DPU |
|---|---:|---:|---:|
| Precision | Existing test result | Not measured | Not measured |
| Recall | Existing test result | Not measured | Not measured |
| mAP50 | Existing test result | Not measured | Not measured |
| mAP50–95 | Existing test result | Not measured | Not measured |
| Model size | 6.22 MB checkpoint | Not measured | Not measured |
| Warm latency (ms/image) | 36.65 ms in saved laptop run | Not measured | Not measured |
| FPS | 27.3 in saved laptop run | Not measured | Not measured |
| Peak RAM | Not measured | Not measured | Not measured |
| Power (W) | Not measured | Not measured | Not measured |

The current laptop timings are not expected KV260 performance and are not directly comparable if the image size, runtime, or measurement method changes.

## Transfer the baseline from Windows

After K0, use the KV260 IP address and SSH user printed by the actual board image. From PowerShell on Windows, create a deployment directory and copy the checkpoint and smoke script (replace `<user>` and `<KV260-IP>` with the values from your board):

```powershell
ssh YOUR_USER@192.168.1.50 "mkdir -p ~/edgeinspect/experiments/EXP-002/weights ~/edgeinspect/deployment/kv260/test_images"
scp .\experiments\EXP-002\weights\best.pt YOUR_USER@192.168.1.50:~/edgeinspect/experiments/EXP-002/weights/best.pt
scp .\deployment\kv260\smoke_infer.py YOUR_USER@192.168.1.50:~/edgeinspect/deployment/kv260/smoke_infer.py
```

Replace `YOUR_USER` and `192.168.1.50` with the SSH account and IP address printed by the actual board image.

Copy only a few held-out test images to `~/edgeinspect/deployment/kv260/test_images/` from a locally prepared dataset. The dataset is not included in this project package. Do not put private camera images into a public repository. Package installation is intentionally deferred until the board report identifies its OS/Python/runtime; an incompatible PyTorch wheel can make the board environment unusable.

## CPU smoke benchmark script

After the board-side Python runtime is installed and the steel checkpoint is copied to the board, place a few held-out NEU-DET test images in `deployment/kv260/test_images/` and run:

```bash
python3 deployment/kv260/smoke_infer.py \
  --weights experiments/EXP-002/weights/best.pt \
  --source deployment/kv260/test_images \
  --imgsz 320 --device cpu --repeats 5
```

The script saves annotated images and `kv260_cpu_smoke_benchmark.json`. It performs one warm-up per image and reports repeated `model.predict` wall-clock timings. Do not compare this directly with the saved laptop benchmark unless the measurement protocol, input, runtime, and thread settings are matched.

## Optional laptop webcam to KV260 CPU preview

The project includes a simple HTTP inference server and laptop webcam client. The Gradio dashboard can use this endpoint for image/webcam snapshots and sampled video frames when `EDGEINSPECT_REMOTE_URL` is set. This integration has not been tested on the current board image. After the CPU runtime is installed, on KV260 run:

```bash
.venv/bin/python deployment/kv260/inference_server.py --host 0.0.0.0 --port 8765
```

On the laptop, with its project virtual environment active, start the standalone preview with:

```powershell
.\.venv\Scripts\python.exe deployment\kv260\stream_webcam_to_kv260.py --url http://<KV260-IP>:8765 --max-fps 1
```

To use the Gradio dashboard instead, set the endpoint in PowerShell before launch:

```powershell
$env:EDGEINSPECT_REMOTE_URL = "http://<KV260-IP>:8765"
.\.venv\Scripts\python.exe app\dashboard.py
```

Use only on a trusted private LAN: the prototype HTTP endpoint has no authentication or TLS. It uses the CPU model, applies a coarse color guard, and labels results as candidate detections. It does not prove FPGA/DPU use or production quality.

## Renesas connection

For the KV260-to-RA6E2 control messages, see [`../renesas/protocol.md`](../renesas/protocol.md) and the FSP example in `../renesas/ra6e2_fsp/`. The example cannot be flashed as-is: confirm the exact RA6E2 kit and select UART pins from that board's manual first.

## FPGA stack check

When the board is available, run [`check_fpga_stack.sh`](check_fpga_stack.sh) to inventory the OS, accelerator utilities, runtimes, and DPU-related firmware without changing the system. Then follow [`FPGA_NEXT_STEPS.md`](FPGA_NEXT_STEPS.md). The checker is read-only; it does not establish model compatibility by itself.
