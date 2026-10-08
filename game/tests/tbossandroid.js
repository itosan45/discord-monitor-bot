// Render every boss attack frame through the production renderer at Android sizes.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-boss-android');fs.mkdirSync(out,{recursive:true});
 const errors=[],reports=[];
 for(const viewport of [{width:915,height:412},{width:412,height:915}]){
  const context=await browser.newContext({viewport,isMobile:true,hasTouch:true}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');
  await page.waitForFunction(()=>['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9'].every(k=>SPR[k]?.ready));
  const result=await page.evaluate(()=>{
   window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('kage',null);G.camx=0;G.lowq=false;G.banner=null;G.state='run';
   const bad=[],sheets=[],counts={};let samples=0;
   for(const key of ['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9']){
    const S=SPR[key],sheet=document.createElement('canvas');sheet.width=2048;sheet.height=768;const sx=sheet.getContext('2d');sx.fillStyle='#252530';sx.fillRect(0,0,2048,768);counts[key]={};
    for(const [row,an] of ['a1','big','dash'].entries()){
     const arr=S.a[an];if(!arr?.length){bad.push({key,an,missing:true});continue;}counts[key][an]=arr.length;
     for(let i=0;i<arr.length;i++)for(const face of [-1,1]){
      const q=arr[i];if(q[0]<0||q[1]<0||q[0]+q[2]>S.img.naturalWidth||q[1]+q[3]>S.img.naturalHeight)bad.push({key,an,i,atlasBounds:true});
      const f=mk(key,640,620,1);Object.assign(f,{face,state:'atk',st:(i+.1)*4,cur:{dur:arr.length*4,hs:4,he:arr.length*4-4,k:an==='dash'?'charge':an==='big'?'heavy':undefined},flash:0,inv:0,gh:[]});
      const sp=sprPos(f,S);if(sp.arr!==arr||Math.floor(sp.pos)!==i)bad.push({key,an,i,mapped:Math.floor(sp.pos)});
      ctx.clearRect(0,0,1280,720);if(!drawSprite(f))bad.push({key,an,i,renderer:false});
      const d=ctx.getImageData(0,0,1280,720).data;let n=0,x0=1280,y0=720,x1=0,y1=0;
      for(let y=0;y<720;y++)for(let x=0;x<1280;x++)if(d[(y*1280+x)*4+3]>40){n++;x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
      if(n<1000||x0<8||y0<8||x1>1271||y1>711)bad.push({key,an,i,face,n,x0,y0,x1,y1});samples++;
      if(face===1){sx.drawImage(ctx.canvas,384,164,512,512,i*256,row*256,256,256);sx.fillStyle='#fff';sx.font='14px sans-serif';sx.fillText(`${an} ${i+1}`,i*256+8,row*256+18);}
     }
    }
    sheets.push({key,data:sheet.toDataURL('image/png').split(',')[1]});
   }
   const rect=ctx.canvas.getBoundingClientRect();if(rect.x<-.5||rect.y<-.5||rect.right>innerWidth+.5||rect.bottom>innerHeight+.5)bad.push({viewportClip:true});
   // Show an actual gameplay frame with the largest polearm boss.
   G.fighters=[G.player,mk('boss7',850,610,1)];G.player.x=390;G.player.y=610;const boss=G.fighters[1];startEAtk(boss,1);boss.st=Math.floor(boss.cur.dur*.45);boss.face=-1;frame();
   return {bad,samples,counts,sheets,viewport:{width:innerWidth,height:innerHeight},canvas:{x:rect.x,y:rect.y,width:rect.width,height:rect.height}};
  });
  for(const s of result.sheets)fs.writeFileSync(path.join(out,`${viewport.width}x${viewport.height}-${s.key}.png`),Buffer.from(s.data,'base64'));delete result.sheets;
  await page.screenshot({path:path.join(out,`game-${viewport.width}x${viewport.height}.png`)});reports.push(result);await context.close();
 }
 await browser.close();fs.writeFileSync(path.join(out,'boss-android-qa.json'),JSON.stringify({reports,errors},null,2));console.log(JSON.stringify({reports,errors}));if(errors.length||reports.some(r=>r.bad.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
