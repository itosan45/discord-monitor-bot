// 2026-10-12 ボスのリンチ対策: 起き上がりの無敵延長+吹き飛ばし、敵のガード(3回受け止めでガードクラッシュ)、家康の鎧武者。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const pg=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];pg.on('pageerror',e=>errors.push(e.message));
 await pg.goto(process.argv[2]||process.env.GAME_URL);await pg.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await pg.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={bad:[]};const bad=m=>out.bad.push(m);
  const setup=()=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.proj=[];const P=G.player;P.x=G.camx+400;P.y=570;P.face=1;P.inv=0;P.hp=P.maxhp=9999;return P;};
  const foe=(P,ty,dx)=>{const e=mk(ty,P.x+dx,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;e.face=-1;e.state='idle';G.fighters.push(e);return e;};
  const orig=Math.random;
  // 1) ガード→3回目でクラッシュ→クラッシュ中は被ダメージ増
  for(const ty of['sword','boss1']){const P=setup();const e=foe(P,ty,70);Math.random=()=>0;const hp0=e.hp;
   hurt(e,P,{dmg:10,kb:2});const g1=e.hp===hp0;hurt(e,P,{dmg:10,kb:2});const g2=e.hp===hp0;const mid=e.state;hurt(e,P,{dmg:10,kb:2});Math.random=orig;
   const crashed=e.state==='hurt'&&e.gcrash>G.t;
   e.state='hurt';e.inv=0;const h1=e.hp;e.gcrash=G.t+50;hurt(e,P,{dmg:10,kb:2});const dmgC=h1-e.hp;
   const e2=foe(P,ty,70);e2.gcrash=0;const h2=e2.hp;Math.random=()=>0.99;hurt(e2,P,{dmg:10,kb:2});Math.random=orig;const dmgN=h2-e2.hp;
   out['guard_'+ty]={g1,g2,mid,crashed,dmgC:+dmgC.toFixed(1),dmgN:+dmgN.toFixed(1)};
   if(!g1||!g2)bad('ガードで受け止めない:'+ty);if(!crashed)bad('3回でクラッシュしない:'+ty);if(!(dmgC>dmgN))bad('クラッシュ中の被ダメが増えない:'+ty);}
  // 1b) 打ち上げ・背後・必殺(unblock)はガードされない
  {const P=setup();const e=foe(P,'sword',70);Math.random=()=>0;const h=e.hp;hurt(e,P,{dmg:10,kb:2,launch:true});const lau=e.hp<h;const e3=foe(P,'sword',-70);e3.face=-1;const h3=e3.hp;hurt(e3,P,{dmg:10,kb:2});const back=e3.hp<h3;Math.random=orig;out.noGuard={lau,back};if(!lau)bad('打ち上げをガードした');if(!back)bad('背後をガードした');}
  // 1c) ガードの頻度(通常の雑魚は約34%)
  {const P=setup();let g=0,N=400;for(let i=0;i<N;i++){const e=foe(P,'sword',70);e.gcrash=0;const h=e.hp;hurt(e,P,{dmg:10,kb:2});if(e.hp===h)g++;G.fighters.pop();}out.rate=g/N;if(out.rate<0.2||out.rate>0.5)bad('ガード率が範囲外:'+out.rate);}
  // 2) 起き上がり: ボスは吹き飛ばしなし・2.5秒(150コマ)の無敵(その間は攻撃中でも当たらない)。雑魚は従来どおり(無敵40・吹き飛ばしなし)
  for(const ty of['sword','boss1']){const P=setup();const e=foe(P,ty,60);e.state='down';e.z=0;e.vz=0;e.lieT=40;P.x=e.x-50;P.face=1;P.inv=0;const hp0=P.hp;updDown(e);
   const ok=e.state==='getup',inv=e.inv,pushed=P.state==='down'||P.state==='hurt'||P.vx!==0||P.hp<hp0;out['wake_'+ty]={ok,inv,pst:P.state,php:hp0-P.hp};
   if(!ok)bad('起き上がらない:'+ty);if(pushed)bad('起き上がりで主人公が吹き飛ぶ:'+ty);
   if(e.T.boss){if(inv!==150)bad('ボスの起き上がり無敵が150コマでない:'+ty+inv);
    // 150コマの間は、立ち上がった後・攻撃中でも主人公の攻撃(strike)が当たらない。切れたら当たる
    e.state='idle';e.cool=9999;const h0=e.hp;for(let k=0;k<140;k++){G.t++;if(k===70){e.state='atk';e.cur=e.T.atk[0];e.st=5;}P.hit=new Set();Math.random=()=>0.99;strike(P,{pz:'thrust',dmg:10,kb:2,rng:300,dep:60});Math.random=orig;if(e.state==='atk'&&k>75){e.state='idle';}e.inv=Math.max(0,e.inv-1);}
    if(e.hp<h0)bad('ボスが起き上がり無敵の間にダメージを受けた:'+ty+(h0-e.hp));
    e.inv=0;e.state='idle';P.hit=new Set();Math.random=()=>0.99;strike(P,{pz:'thrust',dmg:10,kb:2,rng:300,dep:60});Math.random=orig;if(!(e.hp<h0))bad('無敵が切れてもダメージが入らない:'+ty);}
   else{if(inv!==40)bad('雑魚の無敵が従来(40)と違う:'+ty+inv);}}
  // 3) 家康(boss3): 最終幕の波に鎧武者が6体以上、召喚も鎧武者
  {const w=LV[5].waves.find(w=>w.boss==='boss3');const n=w.en.filter(x=>x[0]==='yoroi').length;out.ieyasuYoroi=n;if(n<6)bad('家康の波の鎧武者が少ない:'+n);
   const P=setup();const ie=foe(P,'boss3',300);const before=G.fighters.length;doSummon(ie);const sm=G.fighters.slice(before).map(x=>x.type);out.summon=sm;if(!(SPR.yoroi&&SPR.yoroi.ready)||sm.some(t=>t!=='yoroi'))bad('召喚が鎧武者でない:'+sm);
   for(let i=0;i<5;i++)doSummon(ie);const yc=G.fighters.filter(q=>q.type==='yoroi').length;out.yoroiCap=yc;if(yc>8)bad('鎧武者が増えすぎ:'+yc);}
  // 4) 大入道: ジャンプして着地で地震(衝撃波2本・吹き飛ばし)。AIも距離があればジャンプする
  {const P=setup();const m=foe(P,'monk',300);m.face=-1;m.cool=0;const hp0=P.hp;startEAtk(m,2);let landed=-1,waves=0,q=0;for(let i=0;i<140;i++){G.t++;P.inv=0;P.hp=Math.max(P.hp,1);updEnemy(m);updProj();if(m.leaped&&landed<0)landed=i;waves=Math.max(waves,G.proj.filter(x=>x.k==='wave'&&x.owner===m).length);q=Math.max(q,G.parts.filter(x=>x.k==='qfx').length);if(m.state!=='atk')break;}
   out.monkLeap={landed,waves,qfx:q,airtime:landed,state:m.state,dx:Math.round(Math.abs(m.x-P.x))};if(landed<0)bad('大入道が着地しない');if(waves<2)bad('地震の衝撃波が出ない:'+waves);if(q<1)bad('地割れの表示が出ない');
   const P2=setup();const m2=foe(P2,'monk',250);m2.face=-1;m2.cool=0;m2.entered=true;let jumped=0;const orr=Math.random;Math.random=()=>0.001;for(let i=0;i<400&&!jumped;i++){G.t++;P2.inv=999;P2.x=G.camx+400;m2.cool=0;m2.leapCd=0;updEnemy(m2);if(m2.state==='atk'&&m2.cur&&m2.cur.k==='leap')jumped=1;}Math.random=orr;out.monkAI=jumped;if(!jumped)bad('大入道のAIがジャンプしない');}
  return out;});
 r.errors=errors;console.log(JSON.stringify(r),r.bad.length||errors.length?'FAIL':'OK');
 }finally{await b.close();}})();
