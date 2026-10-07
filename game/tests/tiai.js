// 居合い: 刀の武将(景勝・信長・武蔵)で溜めて離すと、横一筋の線→線上の敵をまとめて斬る
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const OUT=process.env.OUTDIR||'.';
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;window.dropItem=()=>{};const res={},imgs=[];
 for(const h of['kage','nobu','musashi','yuki']){G.noStory=true;startGame(h,null);for(let i=0;i<10;i++)stepGame();const pl=G.player;
  G.fighters=G.fighters.filter(f=>f===pl);pl.x=G.camx+250;pl.y=600;pl.face=1;pl.inv=0;
  const es=[150,260,380,500].map((dx,i)=>{const e=mk('spear',pl.x+dx,pl.y+(i%2?6:-6),1);e.entered=true;e.hp=e.maxhp=500;e.cool=9999;e.face=-1;G.fighters.push(e);return e;});
  let hold=true;window.ctlKeys=()=>({atkH:hold});for(let i=0;i<50;i++)stepGame();hold=false;
  for(let i=0;i<40;i++){stepGame();G.t++;if(h==='kage'&&(i===10||i===26)){renderWorld();imgs.push(ctx.canvas.toDataURL());}}
  res[h]={dmg:es.map(e=>Math.round(500-e.hp)),iai:!!(pl.cur&&pl.cur.iai)||'done'};}
 return {res,imgs};});
r.imgs.forEach((d,i)=>require('fs').writeFileSync(OUT+`/iai${i}.png`,Buffer.from(d.split(',')[1],'base64')));
console.log(r.res,er);await b.close();})();
