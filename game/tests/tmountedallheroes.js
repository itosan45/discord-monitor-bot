// Every playable hero must use the whole rider, with dedicated walking and attack poses.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startAuto('yuki',0);G.camx=0;G.lowq=true;const bad=[],cases=[],shots=[];const native=ctx.drawImage.bind(ctx);let keys=[],coords=[];ctx.drawImage=function(im,...q){const k=Object.keys(SPR).find(k=>SPR[k].img===im);if(k){keys.push(k);coords.push([k,q[0]]);}return native(im,...q);};
for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const weapon of [null,...Object.keys(WPN)])for(const face of [1,-1])for(const y of [YMIN,570,YMAX])for(const low of [true,false]){
const f=mk(hero,640,y,0);f.mount={hp:6,max:6,col:'iron'};f.wpn=weapon?{k:weapon,uses:999}:null;f.face=face;G.player=f;G.fighters=[f];G.items=[];G.parts=[];G.props=[];G.proj=[];G.lowq=low;const walk=new Set(),attack=new Set();
for(const mode of ['idle','walk','attack','special']){f.x=640;f.state='idle';f.st=0;f.cur=null;f.ki=300;if(mode==='attack')updPlayer(f,{atkP:true});if(mode==='special')updPlayer(f,{spcP:true});
const N=mode==='walk'?64:mode==='special'?40:24;for(let t=0;t<N;t++){
keys=[];coords=[];ctx.clearRect(0,0,1280,720);drawFighter(f);
const expected=f.state==='walk'?'mountwalk4_'+hero:(f.state==='matk'||f.state==='mspc')&&hero==='musashi'?'mountfull3_musashi':'mountbody3_'+hero;
if(!keys.includes(expected)||keys.includes(hero)||keys.includes(hero+'_u'))bad.push({hero,weapon,mode,t,keys,expected});
for(const [k,c] of coords){if(k==='mountwalk4_'+hero)walk.add(c);if(k==='mountbody3_'+hero||k==='mountfull3_'+hero)attack.add(c);}
if(!weapon&&face===1&&y===570&&low&&t===12&&mode!=='special'){renderWorld();shots.push({name:hero+'-'+mode,png:cv.toDataURL().split(',')[1]});}
updPlayer(f,mode==='walk'?(face===1?{r:true}:{l:true}):{});G.t++;
}}
if(walk.size!==8)bad.push({hero,weapon,walk:walk.size});if(attack.size<4)bad.push({hero,weapon,attack:attack.size});cases.push({hero,weapon,face,y,low});}
ctx.drawImage=native;return{cases:cases.length,bad:bad.slice(0,30),shots};});const out=process.env.OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006/qa/mounted-all-v4/runtime';fs.mkdirSync(out,{recursive:true});for(const s of r.shots)fs.writeFileSync(path.join(out,s.name+'.png'),Buffer.from(s.png,'base64'));delete r.shots;fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({r,errors},null,2));console.log(JSON.stringify({r,errors}));if(r.bad.length||errors.length)process.exitCode=1;
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
