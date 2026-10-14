const {chromium}=require('playwright');const fs=require('fs');
const OUT=process.argv[2]||'/tmp/claude-0/trailer/f';const PLAN=JSON.parse(process.argv[3]||'[]');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8000/index.html');await p.waitForFunction(()=>sprAllReady(),null,{timeout:180000});
await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;window.dropItem=window.dropItem;window.__rec=[];const f0=AU.sfx;});
let n=0,si=0;
for(const seg of PLAN){n=0;si++;
 await p.evaluate(s=>{G.noStory=true;if(s.k==='title'){startTitle();}else{G.autoPk=s.pk||G.autoPk;startAuto(s.hero,s.st);G.mode='play';G.story=null;G.banner=s.st===0||true?G.banner:null;}if(s.boss){G.waves=[{x:50,en:[],boss:s.boss}];G.wi=0;G.camMax=50;}window.__seg=s;},seg);
 // fast-forward (no render) until condition
 if(seg.ff){await p.evaluate(async(s)=>{const rw=renderWorld,hd=drawHUD,ov=drawOverlays;renderWorld=()=>{};drawHUD=()=>{};drawOverlays=()=>{};try{for(let i=0;i<s.ff;i++){frame();if(s.until==='boss'&&G.boss&&G.boss.entered)break;}}finally{renderWorld=rw;drawHUD=hd;drawOverlays=ov;}},seg);}
 const frames=seg.sec*30;
 for(let i=0;i<frames;i++){
  await p.evaluate(()=>{frame();frame();});
  const d=await p.evaluate(()=>cv.toDataURL('image/jpeg',0.93).slice(23));fs.writeFileSync(`${OUT}${si}_${String(n++).padStart(5,'0')}.jpg`,Buffer.from(d,'base64'));
 }
 console.log('seg done',JSON.stringify(seg),n);
}
console.log('errors',errs.slice(0,3));await b.close();})();
