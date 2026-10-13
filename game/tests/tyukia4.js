// 2026-10-14 真田幸村の通常4(旋回槍7コマ v2・新キー atk3_yuki)。主武器・徒歩の4段目だけが新しい絵を使い、全7コマが順に出て、命中の時刻(hs14〜he20)に4コマ目が出る。
// 1〜3段目と拾得武器(f.wpn)・馬上は従来の絵のまま。QA_OUTがあればAndroid相当(802×360)の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];
  const P=G.player;P.hp=P.maxhp=9999;P.inv=999;
  const U=SPR.atk3_yuki;out.ready=!!(U&&U.ready&&U.a.spin&&U.a.spin.length===7);
  const run=(idx,wpn)=>{P.wpn=wpn||null;P.x=G.camx+500;P.y=570;P.face=1;P.state='atk';P.st=0;P.cur=P.T.atk[idx];P.hit=new Set();const d=P.T.atk[idx];const used=[],hitFr=[];
   for(let i=0;i<d.dur+2;i++){P.st=i;// 実描画の画像を捕まえて、どのコマが出たかを調べる
        const seen=new Set();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(img===U.img)seen.add(a[0]+','+a[1]);return od.call(this,img,...a);};
    ctx.setTransform(RS,0,0,RS,0,0);drawFighter(P);CanvasRenderingContext2D.prototype.drawImage=od;
    const fi=[...seen].map(k=>U.a.spin.findIndex(q=>k===q[0]+','+q[1])).filter(x=>x>=0);used.push(fi.length?fi[0]:-1);if(i>=d.hs&&i<=d.he)hitFr.push(fi.length?fi[0]:-1);}
   return {used:used.join(','),frames:[...new Set(used)].filter(x=>x>=0).join(' '),hit:[...new Set(hitFr)].join(' ')};};
  out.a4=run(3);out.a1=run(0);out.a3=run(2);out.wpn=run(3,{k:Object.keys(WPN)[0],uses:99});P.wpn=null;
  out.def=P.T.atk[3];return out;});
 const bad=[];
 if(!r.ready)bad.push('atk3_yuki が読めていない');
 if(r.a4.frames!=='0 1 2 3 4 5 6')bad.push('4段目に全7コマが出ない '+JSON.stringify(r.a4));
 if(r.a4.hit!=='4')bad.push('命中の時刻に4コマ目でない '+r.a4.hit);
 if(r.a1.frames!==''||r.a3.frames!=='')bad.push('1〜3段目が新しい絵を使っている '+JSON.stringify([r.a1,r.a3]));
 if(r.wpn.frames!=='')bad.push('拾得武器の4段目が新しい絵を使っている '+JSON.stringify(r.wpn));
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const t of [0,5,10,15,19,24,30]){await p.evaluate(t=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];G.items=[];G.decals=[];const P=G.player;P.hp=P.maxhp=9999;P.inv=999;P.x=G.camx+380;P.y=570;P.face=1;
   const e=mk('sword',G.camx+560,570,1);e.entered=true;e.hp=e.maxhp=99999;e.cool=999;e.face=-1;G.fighters.push(e);P.state='atk';P.cur=P.T.atk[3];P.st=t;P.hit=new Set();
   G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},t);await p.screenshot({path:`${process.env.QA_OUT}/yuki_a4_${String(t).padStart(2,'0')}.png`});}}
 console.log(JSON.stringify({bad,errors,summary:r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
