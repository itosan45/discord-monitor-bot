// Seven-fighter reach plus a point-blank foe: pierce all, never stop at the first.
const {chromium}=require('playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:802,height:360},isMobile:true});const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);G.auto=false;G.demo=false;G.lowq=true;G.camx=0;const bad=[],rows=[],shots=[];
 for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const mounted of [false,true])for(const face of [-1,1])for(const edge of [false,true]){
  const f=mk(hero,edge?(face===1?1130:150):(face===1?180:1100),570,0);f.face=face;f.inv=999;f.wpn={k:'kusari',uses:99};if(mounted)f.mount={hp:6,max:6,col:'iron'};G.player=f;G.fighters=[f];G.parts=[];G.items=[];G.props=[];G.proj=[];G.state='run';
  for(let t=0;t<40;t++){G.t++;updPlayer(f,{atkH:true});}
  const enemies=[];if(!edge)for(const distance of [35,100,200,300,400,500,600,700,730]){const e=mk('sword',f.x+face*distance,570,1);e.entered=true;e.hp=e.maxhp=1000;G.fighters.push(e);enemies.push(e);}
  updPlayer(f,{atkH:false});if(!(f.cur?.reach>0))bad.push({hero,mounted,face,edge,missingReleaseReach:true});let tip=null;for(let t=0;t<7;t++){G.t++;updPlayer(f,{atkH:false});if(t<6&&enemies.some(e=>e.hp!==1000))bad.push({hero,mounted,face,earlyHit:t});}
  const reach=f.cur?.reach;const expected=edge?Math.min(700,face===1?W-48-f.x:f.x-48):700;
  if(Math.abs(reach-expected)>1)bad.push({hero,mounted,face,edge,reach,expected});
  ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,1280,720);const arc=ctx.arc.bind(ctx);ctx.arc=function(x,y,r,...rest){if(r===7){const m=ctx.getTransform();tip={x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f};}return arc(x,y,r,...rest);};drawFighter(f);ctx.arc=arc;
  if(!tip||Math.abs(tip.x-(f.x+face*expected))>40||Math.abs(tip.y-(f.y-(mounted?70:90)))>35||tip.x<0||tip.x>W||tip.y<0||tip.y>H)bad.push({hero,mounted,face,edge,tip,expectedX:f.x+face*expected,expectedY:f.y-(mounted?70:90)});
  if(!edge){if(enemies.slice(0,8).some(e=>e.hp>=1000)||enemies[8].hp!==1000)bad.push({hero,mounted,face,hp:enemies.map(e=>e.hp)});if(f.wpn.uses!==98)bad.push({hero,mounted,face,uses:f.wpn.uses});}
  if(!edge&&hero==='musashi'&&face===1){renderWorld();drawHUD();shots.push({mounted,png:cv.toDataURL().split(',')[1]});}
  rows.push({hero,mounted,face,edge,reach,tip});
 }return{bad,rows,shots};});
 const out=process.env.OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006/qa/kusari-seven-fighters';fs.mkdirSync(out,{recursive:true});for(const s of r.shots)fs.writeFileSync(out+'/'+(s.mounted?'mounted':'foot')+'.png',Buffer.from(s.png,'base64'));delete r.shots;fs.writeFileSync(out+'/tests.json',JSON.stringify({r,errors},null,2));console.log(JSON.stringify({cases:r.rows.length,nearPierceCases:r.rows.filter(q=>!q.edge).length,bad:r.bad.slice(0,12),errors}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
