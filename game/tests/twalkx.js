// 2026-10-15 幸村の歩き試験(?walkx=1): AI補間16コマ(walkx_yuki / walkx_yuki_u)への差し替え
// ①既定(フラグなし)では試験の絵を読み込まず、使わない ②?walkx=1 では読み込み・使用される(武器あり/拾得武器あり)
// ③実際の描画で、足元の高さ・身長が従来の歩きと揃う ④1周のコマ間の脚の変化(実描画)が従来より一定 ⑤実際に歩かせてもエラーなし
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const fs=require('fs');
const BASE=process.argv[2]||process.env.GAME_URL;
const OUT=process.env.WALKX_OUT||'';
async function open(b,flag){const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(BASE+(BASE.includes('?')?'&':'?')+'walkx='+(flag?1:0));/* 2026-10-16 既定が walkx=3(納品版)になったので、試験の「なし」は walkx=0 */await p.waitForFunction(()=>typeof G!=='undefined'&&G.mode,null,{timeout:120000});return{p,errors};}
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[],out={};
 try{
 // ① 既定
 {const {p,errors}=await open(b,false);
  const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);startStage(0,'yuki',false);G.mode='play';
   for(let i=0;i<5;i++){G.t++;stepGame();}for(let i=0;i<400&&!sprWantReady();i++)await new Promise(r=>setTimeout(r,50));
   const P=G.player;P.state='walk';P.wp=0.3;P.x=G.camx+640;P.y=560;drawFighter(P);
   return {WALKX,want:!!SPR_RAW.walkx_yuki.want,ready:SPR_RAW.walkx_yuki.ready,wantU:!!SPR_RAW.walkx_yuki_u.want,used:G.walkxN||0};});
  out.off=r;if(r.WALKX||r.want||r.ready||r.wantU||r.used)bad.push('フラグなしで試験の絵を読み込む/使う '+JSON.stringify(r));
  if(errors.length)bad.push('フラグなしでエラー '+errors[0]);await p.context().close();}
 // ②〜⑤ ?walkx=1
 {const {p,errors}=await open(b,true);
  const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);startStage(0,'yuki',false);G.mode='play';
   for(let i=0;i<5;i++){G.t++;stepGame();}for(let i=0;i<400&&!sprWantReady();i++)await new Promise(r=>setTimeout(r,50));
   const res={flag:WALKX,ready:!!(SPR_RAW.walkx_yuki.ready&&SPR_RAW.walkx_yuki_u.ready),n:[SPR.walkx_yuki.a.walk.length,SPR.walkx_yuki_u.a.walk.length]};
   const P=G.player;const wkeys=Object.keys(WPN);
   const oc=document.createElement('canvas');oc.width=1280;oc.height=720;const octx=oc.getContext('2d');
   const grab=(ph)=>{P.state='walk';P.wp=ph;P.face=1;P.z=0;P.vz=0;P.mount=null;P.x=G.camx+640;P.y=560;G.shake=0;G.hitstop=0;const old=ctx;ctx=octx;octx.clearRect(0,0,1280,720);try{drawFighter(P);}finally{ctx=old;}
    const d=octx.getImageData(0,0,1280,720).data;let top=1e9,bot=-1;for(let y=0;y<720;y++)for(let x=480;x<800;x++)if(d[(y*1280+x)*4+3]>40){if(y<top)top=y;if(y>bot)bot=y;}
    // 脚の特徴: 480..800 x 450..570 を4px角で平均した縮小像
    const f=[];for(let y=450;y<570;y+=4)for(let x=480;x<800;x+=4){let s=0;for(let j=0;j<4;j++)for(let i=0;i<4;i++)s+=d[((y+j)*1280+x+i)*4+3];f.push(s/16/255);}
    return {top,bot,f};};
   const cycle=(len)=>{const fr=[];for(let k=0;k<len;k++)fr.push(grab((k+0.5)/len*Math.PI*2));return fr;};
   const stat=(fr)=>{const st=fr.map((a,k)=>{const b2=fr[(k+1)%fr.length];let s=0;for(let i=0;i<a.f.length;i++){const d=a.f[i]-b2.f[i];s+=d*d;}return Math.sqrt(s);});const m=st.reduce((a,c)=>a+c,0)/st.length;const sd=Math.sqrt(st.reduce((a,c)=>a+(c-m)*(c-m),0)/st.length);return {steps:st.map(x=>+x.toFixed(2)),cv:+(sd/m).toFixed(3),ratio:+(Math.max(...st)/Math.max(1e-6,Math.min(...st))).toFixed(2),top:fr.map(a=>a.top),bot:fr.map(a=>a.bot)};};
   // 武器なし: 従来(8)と試験(16)
   WALKX=false;P.wpn=null;res.armedOff=stat(cycle(8));G.walkxN=0;WALKX=true;res.armedOn=stat(cycle(16));res.armedUsed=G.walkxN;
   // 拾得武器あり(素手の歩き+武器)
   P.wpn={k:wkeys[0],uses:9};WALKX=false;res.pickOff=stat(cycle(8));G.walkxN=0;WALKX=true;res.pickOn=stat(cycle(16));res.pickUsed=G.walkxN;P.wpn=null;
   // 画像保存用: 8位相ずつ
   if(window.__save){}
   return res;});
  out.on={flag:r.flag,ready:r.ready,n:r.n,armed:{off:{cv:r.armedOff.cv,ratio:r.armedOff.ratio},on:{cv:r.armedOn.cv,ratio:r.armedOn.ratio},used:r.armedUsed},pick:{off:{cv:r.pickOff.cv,ratio:r.pickOff.ratio},on:{cv:r.pickOn.cv,ratio:r.pickOn.ratio},used:r.pickUsed}};
  if(!r.flag||!r.ready)bad.push('?walkx=1 で試験の絵が読み込まれない');if(r.n[0]!==16||r.n[1]!==16)bad.push('コマ数が16でない '+r.n);
  if(!(r.armedUsed>0))bad.push('武器ありの歩きで試験の絵を使っていない');if(!(r.pickUsed>0))bad.push('拾得武器ありの歩きで試験の絵を使っていない');
  const mm=a=>[Math.min(...a),Math.max(...a)];
  for(const [nm,o,n] of [['武器あり',r.armedOff,r.armedOn],['拾得武器あり',r.pickOff,r.pickOn]]){
   const bo=mm(o.bot),bn=mm(n.bot),to=mm(o.top),tn=mm(n.top);out[nm]={bot:[bo,bn],top:[to,tn]};
   if(Math.abs(bn[1]-bo[1])>3||Math.abs(bn[0]-bo[0])>4)bad.push(nm+': 足元の位置が従来とずれる '+JSON.stringify([bo,bn]));
   if(Math.abs(tn[0]-to[0])>6||Math.abs(tn[1]-to[1])>6)bad.push(nm+': 身長(頭の位置)が従来とずれる '+JSON.stringify([to,tn]));
   if(!(n.cv<=o.cv+0.02))bad.push(nm+': 脚の変化の一定さ(CV)が従来より悪い '+o.cv+' → '+n.cv);}
  // ⑤ 実際に歩かせる(キー操作)
  const w=await p.evaluate(async()=>{const P=G.player;window.ctlKeys=()=>({l:0,r:1,u:0,d:0,atkP:0,jumpP:0,spcP:0});G.walkxN=0;G.waveOn=false;G.waves=[{x:999999,en:[]}];
   const x0=P.x;for(let i=0;i<360;i++){P.hp=P.maxhp;G.t++;stepGame();if(i%3===0)renderWorld();}return {moved:Math.round(P.x-x0),used:G.walkxN,state:P.state};});
  out.walk=w;if(!(w.moved>200&&w.used>100))bad.push('実際に歩かせても試験の歩きが使われない '+JSON.stringify(w));
  if(errors.length)bad.push('?walkx=1 でエラー '+errors[0]);
  if(OUT){await p.screenshot({path:OUT+'/walkx_game.png'});}
  await p.context().close();}
 console.log(JSON.stringify(out));
 if(bad.length){console.log('NG',bad);process.exitCode=1;}else console.log('OK twalkx');
 }finally{await b.close();}})();
