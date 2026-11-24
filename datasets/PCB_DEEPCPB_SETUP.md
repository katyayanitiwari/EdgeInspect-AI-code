# PCB model track — DeepPCB preparation

The existing `EXP-002` checkpoint is a **steel-surface** detector trained on NEU-DET. It must not be presented as a PCB detector. This document adds a separate PCB training track and leaves all steel artifacts unchanged.

## First dataset candidate

Use DeepPCB as the first PCB benchmark candidate. The source describes 1,500 aligned pairs of tested/template 640×640 crops, six annotated defect classes, and official train/validation-vs-test list files. The annotated tested images are labelled with axis-aligned boxes. The first detector baseline will use the tested image only; template-difference algorithms can be investigated separately later.

Classes in the supplied dataset:

1. `open`
2. `short`
3. `mousebite`
4. `spur`
5. `copper` (spurious copper)
6. `pin-hole`

**Dataset-use condition:** the source README says the dataset is for research use. Review the dataset terms before public redistribution or any commercial use. Do not commit the dataset images to the public Git repository unless its terms explicitly permit it.

Source: https://github.com/tangsanli5201/DeepPCB

## Expected raw layout

```text
DeepPCB/
└── PCBData/
    ├── trainval.txt
    ├── test.txt
    ├── group00041/
    │   ├── 00041000_test.jpg
    │   ├── 00041000_temp.jpg
    │   └── 00041000.txt
    └── ...
```

Each annotation row is `x1,y1,x2,y2,type`, with source class IDs 1–6. The preparation script maps those IDs to zero-based YOLO IDs.

## Convert to YOLO format

From the project root (PowerShell):

```powershell
python scripts\prepare_deeppcb.py `
  --source data\raw\DeepPCB\PCBData `
  --output data\processed\deep_pcb `
  --seed 42 `
  --val-fraction 0.10
```

The script:

- requires the dataset's official `trainval.txt` and `test.txt` lists;
- keeps the official test list untouched;
- splits only official trainval entries into train and validation;
- reads only `*_test.jpg`, not the paired clean template image;
- validates image/annotation pairs and box coordinates;
- writes YOLO labels, `deep_pcb.yaml`, and a class/split summary.

It refuses to overwrite a non-empty output folder. If your downloaded package has a different folder layout, stop and inspect it rather than silently inventing a split.

## Train a separate PCB model

Start with a lightweight YOLOv8n baseline at 640 input. Use a GPU if available. Batch 8 is a conservative starting point for the high-resolution source crops; reduce it if GPU memory is insufficient.

```powershell
python training\train_detector.py `
  --data data\processed\deep_pcb\deep_pcb.yaml `
  --name PCB-EXP-001 `
  --model yolov8n.pt `
  --imgsz 640 `
  --epochs 100 `
  --batch 8 `
  --device 0
```

For CPU-only training, replace `--device 0` with `--device cpu` and expect training to be much slower. This creates a new `experiments/PCB-EXP-001/` folder and will not overwrite the existing steel experiments.

### Kaggle GPU option

The notebook `training/kaggle_deeppcb.ipynb` automates preparation, a separate 100-epoch GPU run, evaluation on the official untouched test split, and packaging the measured experiment. In Kaggle, attach both (1) a dataset containing this project folder and (2) the official DeepPCB source as notebook inputs, enable a GPU, then run its cells in order. The notebook stops if it cannot uniquely locate either input or if CUDA is unavailable. It does not include or download the data, and it does not claim any training result until the run finishes.

## Evaluation requirements

Do not report training metrics as test metrics. Evaluate only on the official held-out `test` split after model selection. Record precision, recall, F1, mAP50, mAP50–95, per-class AP, confusion matrix, model size, parameter count, and laptop CPU latency. Keep the test set untouched during model selection.

## Scope limitation

DeepPCB represents **bare-board surface/trace defects** (open, short, mousebite, spur, copper, pin-hole). It does not directly provide the proposed classes `missing component`, `wrong component placement`, or `solder bridge`. Do not claim those component-level capabilities from this dataset. To inspect component placement or solder joints, collect/label a separate component-level PCB dataset and validate it under the intended camera and lighting setup.
