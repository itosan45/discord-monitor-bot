// 手応え検査: 巻き込み(吹き飛んだ敵が他の雑兵を倒す)、反撃(振りかぶり中の敵を斬ると崩れる)、一閃(最後の一人で時間が緩む)。
// 6人の主人公で実際の通常攻撃を当て、数値と攻撃中の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const bad=[],rows=[],shots=[];
  const setup=(hero,list)=>{startGame(hero,null);G.state='run';G.waveOn=false;G.waves=[{x:1e9,en:[]}];G.wi=0;G.items=[];G.props=[];G.proj=[];G.steeds=[];G.hzT=99999;G.sq=[];G.slow=0;G.hitstop=0;
   const f=G.player;f.x=G.camx+300;f.y=570;f.face=1;f.hp=f.maxhp=999;f.inv=0;G.partner=null;const es=list.map(([dx,dy,hp])=>{const e=mk('sword',f.x+dx,570+dy,1);e.hp=e.maxhp=hp;e.entered=true;e.face=-1;e.cool=9999;return e;});G.fighters=[f,...es];G.bowlN=0;G.ctrN=0;G.issenN=0;G.ctrFxT=0;return {f,es};};
  const snap=name=>{renderWorld();shots.push({name,png:cv.toDataURL('image/png').split(',')[1]});};
  const HEROES=['yuki','kage','mitsu','nobu','shin','musashi'];
  for(const hero of HEROES){
   // 巻き込み: 1人目を吹き飛ばし、後ろの2人が倒れるか
   {const {f,es}=setup(hero,[[90,0,500],[170,0,500],[240,8,500]]);hurt(es[0],f,{dmg:6,kb:9,launch:true});let shot=false;
    for(let t=0;t<60;t++){G.t++;stepGame();if(!shot&&G.bowlN>0){shot=true;snap('bowl-'+hero);}}
    const downed=es.slice(1).filter(e=>e.hp<500).length;rows.push({hero,bowl:G.bowlN,downed});if(downed<1)bad.push({hero,noBowl:true});}
   // 反撃: 振りかぶり中の敵に最初の攻撃を当てる
   {const {f,es}=setup(hero,[[80,0,500]]);const e=es[0];startEAtk(e,0);e.st=0;const hs=e.cur.hs;e.cur=Object.assign({},e.cur,{hs:hs+40,he:hs+50});startPAtk(f,0);let st=null;
    for(let t=0;t<30;t++){G.t++;stepGame();if(G.ctrN&&!st){st=e.state;snap('counter-'+hero);}}
    rows.push({hero,counter:G.ctrN,enemyState:st});if(!G.ctrN||st!=='down')bad.push({hero,counter:G.ctrN,st});}
   // 一閃: 最後の1人を倒すと時間が緩み剣閃が出る。他に敵がいる時は出ない
   {const {f,es}=setup(hero,[[80,0,1],[200,0,500]]);G.waves=[{x:1e9,en:[]},{x:1e9,en:[]}];G.waveOn=true;startPAtk(f,0);for(let t=0;t<30;t++){G.t++;stepGame();}
    if(G.issenN)bad.push({hero,issenTooEarly:true});
    const s2=setup(hero,[[80,0,1]]);G.waves=[{x:1e9,en:[]},{x:1e9,en:[]}];G.waveOn=true;startPAtk(s2.f,0);let slow=0,sl=0,shot=false;for(let t=0;t<40;t++){G.t++;stepGame();slow=Math.max(slow,G.slow);sl=Math.max(sl,G.parts.filter(q=>q.k==='slash').length);if(!shot&&sl){shot=true;for(let k=0;k<4;k++){G.t++;stepGame();}snap('issen-'+hero);}}
    const iN=G.issenN;const s3=setup(hero,[[80,0,1]]);startPAtk(s3.f,0);for(let t=0;t<30;t++){G.t++;stepGame();}const offWave=G.issenN;
    rows.push({hero,issen:iN,slow,slash:sl,offWave});if(offWave)bad.push({hero,issenOutsideWave:true});if(iN!==1||!slow||!sl)bad.push({hero,issen:iN,slow,sl});}
  }
  // 見切り: 防御ボタンを押した直後に受けると削られず、相手が崩れる。遅い防御は通常の防御
  for(const hero of HEROES)for(const late of [0,1]){const {f,es}=setup(hero,[[80,0,500]]);const e=es[0];keys.KeyV=true;for(let t=0;t<(late?24:3);t++){G.t++;stepGame();}
   const hp0=f.hp,n0=G.mikiriN||0;hurt(f,e,{dmg:10,kb:3});const mk1=(G.mikiriN||0)-n0;keys.KeyV=false;
   if(!late){for(let t=0;t<3;t++)updParts();snap('mikiri-'+hero);}
   rows.push({hero,late,guard:f.state,mikiri:mk1,chip:Math.round((hp0-f.hp)*10)/10,enemy:e.state});
   if(!late&&(mk1!==1||f.hp<hp0||e.state!=='hurt'))bad.push({hero,mikiriFail:true,mk1,st:e.state});if(late&&(mk1!==0||!(f.hp<hp0)))bad.push({hero,lateGuardWrong:true,mk1});}
  // 追い打ち: 浮いた雑兵に当てると再び浮く。1回の滞空で2回まで。ボスは対象外
  for(const hero of HEROES){const {f,es}=setup(hero,[[70,0,500]]);const e=es[0];G.jugN=0;hurt(e,f,{dmg:5,kb:1,launch:true});let tries=0;
   for(let t=0;t<80;t++){G.t++;stepGame();if(e.state==='down'&&e.z>30&&tries<4&&t%3===0){tries++;f.hit.clear();f.x=e.x-60;strike(f,{rng:120,dmg:5,kb:1,dep:40});if(tries===2)snap('juggle-'+hero);}}
   rows.push({hero,juggle:G.jugN,tries});if(G.jugN<1||G.jugN>2)bad.push({hero,juggle:G.jugN});}
  // 踏み散らし: 馬で走り込むと正面の雑兵が倒れる(既存処理に表示を追加)
  for(const hero of HEROES){const {f,es}=setup(hero,[[260,0,500],[300,10,500]]);f.mount={hp:6,max:6,col:'red'};G.trampleN=0;keys.ArrowRight=true;let shot=false;
   for(let t=0;t<90;t++){G.t++;stepGame();if(!shot&&G.trampleN){shot=true;for(let k=0;k<3;k++){G.t++;stepGame();}snap('trample-'+hero);}}keys.ArrowRight=false;
   const hp=f.mount.hp;rows.push({hero,trample:G.trampleN,mountHp:hp,downed:es.filter(e=>e.hp<500).length});if(G.trampleN<1)bad.push({hero,noTrample:true});}
  // 画面端の跳ね返り: 端へ吹き飛んだ雑兵は1回だけ跳ね返り、画面内に戻る
  for(const hero of HEROES){const {f,es}=setup(hero,[[0,0,500]]);const e=es[0];G.camMax=G.camx;G.waves=[{x:1e9,en:[]},{x:1e9,en:[]}];G.waveOn=true;G.wallPopT=0;f.x=G.camx+W-230;e.x=G.camx+W-140;G.wallN=0;hurt(e,f,{dmg:5,kb:9,launch:true});let shot=false,maxX=0;
   let px=e.x,jump=0,bx=null;for(let t=0;t<160;t++){G.t++;stepGame();maxX=Math.max(maxX,e.x-G.camx);if(G.wallN&&bx===null){const [l,r]=frameExt(e);bx=W-(e.x-G.camx+r);}if(t>0&&!G.hitstop)jump=Math.max(jump,Math.abs(e.x-px)-Math.abs(e.vx||0)-1);px=e.x;if(!shot&&G.wallN){shot=true;snap('wall-'+hero);}}
   const bm=bodyScreenMargin(e),cm=combatScreenMargin(e);rows.push({hero,wall:G.wallN,edgeGap:Math.round(bx),bodyMargin:bm,oldWall:cm,maxJump:+jump.toFixed(1),endX:Math.round(e.x-G.camx),state:e.state});
   if(G.wallN!==1||maxX>W-20||bx>12||jump>5)bad.push({hero,wall:G.wallN,bx,bm,jump});}
  {const {f,es}=setup('yuki',[[150,0,500]]);G.wallN=0;hurt(es[0],f,{dmg:5,kb:9,launch:true});for(let t=0;t<90;t++){G.t++;stepGame();}if(G.wallN)bad.push({wallInMiddle:true});}
  // ボスは巻き込まれない
  {const {f,es}=setup('yuki',[[90,0,500]]);const bo=mk(Object.keys(TY).find(k=>TY[k].boss),f.x+170,570,1);bo.entered=true;bo.cool=9999;G.fighters.push(bo);const h0=bo.hp;hurt(es[0],f,{dmg:6,kb:9,launch:true});for(let t=0;t<60;t++){G.t++;stepGame();}if(bo.hp<h0&&G.bowlN)bad.push({bossBowled:true});}
  return {bad,rows,shots};});
 const dir=(process.env.QA_OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006')+'/qa/feel';fs.mkdirSync(dir,{recursive:true});for(const s of r.shots)fs.writeFileSync(dir+'/'+s.name+'.png',Buffer.from(s.png,'base64'));delete r.shots;
 console.log(JSON.stringify({r,errors}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
