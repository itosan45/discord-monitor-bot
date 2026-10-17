// 伊達政宗の奥義「独眼竜・四天十字」(2026-10-17)の検査。敵がいる場面で:
// 4回の斬り抜けで各敵が1回ずつ(計4回)削られ、納刀の瞬間にまとめて倒れ、222コマで終わる。ボスにも当たる。
// 白い画素の割合が常に小さい(画面が白く止まらない)。左右両向き。描画エラー・有限でない粒の警告なし。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:915,height:412}});const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='warning'&&/PT |drawParts/.test(m.text()))errors.push(m.text().slice(0,160));});
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForTimeout(1500);
 await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;startAuto('masamune',2);if(G.mode==='story')endStory();G.waveOn=false;G.camMax=1e9;G.auto=false;});
 await p.waitForFunction(()=>{frame();return sprAllReady();},null,{timeout:120000,polling:300});
 const out=[];
 for(const side of [1,-1]){
  out.push(await p.evaluate((side)=>{G.mode='play';G.state='run';G.banner=null;G.fighters=G.fighters.filter(f=>f===G.player);G.partner=null;G.proj=[];const P=G.player;P.x=G.camx+640;P.y=570;P.face=side;P.inv=0;P.hp=P.maxhp;P.ki=300;
   const en=[];['spear','spear','boss3','spear','spear','spear'].forEach((kd,i)=>{const e=mk(kd,G.camx+140+i*180,500+(i%3)*50,1);e.entered=true;e.face=-side;e.cool=9999;e.wakeInv=0;e.hp=e.maxhp=kd==='boss3'?4000:260;G.fighters.push(e);en.push(e);});
   const hp0=en.map(e=>e.hp);startSpecial(P);let wmax=0,ended=-1,downAt=-1;const c=document.querySelector('canvas'),x=c.getContext('2d');
   for(let k=0;k<300;k++){frame();if(downAt<0&&en.some(e=>e.state==='down'))downAt=G.ult?G.ult.t:k;if(k%6===0){const im=x.getImageData(0,0,c.width,c.height).data;let w=0;for(let i=0;i<im.length;i+=32)if(im[i]>235&&im[i+1]>235&&im[i+2]>235)w++;wmax=Math.max(wmax,w/(im.length/32));}if(ended<0&&!G.ult&&P.state!=='ult'){ended=k;break;}}
   return {side,dmg:en.map((e,i)=>Math.round(hp0[i]-e.hp)),down:en.filter(e=>e.state==='down'||e.dying).length,downAt,ended,wmax:+wmax.toFixed(4)};},side));}
 const bad=[];for(const r of out){if(r.dmg.some(d=>d<40))bad.push('too little damage '+r.dmg);if(r.down<4)bad.push('blast did not knock down '+r.down);if(r.downAt<190)bad.push('knocked down too early '+r.downAt);if(r.ended<200||r.ended>260)bad.push('ult length '+r.ended);if(r.wmax>0.15)bad.push('white screen '+r.wmax);}
 console.log(JSON.stringify({out,bad,errors}));if(bad.length||errors.length)process.exitCode=1;
}finally{await b.close();}})();
