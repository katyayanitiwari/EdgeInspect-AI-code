# EXP-002 saved-results review

This is a desk review of the saved held-out evaluation JSON files. It does not rerun the model or inspect individual test predictions. Dataset images are not present in this Desktop project copy, so image-level false-positive/false-negative counts are not available here.

## PyTorch checkpoint: measured test AP

Saved source: `evaluation/EXP-002/metrics.json`, 270 NEU-DET test images, 320 px input.

| Class | AP50 | AP50–95 | Review note |
|---|---:|---:|---|
| crazing | 0.4433 | 0.1665 | Lowest class AP; inspect missed/loose crack-network labels first. |
| rolled-in_scale | 0.5510 | 0.2442 | Second-lowest class AP; inspect confusing texture and box boundaries. |
| inclusion | 0.8828 | 0.4724 | AP50 is high; stricter localization score is lower. |
| patches | 0.9147 | 0.6077 | Strongest AP50–95 among these six classes. |
| pitted_surface | 0.8786 | 0.5528 | Strong AP50; localization still has room to improve. |
| scratches | 0.9508 | 0.5728 | Highest AP50; stricter localization remains lower than AP50. |

Overall saved results: precision 0.7118, recall 0.7093, F1 0.7105, mAP50 0.7702, and mAP50–95 0.4361. These are test-split measurements for the NEU-DET steel domain only.

## ONNX comparison

Saved ONNX metrics are in `evaluation/EXP-002/onnx_metrics.json`. On the same 270-image test split, ONNX mAP50 was 0.7559 and mAP50–95 was 0.4208, compared with 0.7702 and 0.4361 for PyTorch. The largest per-class AP50 decrease was crazing: 0.4433 to 0.3969. ONNX remains a conversion candidate, not the dashboard default or a validated board artifact.

## What this does not tell us

- The saved metrics JSON does not include class-by-class FP/FN examples or a current EXP-002 confusion-matrix image.
- AP alone does not identify the exact camera, lighting, contrast, or product causes of an error.
- The report does not validate bottles, arbitrary objects, PCB component placement, or Renesas/Kria hardware.

For image-level analysis, restore the prepared NEU-DET test images/labels, rerun the saved checkpoint with the same 320 px/confidence/NMS settings, and inspect the generated confusion matrix plus per-image predictions. Record actual counts and representative filenames only after that run.
