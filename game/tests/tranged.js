// 2026-10-14 飛び道具の敵・ボスの距離取りと斜め射撃/ボスの斜め回り込み/くノ一の機動力(オーナー「ボスが同じライン上でしか動かない」「鉄砲は至近距離で撃とうとして不自然」「くノ一の機動力が目立たない」)
// 鉄砲足軽: ①詰められたら跳び退く(dodge)・撃つ時の距離 ②主人公と別の列から撃ち、弾は斜めに飛んで別の列の主人公に当たる ③列に張りつかない
// 最上義光(弓): 列に張りつかない・斜めの矢が当たる / 井伊直政: 遠いうちは斜めに近づき、間合いでは列が合う / くノ一: ジグザグに縦へ動く・見切りで跳んでかわす
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.dropItem=()=>{};const out={},bad=[];
  const idle={l:0,r:0,u:0,d:0,atkP:0,jumpP:0,spcP:0};
  const setup=(py)=>{startGame('yuki',null);startStage(0,'yuki',false);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0&&f===G.player);G.partner=null;G.props=[];G.parts=[];G.proj=[];G.camMax=G.camx;const P=G.player;P.x=G.camx+360;P.y=py||570;P.face=1;P.hp=P.maxhp=99999;P.inv=0;window.ctlKeys=()=>idle;return P;};
  const mkE=(type,x,y)=>{const e=mk(type,x,y,1);e.entered=true;e.hp=e.maxhp=99999;e.face=-1;e.cool=30;G.fighters.push(e);return e;};
  const tick=()=>{G.t++;stepGame();};
  // ① 鉄砲足軽: 主人公が近づく→跳び退く。撃った時の距離を集計(弾の発生位置で計測)
  {const P=setup(570);const e=mkE('gun',G.camx+900,570);let shots=[],seen=new Set(),dodges=0,wasD=false,minAdx=1e9;
   for(let i=0;i<900;i++){window.ctlKeys=()=>({l:0,r:(P.x<e.x-40)?1:0,u:0,d:0,atkP:0,jumpP:0,spcP:0});P.hp=P.maxhp;P.inv=999;tick();
    if(e.state==='dodge'&&!wasD)dodges++;wasD=e.state==='dodge';minAdx=Math.min(minAdx,Math.abs(P.x-e.x));
    for(const q of G.proj)if(q.owner===e&&!seen.has(q)){seen.add(q);shots.push(Math.abs(P.x-e.x));}}
   out.gunRush={dodges,shots:shots.length,near:shots.filter(d=>d<130).length,minAdx:Math.round(minAdx)};
   if(!(dodges>=2))bad.push('鉄砲足軽が詰められても跳び退かない '+dodges);
   if(shots.length&&shots.filter(d=>d<130).length/shots.length>0.34)bad.push('鉄砲足軽が至近距離(130未満)で撃つ割合が多い '+shots.filter(d=>d<130).length+'/'+shots.length);}
  // ② 斜め射撃: 主人公は動かず、鉄砲足軽が別の列から撃つ→弾に縦の速さがあり、主人公に当たる。足軽は主人公の列に張りつかない
  {const P=setup(600);P.inv=0;const e=mkE('gun',G.camx+760,520);let seen=new Set(),angled=0,hits=0,hp0=P.hp,adySum=0,n=0,maxAdy=0;
   for(let i=0;i<1500;i++){P.hp=Math.max(P.hp,1);const h=P.hp;tick();if(P.hp<h)hits++;n++;const a=Math.abs(P.y-e.y);adySum+=a;maxAdy=Math.max(maxAdy,a);
    for(const q of G.proj)if(q.owner===e&&!seen.has(q)){seen.add(q);if(Math.abs(q.vy||0)>0.3)angled++;}}
   out.gunDiag={shots:seen.size,angled,hits,meanAdy:Math.round(adySum/n),maxAdy:Math.round(maxAdy)};
   if(!(angled>=1))bad.push('斜めに飛ぶ弾が出ない');if(!(hits>=1))bad.push('別の列の主人公に弾が当たらない');if(!(adySum/n>25))bad.push('鉄砲足軽が主人公の列に張りつく '+adySum/n);}
  // ③ 最上義光(弓の大将): 列に張りつかない・斜めの矢が出る・距離を保つ
  {const P=setup(570);P.x=G.camx+560;const e=mkE('boss2',G.camx+1100,570);e.inv=0;let seen=new Set(),angled=0,aligned=0,n=0,adxSum=0;
   for(let i=0;i<1800;i++){P.hp=P.maxhp;P.inv=999;tick();e.hp=e.maxhp;n++;if(Math.abs(P.y-e.y)<12)aligned++;adxSum+=Math.abs(P.x-e.x);
    for(const q of G.proj)if(q.owner===e&&q.k==='arrow'&&!seen.has(q)){seen.add(q);if(Math.abs(q.vy||0)>0.3)angled++;}}
   out.mogami={alignedRate:+(aligned/n).toFixed(2),meanAdx:Math.round(adxSum/n),arrows:seen.size,angled};
   if(aligned/n>0.5)bad.push('最上が主人公の列に張りつく '+aligned/n);if(!(angled>=3))bad.push('最上の斜めの矢が出ない '+angled);}
  // ④ 井伊直政: 遠いうちは斜めに近づく→間合いに入る頃には列が揃う
  {const P=setup(480);P.x=G.camx+560;const e=mkE('boss1',G.camx+1100,655);e.inv=0;let maxFarAdy=0,closeAdy=[];
   for(let i=0;i<500;i++){P.hp=P.maxhp;P.inv=999;e.cool=9999;tick();const adx=Math.abs(P.x-e.x),ady=Math.abs(P.y-e.y);if(adx>330&&adx<700)maxFarAdy=Math.max(maxFarAdy,ady);if(adx<e.T.atk[0].rng*0.9)closeAdy.push(ady);if(closeAdy.length>40)break;}
   const close=closeAdy.length?closeAdy.reduce((a,c)=>a+c,0)/closeAdy.length:999;out.iiApproach={maxFarAdy:Math.round(maxFarAdy),closeAdy:Math.round(close),n:closeAdy.length};
   if(!(maxFarAdy>40))bad.push('井伊が遠いうちに斜めに近づかない(列のまま) '+maxFarAdy);if(!(closeAdy.length>=10))bad.push('井伊が間合いまで来ない');else if(close>50)bad.push('井伊が間合いに入っても列が合わない '+close);}
  // ⑤ くノ一: 縦にも大きく動く・見切りで跳んでかわす(主人公はデモ操作で攻撃)
  {const P=setup(570);const e=mkE('kunoichi',G.camx+800,570);e.cool=0;let ymin=1e9,ymax=-1e9,dodges=0,wasD=false,fast=0,n=0;window.ctlKeys=()=>demoCtl(G.player);
   for(let i=0;i<1200;i++){P.hp=P.maxhp;P.inv=999;const ox=e.x,oy=e.y;tick();e.hp=e.maxhp;ymin=Math.min(ymin,e.y);ymax=Math.max(ymax,e.y);if(e.state==='dodge'&&!wasD)dodges++;wasD=e.state==='dodge';n++;if(Math.hypot(e.x-ox,e.y-oy)>8)fast++;}
   out.kunoichi={yRange:Math.round(ymax-ymin),dodges,fastRate:+(fast/n).toFixed(2)};
   if(!(ymax-ymin>=120))bad.push('くノ一の縦の動きが小さい '+(ymax-ymin));if(!(dodges>=1))bad.push('くノ一が見切りで跳んでかわさない');}
  // ⑥ ボスの親衛隊: ボスが出ると鎧武者とくノ一が付き、倒されても時間がたつと補充される。ボスが倒れると全員倒れる
  {const P=setup(570);const b=spawnEn('boss1',1);b.x=G.camx+1000;b.y=570;b.cool=9999;G.boss=b;
   const gs=()=>G.fighters.filter(f=>f.guardOf===b&&f.hp>0&&!f.dying);const kinds=()=>gs().map(f=>f.gKind).sort().join();
   out.guard0=kinds();if(out.guard0!=='kunoichi,yoroi')bad.push('親衛隊の構成が鎧武者+くノ一でない '+out.guard0);
   const g=gs()[0];g.hp=0;g.dying=true;g.state='dead';let back=-1;for(let i=0;i<900;i++){P.hp=P.maxhp;P.inv=999;b.hp=b.maxhp;tick();for(const f of G.fighters)if(f.team===1&&f!==b&&f.guardOf===b)f.cool=Math.max(f.cool,30);if(back<0&&kinds()==='kunoichi,yoroi')back=i;}
   out.guardBack=back;if(back<0)bad.push('倒された親衛隊が補充されない');
   const ct=gs().length;bossDown(b,P);out.guardAfter=G.fighters.filter(f=>f.guardOf===b&&f.hp>0).length;if(out.guardAfter)bad.push('ボスが倒れても親衛隊が残る '+out.guardAfter);}
  return{out,bad};});
 console.log(JSON.stringify({bad:r.bad,errors,out:r.out}));
 }finally{await b.close();}})();
