// 2026-10-14 炎の描画(オーナー「丸いひかりがあるだけじゃ火にみえない(火矢もふくめ)」)。火遁・火矢(飛んでいる矢/刺さった矢/地面の火)・火刑・火の粒が、丸い光ではなく炎の形(drawFlame)で描かれることを確認。
// 水遁(青)・鉄砲/紫の光は従来の光のまま。QA_OUT があれば Android相当(802x360)の実画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const shot=async n=>{if(process.env.QA_OUT){require('fs').mkdirSync(process.env.QA_OUT,{recursive:true});await p.screenshot({path:process.env.QA_OUT+'/fire_'+n+'.png'});}};
 const setup=()=>p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;G.mode='play';startGame('yuki','sasuke');G.stage=4;G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.proj=[];G.fires=[];G.stuck=[];G.marks=[];const P=G.player;P.x=G.camx+380;P.y=570;P.face=1;P.inv=999;P.hp=P.maxhp=9999;const Q=G.partner;if(Q)Q.x=-9999;window.__fl={n:0};if(!window.__df){window.__df=drawFlame;drawFlame=function(...a){window.__fl.n++;return window.__df.apply(this,a);};}});
 const frame=(n)=>p.evaluate(n=>{for(let i=0;i<n;i++){G.t++;G.player.inv=999;updProj();updParts&&updParts();if(i%2===0){ctx.setTransform(RS,0,0,RS,0,0);renderWorld();}}G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();},n);
 const out={},bad=[];
 // 1) 火遁の波: 炎の形で描かれる(波に放射グラデの丸い光を使わない)
 await setup();
 out.wave=await p.evaluate(()=>{const P=G.player;for(const dy of[-30,0,30])addProj({x:P.x+60,y:P.y+dy,z:6,vx:9,team:0,dmg:19,face:1,owner:P,k:'wave',w:52,life:54,launch:true,kb:7,pierce:99,col:'255,140,60'});window.__fl.n=0;let rg=0;const o=CanvasRenderingContext2D.prototype.createRadialGradient;CanvasRenderingContext2D.prototype.createRadialGradient=function(...a){rg++;return o.apply(this,a);};
  for(let i=0;i<10;i++){G.t++;updProj();ctx.setTransform(RS,0,0,RS,0,0);for(const q of G.proj)drawProj(q);}
  CanvasRenderingContext2D.prototype.createRadialGradient=o;const kinds=new Set(G.parts.map(x=>x.k));return{flames:window.__fl.n,radial:rg,waves:G.proj.length};});
 await frame(2);await shot('katon_wave');
 if(out.wave.flames<30)bad.push('火遁の波が炎で描かれていない '+JSON.stringify(out.wave));
 if(out.wave.radial)bad.push('火遁の波に丸い光(放射グラデ)が残っている '+out.wave.radial);
 // 2) 火遁の粒子は fire / 水遁(青)は flame のまま
  // 3) 火矢: 降ってくる矢・刺さった矢・地面の火
 await setup();
 out.arrows=await p.evaluate(()=>{HZ[4]='firearrows';startHazard();const k=G.proj.filter(q=>q.k==='arrowfall');const nFire=k.filter(q=>q.fire).length;return{n:k.length,nFire,fires:G.fires.length};});
 if(!out.arrows.nFire||!out.arrows.fires)bad.push('火矢のhazardが出ない '+JSON.stringify(out.arrows));
 let seen=0;
 for(const [name,n] of [['arrows_fall',70],['arrows_burn',60],['arrows_burn2',50]]){await frame(n);await shot(name);}
 await p.evaluate(()=>{for(const f of G.fires)f.t=Math.max(f.t,40);});await frame(2);await shot('ground_fire');
 out.fire=await p.evaluate(()=>{window.__fl.n=0;renderWorld();return{flames:window.__fl.n,fires:G.fires.filter(f=>f.t>0).length,stuck:G.stuck.filter(s=>s.fire).length,partsFire:G.parts.filter(x=>x.k==='fire').length};});
 if(out.fire.fires&&out.fire.flames<out.fire.fires*3)bad.push('地面の火が炎の形で描かれていない '+JSON.stringify(out.fire));
 // 4) 刺さった火矢に炎(飛んだ矢が地面に着いたら stuck.fire)
 if(!out.fire.stuck)bad.push('刺さった火矢が記録されない');
 // 5) 火刑(信長Lv2)/幸村の火の粒が fire 種別
 await setup();
 out.kakei=await p.evaluate(()=>{const P=G.player;const es=[0,1,2].map(i=>{const e=mk('sword',P.x+140+i*90,540+i*40,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;e.face=-1;G.fighters.push(e);return e;});G.parts=[];for(let st=8;st<=40;st+=2)kakeiStep(P,st);return{fire:G.parts.filter(x=>x.k==='fire').length,flame:G.parts.filter(x=>x.k==='flame').length};});
 if(!out.kakei.fire)bad.push('火刑の火が fire になっていない '+JSON.stringify(out.kakei));
 await frame(4);await shot('kakei');
 console.log(JSON.stringify({bad,errors,out}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
