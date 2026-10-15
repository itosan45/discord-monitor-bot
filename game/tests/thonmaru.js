// 2026-10-14 A-017 ボス戦の本丸背景(敵武将8人)。幕を始めるとその幕のボスの本丸だけ読む/ボスが出ると約50コマで本丸へ切り替わる/最終幕は3人のボスが続けて切り替わる/
// 通常の背景はボスのいない間は変わらない。QA_OUTがあれば Android相当(802×360) の画面を保存する(ボス8人×切替前後)。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  const BS=['boss9','boss4','boss8','boss5','boss2','boss1','boss7','boss3'];
  const wait=async k=>{for(let i=0;i<200;i++){const im=HONMARU[k];if(im&&im.complete&&im.naturalWidth)return true;await new Promise(r=>setTimeout(r,50));}return false;};
  // 起動時には本丸を読まない(BGIMGは数字のキーだけ)
  out.bgKeys=Object.keys(BGIMG).join(',');out.honAtBoot=Object.keys(HONMARU).join(',');
  out.dataKeys=Object.keys(DATA.bg).filter(k=>k.startsWith('honmaru_')).length;
  out.stages=[];
  for(let si=0;si<6;si++){startStage(si,'yuki',false);const bosses=G.waves.filter(w=>w.boss).map(w=>w.boss);
   out.stages.push({si,bosses:bosses.join(','),loaded:Object.keys(HONMARU).sort().join(','),hon:G.hon||null});}
  // 各ボスの切替(幕ごとに startStage で読み直す)
  out.fade=[];
  for(const bk of BS){const si=[...Array(6).keys()].find(i=>{startStage(i,'yuki',false);return G.waves.some(w=>w.boss===bk);});
   startStage(si,'yuki',false);G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];
   const ok=await wait(bk);G.t+=1;spawnEn(bk,1);const h0=G.hon&&G.hon.k;
   const px=(a)=>{ctx.setTransform(RS,0,0,RS,0,0);drawBG(G.camx,G.t);return null;};
   out.fade.push({bk,si,ok,hon:h0,prev:G.hon&&G.hon.prev});}
  return out;});
 const bad=[];
 if(r.dataKeys!==9/* 8武将+第七幕の夜の家康本丸(boss3n, 2026-10-15) */)bad.push('配信データの本丸 '+r.dataKeys);
 if(r.honAtBoot.split(',').some(k=>k&&k!=='boss9'))bad.push('起動時に別の幕の本丸まで読んでいる '+r.honAtBoot); // 起動直後のデモは第一幕(boss9)
 if(/honmaru/.test(r.bgKeys))bad.push('BGIMGに本丸が入っている '+r.bgKeys);
 const exp={0:'boss9',1:'boss4',2:'boss8',3:'boss5',4:'boss2',5:'boss1,boss7,boss3'};
 for(const s of r.stages){if(s.bosses!==exp[s.si])bad.push('幕'+s.si+'のボス '+s.bosses);if(s.loaded!==s.bosses.split(',').sort().join(','))bad.push('幕'+s.si+'で読んだ本丸が違う(他の幕の分を捨てていない) '+s.loaded);if(s.hon)bad.push('幕の開始でG.honが残っている');}
 for(const f of r.fade){if(!f.ok)bad.push(f.bk+' の本丸が読めない');if(f.hon!==f.bk)bad.push(f.bk+' G.hon='+f.hon);}
 // 画面の確認(ボスが出た直後=元の背景、50コマ後=本丸)
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const bk of ['boss9','boss4','boss8','boss5','boss2','boss1','boss7','boss3']){for(const [tag,dt] of [['a',2],['b',25],['c',60]]){
   await p.evaluate(async([bk,dt])=>{const si=[0,1,2,3,4,5].find(i=>{startStage(i,'yuki',false);return G.waves.some(w=>w.boss===bk);});startStage(si,'yuki',false);G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.decals=[];G.items=[];
    for(let i=0;i<200&&!(HONMARU[bk]&&HONMARU[bk].complete&&HONMARU[bk].naturalWidth);i++)await new Promise(r=>setTimeout(r,50));
    const P=G.player;P.x=G.camx+330;P.y=570;P.inv=999;P.hp=P.maxhp=9999;G.t+=1;spawnEn(bk,1);const e=G.boss;e.x=G.camx+W-300;e.y=585;e.entered=true;e.inv=999;e.state='idle';e.face=-1;G.banner=null;G.t+=dt;G.hitstop=0;G.shake=0;G.flashT=0;
    ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},[bk,dt]);
   if(tag==='a'||tag==='c')await p.screenshot({path:`${process.env.QA_OUT}/honmaru_${bk}_${tag}.png`});}}}
 console.log(JSON.stringify({bad,errors,summary:{bgKeys:r.bgKeys,dataKeys:r.dataKeys,stages:r.stages.map(s=>s.si+':'+s.bosses),fade:r.fade.map(f=>f.bk+':'+f.hon+(f.prev?'<'+f.prev:''))}}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
