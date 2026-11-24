"""CPU-first YOLO smoke test and benchmark for the Kria KV260.

Run on KV260 from the project root after a compatible Python/Ultralytics/PyTorch
runtime is installed:
  python3 deployment/kv260/smoke_infer.py \
    --weights experiments/EXP-002/weights/best.pt \
    --source deployment/kv260/test_images --imgsz 320 --device cpu

This measures the runtime actually installed on the board. It does not invoke a
DPU/PL accelerator and must not be described as FPGA acceleration.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[2]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def image_paths(source: Path) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image extension: {source.suffix}")
        return [source]
    if source.is_dir():
        return sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    raise FileNotFoundError(f"Input image/folder not found: {source}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weights", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True, help="One image or a folder of test images")
    ap.add_argument("--imgsz", type=int, default=320)
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--repeats", type=int, default=3, help="Measured repeats per image after one warm-up")
    ap.add_argument("--output", type=Path, default=Path("deployment/kv260/results"))
    args = ap.parse_args()

    weights = args.weights if args.weights.is_absolute() else ROOT / args.weights
    source = args.source if args.source.is_absolute() else ROOT / args.source
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if not weights.is_file():
        raise FileNotFoundError(f"Weights not found: {weights}")
    if args.imgsz < 32 or args.repeats < 1 or not 0.0 < args.conf < 1.0:
        raise ValueError("imgsz, repeats, and conf are outside valid ranges")

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "Ultralytics is not installed in this KV260 environment. Check the board OS, "
            "Python, aarch64 PyTorch wheel and compatible package versions before installing."
        ) from exc

    files = image_paths(source)
    if not files:
        raise SystemExit(f"No supported images found in {source}")
    model = YOLO(str(weights))
    output.mkdir(parents=True, exist_ok=True)

    measurements = []
    detection_rows = []
    for image_path in files:
        frame = cv2.imread(str(image_path))
        if frame is None:
            print(f"Skipping unreadable image: {image_path}")
            continue

        # One warm-up call is intentionally excluded from the reported timings.
        model.predict(frame, imgsz=args.imgsz, conf=args.conf, device=args.device, verbose=False)
        elapsed_ms = []
        last_result = None
        for _ in range(args.repeats):
            t0 = time.perf_counter()
            last_result = model.predict(
                frame, imgsz=args.imgsz, conf=args.conf, device=args.device, verbose=False
            )[0]
            elapsed_ms.append((time.perf_counter() - t0) * 1000.0)

        median_ms = statistics.median(elapsed_ms)
        measurements.append(median_ms)
        annotated = last_result.plot()
        out_image = output / f"{image_path.stem}_pred.jpg"
        cv2.imwrite(str(out_image), annotated)
        boxes = []
        for box, class_id, confidence in zip(
            last_result.boxes.xyxy, last_result.boxes.cls, last_result.boxes.conf
        ):
            boxes.append({
                "class": last_result.names[int(class_id)],
                "confidence": round(float(confidence), 5),
                "xyxy": [round(float(x), 2) for x in box.tolist()],
            })
        detection_rows.append({
            "image": str(image_path),
            "annotated_image": str(out_image),
            "detections": boxes,
            "latency_ms_each_repeat": [round(v, 3) for v in elapsed_ms],
            "median_latency_ms": round(median_ms, 3),
        })
        print(f"{image_path.name}: {len(boxes)} detection(s), median {median_ms:.2f} ms")

    if not measurements:
        raise SystemExit("No readable images were evaluated")
    all_sorted = sorted(measurements)
    summary = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
        "device_argument": args.device,
        "weights": str(weights),
        "imgsz": args.imgsz,
        "confidence_threshold": args.conf,
        "repeats_per_image_after_warmup": args.repeats,
        "images_measured": len(measurements),
        "median_latency_ms_across_images": round(statistics.median(measurements), 3),
        "mean_latency_ms_across_images": round(statistics.mean(measurements), 3),
        "approx_fps_from_median_latency": round(1000.0 / statistics.median(measurements), 3),
        "note": "CPU/runtime smoke benchmark only; not an FPGA/DPU acceleration result. Includes model.predict wall time.",
        "per_image": detection_rows,
    }
    summary_path = output / "kv260_cpu_smoke_benchmark.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved benchmark: {summary_path}")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_image"}, indent=2))


if __name__ == "__main__":
    main()
