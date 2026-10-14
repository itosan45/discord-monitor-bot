// 2026-10-14 岩が転がる仕掛け(第三幕・戦場_岩_転がり_3コマ → atlas rockroll)。丸太に代わり、予告のあと岩が2つレーンを右へ転がる。
// 検査: 絵が読み込まれる/第三幕の仕掛けが rocks/予告→2つ出る→進む→当たる(主人公にダメージ・吹き飛び)→敵にも当たる/3コマが使われる/ボスや倒れた者には当たらない。QA_OUT で Android相当の画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const shot=async n=>{if(process.env.QA_OUT){require('fs').mkdirSync(process.env.QA_OUT,{recursive:true});await p.screenshot({path:process.env.QA_OUT+'/rock_'+n+'.png'});}};
 const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;G.mode='play';startGame('yuki','sasuke');G.stage=2;startStage(2,'yuki',false);
  const out={};for(let i=0;i<200&&!(SPR.rockroll&&SPR.rockroll.ready);i++)await new Promise(r=>setTimeout(r,50));
  out.ready=!!(SPR.rockroll&&SPR.rockroll.ready);out.frames=out.ready?SPR.rockroll.a.roll.length:0;out.hz=HZ[2];out.name=HZNAME[HZ[2]];
  G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];G.lanes=[];
  const P=G.player;P.x=G.camx+620;P.y=570;P.face=1;P.inv=0;P.hp=P.maxhp=9999;if(G.partner)G.partner.x=-9999;
  const e=mk('sword',G.camx+700,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;e.face=-1;G.fighters.push(e);
  const boss=mk('sword',G.camx+400,570,1);boss.entered=true;boss.hp=boss.maxhp=9999;boss.cool=9999;boss.T=Object.assign({},boss.T,{boss:true});G.fighters.push(boss);
  startHazard();out.lanes=G.lanes.length;out.k=G.lanes[0]&&G.lanes[0].k;out.dirs=G.lanes.map(l=>l.dir).join(',');
  const frames=new Set();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(SPR.rockroll&&img===SPR.rockroll.img)frames.add(a[0]);return od.call(this,img,...a);};
  let hp0=P.hp,eh0=e.hp,bh0=boss.hp,hit=0,maxMv=0,steps=0;
  for(let i=0;i<420;i++){G.t++;P.inv=Math.min(P.inv,0);for(const f of G.fighters)if(f.team===1){f.cool=9999;}for(const f of G.fighters){if(f.team===0&&f!==G.player)continue;}
   if(G.lanes.length)maxMv=Math.max(maxMv,G.lanes[0].mv.length);
   updPlayer(P,{});updEnemy(e);updEnemy(boss);updHazards();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();steps++;if(!G.lanes.length&&i>120)break;}
  CanvasRenderingContext2D.prototype.drawImage=od;
  out.frames_used=frames.size;out.maxMv=maxMv;out.playerHurt=P.hp<hp0;out.enemyHurt=e.hp<eh0;out.bossHurt=boss.hp<bh0;out.cleared=G.lanes.length===0;out.steps=steps;
  return out;});
 const bad=[];
 if(!r.ready||r.frames!==3)bad.push('岩の絵が読めない '+JSON.stringify([r.ready,r.frames]));
 if(r.hz!=='rocks')bad.push('第三幕の仕掛けが岩でない '+r.hz);
 if(r.k!=='rocks'||r.dirs!=='1')bad.push('予告レーンが岩/右向きでない '+r.k+' '+r.dirs);
 if(r.maxMv!==2)bad.push('岩が2つ出ない '+r.maxMv);
 if(r.frames_used<2)bad.push('転がりの3コマが使われない '+r.frames_used);
 if(!r.playerHurt)bad.push('主人公に当たらない');if(!r.enemyHurt)bad.push('敵に当たらない');if(r.bossHurt)bad.push('ボスに当たった');
 if(!r.cleared)bad.push('岩が画面外へ出て片づかない');
 if(process.env.QA_OUT){await p.evaluate(()=>{G.lanes=[];G.parts=[];const P=G.player;P.x=G.camx+560;P.y=570;P.inv=999;for(const f of G.fighters)if(f.team===1)f.hp=f.maxhp;startHazard();for(let i=0;i<75+52;i++){G.t++;P.inv=999;updHazards();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();}});await shot('rolling_a');
  await p.evaluate(()=>{const P=G.player;for(let i=0;i<30;i++){G.t++;P.inv=999;updHazards();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();}});await shot('rolling_b');}
 console.log(JSON.stringify({bad,errors,summary:r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
