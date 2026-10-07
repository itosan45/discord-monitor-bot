// 勝鬨で味方の足軽が集まるか(真田だけ赤備え+六文銭)
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');const OUT=process.env.OUT||require('os').tmpdir();
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(4000);
await p.evaluate(()=>{window.requestAnimationFrame=()=>0;G.noStory=true;});
const res=[];
for(const ch of ['yuki','kage']){
 await p.evaluate(ch=>{startGame(ch,null);startStage(0,ch,false);window.ctlKeys=()=>({});for(let i=0;i<30;i++){stepGame();G.t++;}G.fighters=G.fighters.filter(f=>f.team===0);G.state='bossdown';G.stateT=0;G.slow=0;},ch);
 for(const kt of [110,190,262]){const r=await p.evaluate(kt=>{while(G.stateT<kt){stepGame();G.t++;}frame();return {kt:G.stateT,n:G.kgun&&G.kgun.length,up:G.kgun&&G.kgun.filter(e=>e.up).length,red:G.kgun&&G.kgun[0].red};},kt);res.push([ch,r]);await p.screenshot({path:`${OUT}/tkachi_${ch}_${kt}.png`});}}
console.log(JSON.stringify(res),er);await b.close();})();
