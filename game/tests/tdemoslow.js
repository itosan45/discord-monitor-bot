// Exercise the real scheduler, including frozen canvas and one-frame advance.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const result=await p.evaluate(()=>{
  window.__qaRAF=window.requestAnimationFrame;window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startDemo(0);G.lowq=true;G.autoSpd=1;
  // Drive the same loop with an exact number of 60 Hz ticks.
  const ticks=n=>{acc=0;last=0;for(let t=1;t<=n;t++)loop(t*1000/60+0.00001);};
  const rows=[],bad=[];
  for(const speed of [1,0.5,0.25]){G.autoSpd=speed;demoView.credit=0;const before=G.t;ticks(120);const updates=G.t-before;rows.push({speed,updates});if(updates!==120*speed)bad.push({speed,updates});}
  demoView.paused=true;autoUI(true);const before=G.t,png=cv.toDataURL();ticks(120);
  if(G.t!==before||cv.toDataURL()!==png)bad.push({pauseMoved:true});
  demoView.steps=1;ticks(120);if(G.t!==before+1)bad.push({stepUpdates:G.t-before});
  // A single step must also override the existing x4 automatic-play multiplier.
  G.mode='play';G.demo=false;G.auto=true;G.autoSpd=4;let calls=0;const original=stepGame;stepGame=()=>{calls++;original();};demoView.steps=1;ticks(4);stepGame=original;if(calls!==1)bad.push({autoStepCalls:calls});
  G.auto=false;demoView.paused=true;G.autoSpd=0.25;const normalBefore=G.t;ticks(120);if(G.t-normalBefore!==120)bad.push({normalPlaySlowed:G.t-normalBefore});
  // A boss attack shown by the actual demo renderer, paused at an attack frame.
  startDemo(0);G.titleT=-9999;G.camx=0;G.banner=null;G.vo=null;G.waveOn=true;G.sq=[];
  const boss=mk('boss2',820,570,1);boss.entered=true;boss.inv=99999;boss.hp=boss.maxhp=99999;boss.face=-1;G.player.x=480;G.player.y=570;G.player.inv=99999;G.fighters=[G.player,boss];G.boss=boss;
  startEAtk(boss,0);G.autoSpd=0.25;demoView.paused=false;demoView.credit=0;
  ticks(32);demoView.paused=true;autoUI(true);
  const rect=autoEl.getBoundingClientRect();if(rect.left<0||rect.right>innerWidth||rect.bottom>innerHeight)bad.push({controlsClipped:true,rect:rect.toJSON()});
  return {rows,bad,autoStepCalls:calls,boss:{state:boss.state,st:boss.st},errors:window.__err||[]};
 });
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-demo-slow');fs.mkdirSync(out,{recursive:true});
 const session=await p.context().newCDPSession(p);const shot=async file=>{const data=await session.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(file,Buffer.from(data.data,'base64'));};
 await p.evaluate(()=>{window.requestAnimationFrame=window.__qaRAF;});
 await shot(path.join(out,'android-slow-boss.png'));
 // Use the visible mobile controls rather than only internal state setters.
 const before=await p.evaluate(()=>G.t);await p.getByRole('button',{name:'1コマ',exact:true}).dispatchEvent('pointerdown');
 await p.evaluate(()=>{window.requestAnimationFrame=()=>0;acc=0;last=0;loop(1000/60+0.00001);window.requestAnimationFrame=window.__qaRAF;});
 const after=await p.evaluate(()=>G.t);if(after-before!==1)result.bad.push({buttonStep:after-before});
 await shot(path.join(out,'android-next-frame.png'));
 const layout=await p.evaluate(()=>{G.mode='play';G.auto=true;demoView.settings=false;autoUI(true);const compact=autoEl.getBoundingClientRect().toJSON();demoView.settings=true;autoUI(true);const stage=autoEl.querySelector('[aria-label="幕"]'),speed=autoEl.querySelector('[aria-label="再生速度"]');return{compact,expanded:autoEl.getBoundingClientRect().toJSON(),stageOptions:stage?.options.length,speedOptions:speed?.options.length,numericButtons:[...autoEl.querySelectorAll('button')].filter(b=>/^\d+$/.test(b.textContent)).length};});
 if(layout.expanded.height>50||layout.compact.height>50||layout.compact.left<0||layout.compact.right>802||layout.stageOptions!==6||layout.numericButtons)result.bad.push({layout});
 await shot(path.join(out,'android-settings-dropdowns.png'));
 await p.evaluate(()=>{demoView.settings=false;autoUI(true);});await shot(path.join(out,'android-compact-controls.png'));result.layout=layout;
 fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({...result,pageErrors:errors},null,2));console.log(JSON.stringify({...result,pageErrors:errors}));
 await b.close();if(result.bad.length||result.errors.length||errors.length)process.exitCode=1;
})();
