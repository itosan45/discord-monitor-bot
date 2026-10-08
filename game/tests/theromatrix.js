// Six heroes x every pickup weapon x foot/mounted actions, with actual updates.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await browser.newContext({viewport:{width:915,height:412},isMobile:true,hasTouch:true})).newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const result=await p.evaluate(()=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);G.camx=0;G.partner=null;G.state='run';G.lowq=true;
  const bad=[],reports=[],sheets=[],weapons=[null,...Object.keys(WPN)],heroes=['yuki','kage','mitsu','nobu','shin','musashi'];
  const native=ctx.drawImage.bind(ctx);let drawn=[],sourceBad=[],calls=[];
  ctx.drawImage=function(im,...q){if(q.length===8){if(q[0]<0||q[1]<0||q[2]<=0||q[3]<=0||q[0]+q[2]>im.width+0.1||q[1]+q[3]>im.height+0.1)sourceBad.push(q.slice(0,4));const s=Object.keys(SPR).find(k=>SPR[k].img===im);if(s){drawn.push(s);calls.push({s,y:q[1]});}}return native(im,...q);};
  for(const hero of heroes){let cases=0,frames=0,samples=0;const modes=[...TY[hero].atk.map((_,i)=>'a'+(i+1)),'dash','jump','charge','spc','mountatk','mountspc'];
   const sheet=document.createElement('canvas');sheet.width=modes.length*160;sheet.height=weapons.length*200;const sc=sheet.getContext('2d');sc.fillStyle='#252530';sc.fillRect(0,0,sheet.width,sheet.height);
   for(let wi=0;wi<weapons.length;wi++)for(let mi=0;mi<modes.length;mi++)for(const face of [-1,1])for(const y of [YMIN,570,YMAX]){
    const weapon=weapons[wi],mode=modes[mi],f=mk(hero,640,y,0);f.face=face;f.t=0;f.ki=1000;f.hp=100000;f.inv=99999;f.wpn=weapon?{k:weapon,uses:999}:null;G.player=f;G.fighters=[f];G.parts=[];G.proj=[];G.trs=[];G.items=[];G.props=[];G.t=0;
    if(mode.startsWith('mount')){f.mount={hp:6,max:6,col:MCOL[hero]};updPlayer(f,mode==='mountatk'?{atkP:true}:{spcP:true});}
    else if(mode==='jump'){updPlayer(f,{jumpP:true});for(let j=0;j<7;j++){G.t++;updPlayer(f,{});}G.t++;updPlayer(f,{atkP:true});if(f.state!=='jatk')bad.push({hero,weapon,mode,wrongState:f.state});}
    else if(mode==='charge')startCharge(f);
    else if(mode==='spc'){f.ki=100;startSpecial(f);}
    else if(mode==='dash'){f.state='atk';f.cur=atkDef(f,f.T.dash,false);f.st=0;}
    else startPAtk(f,Number(mode.slice(1))-1);
    const dur=mode==='jump'?55:mode==='spc'?(SPD[hero]?.dur||60):mode==='mountspc'?40:f.cur?.dur||24;
    for(let t=0;t<dur;t++){
     if(t){G.t++;updPlayer(f,{});}frames++;
     if(t%4&&t!==dur-1)continue;
     ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,1280,720);drawn=[];sourceBad=[];calls=[];drawFighter(f);samples++;
     if(sourceBad.length)bad.push({hero,weapon,mode,t,sourceBad});
     if(mode==='mountatk'&&f.state==='matk'){const key='mountatk2_'+hero,seq=SPR[key]?.a[weapon||'default'];if(!seq||!calls.some(q=>q.s===key&&q.y===seq[0][1]))bad.push({hero,weapon,mode,t,wrongMountedSheet:drawn});}
     if(mode==='jump'&&f.state==='jatk'&&weapon&&!drawn.includes(hero+'_u'))bad.push({hero,weapon,mode,t,wrongJumpWeaponSheet:drawn});
     if(weapon&&weapon!=='kusari'&&(mode.startsWith('a')||mode==='dash'||mode==='charge')&&f.state==='atk'&&!drawn.includes(hero+'_u'))bad.push({hero,weapon,mode,t,wrongPickupBody:drawn});
     const top=ctx.getImageData(0,0,1280,1).data,bottom=ctx.getImageData(0,719,1280,1).data,left=ctx.getImageData(0,0,1,720).data,right=ctx.getImageData(1279,0,1,720).data;
     const ink=a=>{for(let i=3;i<a.length;i+=4)if(a[i]>8)return true;return false;};
     if(ink(top)||ink(bottom)||ink(left)||ink(right))bad.push({hero,weapon,mode,t,x:f.x,y:f.y,z:f.z,edge:{top:ink(top),bottom:ink(bottom),left:ink(left),right:ink(right)}});
     if(face===1&&y===570&&t===Math.floor(dur/8)*4){const pix=ctx.getImageData(0,0,1280,720).data;let x0=1280,y0=720,x1=0,y1=0;for(let yy=0;yy<720;yy+=2)for(let xx=0;xx<1280;xx+=2)if(pix[(yy*1280+xx)*4+3]>8){x0=Math.min(x0,xx);x1=Math.max(x1,xx);y0=Math.min(y0,yy);y1=Math.max(y1,yy);}const bw=x1-x0+12,bh=y1-y0+12,k=Math.min(152/bw,164/bh);sc.drawImage(cv,x0-6,y0-6,bw,bh,mi*160+(160-bw*k)/2,wi*200+22+(164-bh*k)/2,bw*k,bh*k);sc.fillStyle='#fff';sc.font='10px sans-serif';sc.fillText(`${weapon||'default'} ${mode}`,mi*160+3,wi*200+12);}
    }cases++;
   }reports.push({hero,cases,frames,samples});sheets.push({hero,data:sheet.toDataURL('image/png').split(',')[1]});
  }return{bad,reports,sheets};
 });
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-hero-matrix');fs.mkdirSync(out,{recursive:true});for(const s of result.sheets)fs.writeFileSync(path.join(out,s.hero+'.png'),Buffer.from(s.data,'base64'));delete result.sheets;
 fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({result,errors},null,2));console.log(JSON.stringify({reports:result.reports,bad:result.bad.slice(0,15),badCount:result.bad.length,errors}));await browser.close();if(result.bad.length||errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
