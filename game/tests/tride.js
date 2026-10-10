const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
 const out=await p.evaluate(()=>{
  G.lowq=true;G.camx=0;G.state='run';
  const heroes=['yuki','kage','mitsu','nobu','shin','musashi'],weapons=['odachi','takeyari','naginata','ono','yumi','kusari'];
  const cols=8,cw=320,ch=205,labels=[],hashes={},bad=[];
  const sheet=document.createElement('canvas');sheet.width=cols*cw;sheet.height=heroes.length*ch;const sc=sheet.getContext('2d');
  const hashPixels=(d)=>{let h=2166136261;for(let i=0;i<d.length;i++){h^=d[i];h=Math.imul(h,16777619);}return(h>>>0).toString(16);};
  const edgeHasInk=(d)=>{for(let i=3;i<d.length;i+=4)if(d[i])return true;return false;};
  heroes.forEach((type,row)=>{
   const f=mk(type,640,590,0);f.mount={hp:6,max:6,col:MCOL[type]||'red'};f.face=1;f.t=50;f.st=0;f.z=0;f.flash=0;f.inv=0;
   const states=[['待機','idle',null],['走行','walk',null],['攻撃・素手相当','matk',null],...weapons.map(k=>[WPN[k]?.n||k,'matk',k])];
   hashes[type]=[];
   states.forEach(([label,state,weapon],col)=>{
    f.state=state;f.st=12;f.cur=state==='matk'?MATK:null;f.wpn=weapon?{k:weapon,uses:10}:null;f.t=50;
    ctx.clearRect(0,0,1280,720);const ok=drawRiderPlayer(f);if(!ok)bad.push(`${type}:${label}:not-drawn`);
    const edge=[ctx.getImageData(0,0,1280,1).data,ctx.getImageData(0,719,1280,1).data,ctx.getImageData(0,0,1,720).data,ctx.getImageData(1279,0,1,720).data];
    if(edge.some(edgeHasInk))bad.push(`${type}:${label}:canvas-edge`);
    const pix=ctx.getImageData(384,325,512,328).data;const imageHash=hashPixels(pix);hashes[type].push({label,hash:imageHash});
    const cell=document.createElement('canvas');cell.width=cw;cell.height=ch;const cc=cell.getContext('2d');cc.fillStyle='#666';cc.fillRect(0,0,cw,ch);cc.drawImage(ctx.canvas,384,325,512,328,0,0,cw,ch);
    const x=col*cw,y=row*ch;sc.drawImage(cell,x,y);sc.fillStyle='white';sc.font='13px sans-serif';sc.fillText(`${TY[type].name} / ${label}`,x+5,y+15);
   });
  });
  return {bad,hashes,image:sheet.toDataURL().replace('data:image/png;base64,','')};
 });
 const dir=process.env.OUT||process.cwd();fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(path.join(dir,'mounted_hero_weapon_audit.png'),Buffer.from(out.image,'base64'));
 const variants={};for(const [hero,items] of Object.entries(out.hashes)){const base=items.find(x=>x.label==='攻撃・素手相当')?.hash;variants[hero]={attackVariants:items.filter(x=>x.label!=='待機'&&x.label!=='走行').length,uniqueRenderedImages:new Set(items.filter(x=>x.label!=='待機'&&x.label!=='走行').map(x=>x.hash)).size,heldWeaponMatchesBase:items.filter(x=>!['攻撃・素手相当','待機','走行'].includes(x.label)).every(x=>x.hash===base)};}
 console.log(JSON.stringify({bad:out.bad,variants,pageErrors:errors}));if(out.bad.length||errors.length||Object.values(variants).some(v=>v.uniqueRenderedImages<2||v.heldWeaponMatchesBase))process.exitCode=1;await b.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
