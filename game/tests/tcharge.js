// 溜め攻撃が武器ごとに変わるか(居合・回転斬り・地割れ・溜め撃ち・三本矢・疾風・号令・突撃)
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const OUT=process.env.OUTDIR||'.';
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const C=[['kage',''],['yuki',''],['yuki','naginata'],['shin',''],['mitsu',''],['yuki','ono'],['yuki','teppo'],['yuki','yumi'],['nobu','odachi'],['musashi','konbou']];
const r=await p.evaluate((C)=>{window.requestAnimationFrame=()=>0;window.dropItem=()=>{};const res=[],imgs=[];
 for(const [h,w] of C){G.noStory=true;startGame(h,null);for(let i=0;i<10;i++)stepGame();const pl=G.player;
  G.fighters=G.fighters.filter(f=>f===pl);G.proj=[];pl.x=G.camx+300;pl.y=600;pl.face=1;pl.inv=0;pl.wpn=w?{k:w,uses:30}:null;
  const es=[-90,110,220,340].map((dx,i)=>{const e=mk('spear',pl.x+dx,pl.y+(i%2?6:-6),1);e.entered=true;e.hp=e.maxhp=500;e.cool=9999;e.face=-sgn(dx);G.fighters.push(e);return e;});
  let hold=true;window.ctlKeys=()=>({atkH:hold});for(let i=0;i<50;i++)stepGame();hold=false;let ck='';
  for(let i=0;i<45;i++){stepGame();if(i===2)ck=pl.cur&&(pl.cur.ck||(pl.cur.iai?'iai':pl.cur.chg?'rush':'?'));if(i===14){renderWorld();imgs.push(ctx.canvas.toDataURL('image/jpeg',0.7));}}
  res.push(h+(w?'+'+w:'')+' → '+ck+' 後ろ:'+Math.round(500-es[0].hp)+' 前:'+es.slice(1).map(e=>Math.round(500-e.hp)).join('/'));}
 return {res,imgs};},C);
r.imgs.forEach((d,i)=>require('fs').writeFileSync(OUT+`/ck${i}.jpg`,Buffer.from(d.split(',')[1],'base64')));
console.log(r.res.join('\n'),er);await b.close();})();
