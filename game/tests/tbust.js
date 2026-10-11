// 2026-10-12 ステージ外の会話(プロローグ・幕間・エンディング・オープニング)では兜なしの胸像を使い、ステージ中のボス前の会話は従来のまま(兜あり)。QA_OUTで画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;const rows=[];
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(used.has(img))used.set(img,used.get(img)+1);return od.call(this,img,...a);};
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi']){
   const bi=bustFor(hero);for(let i=0;i<100&&!(bi.complete&&bi.naturalWidth);i++)await new Promise(r=>setTimeout(r,50));
   G.curCh=hero;used.clear();used.set(bi,0);
   startGame(hero,null);G.curCh=hero;startStory('s0',()=>{});G.story.L=[['@','……行くぞ。'],['最上義光','来たか。']];G.story.c=99;
   ctx.setTransform(RS,0,0,RS,0,0);drawStory();const normal=used.get(bi);
   // ステージ中のボス戦の会話: 兜なしを使わない
   const e=mk('boss1',G.camx+800,570,1);G.story=null;startBossStory(e);const inStage=!!(G.story&&G.story.inStage);used.set(bi,0);G.story.c=99;ctx.setTransform(RS,0,0,RS,0,0);drawStory();const boss=used.get(bi);
   rows.push({hero,loaded:bi.naturalWidth>0,normal,boss,inStage});}
  // オープニング(幸村の胸像)
  const by=bustFor('yuki');used.clear();used.set(by,0);startOpening();G.opT=0;let t=0,i=0;const OP=[];for(const c of OPN)OP.push(c);let opIdx=OPN.findIndex(c=>c.hero);let acc=0;for(let k=0;k<opIdx;k++)acc+=OPN[k].d;G.opDur=OPN.map(c=>c.d);G.opT=acc+120;ctx.setTransform(RS,0,0,RS,0,0);drawOpening();const op=used.get(by);
  return {rows,op};});
 console.log(JSON.stringify(r));
 const bad=[];for(const o of r.rows){if(!o.loaded||o.normal<1||o.boss!==0||!o.inStage)bad.push(o);}if(!(r.op>=1))bad.push('opening');
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const hero of ['yuki','musashi','shin']){await p.evaluate(hero=>{startGame(hero,null);G.curCh=hero;startStory('s1',()=>{});G.story.L=[['@','真田の槍、受けていただこう。いざ、参る！'],['最上義光','来たか。']];G.story.i=0;G.story.c=999;G.story.t=60;ctx.setTransform(RS,0,0,RS,0,0);drawStory();},hero);await p.screenshot({path:`${process.env.QA_OUT}/story_${hero}.png`});}
  await p.evaluate(()=>{startGame('kage',null);G.curCh='kage';const e=mk('boss1',G.camx+800,570,1);G.story=null;startBossStory(e);G.story.c=999;G.story.t=60;ctx.setTransform(RS,0,0,RS,0,0);drawStory();});await p.screenshot({path:`${process.env.QA_OUT}/boss_kage.png`});}
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
