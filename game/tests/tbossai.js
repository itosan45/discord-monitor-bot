// ボスの行動(ガード・飛び退き・連続技・振り払い・弓の距離取り)が出るか
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;window.dropItem=()=>{};const out={};
 const oA=startEAct,oB=startEAtk;let log;window.startEAct=(e,d)=>{if(e.T.boss)log[d===BGUARD?'ガード':d===BSTEP?'飛び退き':'振り払い']++;return oA(e,d);};
 window.startEAtk=(e,i)=>{if(e.T.boss){log.技++;if(e.comboN)log.連続++;}return oB(e,i);};
 for(const bt of['boss1','boss2','boss3','boss4','boss5','boss7','boss8','boss9']){log={ガード:0,飛び退き:0,振り払い:0,技:0,連続:0};
  G.noStory=true;startGame('kage',null);startStage(0,'kage',false);G.waves=[{x:50,en:[],boss:bt}];G.wi=0;G.camMax=50;window.ctlKeys=()=>demoCtl(G.player);
  G.player.hp=G.player.maxhp=99999;let dist=0,n=0,boss=null,t=0;
  for(;t<4000;t++){stepGame();G.t++;boss=boss||G.fighters.find(f=>f.T.boss);if(boss&&boss.hp>0){dist+=Math.abs(boss.x-G.player.x);n++;}if(boss&&boss.hp<=0)break;}
  out[bt]=Object.assign({},log,{平均距離:Math.round(dist/Math.max(1,n)),撃破まで:t});}
 return out;});
console.log(r,er);await b.close();})();
