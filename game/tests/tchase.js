// 2026-10-15 家康の騎馬追撃戦(試作 ?chase=1): 最終幕の家康が馬で逃げ、主人公も馬で追う(オーナー案)
// ①フラグなし(既定)は従来どおり(家康は馬に乗らず、追撃も始まらない) ②?chase=1: 家康が騎乗・主人公も騎乗・景色(カメラ)が流れ続ける・背景は本丸に固定されない
// ③馬の傷が6以下で守護部隊(カメラが止まる・駆け去った家康に攻撃は当たらない)→倒すと追撃再開 ④3以下で2回目 ⑤馬が尽きると落馬→画面が止まり本丸の背景・一対一 ⑥落馬後の起き上がりは2.5秒無敵(直接hurtも当たらない) ⑦家康を倒すと幕クリア
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const BASE=process.argv[2]||process.env.GAME_URL;
async function open(b,flag){const p=await(await b.newContext({viewport:{width:915,height:412}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(BASE+(flag?(BASE.includes('?')?'&':'?')+'chase=1':''));await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});return{p,errors};}
const SETUP=()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);startStage(5,'yuki',false);G.mode='play';G.diff=1;G.banner=null;G.story=null;G.wi=G.waves.length-1;G.camMax=G.waves[G.wi].x;G.camx=G.camMax;G.props=[];G.fighters=G.fighters.filter(f=>f.team===0);G.sq=[];G.waveOn=false;
 const P=G.player;P.hp=P.maxhp=99999;P.x=G.camx+400;P.y=570;window.ctlKeys=()=>({l:0,r:0,u:0,d:0,atkP:0,jumpP:0,spcP:0});
 window.tick=(n)=>{for(let i=0;i<n;i++){P.hp=P.maxhp;G.t++;stepGame();if(i%4===0)renderWorld();}};};
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[],out={};
 try{
 // ① 既定
 {const {p,errors}=await open(b,false);
  const r=await p.evaluate(([S])=>{eval('('+S+')')();tick(400);const bo=G.boss;return{boss:!!bo,mount:!!(bo&&bo.mount),chase:!!G.chase,CHASE:typeof CHASE!=='undefined'?CHASE:-1,camMoved:Math.round(G.camx-G.camMax)};},[SETUP.toString()]);
  out.off=r;if(!r.boss||r.mount||r.chase)bad.push('フラグなしで追撃戦になっている '+JSON.stringify(r));
  if(errors.length)bad.push('フラグなしでエラー '+errors[0]);await p.context().close();}
 // ② 以降 ?chase=1
 {const {p,errors}=await open(b,true);
  const r=await p.evaluate(([S])=>{eval('('+S+')')();const o={},P=G.player,orig=Math.random;
   tick(60);for(let i=0;i<80&&G.banner;i++)tick(10);tick(30);const bo=G.boss;o.start={chase:!!G.chase,on:G.chase&&G.chase.on,phase:G.chase&&G.chase.phase,mount:bo&&bo.mount&&bo.mount.hp,run:!!(bo&&bo.chaseRun),pMount:!!P.mount,hon:G.hon,guards:G.fighters.filter(f=>f.team===1&&f!==bo).length};
   const cx0=G.camx;tick(150);o.scroll={moved:Math.round(G.camx-cx0),v:+G.chase.v.toFixed(2),pRel:Math.round(P.x-G.camx),bRel:Math.round(bo.x-G.camx)};
   const hit=(n)=>{for(let i=0;i<n;i++){bo.inv=0;bo.pinv=0;Math.random=()=>0.99;hurt(bo,P,{dmg:10,kb:2,pz:'thrust'});Math.random=orig;tick(6);}};
   // ③ 守護部隊1: 馬の傷6以下
   hit(3);tick(10);o.b1={phase:G.chase.phase,mount:bo.mount&&bo.mount.hp};
   tick(200);o.b1g={guards:G.fighters.filter(f=>f.team===1&&f!==bo&&f.hp>0).length,v:+G.chase.v.toFixed(2),camStill:true};
   const h0=bo.mount.hp;bo.inv=0;Math.random=()=>0.99;hurt(bo,P,{dmg:10,kb:2,pz:'thrust'});Math.random=orig;o.b1g.blocked=bo.mount.hp===h0;
   for(const f of G.fighters)if(f.team===1&&f!==bo){f.hp=0;f.dying=true;f.state='dead';}G.sq=[];
   tick(220);o.b1end={phase:G.chase.phase,bRel:Math.round(bo.x-G.camx),v:+G.chase.v.toFixed(2)};
   // ④ 守護部隊2: 馬の傷3以下
   tick(150);hit(3);tick(10);o.b2={phase:G.chase.phase,blk:G.chase.blk,mount:bo.mount&&bo.mount.hp};
   tick(220);for(const f of G.fighters)if(f.team===1&&f!==bo){f.hp=0;f.dying=true;f.state='dead';}G.sq=[];tick(220);o.b2end={phase:G.chase.phase};
   // ⑤ 落馬
   tick(150);hit(Math.max(1,bo.mount?bo.mount.hp:0));tick(20);o.duel={phase:G.chase.phase,mount:!!bo.mount,run:!!bo.chaseRun,hon:G.hon&&G.hon.k,state:bo.state};
   // ⑥ 起き上がり無敵: 直接hurtも当たらない
   tick(120);const hp0=bo.hp;o.wake={state:bo.state,wakeLeft:bo.wakeInv-G.t};if(bo.wakeInv>G.t){bo.inv=0;Math.random=()=>0.99;hurt(bo,P,{dmg:50,kb:2,pz:'thrust'});Math.random=orig;}o.wake.noDmg=bo.hp===hp0;
   tick(200);o.after={camStill:Math.round(G.camx-G.camMax)>=0,v:+G.chase.v.toFixed(2),wakeLeft:bo.wakeInv-G.t};
   // ⑦ 撃破
   bo.hp=1;bo.wakeInv=0;bo.inv=0;Math.random=()=>0.99;hurt(bo,P,{dmg:99999,kb:2,pz:'thrust'});Math.random=orig;tick(260);o.end={state:G.state,bossHp:bo.hp};
   return o;},[SETUP.toString()]);
  out.on=r;
  if(!r.start.chase||!r.start.on||r.start.phase!=='run')bad.push('追撃戦が始まらない '+JSON.stringify(r.start));
  if(r.start.mount!==9||!r.start.run)bad.push('家康が騎乗していない');if(!r.start.pMount)bad.push('主人公が騎乗していない');if(r.start.hon)bad.push('追撃中の背景が本丸に固定されている');
  if(r.start.guards>0)bad.push('追撃の始まりから守護の兵がいる(従来の親衛隊が出ている)');
  if(!(r.scroll.moved>250))bad.push('景色が流れ続けない '+r.scroll.moved);if(!(r.scroll.pRel>0&&r.scroll.pRel<1280))bad.push('主人公が画面の外にいる');
  if(r.b1.phase!=='block'||r.b1.mount>6)bad.push('馬の傷6以下で守護部隊にならない '+JSON.stringify(r.b1));
  if(!(r.b1g.guards>=3))bad.push('守護部隊が出ない '+r.b1g.guards);if(r.b1g.v>0.05)bad.push('守護部隊の戦いでカメラが止まらない');if(!r.b1g.blocked)bad.push('守護部隊の間、家康に攻撃が当たる');
  if(r.b1end.phase!=='run'||!(r.b1end.v>1))bad.push('守護部隊を倒しても追撃が再開しない '+JSON.stringify(r.b1end));
  if(r.b2.phase!=='block'||r.b2.blk!==2)bad.push('2回目の守護部隊にならない '+JSON.stringify(r.b2));if(r.b2end.phase!=='run')bad.push('2回目の後に追撃が再開しない');
  if(r.duel.phase!=='duel'||r.duel.mount||r.duel.run||r.duel.hon!=='boss3')bad.push('落馬して一対一にならない '+JSON.stringify(r.duel));if(!(r.wake.wakeLeft>0))bad.push('落馬後の起き上がり無敵(wakeInv)が付かない '+JSON.stringify(r.wake));
  if(!r.wake.noDmg)bad.push('起き上がり無敵の間にダメージを受ける(直接hurt)');if(r.after.v>0.05)bad.push('一対一でカメラが動く');
  if(!(r.end.state==='bossdown'||r.end.state==='clear'))bad.push('家康を倒しても幕が終わらない '+r.end.state);
  if(errors.length)bad.push('?chase=1 でエラー '+errors[0]);await p.context().close();}
 }finally{await b.close();}
 console.log(JSON.stringify(out));
 if(bad.length){console.log('NG',bad);process.exitCode=1;}else console.log('OK tchase');})();
