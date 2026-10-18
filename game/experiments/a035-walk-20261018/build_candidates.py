from pathlib import Path
from PIL import Image, ImageSequence
import numpy as np, hashlib, json, statistics

ROOT=Path(__file__).resolve().parent
BG=(255,0,255)
TARGET_HEIGHT=188
CELL=(512,384)

def is_magenta(a):
    # Source grid has a slightly warm/pink magenta; distinguish it from costume colors.
    return (a[:,:,0]>130)&(a[:,:,2]>130)&(a[:,:,1]<90)&(np.abs(a[:,:,0].astype(np.int16)-a[:,:,2].astype(np.int16))<55)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def build(key, source_name, output_name, contact_name, gif_name):
    src=ROOT/source_name
    im=Image.open(src).convert('RGB')
    a=np.asarray(im)
    h,w=a.shape[:2]
    if w%4 or h%2: raise ValueError(f'{src.name}: 4x2 grid boundaries are not integral: {w}x{h}')
    cw,ch=w//4,h//2
    crops=[]; source_bboxes=[]
    for r in range(2):
        for c in range(4):
            tile=a[r*ch:(r+1)*ch,c*cw:(c+1)*cw].copy()
            fg=~is_magenta(tile)
            ys,xs=np.where(fg)
            if len(xs)==0: raise ValueError(f'empty source cell {r*4+c+1}')
            box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
            source_bboxes.append(box)
            crops.append(tile)
    heights=[b[3]-b[1] for b in source_bboxes]
    scale=TARGET_HEIGHT/statistics.median(heights)
    sheet=Image.new('RGB',(CELL[0]*8,CELL[1]),BG)
    rendered=[]; qa=[]
    for i,(tile,box) in enumerate(zip(crops,source_bboxes)):
        tile[is_magenta(tile)]=BG
        # One uniform, fixed character scale per sheet. Frame pose changes do not trigger per-frame rescaling.
        resized=Image.fromarray(tile,'RGB').resize((round(cw*scale),round(ch*scale)),Image.Resampling.LANCZOS)
        x=round(i*CELL[0]+CELL[0]/2-resized.width/2)
        resized_mask=~is_magenta(np.asarray(resized))
        rendered_y=np.where(resized_mask.any(1))[0]
        if len(rendered_y)==0: raise ValueError(f'empty resized frame {i+1}')
        # Align each frame's lowest planted pixel by position only; never resize per frame.
        y=363-(int(rendered_y.max())+1)
        sheet.paste(resized,(x,y))
        rendered.append(sheet.crop((i*CELL[0],0,(i+1)*CELL[0],CELL[1])))
        px=np.asarray(rendered[-1])
        m=~is_magenta(px)
        ys,xs=np.where(m)
        if len(xs)==0: raise ValueError(f'empty output frame {i+1}')
        ob=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
        edge=int(m[0,:].sum()+m[-1,:].sum()+m[:,0].sum()+m[:,-1].sum())
        if edge: raise ValueError(f'frame {i+1} touches cell edge ({edge} pixels)')
        qa.append({'frame':i+1,'source_bbox':box,'foreground_bbox':ob,'foreground_height_px':ob[3]-ob[1],
                   'ground_y_px':363,'root_x_px':256,'edge_touch_pixels':edge})
    # Re-pin resampling fringe and every remaining magenta-like background pixel to exact RGB #FF00FF.
    sheet_arr=np.asarray(sheet).copy()
    exact_bg_mask=is_magenta(sheet_arr)
    sheet_arr[exact_bg_mask]=BG
    sheet=Image.fromarray(sheet_arr)
    rendered=[sheet.crop((i*CELL[0],0,(i+1)*CELL[0],CELL[1])) for i in range(8)]
    out=ROOT/output_name
    sheet.save(out,format='PNG',optimize=True)
    # 4x2 contact sheet uses complete final cells, with no resizing of individual frame art.
    contact=Image.new('RGB',(CELL[0]*4,CELL[1]*2),BG)
    for i,fr in enumerate(rendered): contact.paste(fr,((i%4)*CELL[0],(i//4)*CELL[1]))
    contact.save(ROOT/contact_name,format='PNG',optimize=True)
    rendered[0].save(ROOT/gif_name,save_all=True,append_images=rendered[1:],duration=83,loop=0,disposal=2)
    bg_pixels=sum(int(np.all(np.asarray(fr)==BG,axis=2).sum()) for fr in rendered)
    total=sum(fr.width*fr.height for fr in rendered)
    result={'candidate_only':True,'character':key,'source_grid':source_name,'source_sha256':sha(src),
            'source_grid_px':[w,h],'source_layout':'4 columns x 2 rows, read row-major',
            'source_cell_px':[cw,ch],'output':output_name,'output_sha256':sha(out),
            'output_dimensions_px':[CELL[0]*8,CELL[1]],'frame_count':8,'cell_px':list(CELL),
            'background_rgb':list(BG),'background_coverage_fraction':bg_pixels/total,
            'requested_body_height_px':TARGET_HEIGHT,'sheet_fixed_uniform_scale':scale,
            'anchor':{'root_x_px':256,'ground_y_px':363},'frames':qa,
            'note':'bbox is whole visible foreground; crouched/lifted pose silhouette varies. All frames share one uniform scale.'}
    (ROOT/(key+'_qa.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

results=[
 build('masamune','source-masamune-4x2.png','伊達政宗_歩き_8コマ_AI仮_v1.png','伊達政宗_歩き_8コマ_contact-v1.png','伊達政宗_歩き_8コマ_12fps-v1.gif'),
 build('munenori','source-munenori-4x2.png','柳生宗矩_歩き_8コマ_AI仮_v1.png','柳生宗矩_歩き_8コマ_contact-v1.png','柳生宗矩_歩き_8コマ_12fps-v1.gif')]
(ROOT/'qa-summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'built','results':results},ensure_ascii=False))
