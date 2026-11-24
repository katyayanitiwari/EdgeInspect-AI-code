# EdgeInspect-AI on Windows (development-first setup)

This is the **Windows laptop development path**. You can build and run the current EdgeInspect-AI Python application on Windows, use the laptop's built-in webcam, run the trained steel model, work on the PCB model, and develop the dashboard without installing Linux on your laptop.

## Important hardware distinction

- **Windows laptop:** coding, dataset preparation, training/validation, webcam capture, dashboard, and initial CPU/GPU experiments.
- **Kria KV260:** the final edge target for the ARM/FPGA deployment track. The normal KV260 software stack for this project boots a supported Linux image on the board. Windows on the laptop does not mean Windows is installed on KV260.
- We will only move the application/model to KV260 after it works on Windows. KV260-side runtime and accelerator packaging will be handled separately for its Linux/ARM environment.

## Prerequisites

1. 64-bit Windows 10/11.
2. Python **3.11 x64** installed and available through the Windows Python Launcher (`py -3.11`).
3. At least 10 GB of free space for the environment and model/development outputs. Dataset storage needs additional space.
4. Internet connection for the first dependency installation.

## One-time setup

1. Extract the project ZIP to a writable folder, for example `C:\Projects\EdgeInspect-AI-code`.
2. Open that folder in File Explorer.
3. Double-click `setup_windows.bat` or run it from PowerShell/CMD:

```powershell
.\setup_windows.bat
```

The script creates `.venv`, installs a CPU-only PyTorch build and the packages in `requirements.txt`, then checks the important imports. CPU-only is intentional for a reproducible first baseline; CUDA can be configured later if the laptop has a compatible NVIDIA GPU.

## Run the existing steel model with the laptop webcam

Double-click `run_webcam_windows.bat`, or run:

```powershell
.\.venv\Scripts\python.exe inference\detect.py --weights experiments\EXP-002\weights\best.pt --source 0 --imgsz 320
```

Press `q` in the camera window to exit and `s` to save an annotated frame and JSON inspection report. The steel model is trained on NEU-DET steel-surface images. A normal laptop webcam view is useful for checking camera access and application execution, but arbitrary objects in the room are **not valid accuracy tests** for this steel model.

For a proper accuracy evaluation, use the held-out NEU-DET test images and run the evaluation workflow documented in `README.md` and `evaluation/`.

## Run the dashboard

```powershell
.\.venv\Scripts\python.exe app\dashboard.py
```

Then open `http://127.0.0.1:7860` in your browser. The dashboard uses the existing local steel checkpoint and writes inspection records locally.

## Verify the Windows environment

```powershell
.\.venv\Scripts\python.exe check_windows_env.py
```

The report states Python/Windows architecture, package versions, CPU/CUDA availability, checkpoint presence, and camera availability. It does not measure KV260 performance.

## Troubleshooting

- If `py -3.11` is not found, install Python 3.11 x64 and enable the Python Launcher during installation.
- If the webcam does not open, close apps already using it and try camera index `1` instead of `0` by editing the command to `--source 1`.
- If PowerShell blocks a script, run the `.bat` file from Command Prompt, or use `cmd /c setup_windows.bat`.
- Do not copy the laptop `.venv` to KV260. Windows packages are x86-64; KV260 is ARM64 and needs a separate compatible environment.
- Do not overwrite `experiments/EXP-002/weights/best.pt`. It is the current selected steel checkpoint.

## What we do next

1. Verify Windows dependencies and the existing checkpoint.
2. Run held-out steel test images and preserve baseline metrics.
3. Run the dashboard and laptop webcam path.
4. Build and validate the separate PCB model.
5. Add the Windows-to-KV260 LAN inference client/server path.
6. Move the validated inference service to KV260 Linux/ARM, then investigate FPGA/DPU acceleration.
7. Add Renesas BGK-RA6E2 as the inspection I/O controller after defining and checking its UART pin/jumper configuration.
