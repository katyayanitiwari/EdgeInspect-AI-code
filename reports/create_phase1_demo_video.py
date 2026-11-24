from pathlib import Path
import textwrap
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

ROOT=Path(__file__).resolve().parents[1]
SAMPLES=ROOT/'deployment'/'huggingface_static'/'samples'
WEIGHTS=ROOT/'experiments'/'EXP-002'/'weights'/'best.pt'
OUT=ROOT/'demo'/'EdgeInspect-AI-Phase1-Demo.mp4'
ASSETS=ROOT/'demo'/'rendered_assets'
W,H,FPS,SECONDS=1920,1080,15,15
BG=(12,19,31); PANEL=(22,34,51); WHITE=(242,247,252); MUTED=(169,188,207); ORANGE=(242,102,36); TEAL=(49,193,181); RED=(233,90,88)
FONTS=Path('C:/Windows/Fonts')
font_file=FONTS/'segoeuib.ttf'
if not font_file.exists(): font_file=FONTS/'arial.ttf'
def font(size,bold=False):
    path=FONTS/('segoeuib.ttf' if bold and (FONTS/'segoeuib.ttf').exists() else 'segoeui.ttf')
    if not path.exists(): path=FONTS/'arial.ttf'
    return ImageFont.truetype(str(path),size)
TITLE=font(64,True); HEAD=font(42,True); BODY=font(30); SMALL=font(23); TINY=font(18)


def image_fit(img, box):
    x,y,bw,bh=box
    im=img.copy(); im.thumbnail((bw,bh),Image.Resampling.LANCZOS)
    return im,(x+(bw-im.width)//2,y+(bh-im.height)//2)

def text_block(draw,xy,text,ft,fill,width=70,spacing=12):
    x,y=xy
    for para in text.split('\n'):
        lines=textwrap.wrap(para,width=width) or ['']
        for line in lines:
            draw.text((x,y),line,font=ft,fill=fill)
            y += ft.size+spacing
    return y

def base_slide(section,title,subtitle=None):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,12),fill=ORANGE)
    d.text((96,60),'EDGEINSPECT-AI',font=SMALL,fill=TEAL)
    d.text((96,105),section.upper(),font=TINY,fill=MUTED)
    d.text((96,145),title,font=HEAD,fill=WHITE)
    if subtitle: text_block(d,(98,210),subtitle,BODY,MUTED,width=83,spacing=6)
    return im,d

def rounded(draw,box,fill=PANEL,outline=None,r=24,width=2):
    draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def load_sample(name):
    return Image.open(SAMPLES/name).convert('RGB')

def prepare_model_outputs():
    ASSETS.mkdir(parents=True,exist_ok=True)
    model=YOLO(str(WEIGHTS))
    chosen=[]
    for i in range(1,7):
        name=f'steel_sample_{i}.jpg'; path=SAMPLES/name
        if not path.exists(): continue
        pred=model.predict(source=str(path),imgsz=320,conf=0.25,device='cpu',verbose=False)[0]
        plotted=pred.plot()
        annotated=Image.fromarray(cv2.cvtColor(plotted,cv2.COLOR_BGR2RGB))
        annotated.save(ASSETS/f'{Path(name).stem}_prediction.jpg',quality=94)
        orig=load_sample(name); orig.save(ASSETS/f'{Path(name).stem}_input.jpg',quality=94)
        detections=[]
        for b in pred.boxes:
            cid=int(b.cls.item()); confv=float(b.conf.item())
            detections.append((model.names[cid],confv))
        chosen.append({'name':name,'original':orig,'annotated':annotated,'detections':detections})
    if not chosen: raise RuntimeError('No steel sample images found')
    # Prefer examples with actual predictions, but preserve a second result if the model returns none.
    chosen.sort(key=lambda v:len(v['detections']),reverse=True)
    return chosen[:2]

def slide_title():
    im,d=base_slide('Bharat AI-SoC Challenge 2026-27 | PS5','A practical steel-surface inspection prototype','A short, evidence-based walkthrough of the EdgeInspect-AI software prototype.')
    rounded(d,(96,355,1824,810),fill=PANEL,outline=(53,75,99),r=28)
    d.text((150,425),'Image input',font=BODY,fill=WHITE); d.text((430,425),'Defect candidates',font=BODY,fill=WHITE); d.text((800,425),'QC guidance',font=BODY,fill=WHITE); d.text((1135,425),'Inspection log',font=BODY,fill=WHITE)
    d.line((340,465,405,465),fill=ORANGE,width=5); d.line((710,465,775,465),fill=ORANGE,width=5); d.line((1060,465,1110,465),fill=ORANGE,width=5)
    d.text((150,540),'NEU-DET steel images',font=SMALL,fill=MUTED); d.text((430,540),'6 known classes',font=SMALL,fill=MUTED); d.text((800,540),'Rule-based severity',font=SMALL,fill=MUTED); d.text((1135,540),'Local records',font=SMALL,fill=MUTED)
    d.text((150,680),'Scope: steel surfaces',font=SMALL,fill=TEAL); d.text((150,730),'Predictions are candidates and need QC review.',font=SMALL,fill=MUTED)
    return im

def slide_scope(sample):
    im,d=base_slide('01 / model scope','A model trained for steel surfaces','The detector recognizes six NEU-DET labels. It is not a general detector for every object or product.')
    rounded(d,(96,330,1010,915),fill=PANEL,outline=(53,75,99)); pic,pos=image_fit(sample['original'],(125,360,850,500)); im.paste(pic,pos)
    d.text((1080,360),'SUPPORTED CLASSES',font=SMALL,fill=TEAL)
    cls=['crazing','inclusion','patches','pitted surface','rolled-in scale','scratches']
    y=415
    for j,c in enumerate(cls,1):
        d.ellipse((1085,y+6,1115,y+36),fill=ORANGE if j<4 else TEAL)
        d.text((1135,y),c,font=BODY,fill=WHITE); y+=70
    d.text((1080,875),'Unrelated scenes can produce false detections.',font=SMALL,fill=MUTED)
    return im

def slide_inspection(item,number):
    im,d=base_slide(f'02 / model result / example {number}',f'Candidate detections from a sample image','YOLOv8n EXP-002, 320-pixel input. The boxes below are model outputs; review class and location before making a QC decision.')
    rounded(d,(96,320,930,905),fill=PANEL,outline=(53,75,99)); p,xy=image_fit(item['original'],(120,345,785,520)); im.paste(p,xy); d.text((120,875),'INPUT SAMPLE',font=TINY,fill=MUTED)
    rounded(d,(990,320,1824,905),fill=PANEL,outline=(53,75,99)); a,xy=image_fit(item['annotated'],(1015,345,785,520)); im.paste(a,xy); d.text((1015,875),'MODEL OVERLAY',font=TINY,fill=MUTED)
    if item['detections']:
        dets=', '.join(f'{n} {c:.2f}' for n,c in item['detections'][:4])
        text_block(d,(1020,925),'Recorded output: '+dets,SMALL,TEAL,width=92,spacing=3)
    else:
        d.text((1020,925),'Recorded output: no boxes above confidence 0.25 on this sample.',font=SMALL,fill=TEAL)
    return im

def slide_metrics():
    im,d=base_slide('03 / measured model comparison','Choose the speed-accuracy balance','Saved test results use the same 270-image held-out NEU-DET split. Laptop timing is batch one; it is not board timing.')
    cards=[('EXP-001','YOLOv8n / 640','mAP50 0.7724','92.28 ms / 10.8 FPS'),('EXP-002','YOLOv8n / 320','mAP50 0.7702','36.65 ms / 27.3 FPS'),('EXP-003','YOLO11n / 640','mAP50 0.7715','93.10 ms / 10.7 FPS')]
    x0=96
    for i,(run,model,score,speed) in enumerate(cards):
        x=x0+i*575; rounded(d,(x,355,x+530,700),fill=PANEL,outline=ORANGE if i==1 else (53,75,99),r=24,width=3 if i==1 else 2)
        d.text((x+32,395),run,font=HEAD,fill=TEAL if i==1 else WHITE); d.text((x+32,475),model,font=BODY,fill=WHITE); d.text((x+32,545),score,font=BODY,fill=WHITE); d.text((x+32,610),speed,font=SMALL,fill=MUTED)
    d.text((96,785),'EXP-002 selected for the laptop app: similar test mAP50, lower measured laptop latency.',font=BODY,fill=WHITE)
    d.text((96,840),'Recorded results, not a promise of performance on Kria or Renesas hardware.',font=SMALL,fill=MUTED)
    return im

def slide_features(qr,barcode):
    im,d=base_slide('04 / application workflow','Inputs and quality-control logging','The app accepts images, sampled video, and webcam frames. QR/barcode reading is a separate utility from defect detection.')
    rounded(d,(96,330,875,900),fill=PANEL,outline=(53,75,99)); q,xy=image_fit(qr,(125,360,720,420)); im.paste(q,xy); d.text((135,810),'QR SAMPLE INPUT',font=SMALL,fill=TEAL)
    rounded(d,(930,330,1824,900),fill=PANEL,outline=(53,75,99)); b,xy=image_fit(barcode,(960,360,830,420)); im.paste(b,xy); d.text((970,810),'BARCODE SAMPLE INPUT',font=SMALL,fill=TEAL)
    d.text((96,945),'Inspection records include unique IDs; keep a human reviewer in the decision loop.',font=SMALL,fill=MUTED)
    return im

def slide_hardware():
    im,d=base_slide('05 / hardware evidence','What has actually been measured','Different stages ran on different devices. The board labels below match saved project records.')
    rows=[('KAGGLE','Tesla T4 GPU','Three model training runs'),('WINDOWS LAPTOP','Intel i5-13420H CPU','Model evaluation and local ExecuTorch smoke run'),('KRIA KV260','CPU only','6-image smoke: median 762.571 ms/image'),('RENESAS','Template only','Board build and UART exchange not verified')]
    y=340
    for i,(a,b,c) in enumerate(rows):
        rounded(d,(96,y,1824,y+125),fill=PANEL,outline=(53,75,99),r=18)
        d.text((130,y+24),a,font=SMALL,fill=TEAL if i<2 else ORANGE); d.text((435,y+20),b,font=BODY,fill=WHITE); d.text((870,y+22),c,font=SMALL,fill=MUTED); y+=145
    d.text((96,940),'No Kria FPGA/DPU result or on-device Llama result is claimed.',font=SMALL,fill=RED)
    return im

def slide_end():
    im,d=base_slide('06 / conclusion','A tested software prototype - with limits stated','The current detector is specific to NEU-DET steel defects. Review predictions before any real quality-control decision.')
    rounded(d,(96,340,1824,805),fill=PANEL,outline=(53,75,99),r=24)
    d.text((150,405),'What this video shows',font=HEAD,fill=TEAL)
    text_block(d,(155,490),'Saved model comparisons\nActual sample-image inference outputs\nApplication workflow features\nRecorded CPU-only Kria smoke result',BODY,WHITE,width=66,spacing=14)
    d.text((1050,495),'Next validation',font=HEAD,fill=ORANGE)
    text_block(d,(1055,580),'Record a direct live-app walkthrough\nValidate FPGA/DPU separately\nBuild and test Renesas firmware\nMeasure the complete target pipeline',BODY,MUTED,width=50,spacing=14)
    d.text((150,865),'This captioned clip is assembled from project assets and saved outputs, not a live desktop capture.',font=SMALL,fill=MUTED)
    return im

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    chosen=prepare_model_outputs()
    samples=[chosen[0],chosen[1] if len(chosen)>1 else chosen[0]]
    qr=Image.open(SAMPLES/'sample_qr_code.png').convert('RGB')
    barcode=Image.open(SAMPLES/'sample_ean13_barcode.png').convert('RGB')
    slides=[slide_title(),slide_scope(samples[0]),slide_inspection(samples[0],1),slide_inspection(samples[1],2),slide_metrics(),slide_features(qr,barcode),slide_hardware(),slide_end()]
    writer=cv2.VideoWriter(str(OUT),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H))
    if not writer.isOpened(): raise RuntimeError('OpenCV could not open the MP4 writer')
    for idx,slide in enumerate(slides):
        rgb=np.asarray(slide)
        base=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
        total=FPS*SECONDS
        for frame_no in range(total):
            frame=base.copy()
            progress=(idx+frame_no/total)/len(slides)
            cv2.rectangle(frame,(96,H-48),(W-96,H-40),(47,66,86),-1)
            cv2.rectangle(frame,(96,H-48),(96+int((W-192)*progress),H-40),ORANGE,-1)
            cv2.putText(frame,f'{idx+1:02d} / {len(slides):02d}',(W-170,H-62),cv2.FONT_HERSHEY_SIMPLEX,0.65,(180,200,220),1,cv2.LINE_AA)
            writer.write(frame)
    writer.release()
    print('Saved:',OUT)
    print('Duration seconds:',len(slides)*SECONDS,'Resolution:',W,'x',H,'FPS:',FPS)
    for item in samples:
        print(item['name'],item['detections'])

if __name__=='__main__': main()
