# EdgeInspect-AI

EdgeInspect-AI is a prototype for inspecting steel-surface defects and recording quality-control observations. It was prepared for the Bharat AI-SoC Challenge 2026–27, PS5 (Manufacturing & Industry 4.0). Its current vision model was trained on NEU-DET and recognizes six labeled steel defect classes. It is not a general-purpose detector for arbitrary products.

## Project status

**Documentation refreshed 24 November 2026.** Experiment figures below come from saved records. The free public browser demo page, ONNX model, and inference/code-reading libraries returned HTTP 200 on 13 November 2026. Camera permission and end-to-end browser speed have not been measured.

Three 100-epoch experiments were evaluated on the 270-image held-out test split. EXP-002 (YOLOv8n at 320 pixels) is selected for the laptop dashboard because its test accuracy was similar to the other runs and its recorded laptop CPU latency was lower. Crazing and rolled-in scale were weaker classes in the saved class-level results.

| Experiment | Model | Input | Test mAP50 | Test mAP50–95 | Laptop CPU total | FPS |
|---|---|---:|---:|---:|---:|---:|
| EXP-001 | YOLOv8n | 640 | 0.7724 | 0.4307 | 92.28 ms | 10.8 |
| EXP-002 | YOLOv8n | 320 | 0.7702 | 0.4361 | 36.65 ms | 27.3 |
| EXP-003 | YOLO11n | 640 | 0.7715 | 0.4327 | 93.10 ms | 10.7 |

These are laptop measurements on the NEU-DET test split, not hardware deployment results. EXP-002 FP32 ONNX was evaluated separately and recorded test mAP50 0.7559 and mAP50–95 0.4208, so the dashboard remains on PyTorch. The ONNX timing method differs from the table above; see `deployment/EXP-002_ONNX_NOTES.md` and `evaluation/EXP-002/`.

## Prototype features and limits

The Gradio dashboard in `app/dashboard.py` supports image/webcam and video input, candidate defect boxes and confidence, rule-based severity/QC guidance, QR/barcode reading, numbered inspection records, and local SQLite history. Video inspection samples frames. The free public static browser demo supports photo/video upload, live camera sampling and frame capture, QR/barcode reading, built-in samples, unique detection IDs, project-rule severity/QC guidance, and per-browser localStorage history. It uses the fully trained EXP-002 checkpoint converted to ONNX; images are processed in the visitor browser. The ONNX export test mAP50/mAP50–95 were 0.7559/0.4208; browser speed has not been measured. An optional launcher can enable a private local ExecuTorch Llama explanation; rule-based severity and decisions remain authoritative. The Llama output is experimental, can be omitted when it is not relevant to the detected class, and has not been validated for production use.

### Llama + ExecuTorch access status

Hugging Face access was approved and the authorized Llama 3.2 1B Instruct files were downloaded locally. The isolated ExecuTorch 1.6 CPU environment exported an XNNPACK `.pte` file (802,035,968 bytes). A local smoke run loaded that file and generated tokens on the laptop CPU. The `.pte`, checkpoint, tokenizer, and isolated runtime are in `LOCAL_ONLY_DO_NOT_UPLOAD/` and are excluded from uploads. A Python runner adapter is available through `run_dashboard_with_llama_windows.bat`; the usual dashboard launcher continues to use rule-based advice. On one synthetic adapter call, Llama returned generic text, so the adapter now filters out explanations that do not mention a reported defect class and asks for rule-based fallback when its output is not relevant. Board compatibility and output quality remain unverified.

To start the dashboard with the private laptop Llama runtime, double-click this file from the BHARAT EDGE folder:

```powershell
.\run_dashboard_with_llama_windows.bat
```

The optional Llama launcher starts the private Python runner as a separate process for each inspection, so cold-start delay may be noticeable. The standard dashboard launcher remains available for quick rule-only inspection. No C++ runner or Arm-board run has been completed. `LOCAL_ONLY_DO_NOT_UPLOAD/` contains private model/runtime material and is excluded by `.gitignore`; never upload it or the model weights.

The model has produced false detections on unrelated images. Its person/scene filter does not guarantee that every prediction is a real defect. NEU-DET does not establish accuracy for bottles, PCBs, or arbitrary products. Manually review detections. A separate PCB model and evaluation are required before the system can report PCB defects.

## Hardware deployment status (measurements through 2 Nov 2026; preparation updated 12 Nov 2026)

The Kria KV260 booted Ubuntu 24.04.2 LTS (aarch64, kernel 6.8.0-1015-xilinx, Python 3.12.3). The EXP-002 CPU runtime was installed offline from the prepared Crucial X9 transfer bundle. CPU inference succeeded on six held-out NEU-DET images at 320 px. Measured median latency was 762.571 ms/image across those six sample images (approximately 1.311 FPS). This is a CPU smoke run, not an accuracy validation or FPGA/DPU result. The concise measurement record is `deployment/kv260/kv260_cpu_smoke_summary.json`; the full board JSON and annotated images are currently on the Crucial X9 under `EdgeInspect-KV260-results-2026-11-02/`.

The KV260-to-RA6E2 UART protocol and Renesas FSP application template are in `deployment/renesas/`. The Renesas board has not yet been identified precisely, built, flashed, or measured. The parser has a source-level input-validation improvement, not a physical test.

The Windows laptop can be used to edit files and transfer them over Ethernet/SSH. The application itself runs on Linux on the KV260. KV260 CPU inference is the first target milestone. FPGA/DPU acceleration must use a Vitis AI image, DPU platform, compiler, and runtime that AMD documents as a matching KV260 release combination. A generic/new Vitis AI version is not evidence of KV260 compatibility.

The RA6E2 is a low-bandwidth controller for status/trigger messages and indicators; it does not run the vision model. Confirm the exact board variant (for example, FPB-RA6E2 or EK-RA6E2) before wiring or selecting UART pins. The firmware template needs a board-specific FSP project and has not been built or flashed.

The current official PS5 page lists Llama and ExecuTorch as required technologies, Hailo as optional, and Raspberry Pi 5/Arm-based devices among the hardware choices. The planned KV260/Renesas deployment is an additional project track and does not replace the Llama + ExecuTorch requirement. See `CHALLENGE.md` and recheck the official page for submission updates.

## Run the dashboard on Windows

The project needs Python 3.11, packages in `requirements.txt`, and these checkpoints: `experiments/EXP-002/weights/best.pt` and `yolov8n.pt`.

From PowerShell at the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app\dashboard.py
```

Then open `http://127.0.0.1:7860/` while the dashboard process is running. First startup may take a while to load model weights. Inspection history is stored locally under `logs/`.

The sample videos and QR/barcode images are in `app/samples/`. Dataset files are not included; obtain and prepare the datasets separately using the scripts in `scripts/` and `training/`.

## Links

- Phase 1 technical report (PDF): `reports/EdgeInspect-AI_Phase1_Technical_Report.pdf`
- Phase 1 technical report source: `reports/Phase1_Technical_Report.md`
- Submission source ZIP: `EdgeInspect-AI-Phase1-Source.zip` (curated; excludes private/local-only files)
- Source repository for this folder copy: https://github.com/katyayanitiwari/EdgeInspect-AI-code
- Project status website: https://katyayanitiwari.github.io/edgeinspect-ai-site/
- Free public interactive browser demo: https://katyayanivlsi-edgeinspect-ai-live.static.hf.space/index.html (static hosted site; laptop not required; inference runs in the visitor browser)
- Local dashboard: http://127.0.0.1:7860/

## Remaining work

1. Reconnect the Crucial X9 to Windows and copy the full Kria benchmark JSON and annotated images from `EdgeInspect-KV260-results-2026-11-02/` into this project.
2. Measure memory and repeat CPU latency on a larger representative image set; the current six-image smoke run does not establish board accuracy or a stable performance baseline.
3. Confirm the exact Renesas board variant. Configure its UART pins from the board manual and FSP project; build, flash, and verify message/ACK exchange using `deployment/renesas/protocol.md`.
4. Investigate a version-matched KV260 FPGA/DPU flow; the current verified KV260 path is CPU-only.
5. Validate the optional Llama dashboard launcher with real inspection examples; refine output quality and measure cold-start, latency, and memory. Then build/run a compatible ExecuTorch runtime for the intended Linux/Arm target. The current `.pte` was only smoke-run on laptop CPU; see `deployment/executorch/`.
6. Run and validate the prepared KV260 CPU HTTP endpoint and optional Gradio remote mode on the physical board. The code path is wired but not hardware-tested; the default webcam/video inspection remains laptop-local.
7. Obtain the DeepPCB data under its research-use conditions, attach it with the project copy to Kaggle, and run `training/kaggle_deeppcb.ipynb` to prepare, train a separate checkpoint, and evaluate on the untouched official test split. No PCB images or trained PCB model are included in this project copy.
8. Reconnect the Crucial X9 and copy the full KV260 benchmark JSON/annotated images into this project. The six-image CPU smoke run is not a full accuracy validation.
9. Confirm the exact Renesas board variant, configure its UART pins from the board manual and FSP project, build/flash, and verify message/ACK exchange.
10. Recheck the official challenge page and submission format before submitting.

The saved EXP-002 per-class AP review is in `evaluation/EXP-002/ERROR_ANALYSIS.md`. It does not contain image-level false-positive/false-negative counts because those prediction files are absent from this project copy.

The public challenge page lists Phase 1 as 23 November 2026; the newer organizer email received 23 November gives an extended deadline of 25 November 2026, 11:59 pm IST. It lists Phase 2 as 5 February 2027. Recheck the form before submission: https://arm-education.github.io/Arm-Developer-Labs/Bharat_AI_SoC_2026_27.html
