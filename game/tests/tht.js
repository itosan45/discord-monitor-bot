const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3500);
await p.evaluate(()=>{window.requestAnimationFrame=()=>0;G.mode='diff';G.diffSel=1;pressed.Enter=true;frame();for(const k in pressed)delete pressed[k];});
const shots=[[1,40],[2,40],[3,30],[4,62],[5,40],[6,100],[7,60],[8,40],[9,120],[10,22]];
const log=[];
for(const [si,tt] of shots){const r=await p.evaluate(([si,tt])=>{while(G.mode==='howto'&&(G.ht.i<si||(G.ht.i===si&&G.ht.t<tt))){frame();for(const k in pressed)delete pressed[k];}
  const pl=G.player;return [G.mode,G.ht&&G.ht.i,pl.state,pl.chg||0,pl.wpn&&pl.wpn.k,G.fighters.filter(f=>f.team===1).map(f=>f.state).join('/'),!!G.ult].join(' ');},[si,tt]);log.push(r);await p.screenshot({path:'ht_'+si+'.png'});}
console.log(log.join('\n'));
await p.evaluate(()=>{let n=0;while(G.mode==='howto'&&n<5000){frame();for(const k in pressed)delete pressed[k];n++;}});console.log('end',await p.evaluate(()=>G.mode+' '+G.selStep));
console.log(er);await b.close();})();
