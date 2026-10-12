// 2026-10-12 A-006: 鉄球大僧・仮面のくノ一・鎧武者・赤備槍武者。歩き・攻撃(判定)・被弾・ダウン・起き上がり・死亡の全コマ、くノ一の回避とクナイ、大僧のタックルと叩きつけの衝撃、ステージへの登場と絵の読み込み。
// QA_OUTがあればスマホ相当の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){const rec=used.get(img);if(rec)rec.add(a[0]+','+a[1]);return od.call(this,img,...a);};
  const setup=()=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];const P=G.player;P.x=G.camx+400;P.y=570;P.face=1;P.inv=0;P.hp=P.maxhp=9999;return P;};
  const enemy=(ty,P,dx)=>{const e=mk(ty,P.x+dx,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=999;e.face=dx>0?-1:1;G.fighters.push(e);return e;};
  const draw=(e)=>{ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);};
  const TYPES=['monk','kunoichi','yoroi','akabi'];
  out.rows={};
  for(const ty of TYPES){const S=SPR[ty];const A=S&&S.a;const row={ready:!!(S&&S.ready),walkN:A&&A.walk.length,deadN:A&&A.dead.length};
   // 1) 歩き: 移動入力を実際のupdEnemyで与え、歩きの全コマ(8)が出る
   {const P=setup();const e=enemy(ty,P,ty==='kunoichi'?700:420);e.cool=0;const set=new Set();used.set(S.img,set);e.cool=999;e.state='walk';let x0=e.x;e.state='idle';for(let i=0;i<260;i++){G.t++;P.x=G.camx+400;e.cool=999;updEnemy(e);draw(e);}row.walkFrames=set.size;row.moved=Math.round(Math.abs(e.x-x0));used.delete(S.img);}
   // 2) 攻撃: 間合いに置いて全攻撃を出し、主人公に当たる・全コマが出る
   const atkRes=[];
   for(let ai=0;ai<TY[ty].atk.length;ai++){const P=setup();const d=TY[ty].atk[ai];const dist=d.proj?420:d.k==='charge'?250:Math.min(110,d.rng-30);const e=enemy(ty,P,dist);e.face=-1;const set=new Set();used.set(S.img,set);const php=P.hp;let hits=0,lastHp=P.hp,x0=e.x,qfx=false,kun=0;startEAtk(e,ai);for(let i=0;i<d.dur+6&&(e.state==='atk');i++){G.t++;P.inv=0;updEnemy(e);if(P.hp<lastHp){hits++;lastHp=P.hp;}if(G.parts.some(q=>q.k==='qfx'))qfx=true;if(G.proj.some(q=>q.k==='kunai'))kun++;if(P.state==='hurt'||P.state==='down'){P.state='idle';P.st=0;P.vx=0;}draw(e);G.t+=0;}
    atkRes.push({ai,hits,frames:set.size,advance:Math.round(Math.abs(e.x-x0)),qfx,kunaiTicks:kun,len:d.dur});used.delete(S.img);}
   row.atk=atkRes;
   // 3) 被弾→ダウン→起き上がり→死亡(全コマ)
   {const P=setup();const e=enemy(ty,P,100);e.hp=e.maxhp=9999;const set=new Set();used.set(S.img,set);hurt(e,P,{dmg:1,kb:2,launch:true});const seen=new Set();for(let i=0;i<140;i++){G.t++;e.cool=999;updEnemy(e);seen.add(e.state);draw(e);if(e.state==='idle')break;}
    row.afterLaunch=[...seen].join('>');row.dnFrames=set.size;
    // 死亡
    const e2=enemy(ty,P,100);e2.hp=e2.maxhp=30;const set2=new Set();used.set(S.img,set2);const orr0=Math.random;Math.random=()=>0.99;hurt(e2,P,{dmg:99,kb:2,launch:true});Math.random=orr0;const seen2=new Set();for(let i=0;i<200;i++){G.t++;updEnemy(e2);seen2.add(e2.state);draw(e2);}
    row.deadStates=[...seen2].join('>');row.deadFrames=set2.size;used.delete(S.img);}
   out.rows[ty]=row;}
  // 4) 仮面のくノ一: 立ち姿の通常攻撃は低い回避でかわして反撃(打ち上げは受ける)
  {const P=setup();const e=enemy('kunoichi',P,90);e.cool=999;e.state='idle';const orr=Math.random;Math.random=()=>0;const hp0=e.hp;hurt(e,P,{dmg:10,kb:2});const dodged=e.state==='dodge'&&e.hp===hp0;const set=new Set();used.set(SPR.kunoichi.img,set);for(let i=0;i<30;i++){G.t++;updEnemy(e);draw(e);if(e.state==='idle')break;}
   const e2=enemy('kunoichi',P,90);e2.cool=999;e2.state='idle';const h2=e2.hp;hurt(e2,P,{dmg:10,kb:2,launch:true});Math.random=orr;
   out.dodge={dodged,frames:set.size,launchHurts:e2.hp<h2,cdBlocks:(()=>{const e3=enemy('kunoichi',P,90);e3.state='idle';e3.dgcd=G.t+100;e3.gcrash=1e9;const h=e3.hp;Math.random=()=>0;hurt(e3,P,{dmg:10,kb:2});Math.random=orr;return e3.hp<h;})()};used.delete(SPR.kunoichi.img);}
  // 5) くノ一のクナイ: 遠くから当たる・地面に落ちる・落ちたあとは残らない・柵で止まる
  {const P=setup();const e=enemy('kunoichi',P,400);e.face=-1;startEAtk(e,1);const php=P.hp;let hit=false,minZ=999,drew=false;for(let i=0;i<110;i++){G.t++;P.inv=0;e.state==='atk'||(e.cool=999);updEnemy(e);updProj();for(const q of G.proj)if(q.k==='kunai')minZ=Math.min(minZ,q.z);if(P.hp<php)hit=true;if(i===30){const k=G.proj.find(q=>q.k==='kunai');if(k){const ok=ctx.drawImage;ctx.setTransform(RS,0,0,RS,0,0);drawProj(k);drew=true;}}if(P.state==='hurt'||P.state==='down'){P.state='idle';P.st=0;}}
   out.kunai={hit,left:G.proj.filter(q=>q.k==='kunai').length,stuck:G.stuck.length,drew};
   const P2=setup();const f=enemy('kunoichi',P2,400);f.face=-1;G.props.push({isProp:true,team:2,x:P2.x+200,y:570,z:0,hp:8,maxhp:8,shk:0,k:'fence'});startEAtk(f,1);const hp2=P2.hp;for(let i=0;i<110;i++){G.t++;P2.inv=0;f.state==='atk'||(f.cool=999);updEnemy(f);updProj();}out.kunaiFence={blocked:P2.hp===hp2,fenceHp:G.props[0].hp};}
  // 5b) くノ一の動き: 主人公より速く、近づかれると距離を取り、離れてジャンプクナイを投げ、近いときは斬りかかる
  {const P=setup();P.inv=999;const e=enemy('kunoichi',P,500);e.cool=20;e.hp=e.maxhp=9999;let thrown=0,slashes=0,minD=1e9,fastMax=0,lastX=e.x,seenAtk=new Set(),prev=null,near=0;
   for(let i=0;i<1500;i++){G.t++;P.x=G.camx+400;P.y=570;P.hp=P.maxhp=9999;P.inv=999;updEnemy(e);updProj();draw(e);const d=Math.abs(e.x-P.x);minD=Math.min(minD,d);if(d<150)near++;fastMax=Math.max(fastMax,Math.abs(e.x-lastX));lastX=e.x;
    if(e.state==='atk'&&e.cur&&!seenAtk.has(e.st===0?e.atkI+'@'+i:'')){}
    if(e.state==='atk'&&e.st===1){if(e.atkI===1)thrown++;else slashes++;}}
   out.skirm={thrown,slashes,minD:Math.round(minD),maxSpeed:+fastMax.toFixed(1),near,playerSpd:P.T.spd,kunaiSpd:e.spd};}
  // 6) ステージ登場と絵の読み込み
  {const st={};for(let si=0;si<6;si++){startGame('yuki',null);G.noStory=true;startStage(si,'yuki',false);const ty=new Set();for(const w of G.waves)for(const e of w.en)if(TYPES.includes(e[0]))ty.add(e[0]);G.mode='play';const tg=sprTarget()||[];st[si]={types:[...ty].sort().join(','),want:TYPES.concat('monkfx').filter(k=>tg.includes(k)).join(',')};}
   startGame('yuki',null);startStage(2,'yuki',true);G.mode='demo';const dt=sprTarget()||[];st.demo2=TYPES.filter(k=>dt.includes(k)).join(',');G.mode='title';const tt=sprTarget()||[];st.title=TYPES.filter(k=>tt.includes(k)).join(',');out.stage=st;}
  return out;});
 console.log(JSON.stringify(r));
 const bad=[];
 for(const ty of ['monk','kunoichi','yoroi','akabi']){const o=r.rows[ty];if(!o.ready)bad.push(ty+'ready');if(o.walkFrames<(ty==='kunoichi'?8:12))bad.push(ty+'walk'+o.walkFrames);if(o.moved<30)bad.push(ty+'move');
  if(!/hurt|down/.test(o.afterLaunch)||!/getup/.test(o.afterLaunch)||!/idle$/.test(o.afterLaunch))bad.push(ty+'cycle:'+o.afterLaunch);
  if(!/dead$/.test(o.deadStates))bad.push(ty+'dead:'+o.deadStates);if(o.deadFrames<6)bad.push(ty+'deadFrames'+o.deadFrames);
  for(const a of o.atk){if(!(a.hits>=1)&&!(ty==='kunoichi'&&a.ai===1))bad.push(ty+'atk'+a.ai+'hit');}}
 const A=n=>r.rows[n].atk;
 if(A('monk')[0].frames<6||!A('monk')[0].qfx||A('monk')[0].hits!==1)bad.push('monk slam '+JSON.stringify(A('monk')[0]));
 if(A('monk')[1].frames<8||A('monk')[1].advance<90)bad.push('monk tackle '+JSON.stringify(A('monk')[1]));
 if(A('kunoichi')[0].frames<6)bad.push('kuno slash');
 if(A('kunoichi')[1].frames<8||A('kunoichi')[1].kunaiTicks<5)bad.push('kuno throw '+JSON.stringify(A('kunoichi')[1]));
 if(A('yoroi')[0].frames<6||A('akabi')[0].frames<6)bad.push('armor atk frames');
 if(!r.dodge.dodged||r.dodge.frames<4||!r.dodge.launchHurts||!r.dodge.cdBlocks)bad.push('dodge '+JSON.stringify(r.dodge));
 if(!r.kunai.hit||r.kunai.left!==0||!r.kunai.drew||r.kunai.stuck!==0)bad.push('kunai '+JSON.stringify(r.kunai));
 if(!(r.skirm.thrown>=5)||!(r.skirm.maxSpeed>=6)||r.skirm.kunaiSpd<=r.skirm.playerSpd)bad.push('skirm '+JSON.stringify(r.skirm));
 if(!r.kunaiFence.blocked||r.kunaiFence.fenceHp>=8)bad.push('kunai fence');
 const S=r.stage;if(S[0].types||S[0].want)bad.push('stage0');for(const [si,t,w] of [[1,'yoroi','yoroi'],[2,'monk','monk,monkfx'],[3,'kunoichi','kunoichi,monkfx'],[4,'akabi,kunoichi','kunoichi,akabi,monkfx'],[5,'akabi,kunoichi,monk,yoroi','monk,kunoichi,yoroi,akabi,monkfx']]){if(S[si].types!==t)bad.push('stage'+si+'types:'+S[si].types);if(S[si].want.split(',').sort().join(',')!==w.split(',').sort().join(','))bad.push('stage'+si+'want:'+S[si].want);}
 if(S.demo2||S.title)bad.push('demo/title loads');
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  const shots=[['monk_slam','monk',0,36],['monk_tackle','monk',1,30],['kuno_slash','kunoichi',0,12],['kuno_throw','kunoichi',1,24],['yoroi_sweep','yoroi',0,24],['akabi_thrust','akabi',0,20]];
  for(const [name,ty,ai,st] of shots){await p.evaluate(([ty,ai,st])=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.x=G.camx+330;P.y=570;P.face=1;P.inv=0;P.hp=P.maxhp=9999;const e=mk(ty,P.x+(TY[ty].atk[ai].proj?400:TY[ty].atk[ai].k==='charge'?250:Math.min(110,TY[ty].atk[ai].rng-30)),570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=999;e.face=-1;G.fighters.push(e);startEAtk(e,ai);G.parts=[];G.flashT=0;G.hitstop=0;G.slow=0;G.shake=0;G.proj=[];G.stuck=[];G.items=[];G.decals=[];for(let i=0;i<st;i++){G.t++;P.inv=999;updEnemy(e);updProj();}G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation="source-over";ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},[ty,ai,st]);await p.screenshot({path:`${process.env.QA_OUT}/${name}.png`});}
  await p.evaluate(()=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.x=G.camx+240;P.y=570;P.face=1;P.inv=999;[['monk',0,560],['kunoichi',1,640],['yoroi',2,500],['akabi',3,600]].forEach(([ty,k,y],i)=>{const e=mk(ty,P.x+180+i*130,y,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=999;e.face=-1;e.state='walk';e.wp=i;G.fighters.push(e);});G.parts=[];G.flashT=0;G.hitstop=0;G.shake=0;G.items=[];G.decals=[];ctx.globalCompositeOperation="source-over";ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();});await p.screenshot({path:`${process.env.QA_OUT}/four_standing.png`});}
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
