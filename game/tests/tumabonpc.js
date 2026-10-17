// 2026-10-14 デモ(自動プレイ)の主人公とパートナーが、柵の向こうに鉄砲隊がいても馬防柵まで行って壊し、先へ進む(オーナー「NPCが柵を越えようとしない・壊そうともしない」)。
// 柵の向こうの鉄砲隊(見える敵が全部柵の向こう)でも柵を攻撃する/パートナーも手伝う/壊したあとは鉄砲隊と戦いに進む。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(async(HEROES)=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;window.dropItem=()=>{};const out={},bad=[];
  for(const [name,partner,hero] of HEROES.flatMap(h=>[[h,null,h],[h+'+sasuke',h==='yuki'?'sasuke':null,h]])){
   startGame(hero,partner);G.stage=2;startStage(2,hero,false);G.auto=true;G.demo=false;G.state='run';G.banner=null;G.fighters=G.fighters.filter(f=>f.team===0);G.waveOn=false;
   const P=G.player,Q=G.partner;P.hp=P.maxhp=99999;P.inv=999;if(Q){Q.hp=Q.maxhp=99999;Q.inv=999;}
   const w=G.props.find(q=>q.k==='umabo');if(!w){bad.push('柵がない');continue;}
   G.wi=2;G.camMax=G.waves[2].x;G.camx=w.x-640;P.x=w.x-420;P.y=570;P.wx=null;if(Q){Q.x=w.x-480;Q.y=600;Q.wx=null;}
   let t=0,tb=-1,sawGarr=0,minDist=1e9,atkOnFence=0;
   for(;t<5000;t++){G.t++;P.inv=999;if(Q)Q.inv=999;updWorld();const g=G.fighters.filter(f=>f.hold&&f.hp>0&&f.team===1).length;sawGarr=Math.max(sawGarr,g);
    if(!w.broken)minDist=Math.min(minDist,Math.abs(w.x-P.x));if(tb<0&&w.broken){tb=t;}if(tb>=0&&t>tb+400)break;}
   out[name]={broken:!!w.broken,tBroken:tb,sawGarr,minDist:Math.round(minDist),heroPast:P.x>w.x,heroX:Math.round(P.x-w.x),partnerPast:Q?Q.x>w.x:null};
   if(!w.broken)bad.push(name+': 柵を壊さない '+JSON.stringify(out[name]));if(!out[name].sawGarr)bad.push(name+': 鉄砲隊が出ていない(試験が成り立たない)');
   if(tb>3000)bad.push(name+': 壊すのが遅すぎる '+tb);}
  return {out,bad};},(process.env.HEROES||'yuki').split(','));
 console.log(JSON.stringify({bad:r.bad,errors,out:r.out}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
