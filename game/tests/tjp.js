const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;const o={};for(const h of['yuki','kage','mitsu','nobu','shin','musashi']){G.noStory=true;startGame(h,null);for(let i=0;i<20;i++)stepGame();const pl=G.player;G.fighters=G.fighters.filter(f=>f.team===0);
 pl.state='idle';pl.z=0;pl.vz=0;pl.st=0;pl.vz=pl.T.jump*1.2;pl.state='jump';let mz=0,n=0;while(n<200){stepGame();n++;mz=Math.max(mz,pl.z);if(pl.state!=='jump'&&pl.state!=='jatk')break;}o[h]=[Math.round(mz),n];}
 G.noStory=true;startGame('yuki',null);for(let i=0;i<20;i++)stepGame();const pl=G.player;G.fighters=G.fighters.filter(f=>f.team===0);pl.vz=pl.T.jump*1.2;pl.state='jump';for(let i=0;i<20;i++)stepGame();o.top=Math.round(pl.y-pl.z-200*pl.sc);return o;});
console.log(r,er);await b.close();})();
