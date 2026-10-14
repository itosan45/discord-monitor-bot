// 2026-10-14 ボス・中ボスの無敵(オーナー「技が主人公の攻撃で全部つぶされてリンチで終わる」「鉄球大僧のタックル中は無敵、避けるしかない」)+くノ一の速さ・跳躍。
// ①技の出始め〜当たり終わりは無敵(ボス)/当たり8コマ前から(中ボス)/突進(edge)は走り切るまで完全無敵→壁激突後は殴れる ②被弾ごとに短い無敵(ボス10・中ボス5・必殺中は無し)
// ③無敵中の被弾は火花と音だけ ④無敵(被弾後)でも次の技を出せる(canAct) ⑤くノ一は速さ13・ジャンプ投げで跳躍(頂点98px)して着地で0。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;G.mode='play';startGame('yuki',null);G.stage=2;startStage(2,'yuki',false);
  const out={},bad=[];const setup=()=>{G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0&&f===G.player);G.partner=null;G.props=[];G.parts=[];G.proj=[];const P=G.player;P.x=G.camx+500;P.y=570;P.face=1;P.inv=999;P.hp=P.maxhp=99999;return P;};
  const mkE=(type,dx)=>{const P=G.player;const e=mk(type,P.x+dx,570,1);e.entered=true;e.hp=e.maxhp=99999;e.face=-1;e.cool=9999;e.inv=0;G.fighters.push(e);return e;};
  const hit=(e,dmg)=>{const P=G.player;P.face=sgn(e.x-P.x)||1;P.y=e.y;const h0=e.hp;P.hit=new Set();strike(P,{rng:400,dmg:dmg||10,kb:3,dep:60});return h0-e.hp;};
  // ① ボス: 技の最中は無敵(当たりが終わるまで)、そのあとは通る
  {const P=setup();const e=mkE('boss7',-120);const ai=e.T.atk.findIndex(d=>d.hs>=14&&d.k!=='guard');startEAtk(e,ai);const d=e.cur;out.bossAtk={ai,hs:d.hs,he:d.he};
   e.st=d.hs-5;e.inv=0;e.state='atk';const lost1=(()=>{e.inv=0;const t=atkInv(e);return t;})();out.bossArmorOn=lost1;
   e.inv=2;const l=hit(e);out.bossHitDuringAtk=l;if(l!==0)bad.push('ボスの技中に被弾した '+l);
   e.st=d.he+3;e.inv=0;out.bossArmorAfter=atkInv(e);if(out.bossArmorAfter)bad.push('当たり終了後も無敵');e.inv=0;out.bossHitAfter=hit(e);if(!(out.bossHitAfter>0))bad.push('当たり終了後に殴れない');}
  // ② ボスの被弾後の短い無敵(12)・必殺中はなし
  {const P=setup();const e=mkE('boss7',-120);e.state='idle';e.st=0;e.cur=null;e.inv=0;const a=hit(e);out.pinvBoss=[a>0,e.pinv,e.inv];if(!(a>0))bad.push('ボスに当たらない');if(e.pinv!==10)bad.push('ボスの被弾後の無敵が10でない '+e.pinv);
   const b2=hit(e);out.secondHit=b2;if(b2!==0)bad.push('被弾後の無敵中に2発目が通った');
   for(let i=0;i<12;i++){e.inv>0&&e.inv--;e.pinv>0&&e.pinv--;}const c=hit(e);if(!(c>0))bad.push('無敵が切れても当たらない');
   P.state='ult';const e2=mkE('boss8',-120);e2.state='idle';e2.cur=null;hit(e2);out.pinvUlt=e2.pinv||0;if(e2.pinv)bad.push('必殺中の攻撃でも被弾後の無敵が付く');P.state='idle';}
  // ③ 無敵中の被弾は火花(armorFx)
  {const P=setup();const e=mkE('boss7',-120);const ai=e.T.atk.findIndex(d=>d.hs>=14&&d.k!=='guard');startEAtk(e,ai);e.st=e.cur.hs-5;e.inv=2;G.parts=[];hit(e);out.fx=G.parts.length;if(!(out.fx>=5))bad.push('無敵中の被弾に火花が出ない '+out.fx);}
  // ④ 被弾後の無敵でも次の技を出せる(canAct)
  {const P=setup();const e=mkE('boss7',-120);e.inv=12;e.pinv=12;out.canAct=[canAct(e)];e.inv=40;e.pinv=12;out.canAct.push(canAct(e));e.inv=0;e.pinv=0;out.canAct.push(canAct(e));if(out.canAct.join()!=='true,false,true')bad.push('canAct '+out.canAct);}
  // 中ボス(鉄球大僧): 突進は走り切るまで完全無敵→壁激突のあとは殴れる/通常攻撃は当たり8コマ前から
  {const P=setup();const e=mkE('monk',-300);e.state='idle';e.cur=null;startEAtk(e,1);const d=e.cur;let armorDuringRun=0,vuln=0,n=0;
   for(let i=0;i<200;i++){G.t++;P.inv=999;e.cool=9999;updEnemy(e);if(e.state!=='atk')break;n++;if(!e.rushDone){e.inv=Math.max(e.inv,0);const l=hit(e);if(l===0)armorDuringRun++;}else{e.inv=0;e.pinv=0;const l=hit(e);if(l>0){vuln++;break;}}}
   out.monkRush={frames:n,armorDuringRun,vuln};if(armorDuringRun<20)bad.push('大僧の突進中に殴れてしまう/突進が短い '+armorDuringRun);if(!vuln)bad.push('壁激突のあとの隙に殴れない');
   const e2=mkE('monk',-120);e2.state='idle';e2.cur=null;e2.inv=0;startEAtk(e2,0);const d0=e2.cur;e2.st=1;out.monkSmash0=atkInv(e2);e2.st=d0.hs-8;out.monkSmash1=atkInv(e2);e2.st=d0.he+1;out.monkSmash2=atkInv(e2);
   if(out.monkSmash0||!out.monkSmash1||out.monkSmash2)bad.push('中ボスの通常攻撃の無敵の範囲 '+[out.monkSmash0,out.monkSmash1,out.monkSmash2]);
   const a=hit(e2);e2.inv=0;e2.state='idle';e2.cur=null;const l2=hit(e2);out.monkPinv=e2.pinv;if(e2.pinv!==5)bad.push('中ボスの被弾後の無敵が5でない '+e2.pinv);}
  // ⑥ ボスの隙(削りダメージ): 普段は5割・隙(技のあと/ガードクラッシュ/のけぞり)は1.2倍・必殺はいつでも通常。中ボスは7割。
  {const P=setup();const _rnd=Math.random;Math.random=()=>0.5;/* 被ダメにゆらぎ(乱数)があり比率が不安定になるため、この区間だけ固定 */const dmgOf=(e)=>{e.inv=0;e.pinv=0;const d=hit(e,10);e.inv=0;e.pinv=0;return d;};
   const e=mkE('boss7',120);e.state='idle';e.cur=null;const base=dmgOf(e);
   const ai=e.T.atk.findIndex(d=>d.hs>=14&&d.k!=='guard'&&!d.edge);startEAtk(e,ai);e.st=e.cur.he+6;e.state='atk';const rec=dmgOf(e);
   e.state='idle';e.cur=null;e.gcrash=G.t+50;const gc=dmgOf(e);e.gcrash=0;
   P.state='ult';e.state='idle';const ult=dmgOf(e);P.state='idle';
   const m=mkE('monk',120);m.state='idle';m.cur=null;const mBase=dmgOf(m);m.state='hurt';m.hurtT=30;const mOpen=dmgOf(m);
   out.chip={base:+base.toFixed(2),recovery:+rec.toFixed(2),guardCrash:+gc.toFixed(2),ult:+ult.toFixed(2),monkBase:+mBase.toFixed(2),monkOpen:+mOpen.toFixed(2)};
   if(Math.abs(base/ult-0.5)>0.02)bad.push('ボスの削り(普段)が必殺の5割でない '+(base/ult));
   if(Math.abs(rec/ult-1.2)>0.03)bad.push('技のあとの隙が通常の1.2倍でない '+(rec/ult));
   if(Math.abs(gc/ult-1.2*1.35)>0.04)bad.push('ガードクラッシュ中が隙(1.2倍×既存の被ダメ1.35倍)でない '+(gc/ult));
   
   Math.random=_rnd;
   if(Math.abs(mBase/mOpen-0.7)>0.05)bad.push('中ボスの削りが7割でない '+(mBase/mOpen));}
  // ⑤ くノ一: 速さ13、ジャンプ投げで跳躍(頂点98px)・着地で0
  {const P=setup();const k=mk('kunoichi',P.x+400,570,1);k.entered=true;k.hp=k.maxhp=99999;k.face=-1;G.fighters.push(k);out.kunoSpd=k.spd;if(k.spd<12)bad.push('くノ一の速さ '+k.spd);
   startEAtk(k,1);let peak=0,landed=true;for(let i=0;i<60;i++){G.t++;P.inv=999;k.cool=9999;updEnemy(k);peak=Math.max(peak,k.z);if(k.state!=='atk')break;}out.kunoJump={peak:Math.round(peak),zEnd:k.z};if(peak<90||peak>110)bad.push('くノ一の跳躍の高さ '+peak);if(k.z!==0)bad.push('着地してもzが残る '+k.z);}
  return {out,bad};});
 console.log(JSON.stringify({bad:r.bad,errors,out:r.out}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
