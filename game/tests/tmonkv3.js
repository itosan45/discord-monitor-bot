// 2026-10-14 鉄球大僧の転倒8コマ・叩きつけ12コマ(A-015)。
// 転倒: 打ち上げ→空中→着地(弾み)→寝姿まで、8コマすべてが順に出る/空中のコマは地面より上/寝姿は接地。
// 叩きつけ: 12コマすべてが出て、着弾(hs〜he)にフレーム6〜7が出る/ダメージの命中は従来どおり/跳躍攻撃(a1・6コマ)は影響を受けない。
// QA_OUTがあれば Android相当(802×360) の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;const out={};
  const setup=()=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];const P=G.player;P.hp=P.maxhp=9999;P.inv=0;return P;};
  const mkMonk=(x,y,face)=>{const e=mk('monk',x,y,1);e.entered=true;e.hp=e.maxhp=99999;e.cool=999;e.face=face;G.fighters.push(e);return e;};
  const idxOf=(S,arr,pos)=>S.a.down===arr?Math.floor(pos):-1;
  // --- 転倒
  const down=(vz,vx)=>{const P=setup();const e=mkMonk(G.camx+640,570,1);const S=SPR.monk;knock(e,-1,vx,vz);const seq=[],zs=[];let i=0;
   for(;i<200;i++){G.t++;P.inv=0;e.cool=999;updEnemy(e);const sp=sprPos(e,S);seq.push(sp.arr===S.a.down?Math.floor(sp.pos):'x'+(sp.arr===S.a.getup?'g':sp.arr===S.a.dead?'d':'?'));zs.push(Math.round(e.z));if(e.state!=='down')break;}
   const frames=[...new Set(seq)];const lying=seq.filter(v=>v===7).length;
   // 空中のコマ(2〜4)でz>0.6、寝姿(7)でz<=0.6
   let badAir=0,badLie=0;for(let k=0;k<seq.length;k++){if(seq[k]>=2&&seq[k]<=4&&zs[k]<1)badAir++;if(seq[k]===7&&zs[k]>0)badLie++;}
   // 順序: 0→…→7 が逆戻りしない(弾みの5→6→7は除く)
   let back=0;for(let k=1;k<seq.length;k++){if(typeof seq[k]==='number'&&typeof seq[k-1]==='number'&&seq[k]<seq[k-1])back++;}
   return {ticks:i,seq:seq.join(','),frames:frames.join(' '),lying,badAir,badLie,back,bounced:e.bounced,endState:e.state};};
  out.downLaunch=down(10,6);out.downFlat=down(0,0);out.downBig=down(13,9);
  // --- 叩きつけ(通常攻撃1段目): 全コマ・着弾のコマ・命中
  {const P=setup();const e=mkMonk(G.camx+500,570,1);P.x=e.x+120;P.y=570;P.face=-1;const S=SPR.monk,d=TY.monk.atk[0];out.def={panim:d.panim,hs:d.hs,he:d.he,dur:d.dur};
   startEAtk(e,0);const seen=[],hitFr=[];let hp0=P.hp,hits=0,hitTick=-1;
   for(let i=0;i<120;i++){G.t++;P.inv=0;e.cool=999;updEnemy(e);if(e.state!=='atk'&&i>5)break;const sp=sprPos(e,S);const fr=sp.arr===S.a.smash?Math.floor(sp.pos):('x'+Object.keys(S.a).find(k=>S.a[k]===sp.arr));seen.push(fr);if(e.st>=d.hs&&e.st<=d.he)hitFr.push(fr);if(P.hp<hp0&&hitTick<0){hitTick=e.st;hits++;hp0=P.hp;}}
   out.smash={frames:[...new Set(seen)].join(' '),hitFrames:[...new Set(hitFr)].join(' '),hitTick,len:S.a.smash.length};}
  // --- 跳躍攻撃は a1(6コマ)のまま
  {const P=setup();const e=mkMonk(G.camx+500,570,1);const S=SPR.monk;startEAtk(e,2);const used=new Set();for(let i=0;i<120;i++){G.t++;P.inv=0;e.cool=999;updEnemy(e);if(e.state!=='atk'&&i>5)break;const sp=sprPos(e,S);used.add(Object.keys(S.a).find(k=>S.a[k]===sp.arr));}out.leapAnim=[...used].join(',');out.a1len=S.a.a1.length;}
  return out;});
 const bad=[];
 for(const k of['downLaunch','downBig']){const o=r[k];
  if(o.frames.split(' ').filter(x=>/^\d+$/.test(x)).join(' ')!=='0 1 2 3 4 5 6 7')bad.push(k+' コマ '+o.frames);
  if(o.badAir)bad.push(k+' 空中コマが地面 '+o.badAir);if(o.badLie)bad.push(k+' 寝姿が浮く '+o.badLie);if(o.back)bad.push(k+' 順序の逆戻り '+o.back);if(o.lying<10)bad.push(k+' 寝姿が短い '+o.lying);}
 if(!r.downFlat.frames.includes('7'))bad.push('平らな転倒で寝姿が出ない '+r.downFlat.frames);
 if(r.def.panim!=='smash')bad.push('panim '+JSON.stringify(r.def));
 if(r.smash.len!==12)bad.push('smash '+r.smash.len);
 if(r.smash.frames.split(' ').filter(x=>/^\d+$/.test(x)).length!==12)bad.push('叩きつけに全12コマが出ない '+r.smash.frames);
 if(!/6/.test(r.smash.hitFrames)||!/7/.test(r.smash.hitFrames)||/(^| )[0-4]( |$)/.test(r.smash.hitFrames))bad.push('着弾のコマ '+r.smash.hitFrames);
 if(r.smash.hitTick<31||r.smash.hitTick>37)bad.push('命中のタイミング '+r.smash.hitTick);
 if(r.leapAnim!=='mjump'||r.a1len!==6)bad.push('跳躍攻撃の絵(A-014でジャンプ6コマ mjump になった) '+r.leapAnim+' '+r.a1len);
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  const shots=[['down_t3','down',3],['down_t8','down',8],['down_t14','down',14],['down_t20','down',20],['down_t26','down',26],['down_land','down',-1],['down_lie','down',-2],['smash_0','smash',6],['smash_1','smash',20],['smash_2','smash',30],['smash_3','smash',34],['smash_4','smash',44],['smash_5','smash',56]];
  for(const [name,kind,t] of shots){await p.evaluate(([kind,t])=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];G.items=[];G.decals=[];const P=G.player;P.hp=P.maxhp=9999;P.inv=999;P.x=G.camx+250;P.y=570;P.face=1;
   const e=mk('monk',G.camx+640,570,1);e.entered=true;e.hp=e.maxhp=99999;e.cool=999;e.face=-1;G.fighters.push(e);
   if(kind==='down'){knock(e,1,6,10);let landed=-1;const lim=t>=0?t:200;for(let i=0;i<lim;i++){G.t++;P.inv=999;e.cool=999;updEnemy(e);if(t===-1&&e.bounced&&e.vz>0){break;}if(t===-2&&e.state==='down'&&e.z<=0&&e.lieT>=8)break;}}
   else{P.x=G.camx+380;startEAtk(e,0);for(let i=0;i<t;i++){G.t++;P.inv=999;e.cool=999;updEnemy(e);}}
   G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},[kind,t]);await p.screenshot({path:`${process.env.QA_OUT}/${name}.png`});}}
 console.log(JSON.stringify({bad,errors,summary:r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
