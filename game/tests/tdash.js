// 2026-10-15 ダッシュ(走りながら攻撃=突進攻撃)が出しにくい(友達の意見「ダッシュが全然できない」「通常ステージで歩きからのダッシュ操作がやりにくい」)
// 人が操作する主人公: 走り始めて約0.17秒(10コマ)で突進攻撃が出る(従来は17コマ)。方向が数コマ途切れても(指のぶれ)出る。味方・デモは従来どおり(16コマ)。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const pg=await(await b.newContext({viewport:{width:915,height:412}})).newPage(),errors=[];pg.on('pageerror',e=>errors.push(e.message));
 await pg.goto(process.argv[2]||process.env.GAME_URL);await pg.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await pg.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={},bad=[];
  const heroes=Object.keys(TY).filter(k=>TY[k].cost);
  // 毎回新しく始めて、n コマ走る(gap>0 なら方向を離して gap コマ待つ)→ 攻撃ボタン。突進(T.dash)が出たか
  const run=(h,n,gap,partner)=>{startGame(h,null);startStage(0,h,false);G.mode='play';G.banner=null;G.waveOn=false;G.waves=[{x:999999,en:[]}];G.camMax=999999;G.items=[];G.props=[];G.fighters=G.fighters.filter(f=>f.team===0);const P=G.player;P.hp=P.maxhp=9999;P.x=G.camx+300;P.y=570;P.isPartner=!!partner;
   let c={l:0,r:1,u:0,d:0,atkP:0,jumpP:0,spcP:0};window.ctlKeys=()=>c;for(let i=0;i<n;i++){G.t++;stepGame();}
   if(gap){c={l:0,r:0,u:0,d:0,atkP:0,jumpP:0,spcP:0};for(let i=0;i<gap;i++){G.t++;stepGame();}c={l:0,r:0,u:0,d:0,atkP:1,jumpP:0,spcP:0};}else c={l:0,r:1,u:0,d:0,atkP:1,jumpP:0,spcP:0};
   G.t++;stepGame();return P.state==='atk'&&P.cur===P.T.dash;};
  for(const h of heroes){
   const o={short:run(h,6),ten:run(h,10),flick:run(h,14,3),long:run(h,30),late:run(h,14,12),partner10:run(h,10,0,true),partner17:run(h,17,0,true)};
   out[h]=o;
   if(o.short)bad.push(h+': 6コマ走っただけで突進が出る');if(!o.ten)bad.push(h+': 10コマ走っても突進が出ない');if(!o.flick)bad.push(h+': 方向が途切れる(指のぶれ)と突進が出ない');if(!o.long)bad.push(h+': 長く走っても出ない');
   if(o.late)bad.push(h+': 止まって12コマたっても突進が出る(猶予は8コマ)');if(o.partner10)bad.push(h+': 味方が10コマで突進(従来16コマのまま)');if(!o.partner17)bad.push(h+': 味方が17コマで突進しない');}
  return{out,bad};});
 console.log(JSON.stringify(r.out));
 if(errors.length)r.bad.push('エラー '+errors[0]);
 if(r.bad.length){console.log('NG',r.bad);process.exitCode=1;}else console.log('OK tdash');
 }finally{await b.close();}})();
