const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto(process.argv[2]||'http://127.0.0.1:8765/index.html');await p.waitForTimeout(5000);
const r=await p.evaluate(()=>{const bad=[];for(const k in SPR){const S=SPR[k];if(!S.ready||!S.a||!Object.keys(S.a).length)bad.push(k);}return {n:Object.keys(SPR).length,bad};});
console.log(JSON.stringify(r),er.slice(0,3));await b.close();})();
