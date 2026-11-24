"""Synthetic tests for the DeepPCB-to-YOLO converter (no downloaded dataset needed)."""
import tempfile
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.prepare_deeppcb import prepare, parse_annotation_file  # noqa: E402


def make_pair(root: Path, group: str, stem: str, x_offset: int = 0) -> None:
    folder = root / group
    folder.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (640, 640), "white").save(folder / f"{stem}_test.jpg")
    Image.new("RGB", (640, 640), "white").save(folder / f"{stem}_temp.jpg")
    (folder / f"{stem}.txt").write_text(f"{10+x_offset},20,110,120,1\n", encoding="utf-8")


def test_annotation_conversion():
    with tempfile.TemporaryDirectory() as tmp:
        label = Path(tmp) / "a.txt"
        label.write_text("10,20,110,120,1\n", encoding="utf-8")
        rows = parse_annotation_file(label, 640, 640)
        assert rows == ["0 0.09375000 0.10937500 0.15625000 0.15625000"]


def test_split_conversion_preserves_official_test():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "PCBData"
        for i in range(10):
            make_pair(root, "group00001", f"00001{i:03d}", i)
        (root / "trainval.txt").write_text("\n".join(f"group00001/00001{i:03d}" for i in range(8)), encoding="utf-8")
        (root / "test.txt").write_text("\n".join(f"group00001/00001{i:03d}" for i in range(8, 10)), encoding="utf-8")
        out = Path(tmp) / "processed"
        summary = prepare(root, out, seed=42, val_fraction=0.25)
        assert summary["splits"]["train"]["images"] == 6
        assert summary["splits"]["val"]["images"] == 2
        assert summary["splits"]["test"]["images"] == 2
        assert summary["splits"]["test"]["boxes"] == 2
        assert (out / "deep_pcb.yaml").is_file()
        assert len(list((out / "images" / "test").glob("*.jpg"))) == 2


if __name__ == "__main__":
    test_annotation_conversion()
    test_split_conversion_preserves_official_test()
    print("All DeepPCB preparation tests passed.")
