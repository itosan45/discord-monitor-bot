// 2026-10-11 納品: 敵の新しい動き(刀足軽の受け流し反撃・槍足軽の横薙ぎ・鉄砲足軽の装填)と戦場の仕掛け(竹柵・置き盾・焚火)。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){const rec=used.get(img);if(rec){rec.add(a[0]+','+a[1]);if(a.length>=8){const m=this.getTransform(),x=m.a*a[4]+m.e,w=m.a*a[6];rec.minX=Math.min(rec.minX??1e9,x,x+w);rec.maxX=Math.max(rec.maxX??-1e9,x,x+w);}}return od.call(this,img,...a);};
  const setup=()=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];const P=G.player;P.x=G.camx+560;P.y=570;P.face=-1;P.inv=0;P.hp=P.maxhp=9999;return P;};
  const enemy=(ty,P,dx)=>{const e=mk(ty,P.x+dx,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=0;e.face=dx>0?-1:1;G.fighters.push(e);return e;};
  const X=SPR.enemyx1;
  // 1. 受け流し反撃
  {const P=setup();P.face=1;const e=enemy('sword',P,90);P.x=e.x-90;e.face=-1;P.face=1;const set=new Set();used.set(X.img,set);startEAtk(e,1);const hp0=e.hp,php=P.hp;let blocked=false,counterHit=false,stAtBlock=0;
   for(let i=0;i<70&&e.state==='atk';i++){G.t++;updEnemy(e);if(i===10){hurt(e,P,{dmg:10,kb:2});blocked=e.parried===true&&e.hp===hp0;stAtBlock=e.st;}if(P.hp<php)counterHit=true;ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);}
   out.parry={blocked,hpSame:e.hp===hp0,stAtBlock,counterHit,frames:set.size};
   // 打ち上げは受けられない・背後は受けられない
   const e2=enemy('sword',P,90);e2.face=-1;startEAtk(e2,1);for(let i=0;i<10;i++){G.t++;updEnemy(e2);}const h2=e2.hp;hurt(e2,P,{dmg:10,kb:2,launch:true});out.parryLaunchHurts=e2.hp<h2;
   const e3=enemy('sword',P,90);e3.face=-1;startEAtk(e3,1);for(let i=0;i<10;i++){G.t++;updEnemy(e3);}const h3=e3.hp;const back={x:e3.x-80,face:1,team:0,owner:P,hit:null};hurt(e3,back,{dmg:10,kb:2});out.parryBackHurts=e3.hp<h3;used.delete(X.img);}
  // 2. 槍の横薙ぎ
  {const P=setup();P.face=1;const e=enemy('spear',P,120);P.x=e.x-120;e.face=-1;const set=new Set();used.set(X.img,set);startEAtk(e,1);const php=P.hp;let hit=false;for(let i=0;i<70&&e.state==='atk';i++){G.t++;updEnemy(e);if(P.hp<php)hit=true;ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);}out.sweep={hit,frames:set.size};used.delete(X.img);}
  // 3. 鉄砲の装填
  {const P=setup();const e=enemy('gun',P,500);e.face=-1;const set=new Set();used.set(X.img,set);startEAtk(e,0);let n=0;for(;n<200&&e.state==='atk';n++){G.t++;updEnemy(e);}const x0=e.x;const rl=e.reloadT;let moved=0;for(let i=0;i<64;i++){G.t++;updEnemy(e);ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);}moved=Math.abs(e.x-x0);out.reload={reloadT0:rl,moved:Math.round(moved),frames:set.size,after:e.reloadT};used.delete(X.img);}
  // 4. 仕掛け
  {startGame('yuki',null);G.noStory=true;startStage(2,'yuki',false);const kinds={};for(const q of G.props)kinds[q.k]=(kinds[q.k]||0)+1;out.stageProps=kinds;out.deco=(G.deco||[]).length;
   const PS=SPR.props1,set=new Set();used.set(PS.img,set);const P=setup();
   const f=mk('sword',0,0,1);const fence={isProp:true,team:2,x:P.x-150,y:570,z:0,hp:8,maxhp:8,shk:0,k:'fence'};G.props.push(fence);P.face=-1;const seenHp=[];
   for(let i=0;i<20&&!fence.broken;i++){P.hit.clear();G.t++;P.state='atk';P.st=0;P.cur=Object.assign({},TY.yuki.atk[0],{});strike(P,{rng:200,dmg:10,kb:2,dep:60});seenHp.push(fence.hp);ctx.setTransform(RS,0,0,RS,0,0);drawProp(fence);}
   out.fence={broken:fence.broken,hpSeen:seenHp.length,frames:set.size};
   const hpB=fence.hp;P.hit.clear();strike(P,{rng:200,dmg:10,kb:2,dep:60});out.brokenHit=fence.hp!==hpB;
   // 敵の弾: 柵の向こう(柵が弾の前方)=防ぐ、こちら側(柵が弾の後方)=通す
   const fence2={isProp:true,team:2,x:P.x-150,y:570,z:0,hp:8,maxhp:8,shk:0,k:'fence'};G.props=[fence2];G.proj=[];addProj({x:fence2.x-60,y:570,z:90,vx:12,team:1,dmg:5,face:1,owner:null,k:'bullet',w:12});for(let i=0;i<30;i++){G.t++;updProj();}out.shotBlocked={projLeft:G.proj.length,fenceHp:fence2.hp};
   G.proj=[];fence2.hp=8;addProj({x:fence2.x+60,y:570,z:90,vx:12,team:1,dmg:5,face:1,owner:null,k:'bullet',w:12});for(let i=0;i<4;i++){G.t++;updProj();}out.shotBehind={fenceHp:fence2.hp,projLeft:G.proj.length};
   const fire={isProp:true,deco:true,team:2,k:'fire',x:P.x+100,y:600,z:0,hp:1};for(let i=0;i<20;i++){G.t++;ctx.setTransform(RS,0,0,RS,0,0);drawProp(fire);}out.fireFrames=set.size;used.delete(PS.img);}
  CanvasRenderingContext2D.prototype.drawImage=od;return out;});
 console.log(JSON.stringify(r));
 const bad=[];const o=r;
 if(!o.parry.blocked||!o.parry.hpSame||o.parry.stAtBlock<23||!o.parry.counterHit||o.parry.frames<5)bad.push('parry');
 if(!o.parryLaunchHurts)bad.push('launchPierces');if(o.parryBackHurts)bad.push('backBlocked');
 if(!o.sweep.hit||o.sweep.frames<5)bad.push('sweep');
 if(o.reload.reloadT0<50||o.reload.moved>1||o.reload.frames<7)bad.push('reload');
 if(!o.stageProps.fence&&!o.stageProps.mshield)bad.push('stageProps');
 if(!o.fence.broken||o.fence.frames<3)bad.push('fence');if(o.brokenHit)bad.push('brokenHit');
 if(o.shotBlocked.projLeft!==0||o.shotBlocked.fenceHp>=8)bad.push('shotNotBlocked');if(o.shotBehind.fenceHp!==8)bad.push('shotBehindBlocked');
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
