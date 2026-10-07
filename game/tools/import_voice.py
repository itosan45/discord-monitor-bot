"""assets/voice/gemini/*.wav をMP3にしてゲームの音声データ(game/data/audio.json)に入れる。
使い方: python3 game/tools/import_voice.py  → そのあと cd game && python3 build.py
名乗り=iv(キャラ選択)、必殺=sv、気合い=ki、勝ちどき=kd、殿=sh。やられ声は不採用。"""
import os,json,base64,subprocess,glob
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V=os.path.join(R,'assets','voice','gemini');J=os.path.join(R,'game','data','audio.json')
H={'yukimura':'yuki','kagekatsu':'kage','mitsunari':'mitsu','nobunaga':'nobu','shingen':'shin','musashi':'musashi'}
def mp3(n):return base64.b64encode(subprocess.run(['ffmpeg','-v','error','-i',os.path.join(V,n),'-ac','1','-ar','24000','-b:a','64k','-f','mp3','-'],capture_output=True,check=True).stdout).decode()
d=json.load(open(J))
d['iv']={H[k]:mp3('meet_%s.wav'%k) for k in H}
d['sv']={H[k]:mp3('special_%s.wav'%k) for k in H}
d['ki']=[mp3('kiai_%d.wav'%i) for i in range(1,7)]
def army(n):
    # 勝ちどきを軍勢の声に: 高さだけ変えて(長さは同じ)、ほぼ同時に重ねる。ずれは最大30ms
    import random;random.seed(n)
    F=[1.0,0.84,0.9,0.95,1.06,1.12,0.87,0.98,1.03,0.92,1.09,0.8];ins=[];fl=[];m=len(F)
    for i,f in enumerate(F):
        ins+=['-i',os.path.join(V,n)];dl=0 if i==0 else random.randint(0,30);pan=0 if i==0 else random.uniform(-0.8,0.8);v=1.0 if i==0 else random.uniform(0.3,0.5)
        fl.append(f"[{i}:a]aformat=channel_layouts=mono,asetrate={int(24000*f)},aresample=24000,atempo={1/f:.4f},adelay={dl},volume={v:.2f},pan=stereo|c0={(1-max(0,pan)):.2f}*c0|c1={(1+min(0,pan)):.2f}*c0[a{i}]")
    fl.append(''.join(f'[a{i}]' for i in range(m))+f'amix=inputs={m}:normalize=0,alimiter=limit=0.9[o]')
    out=subprocess.run(['ffmpeg','-v','error',*ins,'-filter_complex',';'.join(fl),'-map','[o]','-ar','24000','-b:a','96k','-f','mp3','-'],capture_output=True,check=True).stdout
    return base64.b64encode(out).decode()
d['kd']=[army('kachidoki_%d.wav'%i) for i in (1,2)]
d['sh']=[mp3('shingari_%d.wav'%i) for i in (1,2)]
json.dump(d,open(J,'w'));print({k:len(d[k]) for k in ['iv','sv','ki','kd','sh']},os.path.getsize(J)//1024,'KB')
