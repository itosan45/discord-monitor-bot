// 操作説明(チュートリアル)の更新: 「馬に乗る」の手順が入り、馬上で振り下ろし・騎馬突撃・旋風突撃を順に出す。その後の手順に馬が残らない。QA_OUTがあれば3場面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startHowto(()=>{});
  const idx=HT_STEPS.findIndex(s=>s.cap==='馬に乗る');const caps=HT_STEPS.map(s=>s.cap);const seen={whirl:false,mchg:false,matk:false,mountedAll:true};let nextMount=null,hits=0;
  const oh=window.hurt;window.hurt=function(t,a,d){if(a===G.player&&d&&G.ht&&HT_STEPS[G.ht.i]&&HT_STEPS[G.ht.i].cap==='馬に乗る')hits++;return oh(t,a,d);};
  let guard=0;while(G.ht.i<idx&&guard++<4000){stepHowto();}
  const shots=[];for(let i=0;i<260&&G.mode==='howto'&&G.ht.i===idx;i++){stepHowto();const c=G.player.cur;if(c===MWHIRL)seen.whirl=true;if(c===MCHG)seen.mchg=true;if(c===MATK||c===MATK1||c===MATK2||c===MATK3)seen.matk=true;if(G.ht.i===idx&&!G.player.mount)seen.mountedAll=false;if([14,70,156].includes(G.ht.t))shots.push(G.ht.t);}
  const after=G.ht.i;let mountAfter=null;if(G.mode==='howto'){stepHowto();mountAfter=!!G.player.mount;}
  return {idx,caps,seen,hits,after,mountAfter};});
 console.log(JSON.stringify(r));
 const bad=[];if(r.idx<0)bad.push('nostep');if(!r.seen.matk||!r.seen.mchg||!r.seen.whirl)bad.push('moves');if(!r.seen.mountedAll)bad.push('dismounted');if(r.hits<4)bad.push('hits'+r.hits);if(r.mountAfter)bad.push('mountLeft');
 if(process.env.QA_OUT){require('fs').mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [nm,tt] of [['ht_mount_a',14],['ht_mount_b',66],['ht_mount_c',156]]){await p.evaluate(tt=>{window.requestAnimationFrame=()=>0;startHowto(()=>{});const idx=HT_STEPS.findIndex(s=>s.cap==='馬に乗る');while(G.ht.i<idx)stepHowto();while(G.ht.t<tt&&G.ht.i===idx)stepHowto();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawOverlays();drawHowtoUI(HT_STEPS[G.ht.i],G.ht.t);},tt);await p.screenshot({path:`${process.env.QA_OUT}/${nm}.png`});}}
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
