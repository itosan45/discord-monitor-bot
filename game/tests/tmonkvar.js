// 2026-10-14 鉄球大僧の色違い(オーナー「3体出てくると違和感がすごい。服の色か肌の色で違いをつけて」)。出る順に 元(紫)→b(緑の袈裟)→c(朱の袈裟+日焼け)→元…/
// それぞれ別のアトラス画像で描く(コマの位置は同じ)/画像は monk のある幕だけ読む/旧アトラス(_v1)は読まない。QA_OUTがあれば3体が並んだ Android相当(802×360)の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  const wait=async ks=>{for(let i=0;i<300;i++){if(ks.every(k=>SPR[k]&&SPR[k].ready))return true;await new Promise(r=>setTimeout(r,50));}return false;};
  // 読み込み: monk のない幕(0)は色違いも旧アトラスも読まない/ある幕(2)は monk・b・c
  G.mode='play';startStage(0,'yuki',false);let t=sprTarget();out.stage0={mon:t.filter(k=>/^monk/.test(k)).join(','),v1:t.filter(k=>/_v1$/.test(k)).length};
  startStage(2,'yuki',false);t=sprTarget();out.stage2=t.filter(k=>/^monk/.test(k)).sort().join(',');
  out.ready=await wait(['monk','monk_b','monk_c']);
  const same=JSON.stringify(SPR.monk.a)===JSON.stringify(SPR.monk_b.a)&&JSON.stringify(SPR.monk.a)===JSON.stringify(SPR.monk_c.a);out.samePos=same;
  // 出る順: spawnEn で3体
  G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];
  const vars=[];for(let i=0;i<5;i++){spawnEn('monk',i%2?1:-1);const e=G.fighters[G.fighters.length-1];vars.push(e.var);}out.vars=vars.join(',');
  // 描画: 各変種が自分の画像で描かれる
  const mons=G.fighters.filter(f=>f.T&&f.T.type==='monk').slice(0,3);const used=[];const od=CanvasRenderingContext2D.prototype.drawImage;let cur=null;
  CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(cur!==null){for(const k of['monk','monk_b','monk_c'])if(SPR[k]&&img===SPR[k].img)cur.add(k);}return od.call(this,img,...a);};
  for(const e of mons){e.entered=true;e.x=G.camx+640;e.y=570;e.hp=e.maxhp=99999;e.cool=999;cur=new Set();ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);used.push([e.var,[...cur].join('+')]);}
  CanvasRenderingContext2D.prototype.drawImage=od;cur=null;out.used=used.map(u=>u.join(':')).join(' ');
  // 他の敵は色違いにならない
  spawnEn('spear',1);out.spearVar=G.fighters[G.fighters.length-1].var||null;
  return out;});
 const bad=[];
 if(r.stage0.mon!==''||r.stage0.v1)bad.push('monk のない幕で読んでいる '+JSON.stringify(r.stage0));
 if(r.stage2!=='monk,monk_b,monk_c,monkfx')bad.push('monk のある幕の読み込み '+r.stage2);
 if(!r.ready)bad.push('色違いの画像が読めない');
 if(!r.samePos)bad.push('色違いのコマの位置が元と違う(pack_monk_variants.py を作り直す)');
 if(r.vars!==',b,c,,b')bad.push('出る順の色違い '+r.vars);
 if(r.used!==':monk b:monk_b c:monk_c')bad.push('描画に使った画像 '+r.used);
 if(r.spearVar)bad.push('足軽が色違い '+r.spearVar);
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,st] of [['walk','walk'],['smash','smash']]){await p.evaluate(st=>{G.mode='play';startStage(2,'yuki',false);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.items=[];G.decals=[];
   const P=G.player;P.x=-9999;P.inv=999;for(let k=0;k<3;k++){spawnEn('monk',1);const e=G.fighters[G.fighters.length-1];e.entered=true;e.x=G.camx+330+k*300;e.y=520+k*55;e.hp=e.maxhp=99999;e.cool=999;e.face=-1;e.inv=999;
    if(st==='walk'){e.state='walk';e.wp=(k*5+2)/16*TAU;}else{startEAtk(e,0);for(let i=0;i<30+k*6;i++){e.cool=999;updEnemy(e);}}}
   G.flashT=0;G.hitstop=0;G.shake=0;G.banner=null;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();},st);await p.screenshot({path:`${process.env.QA_OUT}/monkvar_${name}.png`});}}
 console.log(JSON.stringify({bad,errors,summary:r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
