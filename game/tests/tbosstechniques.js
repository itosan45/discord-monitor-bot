// Exercise the actual attack definitions and movement, including the bow leap.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'}),p=await(await b.newContext({viewport:{width:915,height:412},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-boss-techniques');fs.mkdirSync(out,{recursive:true});
const result=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);G.camx=0;G.partner=null;G.banner=null;G.state='run';G.player.hp=G.player.maxhp=100000;const bad=[],reports=[],sheets=[];
for(const key of Object.keys(TY).filter(k=>TY[k].boss)){
 if(!SPR[key]||!SPR[key].ready){bad.push({key,missingSprite:true});continue;}
 const sheet=document.createElement('canvas');sheet.width=2048;sheet.height=TY[key].atk.length*256;const sx=sheet.getContext('2d');sx.fillStyle='#252530';sx.fillRect(0,0,sheet.width,sheet.height);let frames=0,minimumTop=720;
 for(let a=0;a<TY[key].atk.length;a++)for(const face of [-1,1])for(const y of [YMIN,570,YMAX]){
  G.props=[];G.proj=[];G.parts=[];G.items=[];G.fighters=[G.player];G.player.inv=99999;G.player.x=640-face*300;G.player.y=y;G.player.z=0;
  const e=mk(key,640,y,1);e.entered=true;e.face=face;e.inv=99999;e.hp=e.maxhp=100000;G.fighters.push(e);startEAtk(e,a);const d=e.cur;const expected={boss2:{3:'a1'},boss7:{1:'big'},boss9:{3:'big'}}[key]?.[a];if(expected&&sprPos(e,SPR[key]).arr!==SPR[key].a[expected])bad.push({key,a,wrongAnimation:true,expected});const sampleTimes=[1,Math.max(2,d.hs-1),d.hs,Math.floor((d.hs+d.he)/2),d.he,Math.min(d.dur-1,d.he+8),d.dur-2,d.dur-1];
  for(let t=1;t<d.dur;t++){updEnemy(e);const sp=sprPos(e,SPR[key]),q=sp.arr[Math.floor(sp.pos)];if(!q){bad.push({key,a,t,missing:true});continue;}frames++;
   const x0=e.x+Math.min(face*q[4],face*(q[4]+q[2]*(q[6]||1)))*e.sc,x1=e.x+Math.max(face*q[4],face*(q[4]+q[2]*(q[6]||1)))*e.sc,top=e.y-e.z+q[5]*e.sc,bottom=e.y-e.z+(q[5]+q[3]*(q[6]||1))*e.sc;minimumTop=Math.min(minimumTop,top);
   if(x0<8||x1>1272||top<8||bottom>712)bad.push({key,a,k:d.k||'normal',t,x0,x1,top,bottom,z:e.z,y:e.y});
   if(face===1&&y===570){const col=sampleTimes.indexOf(t);if(col>=0){ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,1280,720);ctx.save();ctx.translate(640-e.x,0);drawFighter(e);ctx.restore();sx.drawImage(cv,384,64,512,512,col*256,a*256,256,256);sx.fillStyle='#fff';sx.font='13px sans-serif';sx.fillText(`${a}:${d.k||'normal'} t${t} ${sp.arr._an}`,col*256+5,a*256+14);}}
  }
 }
 reports.push({key,techniques:TY[key].atk.length,frames,minimumTop});sheets.push({key,data:sheet.toDataURL('image/png').split(',')[1]});
}return{bad,reports,sheets};});
for(const s of result.sheets)fs.writeFileSync(path.join(out,s.key+'.png'),Buffer.from(s.data,'base64'));delete result.sheets;fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({result,errors},null,2));console.log(JSON.stringify({reports:result.reports,bad:result.bad.slice(0,12),badCount:result.bad.length,errors}));await b.close();if(result.bad.length||errors.length)process.exitCode=1;})();
