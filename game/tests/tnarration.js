// オープニングのナレーション(2026-10-12): 7本が読み込まれ、各カードの頭(20更新後)に順に再生され、
// カードの長さは「声の長さ+余韻」以上になり、スキップで止まり、消音のときは従来の長さで鳴らさない。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--autoplay-policy=no-user-gesture-required']});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>typeof sprAllReady==='function'&&sprAllReady());
 const r=await p.evaluate(async()=>{requestAnimationFrame=()=>0;const bad=[],out={};
  const calls=[],stops=[];const origN=AU.narr.bind(AU),origS=AU.narrStop.bind(AU);AU.narr=i=>{calls.push({i,opT:G.opT});origN(i);};AU.narrStop=()=>{stops.push(G.opT);origS();};
  AU.init();await new Promise(r=>setTimeout(r,300));
  for(let k=0;k<100&&!AU.nrReady;k++)await new Promise(r=>setTimeout(r,100));
  out.dataN=(DATA.nr||[]).length;out.nrd=DATA.nrd;out.bufN=AU.nrBuf?AU.nrBuf.length:null;out.ready=!!AU.nrReady;out.on=AU.on;
  if(out.dataN!==7||out.bufN!==7||!out.ready)bad.push('読み込み');
  if(AU.nrBuf)for(let i=0;i<7;i++)if(Math.abs(AU.nrBuf[i].duration-DATA.nrd[i])>0.15)bad.push({lenMismatch:i,buf:AU.nrBuf[i].duration,nrd:DATA.nrd[i]});
  // 1) 最後まで流す
  startOpening();let n=0;while(G.mode==='opening'&&n<20000){stepOpening();n++;}
  out.frames=n;out.opDur=G.opDur;out.calls=calls.slice();
  const base=OPN.map(c=>c.d);
  if(!G.opDur||G.opDur.some((d,i)=>d<base[i]))bad.push('カードが元の長さより短い');
  if(AU.on&&AU.nrBuf)for(let i=0;i<7;i++)if(G.opDur[i]<20+AU.nrBuf[i].duration*60+40)bad.push({cardShort:i});
  if(AU.on){if(calls.length!==7||calls.some((c,i)=>c.i!==i))bad.push({calls:calls.map(c=>c.i)});
   let acc=0;calls.forEach((c,i)=>{const start=acc+20;if(Math.abs(c.opT-start)>1)bad.push({timing:i,opT:c.opT,want:start});acc+=G.opDur[i];});}
  if(G.mode!=='title')bad.push('終わってタイトルに戻らない');
  // 2) 2枚目の途中でスキップ
  calls.length=0;stops.length=0;startOpening();n=0;while(G.mode==='opening'&&!(calls.length>=2)&&n<20000){stepOpening();n++;}
  const cardsBefore=calls.length;pressed.Space=true;stepOpening();for(const k in pressed)delete pressed[k];
  out.skip={calls:cardsBefore,mode:G.mode,stopped:stops.length,nrSrc:AU.nrSrc===null};
  if(AU.on&&(G.mode!=='title'||!stops.length||AU.nrSrc!==null))bad.push({skip:out.skip});
  // 3) 消音のときは元の長さで、鳴らさない
  AU.muted=true;AU.narrStop();let played=0;AU.narr=i=>{origN(i);if(AU.nrSrc)played++;};startOpening();n=0;while(G.mode==='opening'&&n<20000){stepOpening();n++;}
  out.muted={played,sameAsBase:JSON.stringify(G.opDur)===JSON.stringify(base)};
  if(played||!out.muted.sameAsBase)bad.push({muted:out.muted});AU.muted=false;
  return {bad,out};});
 console.log(JSON.stringify({bad:r.bad,out:r.out,errors}));
 }finally{await b.close();}})();
