// 2026-10-12 必殺のカットイン(文字なしの細帯): 6人とも徒歩・馬上の必殺で出る・主人公本人だけ・44更新で消える・画面外へ出ない。QA_OUTで画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const rows=[];
  const CS=SPR.cutin;const used=new Set(),rects=[];const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(img===CS.img){used.add(a[0]+','+a[1]);if(a.length>=8)rects.push([a[4],a[5],a[6],a[7]]);}return od.call(this,img,...a);};
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const mounted of [false,true]){
   startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=null;P.x=G.camx+400;P.y=570;P.face=1;P.ki=300-1;
   if(mounted)P.mount={hp:6,max:6,col:'red'};
   used.clear();rects.length=0;
   if(mounted){updMount(P,{spcP:true});}else{startSpecial(P);}
   const has=!!G.cut&&!!G.cut.mine;let drawn=0,maxX=-1e9,minX=1e9,gone=-1;
   for(let i=0;i<60;i++){G.t++;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();if(rects.length>drawn){drawn=rects.length;}if(!G.cut&&gone<0)gone=i;}
   for(const q of rects){minX=Math.min(minX,q[0]);maxX=Math.max(maxX,q[0]+q[2]);}
   rows.push({hero,mounted,has,drawn,frames:used.size,minX:Math.round(minX),maxX:Math.round(maxX),gone});}
  // 相方の必殺では出さない
  startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const Q=mk('kage',G.player.x+200,570,0);Q.isPartner=true;Q.ki=300;G.fighters.push(Q);rects.length=0;startSpecial(Q);for(let i=0;i<20;i++){G.t++;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();}const partnerDrawn=rects.length;
  return {rows,partnerDrawn,W};});
 console.log(JSON.stringify(r));
 const bad=[];for(const o of r.rows){if(!o.has||o.drawn<30||o.frames<1||o.gone<40||o.gone>46||o.maxX>r.W+1||o.minX<-720)bad.push(o);}if(r.partnerDrawn)bad.push('partner');
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,hero,t] of [['yuki',"yuki",14],['kage','kage',22],['musashi','musashi',10]]){await p.evaluate(([hero,t])=>{startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=null;P.x=G.camx+400;P.y=570;P.face=1;P.ki=299;startSpecial(P);G.hitstop=0;G.flashT=0;G.cut.t=t;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();drawOverlays();},[hero,t]);await p.screenshot({path:`${process.env.QA_OUT}/cutin_${name}.png`});}}
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
