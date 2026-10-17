// 2026-10-13 自動デモの主人公は強すぎるのか: 出荷状態(受けるダメージ15%・見切りあり)と、人の腕前に近い状態(ダメージ100%・見切りなし)で、
// 6人×6幕を実際のAIで最後(ボス撃破)まで動かし、死亡回数・受けたダメージ・かかった時間を比べる。合否ではなく計測のレポート。
// 使い方: node tdemodifficulty.js [url]  環境変数 HEROES=yuki,kage STAGES=0,1 RUNS=2 CAP=36000
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 const url=process.argv[2]||process.env.GAME_URL;const heroes=(process.env.HEROES||'yuki,kage,mitsu,nobu,shin,musashi').split(',');const stages=(process.env.STAGES||'0,1,2,3,4,5').split(',').map(Number);const RUNS=+(process.env.RUNS||1),CAP=+(process.env.CAP||36000);
 const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(url);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;});
 const rows=[];
 for(const cond of [{name:'出荷(15%・見切り有)',dmg:0.15,guard:true},{name:'人に近い(100%・見切り無)',dmg:1,guard:false}]){
  for(const ch of heroes)for(const si of stages)for(let run=0;run<RUNS;run++){
   const r=await p.evaluate(([ch,si,cond,CAP])=>{window.__demoDmg=cond.dmg;window.__demoGuard=cond.guard;window.__noGuard=false;
    G.mode='demo';G.curCh=ch;G.partnerType=null;startStage(si,ch,true);G.lowq=true;G.score=0;G.lives=99;G.titleT=-999999;G.banner=null;G.vo=null;G.noStory=true;const P=G.player;P.dm=1.4;
    let deaths=0,wasDead=false,taken=0,hp=P.hp,t0=G.t,bossT=null,steps=0,done='cap';
    for(steps=1;steps<=CAP;steps++){G.t++;stepGame();
     if(P.hp<hp)taken+=hp-P.hp;hp=P.hp;if(P.hp>=hp)hp=P.hp;
     const dead=P.state==='dead'||P.hp<=0;if(dead&&!wasDead)deaths++;wasDead=dead;if(G.boss&&bossT===null)bossT=steps;
     if(G.state==='bossdown'||G.state==='clear'){done='clear';break;}
     if(G.mode!=='demo'&&G.mode!=='play'){done='mode:'+G.mode;break;}}
    return {deaths,taken:Math.round(taken),sec:Math.round(steps/60),bossAt:bossT===null?null:Math.round(bossT/60),done,maxhp:P.maxhp};},[ch,si,cond,CAP]);
   rows.push(Object.assign({cond:cond.name,ch,stage:si+1,run},r));}}
 const agg={};for(const r of rows){const k=r.cond;(agg[k]=agg[k]||{runs:0,deaths:0,taken:0,sec:0,clear:0,hpPct:0});const a=agg[k];a.runs++;a.deaths+=r.deaths;a.taken+=r.taken;a.sec+=r.sec;a.clear+=r.done==='clear'?1:0;a.hpPct+=r.taken/r.maxhp;}
 for(const k in agg){const a=agg[k];a.deathsPerRun=+(a.deaths/a.runs).toFixed(2);a.avgTakenPctOfHP=+(a.hpPct/a.runs*100).toFixed(0);a.avgSec=Math.round(a.sec/a.runs);}
 console.log(JSON.stringify({agg,rows,errors}));await b.close();})().catch(e=>{console.error(e);process.exitCode=1;});
