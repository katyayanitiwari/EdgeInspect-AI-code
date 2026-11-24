# KV260 FPGA work plan

## What we can do before reconnecting the board

- Keep the already measured KV260 CPU smoke result as the known-good fallback.
- Prepare the read-only inventory script `check_fpga_stack.sh` and review the board image/runtime choices before installing anything.
- Check the YOLO export/conversion path on the development computer and document the exact input model, image size, quantization data, and compiler output needed. A successful export alone is not proof that the KV260 DPU can execute it.
- A saved FP32 ONNX export of EXP-002 is now copied to `fpga_candidate/EXP-002_best.onnx`; its SHA-256 and measured laptop accuracy are recorded beside it. This is a conversion input, not a DPU-ready model.
- A prototype CPU HTTP inference endpoint and laptop webcam client are included for a later trusted-LAN preview. They still need a physical KV260 run and are not wired into Gradio.
- Keep all new FPGA results separate from the existing CPU benchmark.

## Current verified position

The project has a successful, small KV260 **CPU** smoke run on six held-out NEU-DET images. The saved median was 762.571 ms per image (about 1.311 images/s) for that specific run. It is not an FPGA result or full accuracy benchmark.

Earlier board inspection found Ubuntu 24.04.2, aarch64, XRT 2.18 and `xmutil`, but no `xdputil`, VART/PYNQ runtime, or identified DPU overlay. The board also had no internet route at that time. These are historical observations; rerun the checker after the board is available because its current state may have changed.

## Next time the KV260 is available

1. Boot it and log in over the existing serial connection.
2. If the CPU smoke deployment is already installed, do not reinstall its wheelhouse. From the copied USB bundle, run:

   ```bash
   bash deployment/kv260/check_fpga_stack.sh | tee ~/edgeinspect_fpga_stack_check.txt
   ```

3. Copy the resulting text back to the laptop. Do not install packages or switch overlays yet.
4. Match the exact board image, DPU overlay, compiler, and runtime to one supported vendor release. If no matching stack is present, preserve the current microSD and prepare/test a separate card or a restorable backup before changing the image.
5. Prove the DPU with a vendor-supported example first. Then attempt conversion of the selected YOLOv8n checkpoint and inspect the compiler report for unsupported or CPU-fallback operations.
6. Run the same held-out images on CPU and DPU and record model file, image size, accuracy, latency protocol, FPS, memory, and power. Report acceleration only after an actual DPU run.

## Important limit

The current `.pt` checkpoint cannot be assumed to run on the FPGA as-is. It needs a compatible export/quantization/compilation flow and a matching DPU runtime. Whether this model is supported remains unverified until the chosen compiler produces a usable artifact and the board executes it.

No board image, overlay, or installed package should be changed based only on this plan. Follow the matching AMD/Xilinx release documentation for the exact KV260 image and DPU stack.
