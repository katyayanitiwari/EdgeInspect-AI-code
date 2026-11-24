"""Generic YOLO detector training entry point for additional domains.

Examples (PowerShell, project root):
  python training/train_detector.py --data data/processed/deep_pcb/deep_pcb.yaml \
      --name PCB-EXP-001 --imgsz 640 --epochs 100 --batch 8 --device 0

This is intentionally separate from training/train.py so the existing NEU-DET
steel experiment recipe and saved checkpoints remain unchanged.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="Ultralytics dataset YAML")
    parser.add_argument("--name", required=True, help="New experiment name; never overwrite an existing run")
    parser.add_argument("--model", default="yolov8n.pt", help="Initial checkpoint or model name")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="0", help="GPU index, cpu, or another Ultralytics-supported device")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--patience", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = args.data if args.data.is_absolute() else (ROOT / args.data)
    if not data_path.is_file():
        raise FileNotFoundError(f"Dataset YAML not found: {data_path}")
    if args.imgsz < 320 or args.imgsz % 32:
        raise ValueError("--imgsz must be at least 320 and divisible by 32")
    if args.epochs < 1 or args.batch < 1:
        raise ValueError("--epochs and --batch must be positive")

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Ultralytics is not installed. Install the project's requirements first.") from exc

    candidate = Path(args.model)
    if not candidate.is_absolute() and (ROOT / candidate).exists():
        candidate = ROOT / candidate
    model = YOLO(str(candidate) if candidate.exists() else args.model)
    model.train(
        data=str(data_path),
        project=str(ROOT / "experiments"),
        name=args.name,
        exist_ok=False,
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        patience=args.patience,
        seed=args.seed,
        deterministic=True,
        optimizer="SGD",
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=5e-4,
        warmup_epochs=3,
        hsv_h=0.0,
        hsv_s=0.15,
        hsv_v=0.20,
        degrees=0.0,
        translate=0.05,
        scale=0.25,
        shear=0.0,
        perspective=0.0,
        fliplr=0.5,
        flipud=0.5,
        mosaic=0.5,
        close_mosaic=10,
        mixup=0.0,
        copy_paste=0.0,
        plots=True,
        save=True,
        verbose=True,
    )


if __name__ == "__main__":
    main()
