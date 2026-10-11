// 必殺・奥義のズームイン: 6人×必殺(Lv1/Lv2)と奥義(Lv3)で、発動中は拡大し(1.2倍以上)、終わると元の1.0倍へ戻る。画面端でも本人が画面内に収まる。QA_OUTがあれば拡大中の画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const rows=[];
  const setup=(hero,lv,edge)=>{startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.x=edge===0?G.camx+640:edge<0?G.camx+60:G.camx+W-60;P.y=570;P.face=1;P.inv=999;P.ki=lv===3?300:lv===2?200:100;P.spLv=undefined;
   const e=mk('sword',P.x+120,575,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);return P;};
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const [lv,edge] of [[1,0],[2,0],[3,0],[1,-1],[1,1]]){
   const P=setup(hero,lv,edge);G.t++;updPlayer(P,{spcP:true});let mx=1,inScene=0,frames=0;
   for(let i=0;i<260;i++){G.t++;stepGame();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();if(G.spcScene||G.ult){inScene++;mx=Math.max(mx,G.zm);}if(!G.spcScene&&!G.ult&&G.state==='run'&&inScene>0)frames++;if(frames>40)break;}
   rows.push({hero,lv,edge,mx:+mx.toFixed(2),inScene,end:+(G.zm||1).toFixed(3)});}
  return rows;});
 const bad=r.filter(o=>o.inScene<5||o.mx<1.2||o.end>1.02);console.log(JSON.stringify({n:r.length,sample:r.slice(0,4),bad:bad.slice(0,6),errors}));
 if(process.env.QA_OUT){require('fs').mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [nm,hero,lv,edge,wait] of [['zoom_yuki_sp','yuki',1,0,10],['zoom_musashi_edge','musashi',2,-1,10],['zoom_nobu_ult','nobu',3,0,70]]){await p.evaluate(([hero,lv,edge,wait])=>{window.requestAnimationFrame=()=>0;startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.x=edge<0?G.camx+60:G.camx+640;P.y=570;P.face=1;P.inv=999;P.ki=lv===3?300:lv===2?200:100;const e=mk('sword',P.x+130,575,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);G.t++;updPlayer(P,{spcP:true});for(let i=0;i<wait;i++){G.t++;stepGame();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();}ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();},[hero,lv,edge,wait]);await p.screenshot({path:`${process.env.QA_OUT}/${nm}.png`});}}
 if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
