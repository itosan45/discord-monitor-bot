// Final boss flow: stop BGM -> call -> chant -> fanfare -> score screen.
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForTimeout(3000);
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;G.noStory=true;startGame('yuki',null);G.demo=false;
  const events=[];Object.defineProperty(AU,'on',{value:true,configurable:true});AU.ac={currentTime:0};AU.taiko=()=>{};AU.sfx=()=>{};
  AU.stopBgm=()=>events.push([0,'stopBgm']);AU.kc=k=>{events.push([G.stateT,'kc',k]);return true;};AU.kachi=()=>{events.push([G.stateT,'kachi']);return true;};
  AU.ffBuf={duration:4};AU.fanfare=()=>events.push([G.stateT,'fanfare']);G.wi=G.waves.length-1;bossDown(mk('boss1',640,590,1),G.player);G.slow=0;
  let frames=0;while(G.state==='bossdown'&&frames<1200){stepGame();frames++;}events.push([frames,'score']);return {events,state:G.state};});
 console.log(JSON.stringify({r,errors}));await b.close();
 const ev=r.events,call=ev.find(e=>e[1]==='kc'),chant=ev.find(e=>e[1]==='kachi'),fan=ev.find(e=>e[1]==='fanfare'),score=ev.find(e=>e[1]==='score');
 if(errors.length||ev[0][1]!=='stopBgm'||!call||!chant||chant[0]-call[0]!==192||!fan||fan[0]<=chant[0]+4.64*60||score[0]<=fan[0]+4*60||r.state!=='clear')process.exit(1);
})().catch(e=>{console.error(e);process.exit(1);});
