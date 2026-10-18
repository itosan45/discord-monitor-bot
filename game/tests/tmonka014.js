// 2026-10-14 A-014 鉄球大僧の不足絵(走り8・壁激突4・ジャンプ6・ガード構え2/受け2/クラッシュ4)の組み込み。
// 突進: 構え(a2の0〜1)→走り(mrun 8コマ周期)→壁激突(mwall 0→3、約45コマの隙)/ジャンプ技: 屈み→上昇→最高点→落下→着地2コマ/ガード: 構え・受け止め・3回受けてクラッシュ。他の敵は変わらない。
// 実動作+Android相当の画面(QA_OUT)。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const shot=async n=>{if(process.env.QA_OUT){require('fs').mkdirSync(process.env.QA_OUT,{recursive:true});await p.screenshot({path:process.env.QA_OUT+'/monka014_'+n+'.png'});}};
 const setup=()=>p.evaluate(async()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;G.mode='play';startGame('yuki','sasuke');G.stage=2;startStage(2,'yuki',false);
  for(let i=0;i<300&&!(SPR.monk&&SPR.monk.ready);i++)await new Promise(r=>setTimeout(r,50));
  G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0&&f===G.player);G.partner=null;G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];G.lanes=[];
  const P=G.player;P.x=G.camx+1100;P.y=570;P.inv=999;P.hp=P.maxhp=99999;  const e=mk('monk',G.camx+200,570,1);e.entered=true;e.hp=e.maxhp=99999;e.face=1;e.cool=9999;e.var='';G.fighters.push(e);window.__e=e;window.__trace=[];return !!SPR.monk.a.mrun;});
 const adv=(n,fn)=>p.evaluate(([n,fn])=>{const e=window.__e,P=G.player,f=fn?eval('('+fn+')'):null;for(let i=0;i<n;i++){G.t++;P.inv=999;e.cool=9999;updEnemy(e);const r=sprPos(e,SPR.monk);const nm=Object.keys(SPR.monk.a).find(k=>SPR.monk.a[k]===r.arr);window.__trace.push([e.state,e.st,nm,Math.floor(r.pos),Math.round(e.x-G.camx),Math.round((e.rushEdge||0)-G.camx),Math.round(G.camx)]);ctx.setTransform(RS,0,0,RS,0,0);renderWorld();if(f)f(e);}},[n,fn&&fn.toString()]);
 const out={},bad=[];
 const has=await setup();out.rows=has;if(!has)bad.push('A-014の行がアトラスにない');
 // 1) 突進: 構え→走り(8コマ周期)→壁激突(4コマが順に)
 await p.evaluate(()=>{startEAtk(window.__e,1);});
 const wantShot=new Set(['a2:1','mrun:3','mrun:6','mwall:0','mwall:1','mwall:2','mwall:3']),shotDone=new Set();
 for(let i=0;i<140;i++){await adv(1);const last=await p.evaluate(()=>window.__trace[window.__trace.length-1]);const key=last[2]+':'+last[3];if(wantShot.has(key)&&!shotDone.has(key)){shotDone.add(key);await shot('rush_'+key.replace(':','_'));}}
 let tr=await p.evaluate(()=>window.__trace.slice());
 out.windup=[...new Set(tr.filter(t=>t[0]==='atk'&&t[1]<46).map(t=>t[2]))].join(',');
 out.run=[...new Set(tr.filter(t=>t[2]==='mrun').map(t=>t[3]))].sort().join(',');
 const wl=tr.filter(t=>t[2]==='mwall').map(t=>t[3]);out.wall=[...new Set(wl)].join(',');out.wallOrder=wl.every((v,i)=>i===0||v>=wl[i-1]);
 out.runFrames=tr.filter(t=>t[2]==='mrun').length;
 if(out.windup!=='a2')bad.push('構えがa2でない '+out.windup);
 if(out.run!=='0,1,2,3,4,5,6,7')bad.push('走り8コマが周期で使われない '+out.run);
 if(out.wall!=='0,1,2,3'||!out.wallOrder)bad.push('壁激突の4コマが順に使われない '+out.wall);
 // 2) ジャンプ技
 await setup();await p.evaluate(()=>{const e=window.__e;e.x=window.__e.x;startEAtk(e,2);});
 const seq=[];for(let i=0;i<110;i++){await adv(1);}
 tr=await p.evaluate(()=>window.__trace.slice());
 const js=tr.filter(t=>t[2]==='mjump').map(t=>t[3]);out.jump=[...new Set(js)].join(',');out.jumpOrder=js.every((v,i)=>i===0||v>=js[i-1]-0);
 if(out.jump!=='0,1,2,3,4,5')bad.push('ジャンプ6コマが使われない '+out.jump);
 if(!out.jumpOrder)bad.push('ジャンプのコマ順が戻る '+js.join(''));
 await setup();await p.evaluate(()=>{startEAtk(window.__e,2);});
 for(const n of [24,18,10,12]){await adv(n);await shot('jump_'+n+'_'+(await p.evaluate(()=>window.__trace.length)));}
 // 3) ガード
 await setup();
 out.guard=await p.evaluate(()=>{const e=window.__e,P=G.player;e.state='idle';e.gdOn=G.t+40;e.gHitT=0;const a=sprPos(e,SPR.monk);const st=a.arr===SPR.monk.a.mgst;e.gHitT=G.t+8;const b=sprPos(e,SPR.monk);const hit=b.arr===SPR.monk.a.mgit;
   e.gdOn=0;e.gHitT=0;e.gcrash=G.t+90;e.state='hurt';e.st=0;e.hurtT=90;const c0=sprPos(e,SPR.monk);e.gcrash=G.t+50;const c1=sprPos(e,SPR.monk);e.gcrash=G.t+5;const c3=sprPos(e,SPR.monk);
   const none=(()=>{e.gcrash=0;e.state='idle';const x=sprPos(e,SPR.monk);return x.arr===SPR.monk.a.mgst||x.arr===SPR.monk.a.mgit||x.arr===SPR.monk.a.mgcr;})();
   // 他の敵(足軽)は変わらない
   const sp=mk('spear',0,570,1);sp.gdOn=G.t+40;const spr=SPR[sp.T.spr||sp.T.type];const other=spr&&spr.ready?sprPos(sp,spr).arr===(spr.a.mgst):false;
   return {st,hit,crash:[c0.arr===SPR.monk.a.mgcr&&Math.floor(c0.pos),c1.arr===SPR.monk.a.mgcr&&Math.floor(c1.pos),c3.arr===SPR.monk.a.mgcr&&Math.floor(c3.pos)],none,other};});
 if(!out.guard.st)bad.push('ガードの構えが出ない');if(!out.guard.hit)bad.push('受け止めの絵が出ない');
 if(out.guard.crash.join()!=='0,1,3')bad.push('ガードクラッシュが時間で進まない '+out.guard.crash);
 if(out.guard.none||out.guard.other)bad.push('ガード中でないのに絵が出る/他の敵に出る '+JSON.stringify(out.guard));
 if(process.env.QA_OUT){await setup();await p.evaluate(()=>{const e=window.__e;e.x=G.camx+640;e.y=570;e.face=-1;e.state='idle';e.gdOn=G.t+999;e.gHitT=0;});await adv(2);await shot('guard_stance');
  await p.evaluate(()=>{const e=window.__e;e.gHitT=G.t+8;});await adv(1);await shot('guard_hit');
  await p.evaluate(()=>{const e=window.__e;e.gdOn=0;e.gHitT=0;e.state='hurt';e.st=0;e.hurtT=90;e.gcrash=G.t+90;e.cur=null;});for(const n of[2,28,28,28]){await adv(n);await shot('guard_crash_'+(await p.evaluate(()=>window.__e.gcrash-G.t)));}}
 // 4) 鉄球投げ(攻撃4、mthrow 6コマ+k:'ironball')
 await setup();
 out.ball=await p.evaluate(async()=>{const e=window.__e,P=G.player;e.x=G.camx+200;e.y=570;e.face=1;P.x=G.camx+640;P.y=570;P.inv=0;P.hp=P.maxhp=9999;const hp0=P.hp;
  for(let i=0;i<200&&!(SPR.monkball&&SPR.monkball.ready);i++)await new Promise(r=>setTimeout(r,50));
  startEAtk(e,3);const frames=[],seen={out:0,ret:0,gone:0};let spawnedAt=-1,maxX=0,hpAfterOut=null,hits=0,lastHp=hp0;
  for(let i=0;i<140;i++){G.t++;e.cool=9999;updEnemy(e);updProj();const r=sprPos(e,SPR.monk);if(r.arr===SPR.monk.a.mthrow)frames.push(Math.floor(r.pos));
   const b=G.proj.find(q=>q.k==='ironball');if(b){if(spawnedAt<0)spawnedAt=e.st;maxX=Math.max(maxX,Math.abs(b.x-e.x));if(b.ret)seen.ret++;else seen.out++;}else if(spawnedAt>=0)seen.gone++;
   if(P.hp<lastHp){hits++;lastHp=P.hp;}P.state==='down'||0;if(P.state!=='atk'&&P.state!=='idle'&&P.state!=='walk'){P.state='idle';P.st=0;}P.inv=0;}
  return {order:frames.every((v,i)=>i===0||v>=frames[i-1]),set:[...new Set(frames)].join(','),spawnedAt,maxX:Math.round(maxX),seen,hits,hpLost:hp0-P.hp,state:e.state,hasKey:!!(SPR.monkball&&SPR.monkball.a.spin&&SPR.monkball.a.spin.length)};});
 if(!out.ball.hasKey)bad.push('鉄球の絵(monkball)が読めない');
 if(out.ball.set!=='0,1,2,3,4,5'||!out.ball.order)bad.push('鉄球投げ6コマが順に出ない '+out.ball.set);
 if(out.ball.spawnedAt<20||out.ball.spawnedAt>24)bad.push('鉄球が出る時刻 '+out.ball.spawnedAt);
 if(out.ball.maxX<450)bad.push('鉄球が遠くまで飛ばない '+out.ball.maxX);
 if(!out.ball.seen.out||!out.ball.seen.ret||!out.ball.seen.gone)bad.push('投げて戻って消えるまで '+JSON.stringify(out.ball.seen));
 if(out.ball.hits<1)bad.push('鉄球が当たらない');if(out.ball.hits>2)bad.push('1回の投げで当たり過ぎ '+out.ball.hits);
 // AI: 離れているとき(adx>330)だけ出す/近いと出さない
 out.ai=await p.evaluate(()=>{const e=window.__e,P=G.player;let far=0,near=0;const run=(dx)=>{let n=0;for(let k=0;k<4000;k++){G.t++;e.state='idle';e.st=0;e.cool=0;e.entered=true;e.x=G.camx+200;e.y=570;e.face=1;e.rushCd=G.t+999;e.leapCd=G.t+999;e.ballCd=0;P.x=e.x+dx;P.y=570;P.inv=999;updEnemy(e);if(e.state==='atk'&&e.atkI===3){n++;}e.state='idle';}return n;};far=run(550);near=run(200);return {far,near};});
 if(!(out.ai.far>20))bad.push('離れていても鉄球投げを使わない '+JSON.stringify(out.ai));
 if(out.ai.near)bad.push('近くで鉄球投げを使う '+JSON.stringify(out.ai));
 if(process.env.QA_OUT){await setup();await p.evaluate(()=>{const e=window.__e,P=G.player;e.x=G.camx+200;e.y=570;e.face=1;P.x=G.camx+1000;P.y=570;P.inv=999;startEAtk(e,3);});
  for(const n of [10,14,14,12,12,12]){await adv(n);await shot('ball_'+(await p.evaluate(()=>window.__e.st)));}}
 console.log(JSON.stringify({bad,errors,out}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
