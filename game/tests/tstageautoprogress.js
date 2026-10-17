// Selected-stage automatic play through the actual waves, boss conversation and clear.
// No health, damage, wave or enemy-AI overrides; seeded RNG only for reproducibility.
const {chromium}=require('playwright'),fs=require('fs');
(async()=>{let b;const errors=[];try{
 const stageIndex=Number(process.argv[4]||0);const dir=process.env.OUT||(process.env.QA_OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006')+'/qa/stage-auto-progress';fs.mkdirSync(dir,{recursive:true});const rows=[];
 for(const hero of (process.argv[3]?[process.argv[3]]:['yuki','kage','mitsu','nobu','shin','musashi']))for(const mounted of [false,true]){
  b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});const p=await b.newPage({viewport:{width:802,height:360},isMobile:true});p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
  await p.evaluate(({hero,mounted,stageIndex})=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=false;G.autoPk=null;demoView.motion='auto';demoView.mounted=mounted;demoView.paused=false;G.lowq=true;AU.init();let seed=1729;Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};startAuto(hero,stageIndex);window.flowQA={ticks:0,events:[],last:'',bossSeen:false,conversationSeen:false,clearSeen:false,start:stageIndex,bosses:[],expectedBosses:G.waves.filter(w=>w.boss).map(w=>w.boss)};},{hero,mounted,stageIndex});
  let r;
  for(let chunk=0;chunk<60;chunk++){
   r=await p.evaluate(()=>{const q=window.flowQA;for(let i=0;i<1000&&G.stage===q.start&&G.mode!=='end';i++){G.t++;if(G.mode==='story')stepStory();else stepGame();q.ticks++;const key=[G.mode,G.state,G.wi,G.boss?.T.type||''].join(':');if(key!==q.last){q.events.push({t:q.ticks,key,x:Math.round(G.player.x),hp:G.player.hp,lives:G.lives});q.last=key;}if(G.mode==='story'&&G.story?.right&&G.boss)q.conversationSeen=true;if(G.boss){q.bossSeen=true;if(!q.bosses.includes(G.boss.T.type))q.bosses.push(G.boss.T.type);}if(G.state==='clear')q.clearSeen=true;}
    return{start:q.start,bosses:q.bosses,expectedBosses:q.expectedBosses,ticks:q.ticks,events:q.events,bossSeen:q.bossSeen,conversationSeen:q.conversationSeen,clearSeen:q.clearSeen,stage:G.stage,mode:G.mode,state:G.state,wave:G.wi,player:{x:G.player.x,y:G.player.y,state:G.player.state,hp:G.player.hp,weapon:G.player.wpn?.k||null},enemies:G.fighters.filter(f=>f.team===1&&f.hp>0).map(f=>({type:f.T.type,x:f.x,y:f.y,hp:f.hp,state:f.state}))};});
   fs.writeFileSync(dir+'/live.json',JSON.stringify({hero,mounted,...r},null,2));if(chunk%10===0)console.log(JSON.stringify({hero,mounted,chunk,ticks:r.ticks,state:r.state,wave:r.wave}));
   if(r.stage>stageIndex||r.mode==='end')break;
  }
 r.hero=hero;r.mounted=mounted;rows.push(r);fs.writeFileSync(dir+'/progress.json',JSON.stringify({rows,errors},null,2));console.log(JSON.stringify({hero,mounted,ticks:r.ticks,stage:r.stage,state:r.state,wave:r.wave,boss:r.bossSeen,conversation:r.conversationSeen,clear:r.clearSeen,enemies:r.enemies.length}));await b.close();b=null;
 }
 if(errors.length||rows.some(r=>(r.stage===r.start&&r.mode!=='end')||r.expectedBosses.some(b=>!r.bosses.includes(b))||!r.bossSeen||!r.conversationSeen||!r.clearSeen))process.exitCode=1;
 }finally{if(b)await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
