"""Build the upload-safe EdgeInspect-AI project status PDF from saved results."""
from datetime import date
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "EdgeInspect-AI_Project_Status.pdf"
OFFICIAL = "https://arm-education.github.io/Arm-Developer-Labs/Bharat_AI_SoC_2026_27.html"


def load(exp):
    return json.loads((ROOT / "evaluation" / exp / "metrics.json").read_text(encoding="utf-8"))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d5dce5"))
    canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526174"))
    canvas.drawString(18 * mm, 10 * mm, "EdgeInspect-AI | Project status | 29 Oct 2026")
    canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    metrics = [load(x) for x in ("EXP-001", "EXP-002", "EXP-003")]
    exp2 = json.loads((ROOT / "evaluation" / "EXP-002" / "onnx_metrics.json").read_text(encoding="utf-8"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Deck", parent=styles["Normal"], fontSize=10,
                              leading=15, textColor=colors.HexColor("#526174"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=14,
                              leading=18, textColor=colors.HexColor("#17365d"), spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5,
                              leading=12, textColor=colors.HexColor("#526174")))
    styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontSize=8,
                              leading=10, spaceAfter=0))
    story = []
    story += [Paragraph("EdgeInspect-AI", styles["Title"]),
              Paragraph("Project status brief · Bharat AI-SoC Challenge 2026–27 · PS5", styles["Deck"]),
              Spacer(1, 5 * mm),
              Paragraph("Status refreshed 29 October 2026 from the saved project files. Model metrics are measurements recorded in the experiment files. The dashboard links last returned HTTP 200 on 15 October 2026; link availability was not rechecked for this refresh.", styles["BodyText"]),
              Paragraph("What the prototype does", styles["Section"]),
              Paragraph("The laptop prototype uses a YOLO model trained on NEU-DET steel-surface images. It accepts images/webcam and video, shows candidate defect boxes and confidence, applies rule-based severity and QC guidance, reads QR/barcodes separately, assigns inspection identifiers, and stores inspection history locally in SQLite. These are prototype features; they have not been validated for production use.", styles["BodyText"]),
              Paragraph("Training data", styles["Section"]),
              Paragraph("NEU-DET: 1,799 images after removing one exact duplicate; six steel defect classes; stratified split of 1,259 train, 270 validation, and 270 test images. The dataset is not bundled with this upload copy.", styles["BodyText"]),
              Paragraph("Recorded model comparison", styles["Section"])]

    rows = [["Experiment", "Model / input", "Test mAP50", "Test mAP50–95", "CPU total", "FPS"]]
    for m in metrics:
        acc = m["accuracy_test_split"]
        lat = m["cpu_latency_ms_median"]
        rows.append([m["exp_id"], f"{m['model']} / {m['imgsz']}",
                     f"{acc['mAP50']:.4f}", f"{acc['mAP50_95']:.4f}",
                     f"{lat['total']:.2f} ms", f"{m['cpu_fps']:.1f}"])
    table = Table(rows, colWidths=[24*mm, 36*mm, 26*mm, 29*mm, 28*mm, 18*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f1f5f9")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [table, Spacer(1, 3*mm),
              Paragraph("EXP-002 (YOLOv8n at 320 px) is selected for the laptop dashboard. These results are from the laptop and the held-out NEU-DET test split, not Raspberry Pi measurements. Its separate FP32 ONNX evaluation recorded mAP50 {:.4f} and mAP50–95 {:.4f}; the PyTorch model remains selected.".format(exp2["mAP50"], exp2["mAP50_95"]), styles["Small"]),
              Paragraph("Limits and remaining work", styles["Section"]),
              Paragraph("The model recognizes only its six NEU-DET steel classes. False detections have occurred on unrelated images, so predictions need human review and do not establish accuracy on bottles, PCBs, or other products. Crazing and rolled-in scale were weaker classes in the recorded results. The current advisor is rule-based; Llama + ExecuTorch has not been implemented or verified on the target device. Raspberry Pi and Hailo performance is unmeasured.", styles["BodyText"]),
              Paragraph("Next: review false positives and misses; collect and label images of the actual target product; confirm target hardware; implement and measure Llama + ExecuTorch on-device; validate offline end-to-end behavior; then prepare the technical report and demo video.", styles["BodyText"]),
              Paragraph("Challenge checkpoint", styles["Section"]),
              Paragraph("The official challenge page currently lists Phase 1 submission as 23 November 2026 and Phase 2 submission as 5 February 2027. PS5 lists Llama + ExecuTorch as required; Hailo is optional. Registration was reported complete by the project owner. <link href='{}' color='#1769aa'>Check the official page before submission.</link>".format(OFFICIAL), styles["BodyText"]),
              Spacer(1, 3*mm),
              Paragraph("Dashboard links (last HTTP 200 confirmation: 15 Oct 2026)", styles["Section"]),
              Paragraph("Local: http://127.0.0.1:7860/ &nbsp; | &nbsp; Public: https://laptop-46vn7dls.tail278ad4.ts.net/", styles["Small"]),
              Paragraph("The public dashboard is hosted from the laptop; it requires the laptop, app, network, and Tailscale Funnel to be available.", styles["Small"])]

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=17*mm, bottomMargin=21*mm, title="EdgeInspect-AI Project Status")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Created {OUT}")


if __name__ == "__main__":
    main()
