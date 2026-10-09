// Hold/release input must work on the whole mounted body, not only foot sprites.
const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:802,height:360},isMobile:true,hasTouch:true}),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);G.auto=false;G.demo=false;G.camx=0;const bad=[],shots=[];let cases=0;
 for(const h of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const mounted of [false,true])for(const face of [-1,1])for(const y of [YMIN,570,YMAX])for(const low of [false,true]){
  G.state='run';G.lowq=low;G.parts=[];G.items=[];G.props=[];G.proj=[];G.t=0;const f=mk(h,640,y,0);f.face=face;f.inv=999;f.wpn={k:'kusari',uses:99};if(mounted)f.mount={hp:6,max:6,col:'iron'};G.player=f;G.fighters=[f];
  const tick=c=>{G.t++;updPlayer(f,c);ctx.clearRect(0,0,1280,720);drawFighter(f);};
  for(let t=0;t<50;t++)tick({atkP:t===0,atkH:true,...(t>40?(face===1?{r:true}:{l:true}):{})});
  const row={h,mounted,face,y,low};if(!f.kspin||Math.abs(f.x-640)<5)bad.push({...row,spin:f.kspin,moved:f.x-640});
  if(mounted&&face===1&&y===570&&low){renderWorld();shots.push({name:h+'-spin',png:cv.toDataURL().split(',')[1]});}
  const e=mk('spear',f.x+face*340,y,1);e.hp=e.maxhp=1000;e.entered=true;e.cool=9999;G.fighters.push(e);
  tick({atkH:false});if(!f.cur?.kth||f.state!==(mounted?'matk':'atk'))bad.push({...row,releaseState:f.state});
  for(let t=0;t<10;t++)tick({atkH:false});const damage=1000-e.hp;if(damage<=0||f.wpn?.uses!==98)bad.push({...row,damage,uses:f.wpn?.uses});
  if(mounted&&face===1&&y===570&&low){renderWorld();shots.push({name:h+'-throw',png:cv.toDataURL().split(',')[1]});}
  for(let t=0;t<30;t++)tick({atkH:false});if(Math.abs(e.x-f.x)>110||f.state!=='idle'||f.kspin)bad.push({...row,pullDistance:Math.abs(e.x-f.x),endState:f.state});
  cases++;
 }
 let lastUseCases=0;
 for(const h of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const mounted of [false,true]){
  const f=mk(h,640,570,0);f.wpn={k:'kusari',uses:1};f.inv=999;if(mounted)f.mount={hp:6,max:6,col:'iron'};G.player=f;G.fighters=[f];G.state='run';
  for(let t=0;t<40;t++){G.t++;updPlayer(f,{atkH:true});}updPlayer(f,{atkH:false});
  for(let t=0;t<20;t++){G.t++;updPlayer(f,{atkH:false});}if(!f.wpn||!f.cur?.kth)bad.push({h,mounted,lastUseEndedEarly:true});
  for(let t=0;t<25;t++){G.t++;updPlayer(f,{atkH:false});}if(f.wpn||f.state!=='idle')bad.push({h,mounted,lastUseNotConsumed:true});lastUseCases++;
 }
 let interruptedCases=0;
 for(const mounted of [false,true]){const f=mk('musashi',640,570,0);f.wpn={k:'kusari',uses:1};if(mounted)f.mount={hp:6,max:6,col:'iron'};G.player=f;G.fighters=[f];G.state='run';for(let t=0;t<40;t++)updPlayer(f,{atkH:true});updPlayer(f,{atkH:false});for(let t=0;t<9;t++)updPlayer(f,{atkH:false});f.state='hurt';f.st=0;updPlayer(f,{atkH:false});if(f.wpn||f.kspin||f.kpull)bad.push({mounted,interruptedThrow:true});interruptedCases++;}
 demoView.actor='musashi';demoView.weapon='kusari';demoView.mounted=true;demoView.motion='spin';G.auto=true;prepareWalkPreview();for(let t=0;t<40;t++)stepGame();autoUI(true);const options=[...document.querySelectorAll('[aria-label="確認する動作"] option')].map(o=>o.value);if(!options.includes('spin')||!options.includes('throw')||!G.player.kspin)bad.push({mountedDebug:options,spin:G.player.kspin});
 demoView.motion='idle';prepareWalkPreview();if(G.player.kspin||G.player.chg||G.player.kpull)bad.push('debug reset retained chain state');
 return{bad,cases,lastUseCases,interruptedCases,options,shots};});
 const out=process.env.OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006/qa/kusari-mounted';fs.mkdirSync(out,{recursive:true});for(const s of r.shots)fs.writeFileSync(out+'/'+s.name+'.png',Buffer.from(s.png,'base64'));delete r.shots;fs.writeFileSync(out+'/tests.json',JSON.stringify({r,errors},null,2));console.log(JSON.stringify({r:{...r,bad:r.bad.slice(0,12)},errors}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
