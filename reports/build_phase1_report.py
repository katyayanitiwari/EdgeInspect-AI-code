from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "EdgeInspect-AI_Phase1_Technical_Report.pdf"
SAMPLE = ROOT / "demo" / "rendered_assets" / "steel_sample_2_prediction.jpg"

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1F497D")
TEAL = colors.HexColor("#148A8A")
ORANGE = colors.HexColor("#F07838")
INK = colors.HexColor("#263746")
MUTED = colors.HexColor("#5D7183")
PALE = colors.HexColor("#F1F5F8")
PALE_TEAL = colors.HexColor("#EAF5F4")
LINE = colors.HexColor("#D7E0E7")
WHITE = colors.white


def P(text, style):
    return Paragraph(text, style)


def footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page == 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, h - 9 * mm, w, 9 * mm, fill=1, stroke=0)
    else:
        canvas.setFillColor(TEAL)
        canvas.rect(0, h - 2.3 * mm, w, 2.3 * mm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(18 * mm, h - 13 * mm, "EDGEINSPECT-AI  /  PHASE 1 REPORT")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, w - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, "Bharat AI-SoC Challenge 2026-27  |  PS5")
    canvas.drawRightString(w - 18 * mm, 9 * mm, f"{doc.page:02d}")
    canvas.restoreState()


def table_style(header=True, font_size=8.5):
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [WHITE, PALE]),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ]
    return TableStyle(commands)


def main():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", fontName="Helvetica-Bold", fontSize=31, leading=36,
        textColor=NAVY, alignment=TA_LEFT, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CoverSub", fontName="Helvetica", fontSize=15, leading=21,
        textColor=TEAL, spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Deck", fontName="Helvetica", fontSize=10, leading=15,
        textColor=MUTED, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Section", fontName="Helvetica-Bold", fontSize=17, leading=21,
        textColor=NAVY, spaceBefore=2, spaceAfter=8, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Subsection", fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=TEAL, spaceBefore=5, spaceAfter=4, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Body2", fontName="Helvetica", fontSize=9.1, leading=13.4,
        textColor=INK, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Small2", fontName="Helvetica", fontSize=7.7, leading=10.5,
        textColor=MUTED, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Cell", fontName="Helvetica", fontSize=8, leading=10.5,
        textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="CellBold", fontName="Helvetica-Bold", fontSize=8, leading=10.5,
        textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="CellHead", fontName="Helvetica-Bold", fontSize=8, leading=10.5,
        textColor=WHITE,
    ))
    styles.add(ParagraphStyle(
        name="Metric", fontName="Helvetica-Bold", fontSize=18, leading=21,
        textColor=NAVY, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="MetricLabel", fontName="Helvetica", fontSize=7.5, leading=9.5,
        textColor=MUTED, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Callout", fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=NAVY,
    ))

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=20 * mm, bottomMargin=19 * mm,
        title="EdgeInspect-AI | Phase 1 Technical Report",
        author="Katyayani Tiwari",
        subject="Steel surface defect inspection prototype",
    )
    story = []

    # Page 1 - Project overview
    story += [Spacer(1, 18 * mm)]
    story.append(P("EDGEINSPECT-AI  /  PROJECT REPORT", styles["Subsection"]))
    story.append(P("Steel Surface<br/>Defect Inspection", styles["CoverTitle"]))
    story.append(P("Phase 1 Technical Report", styles["CoverSub"]))
    story.append(P("Bharat AI-SoC Challenge 2026-27  |  PS5: Manufacturing and Industry 4.0", styles["Deck"]))
    story.append(P("Prepared by Katyayani Tiwari  |  25 November 2026", styles["Small2"]))
    story.append(Spacer(1, 4 * mm))

    hero = Table([[P(
        "A demonstration-ready software prototype that detects six steel-surface defect classes, presents candidate boxes for review, and records an inspection summary.",
        styles["Callout"],
    )]], colWidths=[174 * mm])
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_TEAL),
        ("BOX", (0, 0), (-1, -1), 0, PALE_TEAL),
        ("LINEBEFORE", (0, 0), (0, -1), 4, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story += [hero, Spacer(1, 7 * mm)]

    metrics = [
        [P("1,799", styles["Metric"]), P("6", styles["Metric"]), P("0.7702", styles["Metric"]), P("36.65 ms", styles["Metric"])],
        [P("images in prepared dataset", styles["MetricLabel"]), P("steel defect classes", styles["MetricLabel"]), P("EXP-002 test mAP50", styles["MetricLabel"]), P("laptop median total / image", styles["MetricLabel"])],
    ]
    mt = Table(metrics, colWidths=[43.5 * mm] * 4, rowHeights=[15 * mm, 11 * mm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [mt, Spacer(1, 7 * mm), P("Project overview", styles["Section"])]
    story.append(P(
        "The project uses a YOLOv8n detector trained on the NEU-DET hot-rolled steel dataset. The selected model is EXP-002 at 320 x 320 input. A local dashboard connects image or video input to defect candidates, rule-based severity guidance, a quality-control recommendation, and an inspection log. QR and barcode reading is provided as a separate utility.",
        styles["Body2"],
    ))
    story.append(P(
        "The prototype is scoped to six NEU-DET steel defect classes: crazing, inclusion, patches, pitted surface, rolled-in scale, and scratches. It is not a general-purpose detector for arbitrary products, bottles, or PCBs. Predictions are candidates for human review.",
        styles["Body2"],
    ))
    story.append(P("Inspection flow", styles["Subsection"]))
    flow = [[
        P("1. IMAGE<br/>or video", styles["CellBold"]),
        P("2. MODEL<br/>detect + box", styles["CellBold"]),
        P("3. RULES<br/>severity", styles["CellBold"]),
        P("4. QC NOTE<br/>human review", styles["CellBold"]),
        P("5. LOG<br/>inspection ID", styles["CellBold"]),
    ]]
    ft = Table(flow, colWidths=[34.8 * mm] * 5)
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PALE),
        ("BACKGROUND", (1, 0), (1, 0), PALE_TEAL),
        ("BACKGROUND", (2, 0), (2, 0), PALE),
        ("BACKGROUND", (3, 0), (3, 0), PALE_TEAL),
        ("BACKGROUND", (4, 0), (4, 0), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [ft, PageBreak()]

    # Page 2 - Data and measured model results
    story.append(P("01  /  DATA AND MODEL", styles["Subsection"]))
    story.append(P("Training and measured results", styles["Section"]))
    story.append(P(
        "The dataset preparation workflow checked image readability, removed one exact duplicate, validated the Pascal VOC boxes, converted annotations to YOLO format, and made a stratified split. The test split contains 270 images, with 45 images per class.",
        styles["Body2"],
    ))
    split = [
        [P("TRAIN", styles["CellHead"]), P("VALIDATION", styles["CellHead"]), P("TEST", styles["CellHead"]), P("TOTAL", styles["CellHead"])],
        [P("1,259 images", styles["CellBold"]), P("270 images", styles["CellBold"]), P("270 images", styles["CellBold"]), P("1,799 images", styles["CellBold"])],
    ]
    st = Table(split, colWidths=[43.5 * mm] * 4)
    st.setStyle(table_style())
    story += [st, Spacer(1, 5 * mm)]
    story.append(P("Experiment comparison", styles["Subsection"]))
    comp = [
        ["Run", "Model / input", "Precision", "Recall", "mAP50", "mAP50-95", "CPU ms / FPS"],
        ["EXP-001", "YOLOv8n / 640", "0.6732", "0.7478", "0.7724", "0.4307", "92.28 / 10.8"],
        ["EXP-002 selected", "YOLOv8n / 320", "0.7118", "0.7093", "0.7702", "0.4361", "36.65 / 27.3"],
        ["EXP-003", "YOLO11n / 640", "0.7244", "0.7186", "0.7715", "0.4327", "93.10 / 10.7"],
    ]
    comp_rows = [[P(str(v), styles["CellHead"]) for v in comp[0]]]
    comp_rows += [[P(str(v), styles["CellBold"] if i == 0 and row[0].startswith("EXP-002") else styles["Cell"]) for i, v in enumerate(row)] for row in comp[1:]]
    ct = Table(comp_rows, colWidths=[27 * mm, 32 * mm, 19 * mm, 17 * mm, 17 * mm, 22 * mm, 40 * mm], repeatRows=1)
    ct.setStyle(table_style())
    story += [ct, Spacer(1, 3 * mm)]
    story.append(P(
        "EXP-002 was selected for the laptop prototype because its test scores were similar to the 640-pixel YOLOv8n run while its measured laptop latency was lower. Timing is batch one on the Intel Core i5-13420H CPU; it is not a Kria or Renesas speed result.",
        styles["Small2"],
    ))
    story.append(P("Per-class AP50 for EXP-002", styles["Subsection"]))
    ap = [
        ["Class", "AP50", "Class", "AP50"],
        ["Crazing", "0.4433", "Inclusion", "0.8828"],
        ["Patches", "0.9147", "Pitted surface", "0.8786"],
        ["Rolled-in scale", "0.5510", "Scratches", "0.9508"],
    ]
    ap_rows = [[P(v, styles["CellHead"]) for v in ap[0]]]
    ap_rows += [[P(v, styles["CellBold"] if i in (1, 3) else styles["Cell"]) for i, v in enumerate(row)] for row in ap[1:]]
    apt = Table(ap_rows, colWidths=[55 * mm, 32 * mm, 55 * mm, 32 * mm])
    apt.setStyle(table_style())
    story += [apt, Spacer(1, 3 * mm)]
    story.append(P(
        "Crazing and rolled-in scale are the weakest classes in this test split and should receive additional error review. The overall metrics summarize this dataset and do not establish performance on different factories, cameras, materials, or products.",
        styles["Small2"],
    ))
    story.append(PageBreak())

    # Page 3 - Application
    story.append(P("02  /  SOFTWARE PROTOTYPE", styles["Subsection"]))
    story.append(P("From inspection input to QC record", styles["Section"]))
    story.append(P(
        "The laptop application presents model output as a review aid. Each candidate detection is numbered so a reviewer can connect a box in the image with its row in the results table. Severity is derived from project rules using the predicted class, confidence, and box area. The recommendation is rule-based; it is not generated by a deployed Llama advisor in this dashboard flow.",
        styles["Body2"],
    ))
    features = [
        [P("INPUT", styles["CellHead"]), P("OUTPUT", styles["CellHead"]), P("REVIEW", styles["CellHead"])],
        [P("Still image, webcam capture, or sampled video", styles["Cell"]), P("Numbered defect candidates, class, confidence, and box", styles["Cell"]), P("Severity guidance and quality-control recommendation", styles["Cell"])],
        [P("QR and barcode sample or camera input", styles["Cell"]), P("Decoded text where supported by the code reader", styles["Cell"]), P("Separate from the steel defect detector", styles["Cell"])],
        [P("Inspection identifier and optional part/batch", styles["Cell"]), P("Local history and inspection summary", styles["Cell"]), P("Human review before a quality decision", styles["Cell"])],
    ]
    ft = Table(features, colWidths=[58 * mm, 58 * mm, 58 * mm], repeatRows=1)
    ft.setStyle(table_style())
    story += [ft, Spacer(1, 6 * mm)]
    story.append(P("Example model output", styles["Subsection"]))
    if SAMPLE.exists():
        image = Image(str(SAMPLE), width=59 * mm, height=59 * mm, kind="proportional")
        caption = P(
            "EXP-002 output on a NEU-DET sample image. The displayed boxes and confidence values come from one saved inference example; this illustration is not a separate accuracy measurement.",
            styles["Small2"],
        )
        panel = Table([[image, caption]], colWidths=[66 * mm, 108 * mm])
        panel.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PALE),
            ("BOX", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(panel)
    story += [Spacer(1, 5 * mm), P("Browser demonstration", styles["Subsection"])]
    story.append(P(
        "A static browser demo provides image/video input, camera sampling, built-in examples, QR/barcode reading, and browser-local history. Its detector runs in the visitor's browser. It does not send inference requests to the Kria or Renesas board. The interactive demo URL recorded by the project is <link href='https://katyayanivlsi-edgeinspect-ai-live.static.hf.space/index.html' color='#148A8A'>katyayanivlsi-edgeinspect-ai-live.static.hf.space</link>; check availability and camera permissions before showing it.",
        styles["Body2"],
    ))
    story.append(PageBreak())

    # Page 4 - Hardware and language model evidence
    story.append(P("03  /  HARDWARE AND EDGE STATUS", styles["Subsection"]))
    story.append(P("Measured deployment evidence", styles["Section"]))
    story.append(P(
        "The project spans cloud training, laptop software, and early target-board evaluation. The recorded evidence below separates what ran from what remains unverified on physical targets.",
        styles["Body2"],
    ))
    hw = [
        ["Platform", "Recorded use", "Measured / verified status"],
        ["Kaggle GPU", "YOLOv8n and YOLO11n model training", "Experiment logs identify Tesla T4 GPUs."],
        ["Windows laptop", "Dashboard, evaluation, and local language-model smoke run", "Intel Core i5-13420H CPU; EXP-002 median total 36.65 ms/image."],
        ["AMD Kria KV260", "Six-image YOLO CPU smoke run at 320 px", "Median 762.571 ms/image, about 1.31 images/s. No FPGA/DPU or camera path in this result."],
        ["Renesas board", "UART protocol and firmware template prepared", "Board-specific firmware build, flash, and physical exchange are not verified."],
    ]
    hw_rows = [[P(x, styles["CellHead"]) for x in hw[0]]]
    hw_rows += [[P(x, styles["CellBold"] if j == 0 else styles["Cell"]) for j, x in enumerate(row)] for row in hw[1:]]
    ht = Table(hw_rows, colWidths=[35 * mm, 61 * mm, 82 * mm], repeatRows=1)
    ht.setStyle(table_style())
    story += [ht, Spacer(1, 6 * mm), P("Llama and ExecuTorch", styles["Subsection"])]
    story.append(P(
        "The saved local status record reports that Llama 3.2 1B Instruct was exported with ExecuTorch 1.6 using CPU/XNNPACK to an 802,035,968-byte .pte file, and that a laptop CPU smoke run loaded the artifact and generated tokens. This verifies a laptop software path only. The model has not been deployed to the Kria or Renesas board, and the later re-export attempt ended with a Windows WinError 2, so repeatable export still needs work. Private gated model files and credentials are not part of the public source package.",
        styles["Body2"],
    ))
    story.append(P("Validation summary", styles["Subsection"]))
    status = [
        ["AREA", "CURRENT EVIDENCE"],
        ["Software prototype", "Detector, local inspection UI, rule-based severity/QC guidance, logging, and code reader are implemented."],
        ["Model evaluation", "Three saved 100-epoch experiments were evaluated on the same held-out NEU-DET test split."],
        ["Target hardware", "Kria evidence is CPU-only and small-sample. FPGA/DPU acceleration and camera integration are unverified."],
        ["Full offline edge pipeline", "A complete disconnected camera-to-advisor-to-log pipeline on target hardware has not been demonstrated."],
    ]
    sr = [[P(x, styles["CellHead"]) for x in status[0]]]
    sr += [[P(x, styles["CellBold"] if j == 0 else styles["Cell"]) for j, x in enumerate(row)] for row in status[1:]]
    st = Table(sr, colWidths=[43 * mm, 135 * mm], repeatRows=1)
    st.setStyle(table_style())
    story += [st, Spacer(1, 4 * mm)]
    story.append(P(
        "Project outcome: the Phase 1 software prototype and its evidence-backed report package are prepared. This report describes a completed demonstration workflow while keeping board-specific and full-system claims within the available test evidence.",
        styles["Callout"],
    ))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == "__main__":
    main()
