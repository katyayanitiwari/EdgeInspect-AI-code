# Phase 1 submission checklist

Updated 24 November 2026 from the organizer email received 23 November. The email sets the deadline to **25 November 2026, 11:59 pm IST**. The public challenge page still shows 23 November; follow the newer organizer email and recheck the submission form.

## Required items from the organizer email

- [ ] Public GitHub/GitLab repository URL with source code and relevant documentation
- [ ] Review the prepared two-minute video, upload it publicly to YouTube or Google Drive, and copy its URL; preferred 1080p, 16:9, MP4
- [ ] Final project report PDF/DOCX covering methodology, results, hardware utilization, and optimization techniques
- [ ] Mentor review/approval if available (recommended by the organizer)
- [ ] Enter repository URL, video URL, and report in the designated form fields
- [ ] Submit once only; organizer says duplicate submissions will not replace the first

## Files prepared in BHARAT EDGE

- Curated source archive: `EdgeInspect-AI-Phase1-Source.zip` (review its manifest)
- Report: `reports/EdgeInspect-AI_Phase1_Technical_Report.pdf`
- Editable report source: `reports/Phase1_Technical_Report.md`
- Prepared video: `demo/EdgeInspect-AI-Phase1-Demo.mp4` (two minutes, 1920×1080, 15 FPS). It is a captioned, asset-based walkthrough using actual saved model outputs and project records, not a live desktop capture or voiceover. Review it before public upload; the video URL is still pending.
- Demo inputs: sample photos and sample MP4/WebM files. They are inputs shown in the dashboard, not the project walkthrough itself.

## Current evidence boundaries

- NEU-DET detector: three saved 100-epoch experiments; EXP-002 selected.
- Llama + ExecuTorch: local laptop export and CPU smoke run recorded; no Arm-board deployment verified.
- Kria KV260: small CPU-only smoke run on six images; no FPGA/DPU, camera, or power result.
- Renesas: protocol and source template present; board-specific build, flash, and UART exchange not verified.
- Private model files, tokens, personal notes/prompts, local logs, and runtime environments must not be uploaded.

Official page: https://arm-education.github.io/Arm-Developer-Labs/Bharat_AI_SoC_2026_27.html
