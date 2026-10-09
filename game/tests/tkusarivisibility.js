// A returning browser can retain the pre-kusari atlas for 24 hours.
// Serve that old image for unversioned URLs while keeping current metadata.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),cp=require('child_process');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:915,height:412},isMobile:true,hasTouch:true})).newPage();
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const old=cp.execFileSync('git',['show','92bb33d^:gfx/atlas_musashi.webp'],{maxBuffer:8*1024*1024});
 let staleServed=0;
 await p.route('**/gfx/atlas_musashi.webp*',r=>{if(!new URL(r.request().url()).searchParams.has('v')){staleServed++;return r.fulfill({body:old,contentType:'image/webp'});}return r.continue();});
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const result=await p.evaluate(()=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('musashi',null);G.camx=0;
  const rows=[],bad=[],shots=[];
  for(const h of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const lowq of [false,true])for(const moving of [false,true])for(const face of [-1,1]){
   const f=mk(h,640,570,0);f.wpn={k:'kusari',uses:99};f.inv=99999;f.t=0;f.face=face;G.player=f;G.fighters=[f];G.partner=null;G.proj=[];G.items=[];G.props=[];G.lowq=lowq;
   let minPixels=Infinity;
   for(let t=0;t<96;t++){
    G.t=t;updPlayer(f,{atkH:true,r:moving&&face===1,l:moving&&face===-1});f.x=640;
    if(!f.kspin)continue;
    ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,1280,720);drawFighter(f);
    const data=ctx.getImageData(570,380,140,190).data;let pixels=0;for(let i=3;i<data.length;i+=4)if(data[i]>80)pixels++;
    minPixels=Math.min(minPixels,pixels);if(pixels<1500)bad.push({h,lowq,moving,face,t,pixels});
    if(t===48&&lowq&&face===1)shots.push({name:h+'-'+(moving?'moving':'idle'),png:cv.toDataURL().split(',')[1]});
   }
   rows.push({h,lowq,moving,face,minPixels});
  }
  return {rows,bad,shots};
 });
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-kusari-visible');fs.mkdirSync(out,{recursive:true});
 for(const s of result.shots)fs.writeFileSync(path.join(out,s.name+'.png'),Buffer.from(s.png,'base64'));delete result.shots;
 await p.evaluate(()=>{renderWorld();drawHUD();drawOverlays();tc.style.display='block';});
 await p.screenshot({path:path.join(out,'android-spin-moving.png')});
 fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({...result,staleServed,errors},null,2));
 console.log(JSON.stringify({cases:result.rows.length,bad:result.bad.length,examples:result.bad.slice(0,4),staleServed,errors}));
 await b.close();if(result.bad.length||staleServed||errors.length)process.exitCode=1;
})();
