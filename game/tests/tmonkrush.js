// 2026-10-13 鉄球大僧のダッシュ(画面の端から端まで走る突進)。構え(赤い道筋・列合わせ→固定)→端まで走る→端で激突→隙。
// 左右どちらの端へも走る/同じ列の主人公に当たり打ち上げる/別の列・ジャンプ中は当たらない/全8コマが出る/AIが遠くから使い、連発しない。
// QA_OUTがあればAndroid相当(802×360)の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;const out={};
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){const rec=used.get(img);if(rec)rec.add(a[0]+','+a[1]);return od.call(this,img,...a);};
  const setup=()=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];const P=G.player;P.hp=P.maxhp=9999;P.inv=0;return P;};
  const mkMonk=(x,y,face)=>{x=Math.max(x,G.camx+232);x=Math.min(x,G.camx+W-232);const e=mk('monk',x,y,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=999;e.face=face;G.fighters.push(e);return e;};
  const draw=e=>{ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);};
  const d=TY.monk.atk[1];out.def={edge:d.edge,hs:d.hs,he:d.he,dur:d.dur,move:d.move};
  // run: 主人公(固定位置)へ向けて突進を最後まで進める。opts={py,pz,side}
  const run=(side,opts={})=>{const P=setup();const W2=W;const L=G.camx+200,R=G.camx+W2-200;
   const e=side>0?mkMonk(G.camx+150,570,1):mkMonk(G.camx+W2-150,570,-1);
   P.x=side>0?R:L;P.y=opts.py??570;P.face=-side;P.inv=0;
   const set=new Set();used.set(SPR.monk.img,set);startEAtk(e,1);
   const rec={x0:e.x,hits:0,launched:false,yLock:null,yEnd:null,crashX:null,crashSt:null,recov:0,states:new Set(),maxSpeed:0,warnSt:0,hpStart:P.hp,posHit:null};let lastX=e.x,lastHp=P.hp;
   for(let i=0;i<400;i++){G.t++;P.inv=0;if(opts.pz!==undefined)P.z=opts.pz;e.cool=999;updEnemy(e);updProj();draw(e);
    if(e.st===d.hs-14){rec.yLock=e.y;if(opts.sidestep)P.y=clamp(e.y+opts.sidestep,YMIN,YMAX);}
    if(e.st===d.hs)rec.yStart=e.y;
    rec.maxSpeed=Math.max(rec.maxSpeed,Math.abs(e.x-lastX));lastX=e.x;
    if(P.hp<lastHp){rec.hits++;rec.posHit=Math.round(e.x-rec.x0);lastHp=P.hp;}
    if(P.state==='down'||P.state==='hurt')rec.launched=true;
    if(e.rushDone&&rec.crashX===null){rec.crashX=e.x;rec.crashSt=e.st;}
    if(rec.crashX!==null&&e.state==='atk'){rec.recov++;if(Math.abs(e.x-rec.crashX)>0.01)rec.moved=true;}
    rec.states.add(e.state);
    if(e.state!=='atk'&&i>5)break;}
   rec.dist=Math.round(Math.abs((rec.crashX??e.x)-rec.x0));rec.frames=set.size;rec.marginL=Math.round(e.x-G.camx);rec.marginR=Math.round(G.camx+W2-e.x);rec.endState=e.state;rec.x1=Math.round(e.x-G.camx);
   // 隙: 激突の後でも攻撃は当たる
   rec.vuln=(()=>{const h0=e.hp;hurt(e,P,{dmg:10,kb:2});return e.hp<h0;})();
   used.delete(SPR.monk.img);rec.states=[...rec.states].join('>');return rec;};
  out.right=run(1);out.left=run(-1);
  out.otherLane=run(1,{sidestep:100});out.jump=run(1,{pz:110});
  // 構え中の列合わせ: 主人公が別の列でも、構えの間に近づいて列を合わせ、最後の14コマは固定
  {const P=setup();P.x=G.camx+1000;P.y=640;const e=mkMonk(G.camx+150,540,1);startEAtk(e,1);const ys=[];for(let i=0;i<d.hs;i++){G.t++;P.inv=0;e.cool=999;updEnemy(e);ys.push(e.y);}out.align={y0:540,yAt:Math.round(ys[d.hs-16]),yLockA:Math.round(ys[d.hs-14]),yLockB:Math.round(ys[d.hs-1]),py:640};}
  // AI: 遠くの主人公を見たら、乱数が当たれば突進を始め、480コマたつまで次の突進は出さず、過ぎれば再び出す
  {const P=setup();P.x=G.camx+1000;P.y=570;const e=mkMonk(G.camx+260,570,1);e.cool=0;const orr=Math.random;Math.random=()=>0.01;let first=-1,t0=null,early=false,late=-1;
   for(let i=0;i<900;i++){G.t++;P.inv=0;P.y=570;P.x=e.x<G.camx+640?G.camx+1000:G.camx+260;if(e.state!=='atk')e.cool=0;const was=e.state;updEnemy(e);
    if(e.state==='atk'&&was!=='atk'&&e.atkI===1){if(t0===null){t0=G.t;first=i;}else if(G.t-t0<480)early=true;else if(late<0)late=G.t-t0;}}
   Math.random=orr;out.ai={first,early,late,cd:t0!==null};}
  // ほかの突進(boss1等のk:'charge')は従来どおり固定距離(edgeでない)
  out.others=['boss1','boss2','boss7','boss9'].map(k=>{const dd=TY[k].atk.find(a=>a.k==='charge');return dd?[k,!!dd.edge,dd.move]:[k,null];});
  return out;});
 const bad=[];
 if(!r.def.edge||r.def.move<18)bad.push('def '+JSON.stringify(r.def));
 for(const k of['right','left']){const o=r[k];
  if(o.dist<800)bad.push(k+' 距離が短い '+o.dist);
  if(o.hits!==1||!o.launched)bad.push(k+' 命中 '+o.hits+' 打ち上げ '+o.launched);
  if(o.crashX===null||o.recov<35||o.moved)bad.push(k+' 激突/隙 '+JSON.stringify([o.crashX,o.recov,o.moved]));
  if(o.frames<8)bad.push(k+' コマ '+o.frames);
  if(o.maxSpeed<18||o.maxSpeed>26)bad.push(k+' 速さ '+o.maxSpeed);
  if(k==='right'&&o.marginR<40)bad.push('右の端を越えた '+o.marginR);
  if(k==='left'&&o.marginL<40)bad.push('左の端を越えた '+o.marginL);
  if(!o.vuln)bad.push(k+' 隙に攻撃が効かない');
  if(o.endState!=='idle')bad.push(k+' 終了 '+o.endState);}
 if(r.otherLane.hits!==0)bad.push('別の列に当たった '+r.otherLane.hits);
 if(r.jump.hits!==0)bad.push('ジャンプ中に当たった '+r.jump.hits);
 if(r.otherLane.dist<800||r.jump.dist<800)bad.push('当たらなくても端まで走る '+r.otherLane.dist+','+r.jump.dist);
 if(Math.abs(r.align.yLockA-r.align.yLockB)>0.01)bad.push('構えの最後に列が動く '+JSON.stringify(r.align));
 if(r.align.yLockA-r.align.y0<50)bad.push('列合わせしない '+JSON.stringify(r.align));
 if(!(r.ai.first>=0)||r.ai.early||!(r.ai.late>=480)||!r.ai.cd)bad.push('AI '+JSON.stringify(r.ai));
 if(r.others.some(([k,e])=>e))bad.push('他の突進がedge '+JSON.stringify(r.others));
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,st,pl] of [['rush_windup_early',16],['rush_windup_lock',40],['rush_run_a',58],['rush_run_b',66],['rush_crash',null]]){await p.evaluate(([st])=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];const P=G.player;P.x=G.camx+1050;P.y=570;P.face=-1;P.inv=999;P.hp=P.maxhp=9999;const e=mk('monk',G.camx+150,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=999;e.face=1;G.fighters.push(e);startEAtk(e,1);G.parts=[];G.proj=[];G.items=[];G.decals=[];G.flashT=0;G.hitstop=0;G.slow=0;G.shake=0;
   const lim=st===null?300:st;for(let i=0;i<lim;i++){G.t++;P.inv=999;e.cool=999;updEnemy(e);if(st===null&&e.rushDone&&e.st>TY.monk.atk[1].he+8)break;}
   G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},[st]);await p.screenshot({path:`${process.env.QA_OUT}/${name}.png`});}}
 console.log(JSON.stringify({bad,errors,summary:{right:r.right,left:r.left,otherLane:{hits:r.otherLane.hits,dist:r.otherLane.dist},jump:{hits:r.jump.hits,dist:r.jump.dist},align:r.align,ai:r.ai}}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
