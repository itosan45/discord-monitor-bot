// トレーラー撮影(v2): ゲームの自動プレイを1コマずつ撮影し、鳴らすはずだった効果音の時刻を記録して、あとで本物の音源(AU)でオフライン合成する。
// 使い方: node capture_trailer.js <出力フォルダ> '<区間のJSON>' (区間: {k:'play',hero,st,sec,ff,until,boss} / {k:'title',sec})
const {chromium}=require('playwright');const fs=require('fs');
const OUT=process.argv[2]||'/tmp/claude-0/trailer2/f';const PLAN=JSON.parse(process.argv[3]||'[]');
const HOOK=['sfx','sx','cut','clang','scream','kiai','bossLine','enemyLine','voice','userVoice','vplay','crowd','intro'];
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--autoplay-policy=no-user-gesture-required']});
const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8000/index.html');await p.waitForFunction(()=>sprAllReady(),null,{timeout:180000});
await p.evaluate(async(HOOK)=>{window.requestAnimationFrame=()=>0;window.__trailer=true;AU.muted=true;AU.init();
 for(let i=0;i<200&&!(AU.cutBuf&&AU.cutBuf.length&&AU.sxBuf&&AU.scBuf&&AU.scBuf.length&&AU.kiBuf&&AU.dvBuf&&AU.bvBuf);i++)await new Promise(r=>setTimeout(r,100));
 Object.defineProperty(AU,'on',{get(){return true;},configurable:true});
 window.__ev=[];window.__fc=0;window.__rec=false;let depth=0;
 const stub=o=>(o&&typeof o==='object'&&o.T)?{__f:1,T:{type:o.T.type,ai:o.T.ai,horse:o.T.horse,boss:o.T.boss},x:o.x,y:o.y,z:o.z,face:o.face}:o;
 for(const m of HOOK){const o=AU[m];if(typeof o!=='function')continue;AU[m]=function(...a){if(window.__rec&&depth===0)window.__ev.push({t:window.__fc/60,m,a:a.map(stub)});depth++;try{return o.apply(this,a);}finally{depth--;}};}
 const fr=frame;window.frame=function(){window.__fc++;return fr();};},HOOK);
const evAll=[];let n=0,si=0,tOff=0;
for(const seg of PLAN){n=0;si++;
 await p.evaluate(s=>{G.noStory=true;window.__rec=false;if(s.k==='title'){startTitle();}else{G.autoPk=s.pk||G.autoPk;startAuto(s.hero,s.st);G.mode='play';G.story=null;if(s.boss){G.waves=[{x:50,en:[],boss:s.boss}];G.wi=0;G.camMax=50;}}},seg);
 if(seg.ff){await p.evaluate(async(s)=>{const rw=renderWorld,hd=drawHUD,ov=drawOverlays;renderWorld=()=>{};drawHUD=()=>{};drawOverlays=()=>{};try{for(let i=0;i<s.ff;i++){frame();if(s.until==='boss'&&G.boss&&G.boss.entered)break;}}finally{renderWorld=rw;drawHUD=hd;drawOverlays=ov;}},seg);}
 await p.evaluate(()=>{window.__ev=[];window.__fc=0;window.__rec=true;});
 const frames=Math.round(seg.sec*30);
 for(let i=0;i<frames;i++){
  await p.evaluate(()=>{frame();frame();});
  const d=await p.evaluate(()=>cv.toDataURL('image/jpeg',0.93).slice(23));fs.writeFileSync(`${OUT}${si}_${String(n++).padStart(5,'0')}.jpg`,Buffer.from(d,'base64'));
 }
 const ev=await p.evaluate(()=>{window.__rec=false;return window.__ev;});
 for(const e of ev)evAll.push({t:e.t+tOff,m:e.m,a:e.a});
 tOff+=(seg.trim!==undefined?seg.trim:seg.sec);
 console.log('seg done',JSON.stringify(seg),n,'events',ev.length);
}
fs.writeFileSync(`${OUT}events.json`,JSON.stringify(evAll));
// オフライン合成: 本物の音源(AU)の関数を、記録した時刻に呼んで1本の音声にする
const wav=await p.evaluate(async(args)=>{const [evs,total]=args;const live=AU.ac,sr=live.sampleRate;const off=new OfflineAudioContext(2,Math.ceil(sr*total),sr);
 AU.ac=off;const comp=off.createDynamicsCompressor();comp.threshold.value=-12;comp.ratio.value=5;AU.mg=off.createGain();AU.mg.gain.value=0.75;AU.bg=off.createGain();AU.mg.connect(comp);AU.bg.connect(comp);comp.connect(off.destination);
 AU.lastSc=0;AU.lastCut=0;AU._sxl={};AU._evl={};AU.lastKi=0;AU.lastBuf=null;AU.lastPk=-1;AU.lastCutI=-1;
 const groups=new Map();for(const e of evs){const q=Math.round(e.t*sr/128)*128/sr;const k=Math.max(q,0.01);if(!groups.has(k))groups.set(k,[]);groups.get(k).push(e);}
 const times=[...groups.keys()].sort((a,b)=>a-b);
 const revive=o=>(o&&o.__f)?o:o;
 for(const t of times){off.suspend(t).then(()=>{for(const e of groups.get(t)){try{if(typeof AU[e.m]==='function')AU[e.m](...e.a.map(revive));}catch(err){}}off.resume();});}
 const buf=await off.startRendering();
 const L=buf.getChannelData(0),R=buf.getChannelData(1),N=L.length,out=new Int16Array(N*2);for(let i=0;i<N;i++){out[2*i]=Math.max(-1,Math.min(1,L[i]))*32767;out[2*i+1]=Math.max(-1,Math.min(1,R[i]))*32767;}
 let bin='';const u8=new Uint8Array(out.buffer);for(let i=0;i<u8.length;i+=32768)bin+=String.fromCharCode.apply(null,u8.subarray(i,i+32768));
 return {sr,b64:btoa(bin),peak:(()=>{let m=0;for(let i=0;i<L.length;i++){const v=Math.abs(L[i]);if(v>m)m=v;}return m;})()};},[evAll,tOff]);
fs.writeFileSync(`${OUT}sfx.pcm`,Buffer.from(wav.b64,'base64'));fs.writeFileSync(`${OUT}sfx.sr`,String(wav.sr));
console.log('events',evAll.length,'sr',wav.sr,'errors',errs.slice(0,3));await b.close();})();
