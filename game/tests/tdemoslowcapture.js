// Demo AI chooses and performs the attack. Only the encounter setup is forced.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),p=await(await b.newContext({viewport:{width:915,height:412},isMobile:true,hasTouch:true})).newPage(),errors=[];
 p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;});
 const out=process.env.OUT||path.join(require('os').tmpdir(),'sekigahara-demo-slow-capture');fs.mkdirSync(out,{recursive:true});const rows=[];
 for(const key of ['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9']){
  const r=await p.evaluate(key=>{
   startDemo(0);G.lowq=true;G.titleT=-9999;G.camx=G.camMax=0;G.banner=null;G.vo=null;G.waveOn=true;G.sq=[];G.props=[];G.items=[];G.proj=[];
   const boss=mk(key,850,570,1);boss.entered=true;boss.inv=0;boss.hp=boss.maxhp=99999;boss.face=-1;boss.cool=1;G.player.x=510;G.player.y=570;G.player.inv=99999;G.fighters=[G.player,boss];G.boss=boss;
   G.autoSpd=0.25;demoView.paused=false;demoView.steps=0;demoView.credit=0;acc=0;last=0;
   let captured=false,ticks=0;
   for(ticks=1;ticks<=4800;ticks++){
    loop(ticks*1000/60+0.00001);
    if(boss.state==='atk'&&boss.cur&&!['guard','step'].includes(boss.cur.k)&&boss.st>=boss.cur.hs&&boss.st<=boss.cur.he){captured=true;break;}
   }
   demoView.paused=true;autoUI(true);
   return {key,captured,ticks,state:boss.state,st:boss.st,technique:boss.cur?.k||'normal',animation:boss.cur?.anim||sprPos(boss,SPR[key]).arr._an};
  },key);
  await p.screenshot({path:path.join(out,key+'-attack.png')});rows.push(r);
 }
 const frameErrors=await p.evaluate(()=>window.__err||[]);await b.close();fs.writeFileSync(path.join(out,'qa.json'),JSON.stringify({rows,errors,frameErrors},null,2));console.log(JSON.stringify({rows,errors,frameErrors}));if(rows.some(r=>!r.captured)||errors.length||frameErrors.length)process.exitCode=1;
})();
