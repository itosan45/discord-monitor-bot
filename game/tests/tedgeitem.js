// 画面の左右の端に落ちた拾得品(武器・食べ物)が、主人公6人とも拾える位置へ寄ってくる。長い武器の幸村は端の余白が大きいので特に確認する
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const rows=[];
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const side of [-1,1])for(const k of ['w_odachi','onigiri']){
   startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=null;P.hp=Math.round(P.maxhp*0.5);P.inv=999;P.x=G.camx+640;P.y=570;
   const x0=side<0?G.camx+8:G.camx+W-8;G.items.push({k,x:x0,y:570,t:0});const it=G.items[0];
   for(let i=0;i<90;i++){G.t++;stepGame();}
   const edge=fighterScreenMargin(P),reachable=it.x>=G.camx+edge-48&&it.x<=G.camx+W-edge+48;
   P.x=clamp(it.x,G.camx+edge,G.camx+W-edge);P.y=570;P.z=0;P.state='idle';P.cur=null;P.aT=G.t;let got=false;
   for(let i=0;i<4&&!got;i++){P.aT=G.t;G.t++;stepGame();got=!G.items.includes(it);}
   rows.push({hero,side,k,reachable,got,x:Math.round(it.x-G.camx)});}
  return rows;});
 const bad=r.filter(o=>!o.reachable||!o.got);console.log(JSON.stringify({n:r.length,bad:bad.slice(0,6),errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
