// 必殺ゲージ: 必殺技・奥義のダメージでは増えない/通常攻撃と被ダメージで増える
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;window.dropItem=()=>{};const o={};
 for(const h of['yuki','kage','mitsu','nobu','shin','musashi']){G.noStory=true;startGame(h,null);for(let i=0;i<10;i++)stepGame();const pl=G.player;
  const foes=()=>{G.fighters=G.fighters.filter(f=>f.team===0);for(let i=0;i<5;i++){const e=mk('spear',pl.x+50+i*25,pl.y,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;e.face=-1;G.fighters.push(e);}};
  foes();window.ctlKeys=()=>({});
  pl.ki=200;pl.inv=0;startSpecial(pl);const hp0=G.fighters.filter(f=>f.team===1).reduce((a,f)=>a+f.hp,0);for(let i=0;i<160;i++)stepGame();const sp=pl.ki,spd=hp0-G.fighters.filter(f=>f.team===1).reduce((a,f)=>a+f.hp,0);
  foes();pl.ki=300;startUlt(pl);for(let i=0;i<400;i++){stepGame();if(!G.ult)break;}const ul=pl.ki;
  foes();pl.ki=0;pl.state='idle';startPAtk&&startPAtk(pl,0);for(let i=0;i<40;i++)stepGame();const at=pl.ki;
  pl.ki=0;pl.inv=0;pl.state='idle';const e=G.fighters.find(f=>f.team===1);hurt(pl,e,{dmg:10,kb:2});const hu=pl.ki;
  o[h]={必殺で与えたダメージ:Math.round(spd),必殺後:Math.round(sp),奥義後:Math.round(ul),通常攻撃:Math.round(at),被弾:Math.round(hu)};}
 return o;});
console.log(r,er);await b.close();})();
