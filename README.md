# EdgeInspect-AI

EdgeInspect-AI is a laptop prototype for inspecting steel-surface defects and recording quality-control observations. It was prepared for the Bharat AI-SoC Challenge 2026–27, PS5 (Manufacturing & Industry 4.0). Its vision model was trained on NEU-DET and recognizes six labeled steel defect classes. It is not a general-purpose detector for arbitrary products.

## Project status

**Documentation refreshed 29 October 2026.** The model results below come from the saved experiment records. The dashboard and link were last confirmed responding on 15 October 2026; availability was not rechecked for this documentation refresh. No Raspberry Pi, Hailo, or ExecuTorch performance is claimed.

Three 100-epoch experiments were trained and evaluated on the 270-image held-out test split. EXP-002 (YOLOv8n at 320 pixels) is the selected laptop dashboard model: its accuracy was close to the other runs and it had lower measured laptop CPU latency. Crazing and rolled-in scale were weaker classes in the recorded class-level results.

| Experiment | Model | Input | Test mAP50 | Test mAP50–95 | Laptop CPU total | FPS |
|---|---|---:|---:|---:|---:|---:|
| EXP-001 | YOLOv8n | 640 | 0.7724 | 0.4307 | 92.28 ms | 10.8 |
| EXP-002 | YOLOv8n | 320 | 0.7702 | 0.4361 | 36.65 ms | 27.3 |
| EXP-003 | YOLO11n | 640 | 0.7715 | 0.4327 | 93.10 ms | 10.7 |

These figures are measurements on the laptop and NEU-DET test split, not target-device results. EXP-002 FP32 ONNX was also evaluated; its test mAP50 was 0.7559 and mAP50–95 was 0.4208. The dashboard continues to use the PyTorch checkpoint. The ONNX timing uses a separate method and is not directly comparable with the table above. Details are in `deployment/EXP-002_ONNX_NOTES.md` and `evaluation/EXP-002/`.

## Prototype features

The Gradio dashboard in `app/dashboard.py` supports image/webcam and video input, defect predictions with confidence and boxes, rule-based severity/QC guidance, QR/barcode reading, numbered inspection records, and local SQLite history. Its video feature samples frames; it is not a validated production line system. QR/barcode decoding is a separate function from defect detection.

The model has produced false detections on unrelated images. A scene/person filter is present, but it does not guarantee that every prediction is a real defect. Bottle, PCB, or other product accuracy has not been established. Treat results as prototype observations and manually review predictions.

## Run the dashboard on Windows

The project needs Python 3.11, the requirements in `requirements.txt`, and these two model files (included in this upload copy): `experiments/EXP-002/weights/best.pt` and `yolov8n.pt`.

From the project root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app\dashboard.py
```

The first command creates the environment; the second installs packages; the third starts the app. Open `http://127.0.0.1:7860/` while the process is running. The first startup may take a little while to load the model. Inspection history is saved locally under `logs/` and is not included in the upload.

Sample steel-defect and QR/barcode videos are under `app/samples/`. Dataset files are not included; the training/evaluation scripts need NEU-DET to be downloaded and prepared separately. See `scripts/prepare_neu_det.py` and `training/`.

## Links

- Source repository: https://github.com/katyayanitiwari/EdgeInspect-AI
- Project status site: https://katyayanitiwari.github.io/edgeinspect-ai-site/
- Laptop-hosted public dashboard: https://laptop-46vn7dls.tail278ad4.ts.net/ (last verified 15 October 2026; requires the laptop to be awake, online, signed in to Tailscale, and running the dashboard)
- Local dashboard: http://127.0.0.1:7860/

## What remains

1. Inspect false positives and missed defects on the held-out test examples, especially crazing and rolled-in scale.
2. Collect and label images of the actual target product under the intended camera and lighting; fine-tune only after collecting representative examples.
3. Confirm the Raspberry Pi and camera hardware, then measure the pipeline on the actual device.
4. Implement and verify the Llama-family advisor with ExecuTorch on the target device; the current advisor is rule-based.
5. Verify any Hailo/AI HAT+ path against current official documentation and actual hardware before claiming it works.
6. Validate end-to-end offline behavior, latency, memory use, and the final demo on the target setup.
7. Recheck official challenge dates and submission requirements before submitting.

See `PLAN.md`, `experiments/EXPERIMENTS.md`, `CHALLENGE.md`, and `EdgeInspect-AI_Project_Status.pdf` for project details. No Pi/Hailo/ExecuTorch measurements are recorded yet.
