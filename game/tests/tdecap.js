// 会心の一撃で倒すと首(流血オフなら兜)が飛ぶ
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const OUT=process.env.OUTDIR||require('os').tmpdir();
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;window.dropItem=()=>{};const res=[],imgs=[];const R0=Math.random;
 for(const blood of [true,false])for(const t of['spear','sword','archer','gun','samurai']){G.noStory=true;startGame('kage',null);G.blood=blood;for(let i=0;i<5;i++)stepGame();const pl=G.player;
  G.fighters=G.fighters.filter(f=>f===pl);G.parts=[];pl.x=G.camx+300;pl.y=600;pl.face=1;
  const e=mk(t,pl.x+70,pl.y,1);e.entered=true;e.hp=1;e.cool=9999;e.face=-1;G.fighters.push(e);
  Math.random=()=>0.01;hurt(e,pl,{dmg:10,kb:3});Math.random=R0;
  const ok=!!e.decap,row=[];
  for(let i=0;i<60;i++){stepGame();G.t++;if([3,14,28,50].includes(i)){renderWorld();row.push(ctx.getImageData(pl.x-G.camx-60,300,520,330));}}
  const head=G.parts.find(q=>q.k==='head');res.push(t+(blood?' 流血':' 流血オフ')+': 首飛び='+ok+(head?' 頭の位置z='+Math.round(head.z):''));
  if(t==='spear'||t==='samurai'){const c=document.createElement('canvas');c.width=520*4;c.height=330;const x=c.getContext('2d');row.forEach((d,i)=>x.putImageData(d,i*520,0));imgs.push(c.toDataURL('image/jpeg',0.8));}}
 return {res,imgs};});
r.imgs.forEach((d,i)=>require('fs').writeFileSync(OUT+`/decap${i}.jpg`,Buffer.from(d.split(',')[1],'base64')));
console.log(r.res.join('\n'),er);await b.close();})();
