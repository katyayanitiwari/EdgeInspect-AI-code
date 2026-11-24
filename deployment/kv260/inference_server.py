"""Small CPU inference HTTP endpoint for a laptop webcam preview.

Run on KV260 after the existing CPU runtime is installed. It does not use XRT,
the FPGA fabric, or the DPU. Bind to a trusted private LAN only; this prototype
has no authentication or TLS.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from inference.detect import draw  # noqa: E402
from inference.severity import assess, load_rules  # noqa: E402

MAX_JPEG_BYTES = 8 * 1024 * 1024


def out_of_scope(frame: np.ndarray) -> str | None:
    """Apply the dashboard's coarse color guard; this is not a steel classifier."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    saturated = cv2.threshold(saturation, 60, 255, cv2.THRESH_BINARY)[1]
    color_fraction = cv2.countNonZero(saturated) / float(saturation.size)
    if color_fraction > 0.25:
        return f"{color_fraction:.0%} strongly colored pixels; use a close-up steel-surface frame."
    return None


def inspect_frame(server, frame: np.ndarray) -> tuple[dict, np.ndarray]:
    reason = out_of_scope(frame)
    if reason:
        report = {
            "decision": "MANUAL_REVIEW", "severity": "none", "defect_count": 0,
            "defects": [], "reasons": [reason], "status": "not_inspected",
            "device": "KV260 CPU; no DPU acceleration",
        }
        annotated = frame.copy()
        cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 42), (35, 35, 35), -1)
        cv2.putText(annotated, "NOT INSPECTED - outside coarse color guard",
                    (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 180, 255), 2)
        return report, annotated

    started = time.perf_counter()
    result = server.model.predict(frame, imgsz=server.imgsz,
                                  conf=server.rules["confidence"]["min"],
                                  device="cpu", verbose=False)[0]
    detections = [
        {"cls": result.names[int(cls)], "conf": float(conf), "xyxy": box.tolist()}
        for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf)
    ]
    report = assess(detections, frame.shape[1], frame.shape[0], server.rules)
    for number, defect in enumerate(report["defects"], 1):
        defect["id"] = f"D{number:02d}"
    report["latency_ms"] = {"end_to_end": round((time.perf_counter() - started) * 1000, 1)}
    report["status"] = "inspected_candidate"
    report["device"] = "KV260 CPU; no DPU acceleration"
    return report, draw(frame, report)


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "EdgeInspectKV260/0.1"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        self._send_json(200, {"ok": True, "model": str(self.server.weights),
                              "device": "CPU; no DPU acceleration"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/inspect":
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"ok": False, "error": "invalid Content-Length"})
            return
        if size <= 0 or size > MAX_JPEG_BYTES:
            self._send_json(413, {"ok": False, "error": "JPEG must be 1 byte to 8 MiB"})
            return
        if "image/jpeg" not in self.headers.get("Content-Type", "").lower():
            self._send_json(415, {"ok": False, "error": "Content-Type must be image/jpeg"})
            return
        encoded = self.rfile.read(size)
        if len(encoded) != size:
            self._send_json(400, {"ok": False, "error": "incomplete JPEG body"})
            return
        frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            self._send_json(400, {"ok": False, "error": "could not decode JPEG"})
            return
        try:
            report, annotated = inspect_frame(self.server, frame)
            ok, jpg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 82])
            if not ok:
                raise RuntimeError("could not encode annotated frame")
            self._send_json(200, {
                "ok": True, "report": report,
                "annotated_jpeg_b64": base64.b64encode(jpg.tobytes()).decode("ascii"),
            })
        except Exception as exc:  # return a bounded error rather than killing the server
            self._send_json(500, {"ok": False, "error": str(exc)[:300]})

    def log_message(self, fmt: str, *args) -> None:
        # Keep logs short; do not print image content or inspection details.
        print(f"{self.address_string()} {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path,
                        default=Path("experiments/EXP-002/weights/best.pt"))
    parser.add_argument("--rules", type=Path, default=Path("inference/severity_rules.yaml"))
    parser.add_argument("--host", default="127.0.0.1",
                        help="Use 0.0.0.0 only on a trusted private LAN")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--imgsz", type=int, default=320)
    args = parser.parse_args()
    weights = args.weights if args.weights.is_absolute() else ROOT / args.weights
    rules_path = args.rules if args.rules.is_absolute() else ROOT / args.rules
    if not weights.is_file():
        parser.error(f"weights not found: {weights}")
    if not rules_path.is_file():
        parser.error(f"severity rules not found: {rules_path}")
    if not 1 <= args.port <= 65535 or args.imgsz < 32:
        parser.error("port or image size is outside its valid range")

    server = HTTPServer((args.host, args.port), RequestHandler)
    server.model = YOLO(str(weights))
    server.rules = load_rules(rules_path)
    server.weights = weights
    server.imgsz = args.imgsz
    print(f"CPU inference endpoint ready at http://{args.host}:{args.port}")
    print("Private network only; no authentication/TLS; no DPU acceleration. Ctrl+C stops it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping EdgeInspect KV260 endpoint.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
