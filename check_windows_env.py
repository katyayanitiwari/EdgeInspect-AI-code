"""Check the local Windows development environment for EdgeInspect-AI."""
from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEIGHTS = ROOT / "experiments" / "EXP-002" / "weights" / "best.pt"


def version_of(module_name: str) -> str:
    try:
        module = importlib.import_module(module_name)
        return str(getattr(module, "__version__", "installed"))
    except Exception as exc:  # report the import failure without hiding other checks
        return f"IMPORT FAILED: {type(exc).__name__}: {exc}"


def main() -> int:
    print("=== EdgeInspect-AI Windows environment ===")
    print(f"OS: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]} ({platform.architecture()[0]})")
    if platform.system() != "Windows":
        print("WARNING: This diagnostic is intended for the Windows laptop path.")

    for name in ("numpy", "cv2", "PIL", "yaml", "ultralytics", "gradio", "torch"):
        print(f"{name}: {version_of(name)}")

    try:
        import torch
        print(f"PyTorch device: {'CUDA available' if torch.cuda.is_available() else 'CPU'}")
        if torch.cuda.is_available():
            print(f"CUDA runtime reported by PyTorch: {torch.version.cuda}")
    except Exception as exc:
        print(f"PyTorch device check failed: {exc}")

    print(f"Selected steel checkpoint: {'FOUND' if WEIGHTS.is_file() else 'MISSING'}")
    if WEIGHTS.is_file():
        print(f"Checkpoint size: {WEIGHTS.stat().st_size / (1024 * 1024):.2f} MiB")

    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        camera_ok = cap.isOpened()
        if camera_ok:
            ok, frame = cap.read()
            camera_ok = bool(ok and frame is not None)
        cap.release()
        print(f"Default webcam (index 0): {'AVAILABLE' if camera_ok else 'NOT DETECTED'}")
    except Exception as exc:
        print(f"Webcam check failed: {type(exc).__name__}: {exc}")

    return 0 if WEIGHTS.is_file() else 2


if __name__ == "__main__":
    raise SystemExit(main())
