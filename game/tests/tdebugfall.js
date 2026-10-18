// 一体デバッグの「転倒→起き上がり」と、敵の攻撃確認用の標的(無敵の足軽)を検査する。
// (1) 全キャラ(27種)で 転倒→起き上がり→待機 が実際の物理(updDown)と起き上がり20コマで繰り返される。
// (2) ボスの専用絵 bfall_* が転倒・起き上がりの間に呼ばれる(読み込み済みのボスだけ)。
// (3) 敵の攻撃を見る間だけ標的が前方280pxに居て、跳び込み(dive)は標的の手前55〜90pxに着地する。標的が居ない主人公の動作では出ない。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:802,height:360},isMobile:true,hasTouch:true});const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;startAuto('yuki',0);setInspectionMode(true);
  ctx=MCTX;ctx.setTransform(RS,0,0,RS,0,0);/* 本番と同じ表示キャンバスへ renderWorld で描く(drawFighter を直接呼ぶと本番と違う経路になる) */
  const bad=[],rows=[];
  for(const type of Object.keys(TY))for(const face of [1,-1]){
   demoView.actor=type;demoView.facing=face;demoView.weapon='';demoView.motion='fall';prepareWalkPreview();
   const states=[],seen=new Set();const nat=ctx.drawImage.bind(ctx);ctx.drawImage=function(im,...q){if(q.length===8){const k=Object.keys(SPR).find(k=>SPR[k].img===im);if(k&&/^bfall_/.test(k))seen.add(k);}return nat(im,...q);};
   let zMax=0,fx0=null,fx1=null;
   for(let i=0;i<260;i++){stepGame();G.t++;const q=G.player;if(!states.length||states[states.length-1]!==q.state)states.push(q.state);if(q.state==='down'){if(fx0===null)fx0=q.x;fx1=q.x;zMax=Math.max(zMax,q.z||0);}
    if(i%3===0)renderWorld();
    if(states.join('>').startsWith('idle>down>getup>idle')&&q.state==='idle'&&i>20)break;}
   ctx.drawImage=nat;
   const s=states.join('>');const ok=/^idle>down>getup>idle/.test(s)||/^down>getup>idle/.test(s);
   const knockedAway=fx0!==null&&(fx1-fx0)*face<0;/* 前を向いたまま、後ろへ吹き飛ぶ */
   const needArt=TY[type].boss&&SPR['bfall_'+(TY[type].spr||type)]&&SPR['bfall_'+(TY[type].spr||type)].ready;
   if(!ok||!(zMax>5)||!knockedAway||(needArt&&seen.size===0))bad.push({type,face,states:s,zMax,fx0,fx1,art:[...seen]});
   rows.push({type,face,states:s,zMax,art:[...seen]});
  }
  // 標的: 敵の攻撃を見る間だけ居る
  const dives=[];
  for(const type of Object.keys(TY)){const t=TY[type];if(!t.atk)continue;t.atk.forEach((d,ai)=>{if(!d.dive)return;for(const face of [1,-1]){
    demoView.actor=type;demoView.facing=face;demoView.weapon='';demoView.motion='atk'+ai;prepareWalkPreview();
    if(G.fighters.length!==1)bad.push({type,dummyBeforeAttack:true});
    let started=false,dx=null,seenDummy=false;
    for(let i=0;i<300;i++){stepGame();G.t++;const q=G.player;if(q.cur)started=true;const dm=demoView.dummy;if(started&&dm){seenDummy=G.fighters.includes(dm)&&dm.team===1&&dm.inv>0;if(q.leaped&&dx===null)dx=Math.abs(dm.x-q.x);}if(started&&!q.cur)break;}
    if(!seenDummy||dx===null||dx<55||dx>90)bad.push({type,atk:ai,face,seenDummy,dx});dives.push({type,ai,face,dx});}});}
  // 標的が居ない: 主人公の動作と、敵の歩行
  demoView.actor='yuki';demoView.motion='atk0';prepareWalkPreview();for(let i=0;i<60;i++){stepGame();G.t++;}if(G.fighters.length!==1)bad.push({heroHasDummy:G.fighters.length});
  demoView.actor='boss3';demoView.motion='walk';prepareWalkPreview();for(let i=0;i<40;i++){stepGame();G.t++;}if(G.fighters.length!==1)bad.push({walkHasDummy:G.fighters.length});
  return{bad,types:Object.keys(TY).length,rows:rows.length,dives};});
 console.log(JSON.stringify({types:r.types,cases:r.rows,dives:r.dives,bad:r.bad,errors}));
 if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
