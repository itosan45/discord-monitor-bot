// 主人公とボスが同じ列で重ならないこと(体の幅ぶん押し出す)・押し出しても撃破できること・ボスのセリフが喋りすぎないことを、自動プレイのボス戦で確認
// 重なり: ボスの突進がすり抜ける一瞬などは許し、ボスと同じ列にいるフレームの1%未満であること。撃破のセリフは1回だけ、「切り捨ててくれるわ」は「おのれ」の後にしか出ないこと
// 押し出し後に同じフレームで数ピクセル動く分(見た目に影響しない)は許す: 体の幅より6px以上めり込んだ時だけ重なりとして数える
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const heroes=(process.env.HEROES||'yuki,kage,mitsu,nobu,shin,musashi').split(','),bosses=(process.env.BOSSES||'boss1,boss2,boss3').split(','),rows=[];
 for(const hero of heroes)for(const bt of bosses){
  const r=await p.evaluate(([hero,bt])=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame(hero,null);G.auto=true;G.lives=99;
   const lines={};const ob=AU._bl0||(AU._bl0=AU.bossLine.bind(AU));AU.bossLine=(k,f,v)=>{lines[k]=(lines[k]||0)+1;return ob(k,f,v);};
   G.wi=G.waves.length-1;G.waveOn=true;G.fighters=G.fighters.filter(f=>f.team!==1);const P=G.player;const e=spawnEn(bt,1);e.x=P.x+260;e.y=P.y;G.banner=null;
   const gap=typeof bodyGap==='function'?bodyGap(e):40*(e.sc||1);let ov=0,near=0,n=0,res='timeout',hits=0,last=e.hp;
   for(let i=0;i<20000;i++){G.t++;stepGame();n++;if(G.banner&&G.banner.boss)G.banner=null;if(e.hp<last){hits++;last=e.hp;}
    for(const h of G.fighters)if(h.team===0&&h.hp>0&&e.hp>0&&!['spc','ult','mspc','grab','throw','mega','down','dead'].includes(h.state)&&e.state!=='down'&&e.state!=='dead'&&h.z<=5&&e.z<=5&&Math.abs(h.y-e.y)<24){near++;if(Math.abs(h.x-e.x)<gap-6)ov++;}
    if(e.hp<=0||G.state==='bossdown'||G.state==='clear'){res='kill';break;}if(G.state==='continue'||G.state==='over'){res=G.state;break;}}
   return {hero,boss:bt,res,frames:n,sec:+(n/60).toFixed(1),ov,near,hits,push:G.bossPushN||0,lines};},[hero,bt]);
  rows.push(r);console.error(JSON.stringify(r));}
 const ov=rows.reduce((s,r)=>s+r.ov,0),near=rows.reduce((s,r)=>s+r.near,0),bad=rows.filter(r=>r.res!=='kill');
 console.log(JSON.stringify({ov,near,bad:bad.map(r=>r.hero+'/'+r.boss+':'+r.res),avgSec:+(rows.reduce((s,r)=>s+r.sec,0)/rows.length).toFixed(1),errors}));
 if(errors.length||bad.length||rows.some(r=>(r.lines.masaka||0)+(r.lines.migoto||0)!==1||(r.lines.kirisute||0)>(r.lines.onore||0))||(process.env.EXPECT_OV!=='any'&&ov>near*0.01))process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
