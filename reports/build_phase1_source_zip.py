from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'EdgeInspect-AI-Phase1-Source.zip'
PREFIX='EdgeInspect-AI-Phase1-Source'

ROOT_FILES={'.gitattributes','.gitignore','CHALLENGE.md','README.md','requirements.txt','run_dashboard_windows.bat','run_webcam_windows.bat','setup_windows.bat','WINDOWS_DEV.md','UPLOAD_README.md','UPLOAD_CHECKLIST.md','COLLECTION_README.md','PLAN.md','check_windows_env.py','yolov8n.pt'}
TREE_DIRS=['app','scripts','training','inference','docs','tests','site','datasets','deployment/kv260','deployment/renesas','deployment/executorch','deployment/huggingface_static']
REPORT_FILES=['reports/Phase1_Technical_Report.md','reports/EdgeInspect-AI_Phase1_Technical_Report.pdf','reports/build_phase1_report.py','reports/build_phase1_source_zip.py','reports/create_phase1_demo_video.py']
EVALUATION_FILES=['evaluation/evaluate.py','evaluation/compare_onnx.py','evaluation/EXP-001/metrics.json','evaluation/EXP-002/metrics.json','evaluation/EXP-002/onnx_metrics.json','evaluation/EXP-002/onnx_parity.json','evaluation/EXP-002/pytorch_batch1_metrics.json','evaluation/EXP-002/ERROR_ANALYSIS.md','evaluation/EXP-003/metrics.json']
EXPERIMENT_FILES=['experiments/EXPERIMENTS.md','experiments/results.csv']
for exp in ('EXP-001','EXP-002','EXP-003'):
    EXPERIMENT_FILES += [f'experiments/{exp}/args.yaml',f'experiments/{exp}/results.csv',f'experiments/{exp}/train_env.json']
EXPERIMENT_FILES += ['experiments/EXP-002/weights/best.pt']

blocked_parts={'LOCAL_ONLY_DO_NOT_UPLOAD','.venv','__pycache__','.gradio','logs','outputs','runs','raw','processed','usb_transfer','huggingface_space'}
blocked_names={'MY_NOTES_Done_and_Left.pdf','RESUME_PROMPT.md','EdgeInspect-AI_RESUME_PROMPT.md','SAMPLE_NOT_FOR_SUBMISSION_Hypothetical_Completion.pdf','EdgeInspect-AI_Project_Status.pdf'}

def allowed(p:Path)->bool:
    rel=p.relative_to(ROOT)
    if any(part in blocked_parts for part in rel.parts): return False
    if p.name in blocked_names: return False
    if p.suffix.lower() in {'.zip','.log','.pyc','.pem','.key','.env','.msi','.pte','.pth','.gguf','.hef'}: return False
    if p.name.endswith('.onnx') and rel.as_posix() not in {'deployment/huggingface_static/best.onnx','deployment/kv260/fpga_candidate/EXP-002_best.onnx'}: return False
    return True

selected=set()
for name in sorted(ROOT_FILES)+REPORT_FILES+EVALUATION_FILES+EXPERIMENT_FILES:
    p=ROOT/name
    if p.is_file() and allowed(p): selected.add(p)
for d in TREE_DIRS:
    base=ROOT/d
    if base.exists():
        for p in base.rglob('*'):
            if p.is_file() and allowed(p): selected.add(p)

required={'README.md','requirements.txt','experiments/EXP-002/weights/best.pt','reports/EdgeInspect-AI_Phase1_Technical_Report.pdf','app/dashboard.py'}
missing=required-{p.relative_to(ROOT).as_posix() for p in selected}
if missing: raise SystemExit('Required source files missing: '+', '.join(sorted(missing)))
files=sorted(selected,key=lambda x:x.relative_to(ROOT).as_posix().lower())
manifest=['EdgeInspect-AI Phase 1 source package','Generated from BHARAT EDGE on 24 November 2026.','',f'Files included: {len(files)}','']+[p.relative_to(ROOT).as_posix() for p in files]
manifest += ['', 'Intentionally excluded: local Python environments and caches, gated/private Llama weights and ExecuTorch artifact, credentials, personal notes/prompts, inspection logs/output, datasets, old ZIP bundles, and the hypothetical sample report.', 'The package includes the measured Phase 1 report and source code. The separate two-minute generated walkthrough video is stored at demo/EdgeInspect-AI-Phase1-Demo.mp4 and is not included in this source archive; review and upload it publicly to YouTube/Google Drive. Review README.md and UPLOAD_CHECKLIST.md before submission.']
with ZipFile(ARCHIVE,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
    z.writestr(f'{PREFIX}/SUBMISSION_SOURCE_MANIFEST.txt','\n'.join(manifest)+'\n')
    for p in files: z.write(p, f'{PREFIX}/{p.relative_to(ROOT).as_posix()}')
with ZipFile(ARCHIVE) as z:
    names=z.namelist()
    bad=[n for n in names if any(part in n.split('/') for part in blocked_parts) or n.lower().endswith(('.log','.pyc','.zip','.pte','.pem','.key')) or 'MY_NOTES' in n or 'RESUME_PROMPT' in n]
    if bad: raise SystemExit('Private/unwanted files found in archive: '+repr(bad[:10]))
    if not any(n.endswith('reports/EdgeInspect-AI_Phase1_Technical_Report.pdf') for n in names): raise SystemExit('Factual report missing from archive')
print(f'Created {ARCHIVE}')
print(f'Included {len(files)} project files plus a manifest; archive entries checked for private/runtime/log artifacts.')
