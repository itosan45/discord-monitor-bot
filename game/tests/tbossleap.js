// ボスの大跳躍(BLEAP): 8人とも、主人公を跳び越えて画面の反対側の端まで跳ぶ。頭が画面外へ出ない・着地点が画面内・着地で近くの主人公に当たる・ジャンプ4コマを順に使う
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out=[];
  for(const bt of ['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9']){
   startGame('yuki',null);G.wi=G.waves.length-1;G.waveOn=true;G.fighters=G.fighters.filter(f=>f.team!==1);const P=G.player;P.x=G.camx+640;P.y=570;P.inv=0;P.hp=P.maxhp=9999;
   const e=spawnEn(bt,1);e.x=G.camx+300;e.y=570;e.inv=0;G.banner=null;startEAct(e,BLEAP);
   const x0=e.x;let maxZ=0,frames=new Set(),landX=null,landF=0,n=0,headTop=999,offscreen=0;const J=SPR['bjump_'+bt];
   for(let i=0;i<260&&e.state==='atk';i++){G.t++;stepGame();n++;if(G.banner&&G.banner.boss)G.banner=null;maxZ=Math.max(maxZ,e.z);
    if(J&&J.ready){const k=e.z<=2?0:e.vz>3?1:e.vz>-3?2:3;frames.add(k);const q=J.a.jump[k];headTop=Math.min(headTop,e.y-e.z+q[5]*e.sc);}
    if(e.x<G.camx||e.x>G.camx+W)offscreen++;if(e.blDone&&landX===null){landX=e.x;landF=i;}}
   out.push({bt,x0:Math.round(x0-G.camx),landX:Math.round(landX-G.camx),dist:Math.round(Math.abs(landX-x0)),maxZ:Math.round(maxZ),air:landF,headTop:Math.round(headTop),frames:[...frames].sort().join(''),offscreen,ended:e.state!=='atk',playerHit:P.hp<9999});
   // 着地点のそばにいる主人公には当たる
   P.hp=9999;P.x=G.camx+1000;P.state='idle';P.inv=0;e.x=G.camx+300;e.state='idle';e.z=0;startEAct(e,BLEAP);let hit=false;for(let i=0;i<260&&e.state==='atk';i++){G.t++;stepGame();if(G.banner&&G.banner.boss)G.banner=null;if(e.st===BLEAP.hs+1){P.x=e.blTx+60;P.y=e.blTy;P.state='idle';}if(P.hp<9999)hit=true;}
   out[out.length-1].nearHit=hit;}
  return out;});
 for(const o of r)console.log(JSON.stringify(o));
 const bad=r.filter(o=>o.dist<500||o.headTop<0||o.offscreen||!o.ended||o.frames!=='0123'||o.air<50||o.maxZ<150||!o.nearHit);
 console.log(JSON.stringify({bad:bad.map(o=>o.bt),errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
