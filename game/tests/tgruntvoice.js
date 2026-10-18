// 雑魚の死亡声(2026-10-12 オーナー「ゾンビのような声(元の1・2番)を外して、ぐわー・ぎゃああを作って」):
// dv.foot は 元の7本+新しい3本=10本、外した2本は無く、実際に倒すと10本すべてが選ばれ得て、エラーが出ない。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--autoplay-policy=no-user-gesture-required']});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>typeof sprAllReady==='function'&&sprAllReady());
 const r=await p.evaluate(async()=>{requestAnimationFrame=()=>0;const bad=[],out={};
  const sha=async s=>{const h=await crypto.subtle.digest('SHA-1',new TextEncoder().encode(s));return [...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,'0')).join('').slice(0,12);};
  const REMOVED=['6da9ab56b81f','6411bed900cf'];const hs=[];for(const s of DATA.dv.foot)hs.push(await sha(s));
  out.footN=DATA.dv.foot.length;out.removedPresent=REMOVED.filter(h=>hs.includes(h));
  if(out.footN!==10)bad.push({footN:out.footN});if(out.removedPresent.length)bad.push({removed:out.removedPresent});
  if((DATA.dvn||[]).length!==3||DATA.dvn.some(h=>!hs.includes(h)))bad.push('新しい声の記録');
  AU.init();for(let k=0;k<100&&!(AU.dvBuf&&AU.dvBuf.foot&&AU.dvBuf.foot.length);k++)await new Promise(r=>setTimeout(r,100));
  out.bufN=AU.dvBuf.foot.length;out.durs=AU.dvBuf.foot.map(x=>+x.duration.toFixed(2));if(out.bufN!==10)bad.push({bufN:out.bufN});
  // 実際に雑魚を倒した時の選ばれ方
  const used=new Set();const orig=AU.ac.createBufferSource.bind(AU.ac);AU.ac.createBufferSource=function(){const s=orig();Object.defineProperty(s,'buffer',{set(v){if(v){const i=AU.dvBuf.foot.indexOf(v);if(i>=0)used.add(i);}},get(){return null;}});return s;};
  const e={T:{type:'sword',ai:'melee',boss:false},x:G.camx+400};
  for(let i=0;i<400;i++){AU.lastSc=-9;AU.scream(e);}
  out.used=[...used].sort((a,b)=>a-b);if(used.size<9)bad.push({used:out.used});
  return {bad,out};});
 console.log(JSON.stringify({bad:r.bad,out:r.out,errors}));
 }finally{await b.close();}})();
