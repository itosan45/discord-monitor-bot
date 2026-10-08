// 馬上の全員×全武器系統で5コマを読み込み、打点フレームまで連続描画できることを確認する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');
 const r=await p.evaluate(async()=>{for(let n=0;n<160;n++){const ready=['yuki','kage','mitsu','nobu','shin','musashi'].every(h=>SPR['mountatk2_'+h]?.ready);if(ready)break;await new Promise(r=>setTimeout(r,50));}
  window.requestAnimationFrame=()=>0;G.noStory=true;G.lowq=true;G.camx=0;const heroes=['yuki','kage','mitsu','nobu','shin','musashi'],profiles=['default','odachi','naginata','teppo','yoto','ono','konbou','takeyari','kusari','yumi'],weapons=Object.fromEntries(profiles.filter(k=>k!=='default').map(k=>[k,k])),rows=[];
  for(const h of heroes){const S=SPR['mountfull3_'+h]||SPR['mountatk2_'+h];if(!S?.ready)return{rows:[...rows,{error:h+':atlas-not-ready'}]};for(const kind of profiles){const seq=S.a[kind];if(!seq||seq.length!==5)return{rows:[...rows,{error:h+':'+kind+'-frames'}]};
    const f=mk(h,640,400,0);f.mount={hp:6,max:6,col:({yuki:'red',kage:'blue',mitsu:'purple',nobu:'red',shin:'red',musashi:'iron'})[h]};f.face=1;f.sc=1;f.state='matk';f.cur=MATK;f.mountedDefault=kind==='default';f.wpn=weapons[kind]?{k:weapons[kind],uses:30}:null;f.hit=new Set();const hashes=[];
    for(const st of [0,6,10,16,22]){f.st=st;ctx.clearRect(0,0,1280,720);const drawn=drawRiderPlayer(f);if(!drawn)return{rows:[...rows,{error:h+':'+kind+'-draw'}]};const d=ctx.getImageData(320,0,640,450).data;let hash=2166136261,ink=0;for(let i=0;i<d.length;i+=8){hash=Math.imul(hash^d[i],16777619);if(d[i+3])ink++;}hashes.push({hash:hash>>>0,ink});}
    if(new Set(hashes.map(q=>q.hash)).size<3)return{rows:[...rows,{error:h+':'+kind+'-static-frames'}]};rows.push({hero:h,profile:kind,frames:seq.length,rendered:hashes.length,distinct:new Set(hashes.map(q=>q.hash)).size,minInk:Math.min(...hashes.map(q=>q.ink))});
   }}return{rows};});
 console.log(JSON.stringify({assets:r.rows.length,errors,pageErrors:errors,failures:r.rows.filter(x=>x.error)}));await b.close();if(errors.length||r.rows.length!==60||r.rows.some(x=>x.error||x.frames!==5||x.rendered!==5||x.minInk<100))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
