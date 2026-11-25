# BHARAT EDGE — source package guide

The public repository contains the Windows dashboard and its dependencies, the selected EXP-002 detector checkpoint, evaluation records, training/evaluation scripts, public static-demo source/assets, KV260 and Renesas source/templates, ExecuTorch adapter/export instructions, the Phase 1 report, and the two-minute walkthrough at `demo/EdgeInspect-AI-Phase1-Demo.mp4`. The walkthrough should also be uploaded publicly to YouTube or Google Drive if the submission form requires a hosted video URL. The curated ZIP archive is maintained separately in the local BHARAT EDGE folder and is not duplicated in this repository.

## Run the Windows application

1. Extract the archive.
2. Open PowerShell in the extracted `EdgeInspect-AI-Phase1-Source` folder.
3. Run `setup_windows.bat` once. This installs Python dependencies and checks the environment; it requires internet access for package installation.
4. Run `run_dashboard_windows.bat`.
5. Open `http://127.0.0.1:7860/` while the PowerShell window is running.

The selected weights are included at `experiments/EXP-002/weights/best.pt`. Dataset images are not included; the dashboard can still inspect uploaded images with the saved checkpoint. Retraining and test evaluation require obtaining the NEU-DET dataset and following `README.md` and `scripts/prepare_neu_det.py`.

## What is included for Llama + ExecuTorch

The archive contains the dashboard adapter (`inference/llama_exec_runner.py`), XNNPACK export configuration, setup/download instructions, and the safe gated-model downloader. It intentionally does not contain Llama weights, tokenizer, `.pte`, Hugging Face token, or the private ExecuTorch environment. Model owners must download the gated files themselves after approval and keep them in the ignored `LOCAL_ONLY_DO_NOT_UPLOAD/` folder. The recorded laptop export does not verify deployment on an Arm board.

## Target-board files

Kria CPU smoke scripts/record and FPGA investigation notes are included. The recorded KV260 result is CPU-only; no FPGA/DPU result is included or claimed. Renesas protocol and firmware source template are included; board build/flash/UART exchange is not verified. See the report and `UPLOAD_CHECKLIST.md` for remaining validation.

## Deliberate exclusions

Private/gated model artifacts, tokens, personal notes/prompts, local logs, Python virtual environments, inspection history, datasets, temporary outputs, and the fictional sample report are excluded. The package manifest lists included files. The sample MP4/WebM files are demo inputs; they are **not** a recording of the project demonstration required for submission.

The sample MP4/WebM files are dashboard inputs. The project walkthrough is a generated, captioned asset-based video, not a live GUI capture. Before submitting, review it and verify the challenge form requirements, public demo links, and any required hosted video URL.
