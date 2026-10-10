// オーナー録音のセリフ(bv ボス・ev 雑魚・pk 掛け声)の復号と、ゲーム内の割当てを確認。
// 登場時は喋らない・体力半分「なかなかやりおるわ」・連続被弾の振り払いは無言・起き上がりで「おのれ」・最期のセリフ→討ち取ったり
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
 await p.goto(process.env.GAME_URL||'http://127.0.0.1:8765/index.html');await p.mouse.click(640,360);await p.waitForTimeout(4000);
 const r=await p.evaluate(async()=>{
  AU.init();if(AU.ac.state==='suspended')await AU.ac.resume();for(let i=0;i<200&&!(AU.pkBuf&&AU.pkBuf.length>=6&&AU.bvBuf&&AU.bvBuf.masaka);i++)await new Promise(r=>setTimeout(r,50));
  const dur=Object.fromEntries(Object.entries(AU.bvBuf||{}).map(([k,v])=>[k,+v.duration.toFixed(2)]));
  const log=[];const ob=AU.bossLine.bind(AU),oe=AU.enemyLine.bind(AU),ov=AU.voice.bind(AU);AU.bossLine=(k,f,v)=>{log.push('b:'+k+'@'+G.stateT);return ob(k,f,v);};AU.enemyLine=(k,f,v)=>{const x=oe(k,f,v);if(x)log.push('e:'+k);return x;};AU.voice=k=>{log.push('vo@'+(G.state==='bossdown'?G.stateT:'mid'));return ov(k);};
  // 掛け声
  AU.lastKi=0;AU.kiai({T:{type:'yuki'}},true);const pk1=AU.lastPk;AU.lastKi=0;AU.kiai({T:{type:'yuki'}},true);const pk2=AU.lastPk;
  // 雑魚の断末魔
  const zm=AU.enemyLine('munen',{x:G.camx+640});
  return {dur,pk:AU.pkBuf.length,ev:Object.keys(AU.evBuf||{}),pkFin:[pk1,pk2],zm,log};
 });
 // 最終ボス戦: 登場→半分→連続被弾→撃破(stepGame で決定的に進める)
 const g=await p.evaluate(async()=>{window.requestAnimationFrame=()=>0;G.noStory=true;startGame('yuki',null);G.demo=false;
  const log=[];const ob=AU.bossLine.bind(AU),ov=AU.voice.bind(AU);AU.bossLine=(k,f,v)=>{log.push('b:'+k+'@'+(G.state==='bossdown'?G.stateT:'run'));return ob(k,f,v);};AU.voice=k=>{log.push('vo@'+(G.state==='bossdown'?G.stateT:'mid'));return ov(k);};
  G.wi=G.waves.length-1;G.fighters=G.fighters.filter(f=>f.team!==1);const P=G.player;const e=spawnEn('boss1',1);e.x=P.x+220;e.y=P.y;
  await new Promise(r=>setTimeout(r,900));
  G.banner=null;e.inv=0;e.hp=e.maxhp*0.45;for(let i=0;i<3;i++)stepGame();
  for(let i=0;i<7;i++){e.inv=0;e.state='idle';e.hp=Math.max(e.hp,e.maxhp*0.3);hurt(e,P,{dmg:1,kb:0});stepGame();}
  const shakeLog=log.slice();
  // 倒されて起き上がる時に「おのれ」(乱数を固定: 40%で言わない判定を通す)
  const mr=Math.random;Math.random=()=>0.5;e.state='down';e.st=0;e.z=0;e.vz=0;e.lieT=0;e.inv=0;for(let i=0;i<60&&e.state!=='getup';i++)stepGame();Math.random=mr;
  for(let i=0;i<40;i++)stepGame();
  e.inv=0;e.hp=1;e.state='idle';hurt(e,P,{dmg:99,kb:4});G.slow=0;G.banner=null;
  let n=0;while(G.state==='bossdown'&&n<400){stepGame();n++;}
  return {log,shakeLog,voAt:G.voAt,state:G.state};
 });
 console.log(JSON.stringify({r,g,errors:er}));await b.close();
 const L=g.log.join(' ');const voT=+((g.log.find(x=>x.startsWith('vo@'))||'vo@-1').slice(3));
 const ok=!er.length&&r.pk===6&&r.ev.length===2&&r.pkFin.every(i=>i===2||i===3)&&r.zm&&!/b:kirisute@run.*b:nakanaka/.test(L)&&!g.log[0].startsWith('b:kirisute')&&/b:nakanaka/.test(L)&&!g.shakeLog.some(x=>x.startsWith('b:onore'))&&/b:onore/.test(L)&&/b:(masaka|migoto)/.test(L)&&voT>=g.voAt&&g.voAt>54;
 if(!ok){console.log('NG');process.exit(1);}console.log('OK');
})();
