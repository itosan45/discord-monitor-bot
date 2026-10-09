"""旋律(ホルン/トランペット/ヴァイオリン/尺八など)が、鳴っているコードと半音でぶつかる長い音を探す。"""
import songs, kit
from engine import *
import mido
NAMES='C C# D D# E F F# G G# A A# B'.split()
def run(name):
    S=songs.SONGS[name](); ev=sorted(S.ev,key=lambda e:e[0]); bars=S.bars
    # コードは各 stage()/個別曲の ch を持たないので、MIDIの低音(チェロ ch2 の小節頭の音)から根音を推定、和音は pad 系を使わず簡易判定
    # → 代わりに旋律の各長音について「同じ小節のストリング pad(ch0)/ostinato(ch1) の音高集合」を使う
    on={}; res=[]
    notes=[(tk,m.channel,m.note) for tk,od,m in ev if m.type=='note_on' and m.velocity>0]
    for lead in (4,5,14,11):
        for tk,c,n in notes:
            if c!=lead: continue
            beat=tk/PPQ; bar=int(beat//4)
            if beat%1>0.15 and beat%1<0.85: continue        # 拍頭付近の音だけ
            # 長音かどうか: 次の音までの間隔(同チャンネル)
            nxt=[t for t,cc,nn in notes if cc==lead and t>tk]
            dur=(min(nxt)-tk)/PPQ if nxt else 4
            if dur<1.0: continue
            ctones={x%12 for t,cc,x in notes if cc in (0,1) and int((t/PPQ)//4)==bar}
            if not ctones: continue
            pc=n%12
            if pc in ctones: continue
            if any((pc-x)%12 in (1,11) for x in ctones):
                res.append((bar,round(beat%4,2),NAMES[pc],c))
    return res
for n in songs.SONGS:
    r=run(n); print(n,len(r),r[:12])
