"""Send a laptop webcam JPEG to the KV260 CPU inference preview endpoint.

Requires OpenCV on the laptop. Press q in the preview window to stop. This is a
simple request/response LAN demo, not a production stream or FPGA benchmark.
"""
from __future__ import annotations

import argparse
import base64
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import cv2
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="For example http://192.168.1.50:8765")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--max-fps", type=float, default=1.0,
                        help="Limit requests; CPU inference on KV260 is slow")
    parser.add_argument("--quality", type=int, default=82)
    args = parser.parse_args()
    if args.timeout <= 0 or not 0.1 <= args.max_fps <= 5 or not 30 <= args.quality <= 100:
        parser.error("timeout, max-fps, or JPEG quality is out of range")
    endpoint = args.url.rstrip("/") + "/inspect"
    capture = cv2.VideoCapture(args.camera)
    if not capture.isOpened():
        raise SystemExit(f"Could not open webcam index {args.camera}")
    period = 1.0 / args.max_fps
    print("Sending webcam frames to KV260 CPU. Press q in the preview to stop.")
    print("Only use a trusted private network; this endpoint is unauthenticated HTTP.")
    try:
        while True:
            started = time.perf_counter()
            ok, frame = capture.read()
            if not ok:
                print("Webcam frame read failed; stopping.")
                break
            encoded_ok, encoded = cv2.imencode(
                ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, args.quality]
            )
            if not encoded_ok:
                print("JPEG encoding failed; skipping frame.")
                continue
            request = Request(endpoint, data=encoded.tobytes(),
                              headers={"Content-Type": "image/jpeg"}, method="POST")
            try:
                with urlopen(request, timeout=args.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if not payload.get("ok"):
                    raise RuntimeError(payload.get("error", "server rejected frame"))
                annotated = cv2.imdecode(
                    np.frombuffer(base64.b64decode(payload["annotated_jpeg_b64"]),
                                  dtype=np.uint8), cv2.IMREAD_COLOR
                )
                report = payload["report"]
                elapsed = time.perf_counter() - started
                if annotated is None:
                    raise RuntimeError("server returned an unreadable preview image")
                label = (f"{report['decision']} | {report['defect_count']} candidates | "
                         f"KV260 CPU {report.get('latency_ms', '—')} ms")
                cv2.putText(annotated, label, (8, annotated.shape[0] - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                cv2.imshow("EdgeInspect-AI — remote KV260 CPU preview", annotated)
                print(label)
            except (HTTPError, URLError, TimeoutError, ValueError, KeyError, RuntimeError) as exc:
                print(f"Remote inference failed: {exc}")
                cv2.imshow("EdgeInspect-AI — laptop camera", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(max(0.0, period - (time.perf_counter() - started)))
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
