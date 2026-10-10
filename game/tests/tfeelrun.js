// 手応えの通し検査: 6人×6ステージを自動デモAIで自然進行させ(ステージ開始からクリアまで)、
// 巻き込み・反撃・一閃・見切り・追い打ち・蹴散らしの発生回数、クリア可否、エラー、平均更新時間を記録する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const heroes=(process.env.HEROES||'yuki,kage,mitsu,nobu,shin,musashi').split(','),rows=[],bad=[];
 for(const hero of heroes)for(let si=0;si<6;si++){
  const r=await p.evaluate(([si,hero])=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame(hero,null);startStage(si,hero,false);G.auto=true;G.lives=99;
   const K=['bowlN','ctrN','issenN','mikiriN','jugN','trampleN','wallN'];for(const k of K)G[k]=0;let ms=0,n=0,maxEn=0,res='timeout';
   for(let i=0;i<30000;i++){G.t++;const t0=performance.now();stepGame();if(i%30===0)renderWorld();ms+=performance.now()-t0;n++;
    if(i%10===0)maxEn=Math.max(maxEn,G.fighters.filter(e=>e.team===1&&e.hp>0).length);
    if(G.state==='clear'){res='clear';break;}if(G.state==='continue'||G.state==='over'){res=G.state;break;}}
   const o={hero,stage:si+1,res,frames:n,avgMs:+(ms/n).toFixed(2),maxEn};for(const k of K)o[k.replace('N','')]=G[k];return o;},[si,hero]);
  rows.push(r);console.error(JSON.stringify(r));if(r.res!=='clear')bad.push({hero:r.hero,stage:r.stage,res:r.res});}
 const sum={};for(const k of ['bowl','ctr','issen','mikiri','jug','trample','wall'])sum[k]=rows.reduce((s,r)=>s+r[k],0);
 console.log(JSON.stringify({bad,sum,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
