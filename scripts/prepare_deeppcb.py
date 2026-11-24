"""Convert the official DeepPCB benchmark layout to Ultralytics YOLO format.

Expected source layout (the official repo uses this pattern):
  PCBData/
    trainval.txt
    test.txt
    group00041/00041000_test.jpg
    group00041/00041000_temp.jpg
    group00041/00041000.txt

The official trainval list is split into train/val (seeded); the official test list
is kept intact. Only *_test.jpg images are copied into the detector dataset. Template
images are intentionally not used as model inputs in this first baseline.

Usage:
  python scripts/prepare_deeppcb.py --source data/raw/DeepPCB/PCBData \
      --output data/processed/deep_pcb --seed 42

This script does not download or redistribute DeepPCB. Obtain it from the source and
check its research-use conditions before publishing or using it outside research.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Iterable

from PIL import Image
import yaml

CLASS_NAMES = ["open", "short", "mousebite", "spur", "copper", "pin-hole"]
# Original DeepPCB IDs are 1..6; YOLO IDs are zero-based.
SOURCE_CLASS_TO_YOLO = {i + 1: i for i in range(len(CLASS_NAMES))}
TOKEN_SPLIT = re.compile(r"[\s,]+")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


def read_split_list(path: Path) -> list[str]:
    items = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        value = raw.strip().replace("\\", "/")
        if not value or value.startswith("#"):
            continue
        value = re.sub(r"\.(jpg|jpeg|png|bmp|txt)$", "", value, flags=re.I)
        value = value.removeprefix("./")
        value = re.sub(r"_(test|temp)$", "", value, flags=re.I)
        items.append(value.strip("/"))
    return items


def index_files(source: Path) -> tuple[dict[str, Path], dict[str, Path]]:
    labels: dict[str, Path] = {}
    test_images: dict[str, Path] = {}
    for p in source.rglob("*.txt"):
        if p.name.lower() in {"trainval.txt", "test.txt", "readme.txt", "license.txt"}:
            continue
        labels[p.relative_to(source).with_suffix("").as_posix()] = p
    for p in source.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        stem = re.sub(r"_test$", "", p.stem, flags=re.I)
        # Ignore template images; inference is trained on the tested image only.
        if p.stem.lower().endswith("_temp"):
            continue
        key = (p.parent.relative_to(source) / stem).as_posix()
        test_images[key] = p
    return labels, test_images


def resolve_key(key: str, labels: dict[str, Path], images: dict[str, Path]) -> tuple[Path, Path]:
    candidates = [key]
    # Some split files list just the pair ID while files are nested under group folders.
    if "/" not in key:
        candidates.extend(k for k in labels if k.endswith("/" + key))
    for candidate in candidates:
        if candidate in labels and candidate in images:
            return images[candidate], labels[candidate]
    raise FileNotFoundError(f"Could not match split entry {key!r} to a test image and label file")


def parse_annotation_file(path: Path, width: int, height: int) -> list[str]:
    yolo_rows: list[str] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p for p in TOKEN_SPLIT.split(line) if p]
        if len(parts) != 5:
            raise ValueError(f"{path}:{line_no}: expected x1,y1,x2,y2,class_id; got {raw!r}")
        try:
            x1, y1, x2, y2 = map(float, parts[:4])
            source_class = int(parts[4])
        except ValueError as exc:
            raise ValueError(f"{path}:{line_no}: invalid numeric annotation {raw!r}") from exc
        if source_class not in SOURCE_CLASS_TO_YOLO:
            raise ValueError(f"{path}:{line_no}: class ID {source_class} is not in 1..6")
        # Clip tiny coordinate overshoots caused by rounding; reject degenerate boxes.
        x1 = min(max(x1, 0.0), float(width))
        x2 = min(max(x2, 0.0), float(width))
        y1 = min(max(y1, 0.0), float(height))
        y2 = min(max(y2, 0.0), float(height))
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"{path}:{line_no}: degenerate/out-of-frame bounding box {raw!r}")
        xc = ((x1 + x2) / 2.0) / width
        yc = ((y1 + y2) / 2.0) / height
        bw = (x2 - x1) / width
        bh = (y2 - y1) / height
        class_id = SOURCE_CLASS_TO_YOLO[source_class]
        yolo_rows.append(f"{class_id} {xc:.8f} {yc:.8f} {bw:.8f} {bh:.8f}")
    return yolo_rows


def split_train_val(keys: list[str], val_fraction: float, seed: int) -> tuple[list[str], list[str]]:
    if len(keys) < 2:
        raise ValueError("At least two official trainval entries are needed for a train/val split")
    shuffled = list(keys)
    random.Random(seed).shuffle(shuffled)
    val_count = max(1, round(len(shuffled) * val_fraction))
    val_count = min(val_count, len(shuffled) - 1)
    val = sorted(shuffled[:val_count])
    train = sorted(shuffled[val_count:])
    return train, val


def write_split(
    split: str,
    keys: Iterable[str],
    source: Path,
    out_root: Path,
    labels: dict[str, Path],
    images: dict[str, Path],
) -> dict:
    image_dir = out_root / "images" / split
    label_dir = out_root / "labels" / split
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)
    class_counts: Counter[str] = Counter()
    box_total = 0
    saved = 0
    for index, key in enumerate(sorted(keys)):
        image_path, label_path = resolve_key(key, labels, images)
        with Image.open(image_path) as image:
            width, height = image.size
            image.verify()
        rows = parse_annotation_file(label_path, width, height)
        safe_stem = f"{split}_{index:05d}_{Path(key).name}"
        target_image = image_dir / f"{safe_stem}{image_path.suffix.lower()}"
        target_label = label_dir / f"{safe_stem}.txt"
        shutil.copy2(image_path, target_image)
        target_label.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
        for row in rows:
            class_counts[CLASS_NAMES[int(row.split()[0])]] += 1
        box_total += len(rows)
        saved += 1
    return {"images": saved, "boxes": box_total, "class_counts": dict(class_counts)}


def prepare(source: Path, output: Path, seed: int, val_fraction: float) -> dict:
    source = source.resolve()
    output = output.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Source folder not found: {source}")
    trainval_file = source / "trainval.txt"
    test_file = source / "test.txt"
    if not trainval_file.exists() or not test_file.exists():
        raise FileNotFoundError(
            "Expected official trainval.txt and test.txt in the DeepPCB source folder. "
            "Do not randomly split the full dataset because that could invalidate the official test set."
        )
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Output folder is not empty: {output}. Choose a new folder or move it aside.")

    trainval = read_split_list(trainval_file)
    official_test = read_split_list(test_file)
    if set(trainval) & set(official_test):
        raise ValueError("The official trainval.txt and test.txt lists overlap")
    labels, images = index_files(source)
    # Validate all listed items before writing anything.
    for key in trainval + official_test:
        resolve_key(key, labels, images)

    train_keys, val_keys = split_train_val(trainval, val_fraction, seed)
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset": "DeepPCB",
        "source": str(source),
        "seed": seed,
        "val_fraction_of_official_trainval": val_fraction,
        "split_policy": "official trainval split into train/val; official test preserved untouched",
        "classes": CLASS_NAMES,
        "splits": {},
    }
    summary["splits"]["train"] = write_split("train", train_keys, source, output, labels, images)
    summary["splits"]["val"] = write_split("val", val_keys, source, output, labels, images)
    summary["splits"]["test"] = write_split("test", official_test, source, output, labels, images)

    yaml_path = output / "deep_pcb.yaml"
    data_yaml = {
        "path": str(output).replace("\\", "/"),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": {i: name for i, name in enumerate(CLASS_NAMES)},
    }
    yaml_path.write_text(yaml.safe_dump(data_yaml, sort_keys=False), encoding="utf-8")
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Folder containing trainval.txt, test.txt and group folders")
    parser.add_argument("--output", type=Path, default=Path("data/processed/deep_pcb"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    args = parser.parse_args()
    if not 0.05 <= args.val_fraction <= 0.3:
        parser.error("--val-fraction must be between 0.05 and 0.30")
    summary = prepare(args.source, args.output, args.seed, args.val_fraction)
    print(json.dumps(summary, indent=2))
    print(f"\nUltralytics data YAML: {args.output / 'deep_pcb.yaml'}")


if __name__ == "__main__":
    main()
