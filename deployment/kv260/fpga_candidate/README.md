# EXP-002 FPGA conversion candidate

`EXP-002_best.onnx` is copied from the project's existing EXP-002 ONNX export. It is included as an input candidate for a later, version-matched Vitis AI/DPU conversion attempt.

## Known facts

- Source checkpoint: YOLOv8n EXP-002, 320 × 320 input.
- Export: FP32 ONNX, batch 1, fixed 320 × 320 input, opset 12; graph simplification disabled.
- File size: 12,116,660 bytes.
- SHA-256: `70ADEF5E7EB75740D0FBAD524D2841D4040343C157232FDB5C5415E76F25E892`.
- Saved laptop held-out test result for this ONNX export: precision 0.6806, recall 0.7338, mAP50 0.7559, mAP50–95 0.4208.
- Saved EXP-002 PyTorch checkpoint result on the same test split: precision 0.7118, recall 0.7093, mAP50 0.7702, mAP50–95 0.4361.

These are saved laptop evaluation results, not new measurements. The ONNX export scored lower than the PyTorch checkpoint in the recorded test. Keep this file as a conversion experiment input; the laptop app should continue using the PyTorch checkpoint unless a later validated result changes that choice.

## What is not established

This ONNX file has not been compiled for a KV260 DPU and has not run on the FPGA. ONNX validity does not establish DPU operator support, correct compilation, acceleration, or target-board accuracy. Compile only with a toolchain and DPU platform verified for the exact KV260 image/overlay. Save the compiler report and compare board outputs against the CPU reference before making an FPGA claim.
