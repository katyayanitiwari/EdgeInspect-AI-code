# EdgeInspect-AI - Final Project Report (Phase 1)

**Bharat AI-SoC Challenge 2026-27 · PS5: Manufacturing & Industry 4.0**
**Prepared 24 November 2026 from saved records. Latest saved model evaluations are dated 9 October; the KV260 CPU smoke record is dated 2 November; the local ExecuTorch status record is dated 13 November.**
**Organizer email dated 23 November gives the submission deadline as 25 November 2026, 11:59 pm IST.**

## Executive summary

EdgeInspect-AI is a working software prototype for steel-surface inspection. It combines a YOLOv8n detector trained on NEU-DET, a local inspection dashboard, rule-based severity and quality-control guidance, QR/barcode reading, and inspection history. A public browser demo is available. Laptop model evaluation is documented. A small CPU inference smoke run was also recorded on the AMD Kria KV260.

The prototype is **not a completed end-to-end target-hardware integration**. Llama 3.2 1B was exported to ExecuTorch and smoke-run on the Windows laptop CPU, but has not been deployed to an Arm board. The KV260 result is CPU-only; FPGA/DPU acceleration has not been run. The Renesas firmware has not been built or tested on the board. These distinctions matter for a truthful Phase 1 submission.

## System and data

The selected detector is **YOLOv8n, EXP-002, 320 × 320 input**, trained for 100 epochs on the six NEU-DET steel defect classes: crazing, inclusion, patches, pitted surface, rolled-in scale, and scratches. The prepared dataset contains 1,799 images after removal of one exact duplicate, split into 1,259 train, 270 validation, and 270 test images. Dataset files are not included in the upload copy; their source and preparation steps are documented in the project.

The model is specialized for these steel images. Results do not establish performance on bottles, printed circuit boards, or arbitrary manufactured products. False detections on unrelated scenes have been observed, so predictions require human review.

## Methodology

The preparation script inspects image and annotation pairs, removes corrupt files and exact duplicate images, validates Pascal VOC XML boxes, converts boxes to normalized YOLO labels, and makes a stratified 70/15/15 train/validation/test split with seed 42. The held-out test split was kept separate for the saved final evaluations.

Training used COCO-pretrained YOLOv8n and YOLO11n models. The selected EXP-002 run used YOLOv8n at 320 pixels for 100 epochs, batch 16, SGD (initial learning rate 0.01, momentum 0.937, weight decay 0.0005), seed 42, deterministic mode, and early-stopping patience 25. Augmentation included brightness, translation, scale, horizontal/vertical flips, and mosaic, with mosaic disabled for the final 10 epochs. Training logs identify Tesla T4 GPUs for the three comparison runs.

## Recorded detector results

All scores below are recorded measurements on the same 270-image held-out NEU-DET test split. Laptop speed uses the project’s saved batch-one timing procedure.

| Run | Model / input | Precision | Recall | mAP50 | mAP50-95 | Laptop total / FPS |
|---|---|---:|---:|---:|---:|---:|
| EXP-001 | YOLOv8n / 640 | 0.6732 | 0.7478 | 0.7724 | 0.4307 | 92.28 ms / 10.8 |
| **EXP-002 selected** | **YOLOv8n / 320** | **0.7118** | **0.7093** | **0.7702** | **0.4361** | **36.65 ms / 27.3** |
| EXP-003 | YOLO11n / 640 | 0.7244 | 0.7186 | 0.7715 | 0.4327 | 93.10 ms / 10.7 |

EXP-002 was selected for the laptop prototype because it retained similar test-set scores while recording lower laptop latency. Its weakest per-class AP50 values are crazing (0.4433) and rolled-in scale (0.5510). These are dataset test results, not board accuracy claims. A separate EXP-002 FP32 ONNX evaluation recorded mAP50 0.7559 and mAP50-95 0.4208; the dashboard’s primary model remains PyTorch.

## Hardware utilization and optimization

Training used a Kaggle Tesla T4 GPU as recorded in each experiment environment file. The Windows laptop (Intel Core i5-13420H, CPU-only for these runs) was used for local dashboard operation and the saved CPU inference comparisons. The Kria KV260 ran a small CPU-only smoke measurement on six images. No FPGA/DPU acceleration or camera pipeline was used in that measurement. A local Llama + ExecuTorch CPU smoke run was recorded on the Windows laptop; it has not been deployed to Kria. Renesas is represented by protocol and firmware-template source, not a verified hardware run.

The main measured speed/size trade-off was the 320-pixel YOLOv8n setting: EXP-002 recorded 36.65 ms total per image on the laptop, compared with 92.28 ms for EXP-001 at 640 pixels, while mAP50 was 0.7702 versus 0.7724 on the same test split. YOLO11n at 640 pixels was retained as a comparison, not selected for the laptop dashboard. FP32 ONNX was evaluated separately and scored mAP50 0.7559 / mAP50-95 0.4208, so the dashboard continues to use PyTorch. The dashboard samples video frames instead of running inference on every frame. The ExecuTorch export used an XNNPACK quantization configuration and produced an 802,035,968-byte artifact on the laptop; no target-device speed or memory improvement has been measured. These are prototype optimizations, not target-hardware performance claims.

## Application and demo

The Windows Gradio app supports still images, webcam capture, and sampled video; it displays numbered candidate detections, rule-based severity/QC recommendations, and a local inspection log. QR/barcode decoding is a separate function. The public static browser demo provides photo/video input, live camera sampling, QR/barcode reading, built-in samples, and browser-local history. Its inference runs in the visitor’s browser; it is not connected to a live Kria or Renesas service.

- Public interactive browser demo: https://katyayanivlsi-edgeinspect-ai-live.static.hf.space/index.html
- Project status site: https://katyayanitiwari.github.io/edgeinspect-ai-site/
- Source project reference: https://github.com/katyayanitiwari/EdgeInspect-AI-code

The links were recorded in the project README as responding on 13 November 2026; availability should be rechecked before submission. A two-minute captioned walkthrough has been assembled at `demo/EdgeInspect-AI-Phase1-Demo.mp4` from actual model outputs and project assets. It is not a live desktop capture or voiceover. Review it, then upload it publicly to YouTube or Google Drive; the organizer prefers 1080p, 16:9, MP4. The email also requests a public GitHub/GitLab repository, recommends mentor review, and says the project may be submitted only once.

## Edge and language-model status

**Laptop ExecuTorch:** The private local status record says the authorized Llama 3.2 1B Instruct files were downloaded, ExecuTorch 1.6 CPU/XNNPACK created an 802,035,968-byte `.pte`, and a laptop CPU smoke run loaded it and generated tokens. This verifies a local software path only. A later re-export attempt ended with a Windows `WinError 2`, so export reproducibility still needs fixing. Output relevance needs further review. The private model and runtime are excluded from this report package and must not be uploaded.

**Kria KV260 CPU:** The saved smoke record reports six held-out NEU-DET images at 320 px, median `model.predict` latency 762.571 ms/image and mean 764.019 ms/image (about 1.311 images/s). It used CPU inference, one excluded warm-up, and three timed repeats per image. This is a small smoke test, not a robust accuracy benchmark. No FPGA/DPU inference, camera capture, power measurement, or full live pipeline has been verified.

**Renesas:** UART protocol and firmware template files exist. The exact board variant and pin route have not been confirmed in the project evidence. Firmware build, flash, and physical request/response exchange are not verified.

## Completion matrix

| Area | Evidence-backed state | Remaining validation |
|---|---|---|
| NEU-DET detector | Three 100-epoch runs and saved held-out metrics | Error examples and broader validation |
| Laptop dashboard | Image/video/webcam workflow and local history code | Review prepared walkthrough and publish it |
| QR/barcode | Reader feature and samples are in the app | Show a clear decoded result if the demo/form requires it |
| Public browser demo | Static hosted demo URL documented | Recheck public availability and browser permissions |
| Llama + ExecuTorch | Laptop `.pte` export and CPU smoke recorded | Review outputs; build/run compatible Arm target runtime |
| Kria KV260 | CPU smoke inference on six images recorded | Repeatable benchmark; camera/API; FPGA/DPU path |
| Renesas UART | Protocol and source template prepared | Identify board; build, flash, and test physical exchange |
| Offline end-to-end | Individual local components exist | Verify complete disconnected pipeline on target hardware |
| Phase 1 package | Source and report materials exist in folder | Review final challenge form, make video, upload required deliverables |

## Immediate work before submission

1. Review `demo/EdgeInspect-AI-Phase1-Demo.mp4` (a generated, captioned asset-based walkthrough, not a live screen recording), then upload it publicly to YouTube/Google Drive and copy the URL. The clip shows model outputs, saved metrics, app capabilities, and hardware status with evidence boundaries; it does not claim a live end-to-end board demonstration.
2. Confirm the project repository is public on GitHub/GitLab, recheck the demo/status links, and review the form. Mentor review is recommended by the organizer.
3. Submit the public repository URL, public video URL, and this final PDF in the designated form fields. The organizer says to submit once only. Keep `LOCAL_ONLY_DO_NOT_UPLOAD/`, tokens, private notes, user inspection logs, and gated model files out of public uploads.
4. If time and board access allow, capture new Kria/Renesas results and replace “not verified” only after preserving logs and measurements.

## References and evidence

Project records: `README.md`, `CHALLENGE.md`, `evaluation/EXP-001/metrics.json`, `evaluation/EXP-002/metrics.json`, `evaluation/EXP-003/metrics.json`, `evaluation/EXP-002/ERROR_ANALYSIS.md`, `deployment/kv260/kv260_cpu_smoke_summary.json`, `docs/IMPLEMENTATION_STATUS.md`, and private local `LOCAL_ONLY_DO_NOT_UPLOAD/LLAMA_EXECUTORCH_STATUS.md` (used only to verify local Llama status; do not distribute private model files).

Official challenge page: https://arm-education.github.io/Arm-Developer-Labs/Bharat_AI_SoC_2026_27.html . The page lists Phase 1 deliverables as source code, an application, a technical report, and a demonstration video. Recheck the page and submission form for updates.
