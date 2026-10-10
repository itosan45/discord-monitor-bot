const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'}),p=await(await b.newContext({viewport:{width:915,height:412},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);G.camx=0;G.partner=null;G.player.x=640;G.player.y=570;G.player.hp=G.player.maxhp=100000;const bad=[],report=[];
for(const key of ['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9']){
 const margin=bossScreenMargin(mk(key,640,570,1));let draws=0;
 for(const side of [-1,1]){G.fighters=[G.player];const e=spawnEn(key,side);e.hp=e.maxhp=100000;
  for(let t=0;t<1000;t++){updEnemy(e);if(!e.entered&&e.state==='atk')bad.push({key,side,t,attackedBeforeEntry:true});if(e.entered&&(e.x<margin-.01||e.x>1280-margin+.01))bad.push({key,side,t,x:e.x,margin});}
  if(!e.entered)bad.push({key,side,neverEntered:true});
 }
 // Every attack frame must fit at both arena limits, facing either way.
 for(const an of ['a1','big','dash'])for(const q of SPR[key].a[an])for(const face of [-1,1])for(const x of [margin,1280-margin]){
  const lo=Math.min(face*q[4],face*(q[4]+q[2]*(q[6]||1)))*TY[key].sc+x,hi=Math.max(face*q[4],face*(q[4]+q[2]*(q[6]||1)))*TY[key].sc+x;
  if(lo<8||hi>1272)bad.push({key,an,face,x,lo,hi});draws++;
 }
 report.push({key,margin,draws});
}return{bad,report};});console.log(JSON.stringify({r,errors}));await b.close();if(r.bad.length||errors.length)process.exitCode=1;})();
