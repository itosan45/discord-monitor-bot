// 友人の評価への対応(2026-10-10): 武器ドロップを減らす・馬に乗る利点をはっきりさせる
// 1) 雑魚の撃破では武器が落ちない(武将・騎馬兵・樽などからは落ちる。主人公が武器所持中・地面に武器がある間は何も落とさない)
// 2) 馬上で走りながら攻撃=騎馬突撃(前へ100px以上進み、並んだ敵2体以上に当たる)、止まって攻撃=従来の馬上攻撃
// 3) 蹴散らしで必殺ゲージがたまる
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;
  const out={drops:{},heroes:[]};
  const cnt=w=>{let n=0;const P0=G.player;G.player=null;for(let i=0;i<4000;i++){G.items=[];dropItem(0,0,null,w);if(G.items[0]&&G.items[0].k.startsWith('w_'))n++;}G.items=[];G.player=P0;return n/4000;};
  // 武器所持中・地面に武器がある間は武器が落ちない
  startGame('yuki',null);G.player.wpn={k:'odachi',uses:5};let held=0;for(let i=0;i<2000;i++){G.items=[];dropItem(0,0,null,1);if(G.items[0]&&G.items[0].k.startsWith('w_'))held++;}G.player.wpn=null;let lying=0;for(let i=0;i<2000;i++){G.items=[{k:'w_ono',x:0,y:0,t:0}];dropItem(0,0,null,1);if(G.items[1]&&G.items[1].k.startsWith('w_'))lying++;}G.items=[];out.held=held;out.lying=lying;
  out.drops={grunt:cnt(0),general:cnt(0.6),prop:cnt(0.42),legacy:cnt(undefined)};
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi']){
   startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);const P=G.player;P.mount={hp:6,max:6,col:'red'};P.wpn=null;P.x=G.camx+300;P.y=570;P.face=1;P.state='idle';P.inv=999;
   const es=[0,60,120].map(dx=>{const e=mk('sword',P.x+170+dx,570,1);e.entered=true;e.hp=e.maxhp=500;e.inv=0;e.cool=999;G.fighters.push(e);return e;});
   const k={};window.onkeydown&&0;const ctl=()=>({r:true,atkP:G.t===G.t0});G.t0=G.t+1;
   // 走りながら攻撃
   const x0=P.x;let used=null;
   for(let i=0;i<40;i++){G.t++;const c={r:true,l:false,u:false,d:false,atkP:i===1};updMount(P,c);if(i===1)used=P.cur&&P.cur.charge?'charge':'normal';for(const e of es)e.cool=999;}
   const moved=P.x-x0,hit=es.filter(e=>e.hp<500).length;
   // 止まって攻撃
   P.state='idle';P.cur=null;let used2=null;for(let i=0;i<30;i++){G.t++;updMount(P,{r:false,l:false,u:false,d:false,atkP:i===1});if(i===1)used2=P.cur&&P.cur.charge?'charge':'normal';}
   // 蹴散らしでゲージ
   for(const e of es){e.hp=500;e.trT=0;e.state='idle';e.x=P.x+40;e.y=P.y;e.z=0;}P.ki=0;P.state='idle';for(let i=0;i<20;i++){G.t++;updMount(P,{r:true,l:false,u:false,d:false});}
   out.heroes.push({hero,used,moved:Math.round(moved),hit,used2,ki:Math.round(P.ki)});}
  return out;});
 console.log(JSON.stringify({r,errors}));
 const bad=r.heroes.filter(h=>h.used!=='charge'||h.moved<100||h.hit<2||h.used2!=='normal'||h.ki<4);
 if(errors.length||r.held||r.lying||r.drops.grunt>0||r.drops.general<0.15||r.drops.general>0.3||r.drops.prop<0.08||r.drops.prop>0.22||bad.length){console.log('NG',JSON.stringify(bad));process.exitCode=1;}else console.log('OK');
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
