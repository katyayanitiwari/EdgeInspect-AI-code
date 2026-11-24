# Bharat AI-SoC Challenge 2026–27 — official facts (PS5)

Official source: https://arm-education.github.io/Arm-Developer-Labs/Bharat_AI_SoC_2026_27.html (checked 30 Oct 2026). Recheck this page before submission in case it changes. Details not stated there need verification from the organizers.

## Dates currently listed

| Milestone | Date |
|---|---|
| Launch | 19 Sep 2026 |
| Registration closes | 19 Oct 2026 (closed) |
| **Phase 1 — Open Qualifying submission** | **23 Nov 2026** |
| Phase 1 results | Mid-Dec 2026 |
| Phase 2 — PoC Development submission | 5 Feb 2027 |

## Team and deliverables

The page lists teams of 1–3 members and says registration is closed. Phase 1 deliverables are source code, an application, a technical report, and a demonstration video. Check the challenge form for any submission-format details not included on the public page.

## PS5 — Real-time industrial defect detection and quality-control assistant

The stated objective includes detecting surface defects/cracks/anomalies, classifying defect type and severity, giving actionable recommendations, logging inspections, and operating at the edge without cloud dependence.

**Required technologies:** a Llama-family model for advisory/reasoning, deployed on-device with ExecuTorch as the reference runtime.

**Hardware options listed:** Raspberry Pi 5 CPU-only, Raspberry Pi 5 with AI HAT+ / AI HAT+ 2, Arm-based Linux devices, or Arm-based Android devices. Hailo is optional. If used, the page describes vision on HailoRT/NPU and Llama on ExecuTorch/Arm CPU as separate pipelines.

## How this project maps to the requirement

The current laptop prototype has a rule-based advisor. Llama + ExecuTorch deployment is still unfinished and unverified, so the current prototype does not yet demonstrate that required technology. Kria KV260 and Renesas RA6E2 operation have not been measured. The NEU-DET model is specific to six steel-surface classes and is not proof of general defect detection across arbitrary products.
