# Before uploading this folder

This folder contains the refreshed project source, experiment records, sample videos, dashboard, and the two model files needed for the demo.

## Keep private / do not upload

- `MY_NOTES_Done_and_Left.pdf` — personal notes.
- `RESUME_PROMPT.md` and `EdgeInspect-AI_RESUME_PROMPT.md` — personal continuation prompts.
- `edgeinspect-dashboard.*`, `tailscale-*`, `*.msi`, and `*.log` — local setup/debug material.
- `logs/`, `.gradio/`, `.env*`, certificates/keys, and any credentials.

The `.gitignore` excludes these files. If using Git, confirm the pending changes with `git status --short` and check that none of the private filenames appear before committing. Do not manually drag every file into a website upload form, because that can bypass `.gitignore`.

## Included / intentionally not included

- Included checkpoints: `experiments/EXP-002/weights/best.pt` and `yolov8n.pt`; both are small enough for a normal GitHub repository.
- Dataset images and labels are excluded. They must be obtained and prepared separately for training/evaluation.
- Runtime inspection history and uploaded user images are excluded.
- Kaggle account files, access tokens, and setup installers must never be added.

## Before sharing the demo

- Open `README.md` and `EdgeInspect-AI_Project_Status.pdf` and check the model figures against `evaluation/`.
- The live laptop dashboard link was last checked responding on 15 Oct 2026. Recheck it before sharing; it depends on the laptop and dashboard being online.
- The official challenge page checked 29 Oct 2026 lists Phase 1 submission as **23 Nov 2026** and Phase 2 as **5 Feb 2027**. Recheck the page before submission: https://arm-education.github.io/Arm-Developer-Labs/Bharat_AI_SoC_2026_27.html
- Raspberry Pi, Hailo, and ExecuTorch results have not been verified in this project snapshot. PS5 requires Llama + ExecuTorch; the current advisor remains rule-based.
