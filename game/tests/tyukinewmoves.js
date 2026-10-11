// 2026-10-11 幸村の新素材3点: 徒歩の溜め=六段突き(12コマ・6回命中・最後に打ち上げ)、馬上の旋風突撃の専用絵(6コマ)、タイトルの十文字槍。
// 他の主人公・拾得武器の溜めと旋風突撃は従来どおり。QA_OUTがあればスマホ相当の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;
  const seen=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(seen.has(img))seen.get(img).add(a[0]);return od.call(this,img,...a);};
  const R=SPR.yukirokudan1,M=SPR.mountwhirl1_yuki;seen.set(R.img,new Set());seen.set(M.img,new Set());seen.set(TSPEAR,new Set());
  const setup=(hero,face,mount)=>{startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=null;P.mount=mount?{hp:6,max:6,col:'red'}:null;P.x=G.camx+640;P.y=570;P.face=face;P.state='idle';P.inv=999;return P;};
  const foe=(x)=>{const e=mk('sword',x,570,1);e.entered=true;e.hp=e.maxhp=999;e.cool=999;G.fighters.push(e);return e;};
  let lh=0;const oh=window.hurt;window.hurt=function(t,a,d){if(d&&d.launch&&a===G.player&&a.cur&&a.cur.ck==='rokudan')lh++;return oh(t,a,d);};
  const rows=[];
  for(const face of [1,-1]){const P=setup('yuki',face,false),near=foe(P.x+face*150),far=foe(P.x+face*330);lh=0;seen.get(R.img).clear();
   startCharge(P);const ck=P.cur&&P.cur.ck;let hits=0,last=near.hp,n=0;
   for(;n<120&&P.state==='atk';n++){G.t++;updPlayer(P,{});near.cool=far.cool=999;if(near.hp<last){hits++;last=near.hp;}drawFighter(P);}
   rows.push({face,ck,hits,launched:lh,farHit:far.hp<far.maxhp,frames:seen.get(R.img).size,dur:n});}
  const others={};for(const [hero,w] of [['yuki','naginata'],['kage',null],['mitsu',null],['nobu',null],['shin',null],['musashi',null]]){const P=setup(hero,1,false);if(w)P.wpn={k:w,uses:9};startCharge(P);others[hero+(w?'_'+w:'')]=P.cur&&(P.cur.ck||(P.cur.iai?'iai':'rush'));}
  const whirl=[];for(const [hero,face] of [['yuki',1],['yuki',-1],['kage',1]]){const P=setup(hero,face,true);seen.get(M.img).clear();G.t++;updMount(P,{gdP:true});for(let i=0;i<80&&P.state==='matk';i++){G.t++;updMount(P,{});drawFighter(P);}whirl.push({hero,face,frames:seen.get(M.img).size});}
  startTitle();for(let i=0;i<120;i++){G.ttlT++;drawTitle();}
  return {rows,others,whirl,title:seen.get(TSPEAR).size>0};});
 console.log(JSON.stringify(r));
 const bad=[];for(const o of r.rows){if(o.ck!=='rokudan'||o.hits!==6||o.launched!==1||o.farHit||o.frames!==12)bad.push('rokudan'+o.face);}
 if(r.others.yuki_naginata!=='spin'||r.others.kage!=='iai')bad.push('others');
 for(const o of r.whirl){if(o.hero==='yuki'?o.frames!==6:o.frames!==0)bad.push('whirl'+o.hero+o.face);}
 if(!r.title)bad.push('title');
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,st] of [['rokudan_thrust',30],['rokudan_last',57]])await p.evaluate(st=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.banner=null;G.fighters=G.fighters.filter(f=>f.team===0);const P=G.player;P.wpn=null;P.x=G.camx+560;P.y=570;P.face=1;P.inv=999;for(const dx of [150,190]){const e=mk('sword',P.x+dx,570+(dx-170),1);e.entered=true;e.hp=e.maxhp=999;e.cool=999;G.fighters.push(e);}
   startCharge(P);for(let i=0;i<st;i++){G.t++;updPlayer(P,{});}ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},st),await p.screenshot({path:`${process.env.QA_OUT}/${name}.png`});
  for(const [name,st] of [['whirl_a',12],['whirl_b',21]])await p.evaluate(st=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.banner=null;G.fighters=G.fighters.filter(f=>f.team===0);const P=G.player;P.wpn=null;P.mount={hp:6,max:6,col:'red'};P.x=G.camx+500;P.y=570;P.face=1;P.inv=999;G.t++;updMount(P,{gdP:true});for(let i=0;i<st;i++){G.t++;updMount(P,{});}ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},st),await p.screenshot({path:`${process.env.QA_OUT}/${name}.png`});
  await p.evaluate(()=>{startTitle();G.ttlT=150;ctx.setTransform(RS,0,0,RS,0,0);drawTitle();});await p.screenshot({path:`${process.env.QA_OUT}/title_spear.png`});}
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
