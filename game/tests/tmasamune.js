// 2026-10-15 第七幕の途中に伊達政宗(仮の絵=最上義光)が遅れて駆けつける。オーナー「政宗OK、本体に七幕を入れて」
// ①既定で幕が7つ ②第七幕の波の途中(最後ではない)に政宗 ③登場の掛け合い(幸村は専用の返し、他の武将は「撃てぇ」) ④絵が読めている
// ⑤鉄砲隊を呼ぶ技がある ⑥倒すと「借りは大坂で」と言い、幕はクリアせず先へ進む ⑦Android相当の画面を保存
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const BASE=process.argv[2]||process.env.GAME_URL;const OUT=process.env.SHOT_DIR||'.';
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[],out={};
 try{for(const hero of ['yuki','nobu']){
  const p=await(await b.newContext({viewport:{width:915,height:412}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
  const r=await p.evaluate((hero)=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame(hero,null);startStage(6,hero,false);G.mode='play';G.diff=1;G.banner=null;G.story=null;
   const o={n:STG.length,waves:G.waves.map(w=>w.boss||'-').join(',')};const wi=G.waves.findIndex(w=>w.boss==='masamune');o.wi=wi;o.last=G.waves.length-1;
   G.wi=wi;G.camMax=G.waves[wi].x;G.camx=G.camMax;G.props=[];G.fighters=G.fighters.filter(f=>f.team===0);const P=G.player;P.hp=P.maxhp=99999;P.x=G.camx+380;P.y=570;window.ctlKeys=()=>({});
   const tick=n=>{for(let i=0;i<n;i++){P.hp=P.maxhp;G.t++;stepGame();}};tick(60);
   const m=G.fighters.find(f=>f.T.type==='masamune');o.spawn=!!m;o.name=m&&m.T.name;o.spr=m&&m.T.spr;o.sprReady=!!(SPR.boss2&&SPR.boss2.ready);o.volley=!!(m&&m.T.atk.some(a=>a.k==='volley'));
   for(let i=0;i<80&&G.banner;i++)tick(10);const s=[];for(let i=0;i<560;i++){tick(1);if(m.say&&!s.some(x=>x.s===m.say.s))s.push({who:'政宗',s:m.say.s});if(P.say&&!s.some(x=>x.s===P.say.s))s.push({who:'自機',s:P.say.s});}
   o.says=s;m.inv=99999;window.__m=m;return o;},hero);
  for(let i=0;i<3;i++)await p.evaluate(()=>{G.t++;stepGame();});
  await p.evaluate(()=>{const m=__m,P=G.player;m.x=P.x+220;m.y=P.y;m.say={s:'奥州より、ただいま参上！\n遅参の詫びは、その首で払おうぞ',t:120,d:120};frame();});
  await p.screenshot({path:`${OUT}/masamune_${hero}.png`});
  const k=await p.evaluate(()=>{const m=__m,P=G.player;m.inv=0;m.pinv=0;m.hp=1;hurt(m,P,{dmg:50,kb:2,pz:'thrust'});const said=m.say&&m.say.s;for(let i=0;i<200;i++){G.t++;stepGame();}return{said,state:G.state,wi:G.wi,boss:G.boss&&G.boss.T.type};});
  r.kill=k;r.errors=errors;out[hero]=r;
  if(r.n!==7)bad.push(hero+' 幕が7つでない');if(!(r.wi>0&&r.wi<r.last))bad.push(hero+' 政宗が途中の波にいない '+r.waves);
  if(!r.spawn||r.name!=='伊達政宗'||!r.sprReady)bad.push(hero+' 政宗が出ない/絵が無い');if(!r.volley)bad.push(hero+' 鉄砲隊の技が無い');
  const want=hero==='yuki'?['奥州より','真田か','六文銭']:['奥州より','百万石','撃てぇ'];for(const w of want)if(!r.says.some(x=>x.s.includes(w)))bad.push(hero+' セリフ無し '+w);
  if(!(k.said||'').includes('大坂'))bad.push(hero+' 倒したときのセリフ無し');if(k.state!=='run')bad.push(hero+' 政宗で幕が終わった '+k.state);
  if(errors.length)bad.push(hero+' エラー '+errors[0]);await p.context().close();}
 }catch(e){bad.push('例外 '+e.message);}
 console.log(JSON.stringify(out));if(bad.length){console.log('NG\n'+bad.join('\n'));process.exitCode=1;}else console.log('OK tmasamune');await b.close();})();
