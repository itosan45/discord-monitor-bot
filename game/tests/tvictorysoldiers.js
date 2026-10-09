// Real victory soldier rendering, including Android viewport scaling.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-victory-soldiers');fs.mkdirSync(out,{recursive:true});
 const errors=[],reports=[];
 for(const viewport of [{width:1280,height:720},{width:915,height:412},{width:412,height:915}]){
  const context=await browser.newContext({viewport}),p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');
  await p.waitForFunction(()=>SPR.kgun_sword?.ready&&SPR.kgun_armor?.ready);
  const r=await p.evaluate(()=>{
   window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('kage',null);G.banner=null;G.fighters=G.fighters.filter(f=>f.team===0);G.camx=0;G.player.x=640;G.player.y=620;G.state='bossdown';G.stateT=0;G.slow=0;G.victoryShift=0;G.lowq=true;
   const bad=[],samples=[];
   for(const key of ['kgun_sword','kgun_armor'])for(const red of [false,true])for(const face of [-1,1])for(let pose=0;pose<4;pose++){
    ctx.clearRect(0,0,1280,720);drawKgun({key,red,face,pose,x:640,y:600,z:0,t:0,mv:false,up:true});
    const pixels=ctx.getImageData(0,0,1280,720).data;let x0=1280,x1=0,y0=720,y1=0,count=0;
    for(let y=0;y<720;y++)for(let x=0;x<1280;x++)if(pixels[(y*1280+x)*4+3]>40){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);count++;}
    if(count<1500||x0<16||x1>1263||y0<16||y1>703)bad.push({key,red,face,pose,count,x0,x1,y0,y1});
    samples.push({key,red,face,pose,ground:y1});
   }
   const states=[];for(const t of [328,370,405,440,478,520]){while(G.stateT<t){stepGame();G.t++;}frame();states.push({t:G.stateT,n:G.kgun?.length,armor:G.kgun?.filter(e=>e.key==='kgun_armor').length,up:G.kgun?.filter(e=>e.up).length,airborne:G.kgun?.filter(e=>e.z!==0).length});}
   if(states.some(s=>s.n!==10||s.armor!==3||s.airborne!==0)||states[0].up!==0||states.slice(1).some(s=>s.up!==10))bad.push({states});
   const grounds=new Set(samples.filter(s=>!s.red).map(s=>s.key+':'+s.ground));if(grounds.size!==2)bad.push({grounds:[...grounds]});
   const rect=ctx.canvas.getBoundingClientRect();
   return {bad,samples:samples.length,states,canvas:{x:rect.x,y:rect.y,width:rect.width,height:rect.height},viewport:{width:innerWidth,height:innerHeight}};
  });
  await p.screenshot({path:path.join(out,`victory-${viewport.width}x${viewport.height}.png`)});reports.push(r);await context.close();
 }
 await browser.close();fs.writeFileSync(path.join(out,'browser-qa.json'),JSON.stringify({reports,errors},null,2));console.log(JSON.stringify({reports,errors}));
 if(errors.length||reports.some(r=>r.bad.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
