// A repeatable gait scene must use real player updates, remain on screen and pause.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await b.newPage({viewport:{width:802,height:360},hasTouch:true,isMobile:true}),errors=[];
 p.on('pageerror',e=>errors.push(e.message));
 await p.goto((process.argv[2]||'http://127.0.0.1:8876/index.html')+'?preview=walk&hero=musashi&mount=1');await p.waitForFunction(()=>sprAllReady());
 const result=await p.evaluate(()=>{
  if(typeof prepareWalkPreview!=='function')return{bad:['walk preview missing']};
  window.__qaRAF=window.requestAnimationFrame;window.requestAnimationFrame=()=>0;AU.muted=true;const bad=[],keys=new Set(),faces=new Set(),f=G.player;
  if(!G.auto||G.mode!=='play'||demoView.motion!=='walk'||!f.mount||f.T.type!=='musashi')bad.push('query did not enter the mounted Musashi scene');
  const native=ctx.drawImage.bind(ctx);ctx.drawImage=function(im,...q){if(im===SPR.mountwalk4_musashi.img)keys.add(q[0]);return native(im,...q);};
  for(let i=0;i<600;i++){stepGame();G.t++;if(i<64){ctx.clearRect(0,0,1280,720);drawFighter(f);}faces.add(f.face);if(G.fighters.length!==1||G.proj.length||G.items.length||G.steeds.length)bad.push('scene gained actors');if(f.x<440||f.x>840||f.state!=='walk')bad.push('walk left bounds or stopped');}
  ctx.drawImage=native;if(keys.size!==8||faces.size!==2)bad.push({keys:keys.size,faces:faces.size});
  demoView.paused=true;const x=f.x;for(let i=0;i<10;i++)if(demoViewTick())stepGame();if(f.x!==x)bad.push('pause moved');
  demoView.steps=1;if(demoViewTick())stepGame();if(f.x===x||demoViewTick())bad.push('step did not advance exactly once');
  demoView.settings=true;autoUI(true);return{bad,keys:keys.size,faces:[...faces],mode:G.mode};
 });
 await p.evaluate(()=>{window.requestAnimationFrame=window.__qaRAF;requestAnimationFrame(loop);});if(!result.bad.length){await p.getByLabel('確認モード').selectOption('stage');await p.waitForTimeout(100);if(!await p.evaluate(()=>demoView.motion==='auto'&&G.mode==='story'))result.bad.push('auto did not restore story');await p.getByRole('button',{name:'一体デバッグ',exact:true}).click();await p.waitForTimeout(100);if(!await p.evaluate(()=>G.mode==='play'&&G.fighters.length===1))result.bad.push('walk control did not restore preview');}
 await p.evaluate(()=>{if(window.__qaRAF)window.requestAnimationFrame=window.__qaRAF;ctx=MCTX;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();});
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-gait-preview');fs.mkdirSync(out,{recursive:true});await p.reload();await p.waitForFunction(()=>sprAllReady()&&G.auto&&demoView.motion==='walk');await p.screenshot({path:path.join(out,'android-walk-preview.png')});
 result.pageErrors=errors;fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await b.close();if(result.bad.length||errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
