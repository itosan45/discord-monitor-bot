// 2026-10-15 家康の追撃戦: 体力を1割削ると家来が盾になって立ちはだかり、吹き出しの会話のあと家康が逃げ、盾を破ると第七幕へ(オーナー案)
// ①フラグなし: 幕は6つのまま ②?chase=1: 幕は7つ ③家康の体力が9割以下で盾の場面(守護部隊の戦いの間は無効)・操作不能・家来5人・会話の吹き出し・家康が逃げて画面から消える
// ④会話のあと操作が戻り、家来(盾)を倒すと幕クリア→第七幕(追撃なしの通常の家康戦) ⑤実際の1撃で何回で盾の場面になるか(到達できる回数か)
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const BASE=process.argv[2]||process.env.GAME_URL;
async function open(b,flag){const p=await(await b.newContext({viewport:{width:915,height:412}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(BASE+(flag?(BASE.includes('?')?'&':'?')+'chase=1':''));await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});return{p,errors};}
const SETUP=()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);startStage(5,'yuki',false);G.mode='play';G.diff=1;G.banner=null;G.story=null;G.wi=G.waves.length-1;G.camMax=G.waves[G.wi].x;G.camx=G.camMax;G.props=[];G.fighters=G.fighters.filter(f=>f.team===0);
 const P=G.player;P.hp=P.maxhp=99999;P.x=G.camx+400;P.y=570;window.ctlKeys=()=>({l:0,r:0,u:0,d:0,atkP:0,jumpP:0,spcP:0});
 window.tick=(n)=>{for(let i=0;i<n;i++){P.hp=P.maxhp;G.t++;stepGame();if(i%4===0)renderWorld();}};};
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[],out={};
 try{
 {const {p,errors}=await open(b,false);const r=await p.evaluate(()=>({n:STG.length,l:LV.length,bg6:!!BGIMG[6]}));out.off=r;if(r.n!==6||r.l!==6||r.bg6)bad.push('フラグなしで幕の数が6でない/第七幕の背景を読んでいる '+JSON.stringify(r));if(errors.length)bad.push('フラグなしでエラー '+errors[0]);await p.context().close();}
 {const {p,errors}=await open(b,true);
  const r=await p.evaluate(([S])=>{eval('('+S+')')();const o={},P=G.player,orig=Math.random;o.n=STG.length;
   tick(60);for(let i=0;i<80&&G.banner;i++)tick(10);tick(30);const bo=G.boss;
   const hit=(d)=>{bo.inv=0;bo.pinv=0;Math.random=()=>0.99;hurt(bo,P,{dmg:d,kb:2,pz:'thrust'});Math.random=orig;};
   // ⑤ 実際の1撃(威力20)で何回か
   o.maxhp=bo.maxhp;let n=0;while(G.chase.phase==='run'&&n<80){hit(20);tick(6);n++;if(G.chase.phase==='block'){for(const f of G.fighters)if(f.team===1&&f!==bo){f.hp=0;f.dying=true;f.state='dead';}G.sq=[];tick(250);}}
   o.hits=n;o.phase=G.chase.phase;o.hpRatio=+(bo.hp/bo.maxhp).toFixed(3);o.mountHp=bo.mount&&bo.mount.hp;
   // ③ 盾の場面
   tick(5);o.hold=G.chase.hold;tick(30);
   tick(80);o.rt=G.fighters.filter(f=>f.team===1&&f.scene).length;o.camV=+G.chase.v.toFixed(2);
   tick(70);o.say1=!!(G.chase.rt[0]&&G.chase.rt[0].say);
   tick(160);o.say2=!!(bo.say);
   tick(100);const mk=G.chase.monk;o.mk0=!!mk;o.monk={type:mk&&mk.T.type,name:mk&&mk.T.name,hp:mk&&mk.maxhp,mid:!!(mk&&mk.T.mid),scene:!!(mk&&mk.scene)};
   o.monkRatio=+(mk.maxhp/(TY.monk.hp*diffNow().hp)).toFixed(2);o.monkAtk=mk.T.atk[0].dmg;o.baseAtk=TY.monk.atk[0].dmg;o.baseHp=TY.monk.hp;
   tick(80);o.say3=!!(mk.say||bo.say);
   tick(140);o.fled=!G.fighters.includes(bo);o.bossHud=G.boss&&G.boss.T.name;o.phase2=G.chase.phase;
   tick(250);o.after={phase:G.chase.phase,hold:G.chase.hold,scene:G.fighters.filter(f=>f.scene).length,alive:G.fighters.filter(f=>f.team===1&&f.hp>0).length,boss:G.boss&&G.boss.T.type};
   // ④ 盾を倒す → 幕クリア
   for(const f of G.fighters)if(f.team===1){f.hp=0;f.dying=true;f.state='dead';}tick(150);o.clear={state:G.state,phase:G.chase.phase};
   G.stateT=9999;P.hp=P.maxhp;tick(5);o.next={stage:G.stage,jp:STG[G.stage].jp,chase:G.chase,waves:G.waves.length,boss:G.waves[G.waves.length-1].boss};
   // 第七幕の家康は追撃なしの通常戦
   G.mode='play';G.banner=null;G.story=null;G.wi=G.waves.length-1;G.camMax=G.waves[G.wi].x;G.camx=G.camMax;G.fighters=G.fighters.filter(f=>f.team===0);G.props=[];tick(60);for(let i=0;i<80&&G.banner;i++)tick(10);tick(30);
   const b7=G.boss;o.s7={boss:b7&&b7.T.type,mount:!!(b7&&b7.mount),chaseRun:!!(b7&&b7.chaseRun),chase:!!G.chase,hon:G.hon&&G.hon.k,bg:!!(BGIMG[6]&&BGIMG[6].complete&&BGIMG[6].naturalWidth),honOK:!!HONMARU.boss3n,stage:G.stage};
   tick(600);o.s7run={state:G.state,bossHp:b7&&Math.round(b7.hp)};
   return o;},[SETUP.toString()]);
  out.on=r;await p.waitForFunction(()=>HONMARU.boss3n&&HONMARU.boss3n.complete&&HONMARU.boss3n.naturalWidth>0&&BGIMG[6]&&BGIMG[6].naturalWidth>0,null,{timeout:20000}).catch(()=>{r.s7.honOK=false;});
  if(r.n!==7)bad.push('?chase=1 で幕が7つでない '+r.n);
  if(r.phase!=='shield')bad.push('体力を削っても盾の場面にならない '+JSON.stringify({hits:r.hits,phase:r.phase,hp:r.hpRatio}));
  if(!(r.hits>=5&&r.hits<=30))bad.push('1割に届くまでの回数が極端 '+r.hits);
  if(!r.hold)bad.push('場面の間も操作できる');if(r.rt<5)bad.push('家来が5人並ばない '+r.rt);if(r.camV>0.05)bad.push('場面でカメラが動く');
  if(!r.say1)bad.push('家来の吹き出しが出ない');if(!r.say2)bad.push('家康の吹き出しが出ない');
  if(!r.fled)bad.push('家康が逃げて画面から消えない');
  if(!r.mk0||r.monk.type!=='tenkai'||r.monk.name!=='天海'||!r.monk.mid)bad.push('天海が現れない '+JSON.stringify(r.monk));if(!(r.monkAtk>=r.baseAtk*1.45&&r.monkAtk<=r.baseAtk*1.55)||!(r.monkRatio>=1.45&&r.monkRatio<=1.55))bad.push('天海が鉄球大僧の約1.5倍の強さでない '+r.monkRatio+' '+r.monkAtk+'/'+r.baseAtk);if(r.bossHud!=='天海'||r.after.boss!=='tenkai')bad.push('天海の体力ゲージが出ない(G.boss) '+r.bossHud);if(!r.say3)bad.push('天海・家康のやりとりの吹き出しが出ない');
  if(r.after.phase!=='shield2'||r.after.hold)bad.push('会話のあと操作が戻らない '+JSON.stringify(r.after));if(r.after.scene>0)bad.push('会話のあとも家来が動かない');
  if(r.clear.state!=='clear')bad.push('盾を倒しても幕クリアにならない '+JSON.stringify(r.clear));
  if(r.next.stage!==6||r.next.jp!=='第七幕'||r.next.chase)bad.push('第七幕に進まない '+JSON.stringify(r.next));if(r.next.boss!=='boss3')bad.push('第七幕の最後が家康でない');
  if(r.s7.boss!=='boss3'||r.s7.mount||r.s7.chaseRun||r.s7.chase)bad.push('第七幕の家康が追撃戦になっている '+JSON.stringify(r.s7));
  if(r.s7.hon!=='boss3n'||!r.s7.honOK)bad.push('第七幕の家康の本丸が夜の絵でない/読めていない '+JSON.stringify(r.s7));if(!r.s7.bg)bad.push('第七幕の背景(bg_6)が読めていない');
  if(errors.length)bad.push('?chase=1 でエラー '+errors[0]);await p.context().close();}
 }finally{await b.close();}
 console.log(JSON.stringify(out));
 if(bad.length){console.log('NG',bad);process.exitCode=1;}else console.log('OK tshield');})();
