// Focused reproduction of the reported Musashi rider proportion/cropping defect.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;G.autoPk=null;startAuto('musashi',0);G.mode='play';G.state='run';G.banner=null;G.vo=null;G.cut=null;G.lowq=true;G.camx=0;
  const bad=[],rows=[],shots=[],native=ctx.drawImage.bind(ctx);let drawn=[];ctx.drawImage=function(im,...q){if(q.length===8){const key=Object.keys(SPR).find(k=>SPR[k].img===im);if(key)drawn.push(key);if(q[0]<0||q[1]<0||q[0]+q[2]>im.width||q[1]+q[3]>im.height)bad.push({sourceBounds:key,q});}return native(im,...q);};
  for(const weapon of [null,...Object.keys(WPN)])for(const low of [true,false])for(const face of [1,-1])for(const y of [YMIN,570,YMAX]){
   const f=mk('musashi',640,y,0);f.wpn=weapon?{k:weapon,uses:999}:null;f.mount={hp:6,max:6,col:'iron'};f.face=face;G.player=f;G.fighters=[f];G.items=[];G.props=[];G.parts=[];G.proj=[];G.lowq=low;G.t=0;
   for(const mode of ['idle','walk','attack']){
    f.state='idle';f.st=0;f.x=640;f.z=0;f.cur=null;if(mode==='attack')updPlayer(f,{atkP:true});
    for(let t=0;t<24;t++){
     if(mode!=='attack'||t)updPlayer(f,mode==='walk'?{r:true}:{});G.t++;drawn=[];ctx.clearRect(0,0,1280,720);drawFighter(f);
     if(!drawn.includes(mode==='attack'&&f.state==='matk'?'mountfull3_musashi':mode==='walk'?'mountwalk4_musashi':'mountbody3_musashi'))bad.push({wrongSheet:drawn,weapon,mode,t});
     if(drawn.includes('musashi')||drawn.includes('musashi_u'))bad.push({standingBodyUsed:true,mode,weapon,t});
     const ink=(x,y,w,h)=>{const a=ctx.getImageData(x,y,w,h).data;for(let j=3;j<a.length;j+=4)if(a[j]>8)return true;return false;};
     if(ink(0,0,1280,1)||ink(0,719,1280,1)||ink(0,0,1,720)||ink(1279,0,1,720))bad.push({edge:true,weapon,mode,t,y});
     if(!weapon&&low&&face===1&&y===570&&t===10){renderWorld();shots.push({name:mode,png:cv.toDataURL().split(',')[1]});}
    }
   }rows.push({weapon,low,face,y});
  }
  // Mounted special must animate the whole rider too, rather than hold idle.
  for(const weapon of [null,...Object.keys(WPN)]){
   const f=mk('musashi',640,570,0);f.wpn=weapon?{k:weapon,uses:999}:null;f.mount={hp:6,max:6,col:'iron'};f.ki=300;G.player=f;G.fighters=[f];G.lowq=true;const phases=new Set();
   const spy=ctx.drawImage;ctx.drawImage=function(im,...q){if(im===SPR.mountfull3_musashi.img&&q.length===8)phases.add(q.slice(0,4).join(','));return spy(im,...q);};
   updPlayer(f,{spcP:true});for(let t=0;t<40;t++){drawFighter(f);if(!weapon&&[10,17,27].includes(t)){renderWorld();shots.push({name:'special-'+t,png:cv.toDataURL().split(',')[1]});}updPlayer(f,{});}
   ctx.drawImage=spy;if(phases.size<4)bad.push({mountedSpecialFrozen:true,weapon,phases:phases.size});
  }
  ctx.drawImage=native;
  // The visible dropdown sets the current rider and survives hero/stage restart.
  demoView.paused=true;demoView.settings=true;autoUI(true);const horse=autoEl.querySelector('[aria-label="馬の有無"]');horse.value='1';horse.dispatchEvent(new Event('change'));if(!G.player.mount||demoView.steps!==1)bad.push({horseOptionFailed:true});startAuto('musashi',1);if(!G.player.mount)bad.push({horseRestartFailed:true});horse.value='0';horse.dispatchEvent(new Event('change'));if(G.player.mount)bad.push({dismountOptionFailed:true});
  setDemoMount(true);const rider=G.player,enemy=mk('sword',rider.x+30,rider.y,1);rider.hp=99999;
  for(let i=0;i<8;i++){rider.inv=0;hurt(rider,enemy,{dmg:1,kb:0});}
  if(!rider.mount||rider.mount.hp!==6)bad.push({fixedHorseLost:true});
  respawn(rider);if(!rider.mount)bad.push({fixedHorseLostOnRespawn:true});
  G.auto=false;setDemoMount(true);for(let i=0;i<8;i++){rider.inv=0;hurt(rider,enemy,{dmg:1,kb:0});}if(rider.mount)bad.push({normalGameHorseInvulnerable:true});respawn(rider);if(rider.mount)bad.push({normalRespawnMounted:true});G.auto=true;
  setDemoMount(false);G.steeds=[{x:rider.x,y:rider.y,face:1,t:60}];rider.state='idle';updSteeds();if(rider.mount)bad.push({unwantedAutoMount:true});
  return{rows:rows.length,frames:rows.length*72,specialCases:10,specialFrames:400,bad,shots};
 });
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-mounted-musashi');fs.mkdirSync(out,{recursive:true});for(const s of r.shots)fs.writeFileSync(path.join(out,s.name+'.png'),Buffer.from(s.png,'base64'));delete r.shots;fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({r,errors},null,2));console.log(JSON.stringify({r,errors}));await b.close();if(r.bad.length||errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
