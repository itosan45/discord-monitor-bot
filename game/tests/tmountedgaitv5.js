// Registration/order evidence; horse anatomy is reviewed separately in decoded.png.
const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:802,height:360},isMobile:true});const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startAuto('mitsu',0);const rows=[],shots=[],bad=[];
 for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi']){demoView.actor=hero;demoView.mounted=true;demoView.weapon='';demoView.motion='walk';prepareWalkPreview();G.curCh=hero;G.lowq=true;const order=[],native=ctx.drawImage.bind(ctx);let phase=-1;
 ctx.drawImage=function(im,...q){if(im===SPR['mountwalk5_'+hero].img)phase=q[0]/256;return native(im,...q);};
 for(let t=0;t<80;t++){stepGame();phase=-1;renderWorld();drawHUD();if(phase<0)bad.push({hero,t,bodyMissing:true});if(order.at(-1)!==phase){order.push(phase);if(!shots.some(s=>s.hero===hero&&s.phase===phase))shots.push({hero,phase,png:cv.toDataURL().split(',')[1]});}}
 ctx.drawImage=native;if(order.slice(0,8).join(',')!=='0,1,2,3,0,1,2,3')bad.push({hero,order});if(DATA.spr['mountwalk4_'+hero])bad.push({hero,retiredGaitPreloaded:true});rows.push({hero,order});}return{rows,bad,shots};});
 const out=process.env.OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006/qa/mounted-gait-v5-all/runtime';fs.mkdirSync(out,{recursive:true});for(const s of r.shots)fs.writeFileSync(out+'/'+s.hero+'-phase-'+s.phase+'.png',Buffer.from(s.png,'base64'));delete r.shots;fs.writeFileSync(out+'/tests.json',JSON.stringify({r,errors},null,2));console.log(JSON.stringify({r,errors}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
