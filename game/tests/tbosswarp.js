// 小早川の瞬身: 消える→主人公の背後(向きの反対側)に予告→現れる→一呼吸おいて斬る。現れる前は当たらず、現れた後に当たる。割り込まれても姿が戻る
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out=[];
  for(const face of [1,-1]){startGame('yuki',null);G.wi=G.waves.length-1;G.waveOn=true;G.fighters=G.fighters.filter(f=>f.team!==1);const P=G.player;P.x=G.camx+640;P.y=570;P.face=face;P.hp=P.maxhp=9999;P.inv=0;
   const e=spawnEn('boss4',1);e.x=P.x+face*260;e.y=570;e.inv=0;G.banner=null;e.cool=999;startEAtk(e,1);const log={hidAt:-1,showAt:-1,hitAt:-1,side:0};
   const PX=P.x;for(let i=1;i<=70&&e.state==='atk';i++){P.x=PX;P.face=face;G.t++;stepGame();if(G.banner&&G.banner.boss)G.banner=null;
    if(e.hide&&log.hidAt<0)log.hidAt=e.st;if(!e.hide&&log.hidAt>=0&&log.showAt<0){log.showAt=e.st;log.side=sgn(e.x-P.x);}if(P.hp<9999&&log.hitAt<0)log.hitAt=e.st;}
   out.push({face,...log,behind:log.side===-face});}
  // 割り込み: 消えている間にやられ状態にしても姿が戻る
  startGame('yuki',null);G.wi=G.waves.length-1;G.fighters=G.fighters.filter(f=>f.team!==1);const e=spawnEn('boss4',1);G.banner=null;startEAtk(e,1);for(let i=0;i<14;i++){G.t++;stepGame();}const hid=e.hide;e.state='hurt';e.st=0;G.t++;stepGame();
  return {out,interrupt:{hid,after:e.hide}};});
 console.log(JSON.stringify({r,errors}));
 const bad=r.out.filter(o=>o.hidAt!==10||o.showAt!==24||!o.behind||o.hitAt<38);
 if(errors.length||bad.length||!r.interrupt.hid||r.interrupt.after)process.exitCode=1;else console.log('OK');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
