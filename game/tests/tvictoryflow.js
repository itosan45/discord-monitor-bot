// 勝鬨(えいえいおー)を終えたら、ファンファーレとスコア画面(STAGE CLEAR)が同時に始まる。ファンファーレの前にスコアが出たり、後に遅れたりしない。デモは従来どおり
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;
  startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;
  let ffFrame=-1,clearFrame=-1,ffN=0,stopN=0;const of=AU.fanfare;AU.fanfare=function(){ffN++;ffFrame=G.stateT;return of.apply(this,arguments);};const os=AU.ffStop;AU.ffStop=function(){stopN++;return os.apply(this,arguments);};
  G.demo=false;G.state='bossdown';G.stateT=0;G.victoryShift=0;G.ffAt=400;G.clearLim=0;G.slow=0;
  let n=0;for(;n<900&&G.state==='bossdown';n++){G.t++;stepGame();}
  clearFrame=G.stateT;const stateAfter=G.state;
  // 画面: STAGE CLEARが描かれる + 勝鬨の最後のポーズ
  ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();
  // スキップでファンファーレが止まる
  for(let i=0;i<70;i++){G.t++;stepGame();}
  return {ffFrame,ffN,stateAfter,n,ffAt:G.ffAt,clearFrame,lim:G.clearLim,stateAfterSkip:G.state,stopN};});
 console.log(JSON.stringify(r));
 const bad=[];if(r.stateAfter!=='clear')bad.push('state');if(r.ffN!==1)bad.push('ffN'+r.ffN);if(r.ffFrame!==r.ffAt||r.n!==r.ffAt)bad.push('timing'+r.n+'/'+r.ffAt);
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
