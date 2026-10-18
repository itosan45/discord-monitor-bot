// 画像のステージ別読み込み: 全画像モードにせず(sprAllReady を呼ばない)、6人×6ステージを自動で遊ばせ、
// ボス戦・騎乗・拾得武器・必殺/奥義・勝鬨まで描画して、予定外に使われた画像(G.sprMiss)が無いことと、展開後の大きさを確かめる。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');
 await p.waitForFunction(()=>typeof sprWantReady==='function'&&sprWantReady(),null,{timeout:60000});
 const boot=await p.evaluate(()=>({mb:sprMB(),all:SPR_ALL}));
 const heroes=['yuki','kage','mitsu','nobu','shin','musashi'],rows=[],bad=[];
 for(let si=0;si<6;si++)for(let hi=0;hi<6;hi++){const hero=heroes[(hi+si)%6],pk=heroes[(hi+si+1)%6];
  const r=await p.evaluate(async([si,hero,pk])=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;G.sprMiss=[];
   const wait=async()=>{for(let i=0;i<600&&!sprWantReady();i++)await new Promise(r=>setTimeout(r,25));return sprWantReady();};
   startGame(hero,pk);startStage(si,hero,false);const ok1=await wait();const mbStage=sprMB();window.ctlKeys=()=>demoCtl(G.player);
   const draw=()=>{renderWorld();drawHUD();};
   for(let i=0;i<900;i++){stepGame();if(i%15===0)draw();}
   // 拾得武器と騎乗と必殺・奥義
   const f=G.player;for(const k of ['kusari','teppo','yumi','odachi']){f.wpn={k,uses:99};for(let i=0;i<40;i++){stepGame();if(i%10===0)draw();}}
   f.wpn=null;if(typeof setDemoMount==='function'){f.mount={hp:6,max:6,col:'red'};for(let i=0;i<60;i++){stepGame();if(i%10===0)draw();}f.mount=null;}
   f.ki=200;startSpecial(f);for(let i=0;i<120;i++){stepGame();if(i%8===0)draw();}
   f.ki=300;startSpecial(f);for(let i=0;i<260;i++){stepGame();if(i%8===0)draw();}
   // ボス戦から勝鬨まで
   const L=LV[si],bs=L.waves.filter(w=>w.boss).map(w=>w.boss);
   for(const bt of bs){G.state='run';G.waves=[{x:G.camx+40,en:[],boss:bt}];G.wi=0;G.waveOn=false;G.camMax=G.camx+40;for(let i=0;i<1600;i++){stepGame();if(i%15===0)draw();if(G.state!=='run'&&G.state!=='bossdown')break;}}
   for(let i=0;i<700;i++){stepGame();if(i%12===0)draw();}
   return {ok1,mbStage,mbEnd:sprMB(),miss:[...new Set(G.sprMiss)],mode:G.mode,state:G.state};},[si,hero,pk]);
  rows.push({si,hero,pk,...r});if(!r.ok1||r.miss.length)bad.push({si,hero,miss:r.miss,ok1:r.ok1});}
 const maxMB=Math.max(...rows.map(r=>Math.max(r.mbStage,r.mbEnd)));
 console.log(JSON.stringify({boot,maxMB,rows:rows.map(r=>[r.si,r.hero,r.pk,r.mbStage,r.mbEnd,r.miss.join(',')]),bad,errors}));
 if(bad.length||errors.length||maxMB>150)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
