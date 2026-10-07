// 鎖鎌: 長押しで分銅回転(周囲にダメージ)→離すと貫通投げ+一番奥の敵を引き寄せ
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const shots=[];
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;G.noStory=true;startGame('mitsu',null);for(let i=0;i<10;i++)stepGame();const pl=G.player;
 G.fighters=G.fighters.filter(f=>f.team===0&&f===pl);G.partner=null;pl.x=G.camx+300;pl.y=600;pl.face=1;pl.wpn={k:'kusari',uses:28};
 const mkE=(dx,dy)=>{const e=mk('spear',pl.x+dx,pl.y+dy,1);e.entered=true;e.hp=e.maxhp=500;e.cool=9999;e.face=-1;G.fighters.push(e);return e;};
 const near=mkE(90,0),line=[mkE(200,0),mkE(300,2),mkE(400,-2)];
 let hold=true;window.ctlKeys=()=>({atkH:hold,atkP:false});const out={};const imgs=[];
 for(let i=0;i<70;i++){stepGame();if(i===50){renderWorld&&renderWorld();imgs.push(ctx.canvas.toDataURL());}}
 out.spin=pl.kspin;out.nearDmg=500-near.hp;
 const far0=line[2].x;hold=false;
 for(let i=0;i<14;i++){stepGame();if(i===10){renderWorld();imgs.push(ctx.canvas.toDataURL());}}
 out.lineDmg=line.map(e=>500-e.hp);
 for(let i=0;i<20;i++){stepGame();if(i===6){renderWorld();imgs.push(ctx.canvas.toDataURL());}}
 out.farMoved=Math.round(far0-line[2].x);out.farDist=Math.round(line[2].x-pl.x);out.uses=pl.wpn&&pl.wpn.uses;out.state=pl.state;
 return {out,imgs};});
r.imgs.forEach((d,i)=>require('fs').writeFileSync(`/tmp/claude-0/-home-user-discord-monitor-bot/700bd5a1-9c8f-55df-81ff-13c1ce410a00/scratchpad/ks${i}.png`,Buffer.from(d.split(',')[1],'base64')));
console.log(r.out,er);await b.close();})();
