const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(4000);
await p.evaluate(()=>{window.requestAnimationFrame=()=>0;G.noStory=true;});
let k=0;
for(const [si,bt] of [[0,'boss9'],[2,'boss8'],[5,'boss3']]){
 await p.evaluate(([si,bt])=>{startGame('yuki',null);startStage(si,'yuki',false);G.waves=[{x:50,en:[],boss:bt}];G.wi=0;G.camMax=50;window.ctlKeys=()=>demoCtl(G.player);for(let i=0;i<500;i++)stepGame();frame();},[si,bt]);
 await p.screenshot({path:`tbo_${k++}.png`});}
// full boss playthrough dead check
const r=await p.evaluate(()=>{startGame('yuki',null);startStage(5,'yuki',false);G.waves=[{x:50,en:[],boss:'boss3'}];G.wi=0;G.camMax=50;window.ctlKeys=()=>demoCtl(G.player);let n=0;for(;n<6000;n++){stepGame();if(G.mode!=='play'||G.state!=='run')break;}return [n,G.mode,G.state,G.boss&&G.boss.hp]});
console.log(r,er);await b.close();})();
