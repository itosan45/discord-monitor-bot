const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const h=process.argv[2]||'yuki',wp=process.argv[3]||'';
const out=await p.evaluate(({h,wp})=>{window.requestAnimationFrame=()=>0;G.noStory=true;startGame(h,null);for(let i=0;i<10;i++)stepGame();
 const pl=G.player,T=pl.T;const rows=[['idle',null,40,4,1],['walk',null,40,4,1],['a1',T.atk[0]],['a2',T.atk[1]],['a3',T.atk[2]],['a4',T.atk[3]],['dash',T.dash],['jatk',T.jatk],['guard',null,10,1],['hurt',null,10,1]];
 const CW=170,CH=210,N=10;const cv=document.createElement('canvas');cv.width=CW*N;cv.height=CH*rows.length;const c2=cv.getContext('2d');c2.fillStyle='#456';c2.fillRect(0,0,cv.width,cv.height);const info=[];
 rows.forEach(([nm,d,len,stp],r)=>{if(!len&&!d)return;pl.wpn=wp?{k:wp,uses:20}:null;const dd=d?(wp?atkDef(pl,d,nm==='jatk'):d):null;const dur=dd?dd.dur:len;
  for(let i=0;i<N;i++){G.fighters=G.fighters.filter(f=>f.team===0);G.items=[];G.proj=[];G.parts=[];G.lowq=true;pl.x=G.camx+640;pl.y=600;pl.z=nm==='jatk'?60:0;pl.face=1;pl.flash=0;pl.inv=0;pl.gh=null;
   const st=Math.round(i*(dur-1)/(N-1));pl.state=dd?(nm==='jatk'?'jatk':'atk'):(nm==='hurt'?'hurt':nm==='guard'?'guard':nm);pl.cur=dd;pl.st=st;pl.t=st;pl.wp=st*0.25;
   ctx.fillStyle='#456';ctx.fillRect(0,0,1280,720);drawSprite(pl);c2.drawImage(ctx.canvas,pl.x-G.camx-80,600-pl.z-195,CW,CH,i*CW,r*CH,CW,CH);c2.fillStyle='#fff';c2.font='13px sans-serif';c2.fillText(nm+' st'+st+(dd?' hs'+dd.hs+' '+(dd.pz||''):''),i*CW+3,r*CH+13);}
  info.push(nm+':'+(dd?JSON.stringify({dur:dd.dur,hs:dd.hs,he:dd.he,pz:dd.pz}):''));});
 return {img:cv.toDataURL(),info};},{h,wp});
require('fs').writeFileSync(`yk_${h}${wp}.png`,Buffer.from(out.img.split(',')[1],'base64'));console.log(out.info.join('\n'),er);await b.close();})();
