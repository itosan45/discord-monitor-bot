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
d['kd']=[mp3('kachidoki_%d.wav'%i) for i in (1,2)]
d['sh']=[mp3('shingari_%d.wav'%i) for i in (1,2)]
json.dump(d,open(J,'w'));print({k:len(d[k]) for k in ['iv','sv','ki','kd','sh']},os.path.getsize(J)//1024,'KB')
