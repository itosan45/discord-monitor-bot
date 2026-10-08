// Walk must use a dedicated full-body gait, not alternate two idle horse poses.
const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true})).newPage();
 await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('musashi',null);G.camx=0;G.lowq=true;
  const bad=[],cases=[];
  for(const face of [1,-1]){
   const f=mk('musashi',640,570,0);f.mount={hp:6,max:6,col:'iron'};f.face=face;G.player=f;G.fighters=[f];
   const frames=new Set(),native=ctx.drawImage.bind(ctx);
   ctx.drawImage=function(im,...q){if(q.length===8){const key=Object.keys(SPR).find(k=>SPR[k].img===im);if(key==='mountwalk4_musashi')frames.add(q.slice(0,4).join(','));}return native(im,...q);};
   for(let t=0;t<64;t++){updPlayer(f,face===1?{r:true}:{l:true});ctx.clearRect(0,0,1280,720);drawFighter(f);}
   ctx.drawImage=native;cases.push({face,frames:frames.size});if(frames.size!==8)bad.push({face,walkingFrames:frames.size,expected:8});
  }
  return{cases,bad};
 });console.log(JSON.stringify(r));await b.close();if(r.bad.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
