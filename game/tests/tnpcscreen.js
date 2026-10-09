// Enter from either side, fight, knock back, and scroll the camera. The demo
// must ignore waiting/off-screen enemies and keep every entered NPC in view.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startDemo(0);const bad=[],rows=[];
  for(const key of Object.keys(TY).filter(k=>TY[k].ai))for(const side of [-1,1]){
   G.state='run';G.demoT=0;G.waveT=0;G.camx=0;G.camMax=0;G.waveOn=true;G.wi=0;G.sq=[];G.fighters=[];G.parts=[];G.items=[];G.props=[];G.proj=[];G.steeds=[];G.lanes=[];G.fires=[];G.marks=[];G.stuck=[];G.hzT=99999;G.hitstop=0;G.slow=0;
   const f=mk('musashi',640,570,0);f.hp=f.maxhp=99999;f.inv=99999;G.player=f;G.partner=null;G.fighters=[f];
   const e=spawnEn(key,side);e.hp=e.maxhp=99999;e.inv=0;e.cool=1;e.rt=1;G.boss=e.T.boss?e:null;let entered=false,frames=0;
   const spawnX=e.x;if(!e.entered||spawnX<G.camx+fighterScreenMargin(e)||spawnX>G.camx+W-fighterScreenMargin(e))bad.push({key,side,spawnOutside:true});
   e.entered=false;e.x=side<0?-70:W+70;const off=demoCtl(f);if(off.atkP||off.spcP||off.r||off.l)bad.push({key,side,chasedBeforeEntry:true});e.entered=true;e.x=spawnX;
   for(let t=0;t<650;t++){
    G.t++;if(t===350){G.camMax=1000;f.x=G.camx+850;}
    if(t===450&&e.entered){e.state='hurt';e.hurtT=20;e.st=0;e.vx=side*50;}
    updWorld();frames++;
    if(!e.entered){if(e.state==='atk'||e.mA?.k==='a1')bad.push({key,side,t,offscreenAttack:true});continue;}
    entered=true;const margin=fighterScreenMargin(e),x=e.x-G.camx;
    if(x<margin-.01||x>W-margin+.01)bad.push({key,side,t,x,margin});
   }
   if(!entered)bad.push({key,side,neverEntered:true});rows.push({key,side,frames,entered,finalType:e.T.type});
  }
  // Long hero attacks at both edges must reserve the full silhouette as well.
  for(const h of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const face of [-1,1]){
   G.camx=0;const f=mk(h,face<0?0:1280,570,0);f.face=face;startPAtk(f,Math.min(2,f.T.atk.length-1));updPlayer(f,{});const sp=sprPos(f,SPR[h]),q=sp.arr[Math.floor(sp.pos)],left=f.x+Math.min(face*q[4],face*(q[4]+q[2]*(q[6]||1)))*f.sc,right=f.x+Math.max(face*q[4],face*(q[4]+q[2]*(q[6]||1)))*f.sc;
   if(left<8||right>1272)bad.push({hero:h,face,left,right});
  }
  return {rows,bad:bad.slice(0,30),badCount:bad.length,frameErrors:window.__err||[]};
 });
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-npc-screen');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({...r,errors},null,2));console.log(JSON.stringify({...r,errors}));await b.close();if(r.badCount||r.frameErrors.length||errors.length)process.exitCode=1;
})();
