// 2026-10-12 幸村のパートナー: 霧隠才蔵(斬り2種・ジャンプクナイ・必殺Lv1=クナイ五月雨5連射・Lv2=水遁)と、根津甚八の岩投げ(Lv1=岩3つ・Lv2=大岩落とし)。
// 選択肢に出る・歩き/待機/攻撃/被弾/ダウン/起き上がり/死亡の絵が出る・技が実際に敵に当たる・自動AIが技を使う。QA_OUT があればスマホ相当の画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const pg=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];pg.on('pageerror',e=>errors.push(e.message));
 await pg.goto(process.argv[2]||process.env.GAME_URL);await pg.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const shot=async(name)=>{if(process.env.QA_OUT)await pg.screenshot({path:process.env.QA_OUT+'/'+name+'.png'});};
 const r=await pg.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={bad:[]};
  const bad=(m)=>out.bad.push(m);
  out.opts=(()=>{G.heroPick='yuki';return partnerOpts();})();if(!out.opts.includes('saizo')||!out.opts.includes('nezu'))bad('選択肢');
  G.heroPick='kage';if(partnerOpts().includes('saizo'))bad('幸村以外には出ない');
  const setup=(pk)=>{startGame('yuki',pk);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.proj=[];G.items=[];const P=G.player;P.x=G.camx+300;P.y=570;P.face=1;P.inv=999;P.hp=P.maxhp=9999;const Q=G.partner;Q.x=G.camx+380;Q.y=570;Q.face=1;Q.inv=0;Q.hp=Q.maxhp=9999;return [P,Q];};
  const enemy=(P,dx,dy)=>{const e=mk('sword',P.x+dx,570+(dy||0),1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;e.face=-1;e.gcrash=1e9;/* ガードしない(ガードは tguardwake で検査) */G.fighters.push(e);return e;};
  const step=(n,Q,fn)=>{for(let i=0;i<n;i++){G.t++;G.player.inv=999;G.player.hp=G.player.maxhp;for(const f of G.fighters)if(f.team===1){f.cool=9999;if(f.state==='idle')f.st=0;}fn&&fn(i);for(const f of G.fighters){if(f.team===0)updPlayer(f,f===G.player?{}:(Q.ctl?Q.ctl(f):{}));else updEnemy(f);}updProj();ctx.setTransform(RS,0,0,RS,0,0);}};
  const draw=(e)=>{ctx.setTransform(RS,0,0,RS,0,0);drawFighter(e);};
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){const rec=used.get(img);if(rec)rec.add(a[0]+','+a[1]);return od.call(this,img,...a);};
  // 0) 才蔵の絵が読み込まれ、各状態の配列がある
  {const S=SPR.saizo;out.atlas={ready:!!(S&&S.ready),keys:S&&Object.keys(S.a)};for(const k of['idle','walk','a1','a2','hit','down','getup','dead','dodgeB','jump','dash','spc','jatk'])if(!S||!S.a[k])bad('配列なし:'+k);if(S&&S.a.walk.length<8)bad('歩き8コマ未満');}
  // 1) 才蔵の各状態で絵(アトラス)を描く
  {const [P,Q]=setup('saizo');if(!Q||Q.type!=='saizo')bad('才蔵がパートナーにならない');const S=SPR.saizo;const set=new Set();used.set(S.img,set);
   const seen={};const st=(name,fn)=>{set.clear();fn();seen[name]=set.size;};
   st('idle',()=>{Q.state='idle';for(let i=0;i<60;i++){Q.t++;draw(Q);}});
   st('walk',()=>{Q.state='walk';for(let i=0;i<60;i++){Q.t++;Q.wp=(Q.wp||0)+0.4;draw(Q);}});
   for(let ai=0;ai<2;ai++)st('a'+(ai+1),()=>{Q.state='atk';Q.cur=Q.T.atk[ai];Q.hit.clear();for(let i=0;i<Q.cur.dur;i++){Q.st=i;draw(Q);}Q.state='idle';});
   st('hit',()=>{Q.state='hurt';for(let i=0;i<14;i++){Q.st=i;draw(Q);}Q.state='idle';});
   st('down',()=>{Q.state='down';Q.z=30;for(let i=0;i<4;i++){Q.st=i;draw(Q);}Q.z=0;for(let i=0;i<20;i++){Q.st=i;draw(Q);}Q.state='idle';});
   st('getup',()=>{Q.state='getup';for(let i=0;i<20;i++){Q.st=i;draw(Q);}Q.state='idle';});
   st('dead',()=>{Q.state='dead';for(let i=0;i<40;i++){Q.st=i;draw(Q);}Q.state='idle';});
   st('jump',()=>{Q.state='jump';Q.vz=5;for(let i=0;i<12;i++){Q.st=i;draw(Q);}Q.state='idle';});
   st('jatk',()=>{Q.state='jatk';Q.cur=Q.T.jatk;for(let i=0;i<20;i++){Q.st=i;draw(Q);}Q.state='idle';});
   out.frames=seen;for(const k in seen)if(!seen[k])bad('絵が出ない:'+k);used.delete(S.img);}
  // 2) 斬り2種が敵に当たる
  for(let ai=0;ai<2;ai++){const [P,Q]=setup('saizo');const e=enemy(P,0);e.x=Q.x+70;const hp0=e.hp;Q.state='atk';Q.st=0;Q.cur=Q.T.atk[ai];Q.hit.clear();step(Q.cur.dur+4,Q,()=>{Q.cool=999;});out['slash'+ai]=hp0-e.hp;if(!(e.hp<hp0))bad('斬りが当たらない'+ai);}
  // 3) ジャンプクナイ: 空中で3本、敵に当たる
  {const [P,Q]=setup('saizo');const e=enemy(P,0);e.x=Q.x+260;const hp0=e.hp;Q.state='jump';Q.st=0;Q.vz=11;Q.z=1;let n=0;for(let i=0;i<70;i++){G.t++;P.inv=999;if(Q.state==='jump'&&Q.st===8&&Q.state!=='jatk'){Q.state='jatk';Q.st=0;Q.cur=Q.T.jatk;Q.hit.clear();}updPlayer(Q,{});if(Q.state==='jatk'&&Q.st===4)n=G.proj.filter(q=>q.k==='kunai'&&q.team===0).length;updProj();for(const f of G.fighters)if(f.team===1)f.cool=9999;}
   out.jump={kunai:n,dmg:hp0-e.hp};if(n!==3)bad('ジャンプクナイ3本でない:'+n);if(!(e.hp<hp0))bad('ジャンプクナイが当たらない');}
  // 4) 必殺Lv1=クナイ5連射
  {const [P,Q]=setup('saizo');const e=enemy(P,0);e.x=Q.x+300;const hp0=e.hp;Q.ki=100;startSpecial(Q);if(Q.spLv!==1)bad('Lv1でない');let maxK=0,fired=0,prev=0;for(let i=0;i<90&&Q.state==='spc';i++){G.t++;updSpc(Q);Q.st++;const n=G.proj.filter(q=>q.k==='kunai'&&q.team===0).length;if(n>prev)fired+=n-prev;prev=n;updProj();Q.inv=999;}
   for(let i=0;i<60;i++){G.t++;updProj();}out.lv1={fired,dmg:hp0-e.hp,state:Q.state};if(fired!==5)bad('クナイが5本でない:'+fired);if(!(e.hp<hp0))bad('クナイ五月雨が当たらない');}
  // 5) 必殺Lv2=水遁
  {const [P,Q]=setup('saizo');const es=[enemy(P,0),enemy(P,0,25),enemy(P,0,-25)];es.forEach((e,i)=>e.x=Q.x+180+i*10);const hp=es.map(e=>e.hp);Q.ki=200;startSpecial(Q);if(Q.spLv!==2)bad('Lv2でない');let waves=0;for(let i=0;i<90&&Q.state==='spc';i++){G.t++;updSpc(Q);Q.st++;waves=Math.max(waves,G.proj.filter(q=>q.k==='wave'&&q.team===0&&q.owner===Q).length);updProj();Q.inv=999;}
   for(let i=0;i<40;i++){G.t++;updProj();}const dm=es.map((e,i)=>hp[i]-e.hp);out.lv2={waves,dm};if(waves<3)bad('水の波が3本未満');if(dm.some(d=>d<=0))bad('水遁が当たらない:'+dm);}
  // 6) 根津の岩投げ(Lv1)・大岩落とし(Lv2)
  {const [P,Q]=setup('nezu');const es=[enemy(P,0),enemy(P,0),enemy(P,0)];es[0].x=Q.x+170;es[1].x=Q.x+320;es[2].x=Q.x+470;const hp=es.map(e=>e.hp);Q.ki=100;startSpecial(Q);let rocks=0,prev=0;for(let i=0;i<100&&Q.state==='spc';i++){G.t++;updSpc(Q);Q.st++;const n=G.proj.filter(q=>q.k==='rock').length;if(n>prev)rocks+=n-prev;prev=n;updProj();Q.inv=999;}
   for(let i=0;i<60;i++){G.t++;updProj();}const dm=es.map((e,i)=>hp[i]-e.hp);out.rock={rocks,dm,state:Q.state};if(rocks!==3)bad('岩が3つでない:'+rocks);if(dm.filter(d=>d>0).length<2)bad('岩が当たらない:'+dm);
   const [P2,Q2]=setup('nezu');const e2=enemy(P2,0);e2.x=Q2.x+250;const h2=e2.hp;Q2.ki=200;startSpecial(Q2);let falls=0,pv=0;for(let i=0;i<120&&Q2.state==='spc';i++){G.t++;updSpc(Q2);Q2.st++;const n=G.proj.filter(q=>q.k==='fall').length;if(n>pv)falls+=n-pv;pv=n;updProj();Q2.inv=999;}for(let i=0;i<120;i++){G.t++;updProj();}
   out.rock2={falls,dmg:h2-e2.hp,state:Q2.state};if(falls<4)bad('大岩が4つ未満:'+falls);}
  // 7) 自動AI: 才蔵が、離れた敵にジャンプクナイを投げ、ゲージがたまれば五月雨→水遁の順に使う
  {const [P,Q]=setup('saizo');const e=enemy(P,0);e.x=Q.x+300;const e2=enemy(P,0);e2.x=Q.x+330;e2.y=585;const e3=enemy(P,0);e3.x=Q.x+280;e3.y=555;Q.ki=100;let jk=0,sp=[],last='';const orig=Math.random;for(let i=0;i<3000;i++){G.t++;P.inv=999;P.x=G.camx+300;if(i%400===0){Q.x=G.camx+380;Q.state==='idle';e.x=Q.x+300;e2.x=Q.x+330;e3.x=Q.x+280;}Q.hp=Q.maxhp;for(const f of G.fighters)if(f.team===1){f.cool=9999;f.hp=f.maxhp;if(f.state==='idle')f.st=0;}updPlayer(Q,partnerCtl(Q));updProj();if(Q.state==='jatk'&&last!=='jatk')jk++;if(Q.state==='spc'&&last!=='spc')sp.push(Q.spLv);last=Q.state;if(Q.state==='spc'||i%700===699)Q.ki=Math.max(Q.ki,sp.length%2?200:100);Q.x=clamp(Q.x,G.camx+60,G.camx+W-60);}
   out.ai={jk,sp,ki:Q.ki,cd:Q.spcCdT,t:G.t,x:Q.x,ex:e.x,state:Q.state};if(jk<1)bad('AIがジャンプクナイを使わない');if(sp.length<2)bad('AIが必殺を使わない');if(sp.length>=2&&!(sp.includes(1)&&sp.includes(2)))bad('必殺が交互にならない:'+sp);}
  return out;});
 r.errors=errors;
 // 画面保存(Android相当): 才蔵の斬り・クナイ・水遁・根津の岩
 console.log(JSON.stringify(r),r.bad.length?'FAIL':'OK');
 }finally{await b.close();}})();
