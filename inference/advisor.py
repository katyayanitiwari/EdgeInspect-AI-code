"""QC guidance from fixed rules, with an optional local ExecuTorch Llama runner.

The LLM may explain the report but must not change the severity or QC decision.
ExecuTorch is opt-in through environment variables; the normal offline dashboard
continues to use the deterministic rule-based advisor until a local runtime is
installed and configured.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

RULES_ENGINE = "rule-based template (ExecuTorch not configured)"
EXECUTORCH_ENGINE = "local ExecuTorch Llama runner"
EXECUTORCH_FALLBACK_ENGINE = "rule-based fallback (ExecuTorch unavailable)"

CLASS_NOTES = {
    "crazing": "network of fine surface cracks",
    "inclusion": "foreign material embedded in the surface",
    "patches": "irregular surface patch",
    "pitted_surface": "small cavities on the surface",
    "rolled-in_scale": "oxide scale pressed into the surface during rolling",
    "scratches": "linear scratch marks",
}

ACTIONS = {
    "PASS": "No defect detected above the confidence threshold. Part can continue.",
    "PASS_WITH_NOTE": "Minor defect only. Part can continue; record it for trend monitoring.",
    "REWORK": "Major defect. Hold the part and send it for rework or supervisor inspection.",
    "REJECT": "Critical defect. Reject the part and quarantine it. If several rejects of the same "
              "defect type occur in a row, check the upstream process.",
    "MANUAL_REVIEW": "The model is not confident. A QC operator must inspect this part manually "
                     "before a decision is made.",
}


def _rule_advice(report):
    lines = [f"Decision: {report['decision']} (overall severity: {report['severity']})",
             ACTIONS[report["decision"]]]
    for i, defect in enumerate(sorted(report["defects"], key=lambda d: -d["area_pct"]), 1):
        note = CLASS_NOTES.get(defect["cls"], defect["cls"])
        flag = " - low confidence, verify" if defect["uncertain"] else ""
        ref = defect.get("id", f"D{i:02d}")
        lines.append(f"{ref} — {defect['cls']} ({note}): {defect['severity']}, "
                     f"{defect['area_pct']}% of image, confidence {defect['conf']:.2f}{flag}")
    return "\n".join(lines)


def _llm_prompt(report):
    # Llama 3.2 Instruct chat framing; never send image bytes, paths, or user text.
    payload = {
        "decision": report["decision"],
        "severity": report["severity"],
        "defects": [
            {
                "id": defect.get("id", ""),
                "type": defect.get("cls", ""),
                "confidence": round(float(defect.get("conf", 0)), 2),
                "area_pct": round(float(defect.get("area_pct", 0)), 1),
                "severity": defect.get("severity", ""),
                "verify": bool(defect.get("uncertain", False)),
            }
            for defect in report["defects"][:3]
        ],
    }
    system = (
        "Explain industrial steel quality inspections in plain language. Use only the supplied "
        "findings. Keep the given decision and severity unchanged. If verify is true, ask for a "
        "manual check. In at most two short sentences, summarize findings and the next QC action."
    )
    user = "Inspection data: " + json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        + system
        + "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
        + user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
    )


def _executorch_advice(report):
    if os.environ.get("EDGEINSPECT_ADVISOR", "rules").strip().lower() != "executorch":
        return None, False

    python = Path(os.environ.get("EDGEINSPECT_EXECUTORCH_PYTHON", ""))
    runner = Path(__file__).with_name("llama_exec_runner.py")
    model = Path(os.environ.get("EDGEINSPECT_LLM_MODEL", ""))
    params = Path(os.environ.get("EDGEINSPECT_LLM_PARAMS", ""))
    tokenizer = Path(os.environ.get("EDGEINSPECT_LLM_TOKENIZER", ""))
    if not python.is_file() or not runner.is_file() or not model.is_file() or not params.is_file() or not tokenizer.is_file():
        return None, True

    try:
        timeout = float(os.environ.get("EDGEINSPECT_LLM_TIMEOUT", "60"))
        if timeout <= 0:
            return None, True
        result = subprocess.run(
            [str(python), str(runner), "--model", str(model), "--params", str(params),
             "--tokenizer", str(tokenizer), "--prompt", _llm_prompt(report)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
        marker = "EDGEINSPECT_RESULT:"
        output = result.stdout.rsplit(marker, 1)[-1].strip() if marker in result.stdout else ""
        if result.returncode != 0 or not output:
            return None, True
        answer_lower = output.lower()
        class_terms = set()
        for defect in report["defects"]:
            name = defect.get("cls", "").lower()
            if not name:
                continue
            class_terms.add(name.replace("_", " ").replace("-", " "))
            class_terms.add(name.replace("_", "").replace("-", ""))
            if name.endswith("s"):
                class_terms.add(name[:-1])
            if name == "pitted_surface":
                class_terms.update(("pitted", "cavity", "cavities"))
            if name == "rolled-in_scale":
                class_terms.update(("scale", "rolled in"))
        if class_terms and not any(term in answer_lower for term in class_terms):
            return None, True
        if any(d.get("uncertain") for d in report["defects"]):
            if not any(term in answer_lower for term in ("manual", "inspect", "verify", "review")):
                return None, True
        return output[:6000], False
    except (OSError, subprocess.SubprocessError, ValueError):
        return None, True


def advise(report):
    """Keep the deterministic QC action authoritative; Llama may only add context."""
    authoritative = _rule_advice(report)
    generated, unavailable = _executorch_advice(report)
    if generated:
        return {
            "text": (
                "RULE-BASED QC GUIDANCE (authoritative)\n"
                + authoritative
                + "\n\nOPTIONAL LLAMA EXPLANATION (verify against the image and detections)\n"
                + generated
            ),
            "engine": EXECUTORCH_ENGINE,
        }
    return {
        "text": authoritative,
        "engine": EXECUTORCH_FALLBACK_ENGINE if unavailable else RULES_ENGINE,
    }
