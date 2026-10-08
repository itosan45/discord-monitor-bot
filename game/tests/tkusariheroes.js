const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),p=await(await b.newContext({viewport:{width:915,height:412},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);G.lowq=true;G.camx=0;const rows=[],shots=[];
for(const h of ['yuki','kage','mitsu','nobu','shin','musashi']){const f=mk(h,350,570,0);f.t=0;f.inv=99999;f.wpn={k:'kusari',uses:99};G.player=f;G.partner=null;G.fighters=[f];G.parts=[];G.proj=[];G.props=[];G.items=[];G.t=0;
const near=mk('spear',440,570,1),far=mk('spear',740,570,1);for(const e of [near,far]){e.hp=e.maxhp=1000;e.cool=99999;e.entered=true;G.fighters.push(e);}
const snap=tag=>{ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,1280,720);drawFighter(f);shots.push({h,tag,png:cv.toDataURL().split(',')[1]});};
for(let t=0;t<40;t++){G.t++;updPlayer(f,{atkH:true,r:t>32});}const spin=f.kspin,moved=f.x>350,spinDamage=1000-near.hp;snap('spin-moving');
G.t++;updPlayer(f,{atkH:false});const throwStarted=!!f.cur?.kth;
for(let t=0;t<9;t++){G.t++;updPlayer(f,{atkH:false});}const thrownDamage=1000-far.hp,reach=f.cur?.reach;snap('throw');
for(let t=0;t<22;t++){G.t++;updPlayer(f,{atkH:false});}const pulled=Math.abs(far.x-f.x)<110;snap('pull');
rows.push({h,spin,moved,spinDamage,throwStarted,thrownDamage,reach,pulled});}
return{rows,shots};});const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-kusari');fs.mkdirSync(out,{recursive:true});for(const s of r.shots)fs.writeFileSync(path.join(out,s.h+'-'+s.tag+'.png'),Buffer.from(s.png,'base64'));delete r.shots;console.log(JSON.stringify({...r,errors}));fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({...r,errors},null,2));await b.close();if(errors.length||r.rows.some(q=>!q.spin||!q.moved||!q.spinDamage||!q.throwStarted||!q.thrownDamage||!q.pulled))process.exitCode=1;})();
