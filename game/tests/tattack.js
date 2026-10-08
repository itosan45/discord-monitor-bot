const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch();
 const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
 const out=await p.evaluate(()=>{
  G.camx=0;G.lowq=true;G.demo=false;G.state='run';
  const heroes=['yuki','kage','mitsu','nobu','shin','musashi','nezu'];
  const bosses=['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9'];
  const cw=220,ch=230,cols=8,canvas=document.createElement('canvas'),c=canvas.getContext('2d');
  const rows=[],bad=[],counts={};
  const actors=heroes.concat(bosses);
  for(const type of actors){
   const boss=!!TY[type].boss,f=mk(type,640,590,boss?1:0),S=SPR[TY[type].spr||type];
   if(!S||!S.ready){bad.push(`${type}:atlas-not-ready`);continue;}
   const groups=[];
   if(boss){
    for(const d of TY[type].atk){if(d.k==='guard')continue;const name=d.k==='charge'?'dash':d.k?'big':'a1';if(!groups.some(g=>g.name===name))groups.push({name,d});}
   }else{
    TY[type].atk.forEach((d,i)=>groups.push({name:'a'+(i+1),d}));
    if(TY[type].dash&&S.a.dash)groups.push({name:'dash',d:TY[type].dash});
    if(S.a.spc)groups.push({name:'spc',d:TY[type].atk[0],state:'spc'});
   }
   counts[type]={};
   for(const g of groups){
    const arr=S.a[g.name];if(!Array.isArray(arr)||!arr.length){bad.push(`${type}:${g.name}-missing`);continue;}
    const seen=new Map(),limit=Math.max(1,g.state==='spc'?(SPD[type]&&SPD[type].dur||60):(g.d.dur||28));
    for(let st=0;st<limit;st++){
     f.state=g.state||'atk';f.cur=g.d;f.st=st;f.t=st;f.face=1;f.x=640;f.y=590;f.z=0;f.flash=0;f.inv=0;f.wpn=null;
     const q=sprPos(f,S),ix=Math.floor(q.pos+1e-6);
     if(q.arr!==arr)continue;
     if(!seen.has(ix)){ctx.clearRect(0,0,1280,720);const drawn=drawSprite(f);if(!drawn){bad.push(`${type}:${g.name}:${ix}-not-drawn`);continue;}
      const pix=ctx.getImageData(0,0,1280,720).data;let x0=1280,y0=720,x1=-1,y1=-1;
      for(let y=0;y<720;y++)for(let x=0;x<1280;x++){if(pix[(y*1280+x)*4+3]>0){x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}}
      if(x0<8||y0<8||x1>1271||y1>711)bad.push(`${type}:${g.name}:${ix}-canvas-edge`);
      const cell=document.createElement('canvas');cell.width=cw;cell.height=ch;const cc=cell.getContext('2d');cc.fillStyle='#666';cc.fillRect(0,0,cw,ch);cc.drawImage(ctx.canvas,460,340,360,240,0,0,cw,ch);
      seen.set(ix,cell);
     }
    }
    counts[type][g.name]=seen.size;
    if(seen.size!==arr.length)bad.push(`${type}:${g.name}-only-${seen.size}-of-${arr.length}-frames`);
    for(let i=0;i<arr.length;i++)if(seen.has(i))rows.push({label:`${type} ${g.name} ${i+1}/${arr.length}`,cell:seen.get(i)});
   }
  }
  const makeSheet=(group)=>{
   const list=rows.filter(x=>group==='heroes'?heroes.some(h=>x.label.startsWith(h+' ')):bosses.some(h=>x.label.startsWith(h+' ')));
   const cv=document.createElement('canvas');cv.width=cols*cw;cv.height=Math.max(1,Math.ceil(list.length/cols))*ch;const x=cv.getContext('2d');
   list.forEach((r,i)=>{const xx=(i%cols)*cw,yy=Math.floor(i/cols)*ch;x.drawImage(r.cell,xx,yy);x.fillStyle='white';x.font='12px sans-serif';x.fillText(r.label,xx+4,yy+14);});
   return cv.toDataURL();
  };
  return {bad,counts,heroes:makeSheet('heroes').replace('data:image/png;base64,',''),bosses:makeSheet('bosses').replace('data:image/png;base64,',''),heroRows:rows.filter(x=>heroes.some(h=>x.label.startsWith(h+' '))).length,bossRows:rows.filter(x=>bosses.some(h=>x.label.startsWith(h+' '))).length};
 });
 const dir=process.env.OUT||process.cwd();fs.mkdirSync(dir,{recursive:true});
 fs.writeFileSync(path.join(dir,'attack_frames_heroes.png'),Buffer.from(out.heroes,'base64'));
 fs.writeFileSync(path.join(dir,'attack_frames_bosses.png'),Buffer.from(out.bosses,'base64'));
 console.log(JSON.stringify({bad:out.bad,counts:out.counts,heroFrameTiles:out.heroRows,bossFrameTiles:out.bossRows,pageErrors:errors}));
 if(out.bad.length||errors.length)process.exitCode=1;
 await b.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
