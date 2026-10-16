// A moving hero must use walking artwork, including while holding a pickup.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage();
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(heroFilter=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('musashi',null);G.camx=0;G.lowq=true;
  const rows=[],bad=[],sheets=[];
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'].filter(h=>!heroFilter||h===heroFilter))for(const weapon of [null,'odachi','kusari']){
   const f=mk(hero,400,570,0);f.wpn=weapon?{k:weapon,uses:999}:null;G.player=f;G.fighters=[f];G.items=[];G.props=[];
   const drawn=[],native=ctx.drawImage.bind(ctx),legHashes=new Set(),frames=new Set();let atlas='';
   ctx.drawImage=function(im,...q){if(q.length===8){const key=Object.keys(SPR).find(k=>SPR[k].img===im);if(key&&key!=='items'){atlas=key;drawn.push({key,q});const fk=key+':'+q.slice(0,4).join(',');if(!frames.has(fk)){frames.add(fk);const sw=Math.max(1,Math.round(q[2])),sh=Math.max(1,Math.round(q[3])),top=Math.floor(sh*0.6),lh=sh-top,cc=document.createElement('canvas');cc.width=sw;cc.height=lh;const cx=cc.getContext('2d');cx.drawImage(im,q[0],q[1]+top,q[2],lh,0,0,sw,lh);const d=cx.getImageData(0,0,sw,lh).data;let hh=2166136261;for(let i=3;i<d.length;i+=4)hh=Math.imul(hh^(d[i]>128?1:0),16777619);legHashes.add(hh>>>0);}}}return native(im,...q);};
   const c=document.createElement('canvas');c.width=8*200;c.height=260;const x=c.getContext('2d');x.fillStyle='#35353a';x.fillRect(0,0,c.width,c.height);
   for(let t=0;t<48;t++){
    G.t++;updPlayer(f,{r:true});ctx.clearRect(0,0,1280,720);drawFighter(f);
    if(t%6===0){x.drawImage(cv,f.x-100,f.y-240,200,260,(t/6)*200,0,200,260);x.fillStyle='white';x.fillText(String(t),t/6*200+4,14);}
   }
   ctx.drawImage=native;
   // Pickup fallback to idle used to leave Musashi, Nobunaga and Shingen sliding.
   const S=SPR[atlas],idle=S?.a.idle||[],walk=S?.a.walk||[];
   if(JSON.stringify(walk)===JSON.stringify(idle)||walk.length<4||frames.size<4||legHashes.size<4)bad.push({hero,weapon,atlas,walkFrames:walk.length,distinct:frames.size,legs:legHashes.size,idleFallback:JSON.stringify(walk)===JSON.stringify(idle)});
   rows.push({hero,weapon,atlas,walkFrames:walk.length,distinct:frames.size,legs:legHashes.size});
   sheets.push({name:hero+'-'+(weapon||'default'),png:c.toDataURL().split(',')[1]});
  }
  return{rows,bad,sheets};
 },process.argv[3]||null);
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-walk');fs.mkdirSync(out,{recursive:true});for(const s of r.sheets)fs.writeFileSync(path.join(out,s.name+'.png'),Buffer.from(s.png,'base64'));delete r.sheets;fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify(r,null,2));console.log(JSON.stringify(r));await b.close();if(r.bad.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
