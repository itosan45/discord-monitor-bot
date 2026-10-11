// 2026-10-12 奥義(Lv3)の切り込み帯も、新しい細帯の絵(全6人)を使う。QA_OUTで画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const rows=[];const CS=SPR.cutin;let n=0;const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(img===CS.img)n++;return od.call(this,img,...a);};
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi']){startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.x=G.camx+400;P.y=570;P.ki=300;n=0;startUlt(P);let first=-1;for(let i=0;i<60;i++){G.ult&&(G.ult.t=i);ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();if(n>0&&first<0)first=i;}rows.push({hero,n,first});}
  return rows;});
 console.log(JSON.stringify(r));const bad=r.filter(o=>o.n<10);
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});for(const hero of ['yuki','shin']){await p.evaluate(hero=>{startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.x=G.camx+400;P.y=570;P.ki=300;startUlt(P);G.ult.t=16;G.flashT=0;G.hitstop=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();},hero);await p.screenshot({path:`${process.env.QA_OUT}/ult_${hero}.png`});}}
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
