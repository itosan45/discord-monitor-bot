const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const ctxx=await b.newContext({viewport:{width:1280,height:720},hasTouch:true,isMobile:false});const p=await ctxx.newPage();
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3500);
const cdp=await ctxx.newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:parseFloat(process.argv[2]||'6')});
const r=await p.evaluate(async()=>{G.noStory=true;G.diff=1;startGame('yuki','shin');await new Promise(r=>setTimeout(r,1500));G.banner=null;
 // busy scene
 for(let i=0;i<10;i++){const e=mk(['spear','sword','gun','archer','samurai'][i%5],G.camx+300+i*80,500+(i%4)*40,1);e.entered=true;G.fighters.push(e);}
 const T={};const wrap=n=>{const f=window[n];if(!f)return;window[n]=function(){const t=performance.now();const r=f.apply(this,arguments);T[n]=(T[n]||0)+performance.now()-t;return r;};};
 ['renderWorld','drawFighter','drawSprite','drawFighterP','drawTrail','drawShadowF','drawHazards','drawSteeds','drawProj','drawItem','drawProp','sprWhite','drawWarn','postFX','drawBG'].forEach(wrap);
 let n=0,t0=performance.now();const fr=[];let last=t0;await new Promise(res=>{function f(now){fr.push(now-last);last=now;n++;if(now-t0<5000)requestAnimationFrame(f);else res();}requestAnimationFrame(f);});
 fr.sort((a,b)=>a-b);const o={fps:(n/5).toFixed(1),p50:fr[n>>1].toFixed(1),p90:fr[Math.floor(n*0.9)].toFixed(1),lowq:G.lowq,parts:G.parts.length};for(const k in T)o[k]=(T[k]/5).toFixed(0)+'ms/s';return o;});
console.log(JSON.stringify(r));await b.close();})();
