"""Client for the optional KV260 CPU HTTP inference endpoint."""
from __future__ import annotations

import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import cv2
import numpy as np


class RemoteInferenceError(RuntimeError):
    """Raised when the configured edge endpoint cannot inspect a frame."""


def inspect_frame(frame, base_url: str, timeout_s: float = 20.0):
    if not base_url or timeout_s <= 0:
        raise RemoteInferenceError("Remote endpoint URL and positive timeout are required")
    ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
    if not ok:
        raise RemoteInferenceError("Could not encode image for the KV260 endpoint")
    request = Request(
        base_url.rstrip("/") + "/inspect", data=encoded.tobytes(),
        headers={"Content-Type": "image/jpeg"}, method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise RemoteInferenceError(f"KV260 returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        raise RemoteInferenceError(f"Could not reach KV260 inference endpoint: {exc}") from exc

    if not payload.get("ok"):
        raise RemoteInferenceError(payload.get("error", "KV260 rejected the frame"))
    try:
        report = payload["report"]
        image_bytes = base64.b64decode(payload["annotated_jpeg_b64"], validate=True)
        annotated = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    except (KeyError, ValueError, TypeError) as exc:
        raise RemoteInferenceError("KV260 response was missing a valid report or image") from exc
    if annotated is None:
        raise RemoteInferenceError("KV260 returned an unreadable annotated image")

    latency = report.get("latency_ms")
    if isinstance(latency, (int, float)):
        report["latency_ms"] = {"end_to_end": float(latency)}
    elif not isinstance(latency, dict):
        report["latency_ms"] = {"end_to_end": 0.0}
    return report, annotated
