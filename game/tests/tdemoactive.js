// 2026-10-12 自動デモの主人公: 溜め攻撃を積極的に出す・落ちている武器を戦闘中でも拾う・馬が出たら必ず乗る(馬なし設定でも)。
// 実際の波・敵AIのまま、乱数だけ固定して数千更新を流し、回数を数える。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const errors=[],rows=[];
 try{for(const [hero,stage] of [['yuki',0],['kage',1],['musashi',2],['nobu',3],['shin',4],['mitsu',5]]){
  const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
  const r=await p.evaluate(({hero,stage})=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;G.autoPk=null;demoView.motion='auto';demoView.mounted=false;demoView.paused=false;G.lowq=true;AU.init();let seed=4242+stage;Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
   startAuto(hero,stage);let charges=0,pick=0,mounts=0,wasMounted=false,wpnPick=0,whirls=0;const oc=startCharge,op=pickup;startCharge=function(pl){if(pl===G.player)charges++;return oc.apply(this,arguments);};pickup=function(pl,it){if(pl===G.player&&it.k.startsWith('w_'))wpnPick++;return op.apply(this,arguments);};
   const ticks=7000;let wave0=G.wi;for(let i=0;i<ticks&&G.mode!=='end'&&G.stage===stage;i++){G.t++;if(G.mode==='story')stepStory();else stepGame();const P=G.player;if(P){const m=!!P.mount;if(m&&!wasMounted)mounts++;wasMounted=m;if(P.state==='matk'&&P.cur&&P.st===1&&P.cur.whirl)whirls++;}}
   return {hero,stage,charges,wpnPick,mounts,wave:G.wi,from:wave0,stageNow:G.stage,hp:G.player&&G.player.hp};},{hero,stage});
  rows.push(r);await p.context().close();}
 }finally{await b.close();}
 console.log(JSON.stringify({rows,errors}));
 const tot=k=>rows.reduce((a,r)=>a+r[k],0),bad=[];if(tot('charges')<12)bad.push('charges '+tot('charges'));if(tot('wpnPick')<3)bad.push('wpnPick '+tot('wpnPick'));if(tot('mounts')<2)bad.push('mounts '+tot('mounts'));
 console.log(JSON.stringify({bad}));if(bad.length||errors.length)process.exitCode=1;})().catch(e=>{console.error(e);process.exitCode=1;});
