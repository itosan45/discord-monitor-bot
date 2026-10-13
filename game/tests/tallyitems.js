// 2026-10-13 味方NPC(お供)も回復アイテムを取る。傷ついているお供は近くの回復アイテムを取りに行き、足元で取る。
// 武器は取らない/元気なお供は取らない/主人公のほうが傷ついていて近くにいれば譲る/効果(HP・必殺ゲージ)が正しい/敵が攻撃してくる最中は後回し。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;const out={};
  const setup=(pk)=>{startGame('yuki',pk||'nezu');G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.items=[];G.deco=[];G.proj=[];const P=G.player;P.x=G.camx+350;P.y=575;P.hp=P.maxhp=9999;P.inv=999;const q=G.partner;q.x=G.camx+250;q.y=575;q.maxhp=q.hp=100;q.ki=0;q.inv=999;return {P,q};};
  const run=(n,fn)=>{for(let i=0;i<n;i++){G.t++;G.player.inv=999;if(G.partner)G.partner.inv=999;stepGame();fn&&fn(i);}};
  // 1. 傷ついたお供は、離れたおにぎりを取りに行く(約300px先)
  {const {P,q}=setup();q.hp=40;P.x=G.camx+250;G.items.push({x:G.camx+560,y:600,k:'onigiri',t:0});let got=-1;run(400,i=>{if(got<0&&q.hp>40)got=i;});out.seek={got,hp:Math.round(q.hp),itemsLeft:G.items.length,x:Math.round(q.x-G.camx)};}
  // 2. 元気なお供は取らない(足元に置いても)
  {const {P,q}=setup();q.hp=95;G.items.push({x:q.x,y:q.y,k:'onigiri',t:0});run(60);out.healthy={itemsLeft:G.items.length,hp:Math.round(q.hp)};}
  // 3. 武器は取らない(傷ついていても)
  {const {P,q}=setup();q.hp=30;G.items.push({x:q.x,y:q.y,k:'w_odachi',t:0});run(80);out.weapon={itemsLeft:G.items.length,wpn:!!q.wpn};}
  // 4. 効果: 兵糧+70(上限まで)・酒(必殺ゲージ)・寿司+45・饅頭+20と必殺+40
  out.effects=[];for(const [k,hp0,ki0] of [['hyorou',20,0],['sushi',30,0],['sake',90,0],['manju',50,0]]){const {P,q}=setup();q.hp=hp0;q.ki=ki0;G.items.push({x:q.x,y:q.y,k,t:0});run(8);out.effects.push([k,Math.round(q.hp),Math.round(q.ki),G.items.length]);}
  // 5. 主人公のほうが傷ついていて近くにいれば譲る
  {const {P,q}=setup();q.hp=60;P.hp=20;P.maxhp=100;P.x=G.camx+330;P.y=575;const it={x:G.camx+300,y:575,k:'onigiri',t:0};G.items.push(it);P.x=G.camx+700;/* 主人公は少し離れた所へ */
   run(1);const near=G.items.length;P.x=G.camx+340;run(1);out.yield={items:G.items.length,qhp:Math.round(q.hp)};}
  // 6. 敵が攻撃してくる最中は、取りに行かない
  {const {P,q}=setup();q.hp=30;P.x=G.camx+250;G.items.push({x:G.camx+520,y:575,k:'onigiri',t:0});const e=mk('sword',q.x+100,575,1);e.entered=true;e.hp=e.maxhp=9999;e.face=-1;G.fighters.push(e);e.state='atk';e.st=0;e.cur=TY.sword.atk[0];const x0=q.x;
   for(let i=0;i<8;i++){G.t++;q.inv=999;e.cool=9999;e.st=Math.min(e.st+0,3);const c=partnerCtl(q);if(c.r&&q.x>x0&&false){}}
   out.threat={seeking:!!q.seeking};}
  return out;});
 const bad=[];
 if(!(r.seek.got>=0)||r.seek.itemsLeft!==0)bad.push('取りに行かない '+JSON.stringify(r.seek));
 if(r.healthy.itemsLeft!==1)bad.push('元気なのに取った '+JSON.stringify(r.healthy));
 if(r.weapon.itemsLeft!==1||r.weapon.wpn)bad.push('武器を取った '+JSON.stringify(r.weapon));
 const ex=Object.fromEntries(r.effects.map(e=>[e[0],e]));
 if(ex.hyorou[1]!==90||ex.hyorou[3]!==0)bad.push('兵糧 '+JSON.stringify(ex.hyorou));
 if(ex.sushi[1]!==75)bad.push('寿司 '+JSON.stringify(ex.sushi));
 if(ex.sake[2]!==100)bad.push('酒 '+JSON.stringify(ex.sake));
 if(ex.manju[1]!==70||ex.manju[2]!==40)bad.push('饅頭 '+JSON.stringify(ex.manju));
 if(r.yield.items!==1)bad.push('譲らない '+JSON.stringify(r.yield));
 if(r.threat.seeking)bad.push('攻撃中なのに取りに行く');
 console.log(JSON.stringify({bad,errors,r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
