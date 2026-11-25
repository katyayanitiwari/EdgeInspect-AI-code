# EdgeInspect-AI - Steel Surface Defect Inspection

## Phase 1 Technical Report

**Bharat AI-SoC Challenge 2026-27 | PS5: Manufacturing and Industry 4.0**
Prepared by Katyayani Tiwari | 25 November 2026

## Project overview

EdgeInspect-AI is a demonstration-ready software prototype for steel-surface inspection. It detects six NEU-DET defect classes, displays candidate boxes for review, applies rule-based severity and quality-control guidance, and records an inspection summary. QR and barcode reading is available as a separate utility.

The selected model is YOLOv8n EXP-002 at 320 x 320 input. The prototype is scoped to crazing, inclusion, patches, pitted surface, rolled-in scale, and scratches. It is not a general-purpose detector for arbitrary products, bottles, or PCBs. Predictions are candidates for human review.

## Dataset and method

The preparation workflow checked image readability, removed one exact duplicate, validated Pascal VOC boxes, converted annotations to YOLO format, and made a stratified split. The prepared dataset contains 1,799 images: 1,259 train, 270 validation, and 270 test. The test split has 45 images per class.

Training logs identify Tesla T4 GPUs on Kaggle. Three 100-epoch comparison runs were evaluated on the same held-out test split. Laptop speed measurements used batch one on an Intel Core i5-13420H CPU.

## Recorded detector results

| Run | Model / input | Precision | Recall | mAP50 | mAP50-95 | Laptop ms / FPS |
|---|---|---:|---:|---:|---:|---:|
| EXP-001 | YOLOv8n / 640 | 0.6732 | 0.7478 | 0.7724 | 0.4307 | 92.28 / 10.8 |
| **EXP-002 selected** | **YOLOv8n / 320** | **0.7118** | **0.7093** | **0.7702** | **0.4361** | **36.65 / 27.3** |
| EXP-003 | YOLO11n / 640 | 0.7244 | 0.7186 | 0.7715 | 0.4327 | 93.10 / 10.7 |

EXP-002 was selected for the laptop prototype because its test scores were similar to the 640-pixel YOLOv8n run while its measured laptop latency was lower. This is not a Kria or Renesas speed result.

| Class | AP50 | Class | AP50 |
|---|---:|---|---:|
| Crazing | 0.4433 | Inclusion | 0.8828 |
| Patches | 0.9147 | Pitted surface | 0.8786 |
| Rolled-in scale | 0.5510 | Scratches | 0.9508 |

Crazing and rolled-in scale are the weakest classes in this test split and should receive further error review. These results do not establish performance on different factories, cameras, materials, or products.

## Software prototype

The laptop dashboard supports still images, webcam capture, and sampled video. It displays numbered candidate detections, class/confidence/box details, rule-based severity, quality-control guidance, and a local inspection log. QR and barcode reading is separate from the steel defect detector.

The static browser demo provides image/video input, camera sampling, built-in examples, QR/barcode reading, and browser-local history. Inference runs in the visitor's browser; the site is not connected to the Kria or Renesas board. The recorded interactive demo address is https://katyayanivlsi-edgeinspect-ai-live.static.hf.space/index.html; verify availability and camera permissions before presenting.

## Hardware and edge evidence

| Platform | Recorded use | Evidence status |
|---|---|---|
| Kaggle GPU | YOLOv8n and YOLO11n training | Experiment logs identify Tesla T4 GPUs. |
| Windows laptop | Dashboard, evaluation, and local language-model smoke run | Intel Core i5-13420H CPU; EXP-002 median total 36.65 ms/image. |
| AMD Kria KV260 | Six-image YOLO CPU smoke run at 320 px | Median 762.571 ms/image, about 1.31 images/s. No FPGA/DPU or camera path in this result. |
| Renesas board | UART protocol and firmware template prepared | Board-specific firmware build, flash, and physical exchange are not verified. |

## Llama and ExecuTorch

The saved local status record reports Llama 3.2 1B Instruct exported with ExecuTorch 1.6 using CPU/XNNPACK to an 802,035,968-byte `.pte` artifact. A laptop CPU smoke run loaded the artifact and generated tokens. This verifies the laptop software path only; the model has not been deployed to the Kria or Renesas board. A later re-export attempt ended with a Windows WinError 2, so repeatable export remains unresolved. Private gated model files and credentials are excluded from the public package.

## Validation summary

- **Software prototype:** detector, local inspection UI, rule-based severity/QC guidance, logging, and code reader are implemented.
- **Model evaluation:** three saved 100-epoch experiments were evaluated on the same held-out NEU-DET test split.
- **Target hardware:** Kria evidence is CPU-only and small-sample. FPGA/DPU acceleration and camera integration are unverified.
- **Full offline edge pipeline:** a complete disconnected camera-to-advisor-to-log pipeline on target hardware has not been demonstrated.

## Project outcome

The Phase 1 software prototype and its evidence-backed report package are prepared. The demonstration workflow is complete for the laptop/browser scope described here. Board-specific and full-system claims are limited to the test evidence recorded above.
