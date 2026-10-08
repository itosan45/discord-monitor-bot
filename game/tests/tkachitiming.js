// 勝ちどきをあげよ音声の発話後約0.8秒で勝鬨を開始し、最後まで場面を維持する
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForTimeout(3000);
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;G.noStory=true;startGame('yuki',null);G.state='bossdown';G.stateT=0;G.slow=0;G.demo=false;
  const events=[];AU.on=true;AU.ac={currentTime:0};AU.taiko=()=>{};AU.kc=(k)=>{events.push([G.stateT,'kc',k]);return true;};AU.kachi=()=>{events.push([G.stateT,'kachi']);return true;};AU.crowd=()=>events.push([G.stateT,'crowd']);
  while(G.state==='bossdown'&&G.stateT<660)stepGame();return {events,state:G.state,endFrame:660};});
 console.log(JSON.stringify({r,errors}));await b.close();
 const speech=r.events.find(e=>e[1]==='kc'&&e[2]==='call'),chant=r.events.find(e=>e[1]==='kachi');
 if(errors.length||!speech||!chant||chant[0]-speech[0]!==192||r.state!=='bossdown')process.exit(1);
})().catch(e=>{console.error(e);process.exit(1);});
