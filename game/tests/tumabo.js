// 2026-10-14 A-016 馬防柵(画面の上から下まで続く、壊せる柵)。第3幕から波の間に置く(前の波の画面の外・次の波の画面の外)/壊すまで全レーンを遮る(吹き飛ばしでも抜けない)/
// どのレーンからの攻撃・飛び道具も当たる/敵の飛び道具は通らない/HPで健全→損傷→倒壊の絵/倒壊後は通れる/ゲームの奥行き(最下端y≈690・最上端y>340、空まで伸ばさない)に描く/デモには置かない。
// QA_OUTがあれば Android相当(802×360) の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;const out={};
  const wallsOf=()=>G.props.filter(q=>q.k==='umabo');
  out.stages=[];for(let si=0;si<6;si++){startStage(si,'yuki',false);const w=wallsOf();out.stages.push({si,n:w.length,pos:w.map(q=>[Math.round(q.x),Math.round(G.waves.findIndex(v=>v.x>q.x))])});
   if(w.length){const i=G.waves.findIndex(v=>v.x>w[0].x);out['gap'+si]={prevEdge:Math.round(w[0].x-(G.waves[i-1].x+W)),toNext:Math.round(G.waves[i].x-w[0].x),gap:Math.round(G.waves[i].x-G.waves[i-1].x)};}}
  startStage(2,'yuki',true);out.demoN=wallsOf().length;
  // --- 以降は第3幕で
  startStage(2,'yuki',false);G.waveOn=false;G.waves=G.waves.slice();G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;
  const P=G.player,w=wallsOf()[0];P.hp=P.maxhp=9999;P.inv=999;G.camx=Math.max(0,w.x-500);G.camMax=1e9;
  const place=(x,y)=>{P.x=x;P.y=y;P.vx=0;P.wx=null;};
  // 遮る: 左側にいた主人公が右へ抜けようとしても戻される(全レーン・速い吹き飛ばしでも)
  const crossed=[];for(const y of[490,540,590,640,700]){place(w.x-80,y);wallClamp();P.x=w.x+10;wallClamp();crossed.push(Math.round(P.x-w.x));place(w.x-80,y);wallClamp();P.x=w.x+400;wallClamp();crossed.push(Math.round(P.x-w.x));}
  out.crossed=crossed;
  // 反対側(右)にいる敵は右に残る
  {const e=mk('sword',w.x+120,570,1);e.entered=true;e.hp=e.maxhp=9999;G.fighters.push(e);wallClamp();e.x=w.x-100;wallClamp();out.enemyX=Math.round(e.x-w.x);G.fighters.splice(G.fighters.indexOf(e),1);}
  // 攻撃: どのレーンからでも当たる/飛び道具も
  const d0=P.T.atk[0];const hits=[];for(const y of[490,560,640,700]){const h0=w.hp;place(w.x-60,y);P.face=1;P.hit=new Set();strike(P,d0);hits.push(h0-w.hp);w.hp=h0;}out.hits=hits;
  {const h0=w.hp;G.proj.length=0;addProj({x:w.x-40,y:700,z:70,vx:12,team:0,dmg:5,face:1,owner:P,k:'arrow'});updProj();out.projHit=h0-w.hp;w.hp=h0;G.proj.length=0;}
  // 敵の飛び道具は通らない
  {const h0=w.hp;G.proj.length=0;addProj({x:w.x+80,y:520,z:70,vx:-9,team:1,dmg:5,face:-1,owner:null,k:'arrow'});for(let i=0;i<12;i++)updProj();out.enemyProj={removed:G.proj.length===0,hpLost:h0-w.hp};w.hp=h0;G.proj.length=0;}
  // 絵: 健全・損傷・倒壊が選ばれ、全高に描く
  const US=SPR.umabo;out.ready=!!(US&&US.ready&&US.a.wall&&US.a.wall.length===3);
  const od=CanvasRenderingContext2D.prototype.drawImage;const rec=[];CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(US&&img===US.img)rec.push(a.slice());return od.call(this,img,...a);};
  const frameOf=()=>{rec.length=0;ctx.setTransform(RS,0,0,RS,0,0);drawProp(w);const a=rec[0];return a?{f:US.a.wall.findIndex(q=>q[0]===a[0]),dy:a[5],h:a[3],dx:a[4]}:null;};
  w.hp=w.maxhp;out.d0=frameOf();w.hp=Math.floor(w.maxhp*0.5);out.d1=frameOf();w.hp=1;out.d1b=frameOf();
  // 壊す: 12回当てると倒壊→通れる
  w.hp=w.maxhp;let n=0;while(!w.broken&&n<60){place(w.x-60,570);P.hit=new Set();strike(P,d0);n++;}out.breakHits=n;out.broken=w.broken;out.d2=frameOf();
  place(w.x-80,570);wallClamp();P.x=w.x+10;wallClamp();out.afterBreakX=Math.round(P.x-w.x);
  CanvasRenderingContext2D.prototype.drawImage=od;
  // 実際の進行: 波の間を右へ歩き続けると柵の手前で止まり、カメラも止まる(波は始まらない)。壊すと先へ進み、次の波が始まる
  {startStage(2,'yuki',false);G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.partner=null;G.state='run';G.waveOn=false;
   const w=wallsOf()[0],P=G.player;P.hp=P.maxhp=99999;P.inv=999;const oc=window.ctlKeys;window.ctlKeys=()=>({r:1,l:0,u:0,d:0,a:0,j:0,s:0,g:0});
   // 最初の波(waves[0])を飛ばして、柵の手前の道へ
   G.wi=2;G.camMax=G.waves[2].x;G.camx=G.waves[1].x;P.x=G.waves[1].x+500;P.y=570;P.wx=null;
   let t=0;for(;t<1200&&!G.waveOn;t++){G.t++;P.inv=999;updWorld();}
   out.walk={x:Math.round(P.x-w.x),waveOn:G.waveOn,camx:Math.round(G.camx),camMaxGap:Math.round(G.camMax-G.camx),t};
   w.broken=true;w.hp=0;for(;t<2400&&!G.waveOn;t++){G.t++;P.inv=999;updWorld();}
   out.walk2={x:Math.round(P.x-w.x),waveOn:G.waveOn,t};window.ctlKeys=oc;}
  // 自動プレイ(demoCtl)は柵まで歩いて壊し、先へ進む
  {startStage(2,'yuki',false);G.auto=true;G.demo=false;G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.partner=null;G.state='run';G.waveOn=false;
   const w=wallsOf()[0],P=G.player;P.hp=P.maxhp=99999;P.inv=999;G.wi=2;G.camMax=G.waves[2].x;G.camx=G.waves[1].x;P.x=G.waves[1].x+500;P.y=570;P.wx=null;
   let t=0,tb=-1;for(;t<4000&&!G.waveOn;t++){G.t++;P.inv=999;updWorld();if(tb<0&&w.broken)tb=t;}
   out.auto={broken:!!w.broken,tBroken:tb,waveOn:G.waveOn,t};G.auto=false;}
  return out;});
 const bad=[];
 if(!r.ready)bad.push('umabo の絵が読めない');
 const exp={0:0,1:0,2:1,3:1,4:2,5:2};for(const s of r.stages)if(s.n!==exp[s.si])bad.push('幕'+s.si+'の柵の数 '+s.n);
 for(const k of['gap2','gap4']){const g=r[k];if(g){if(g.gap<1900)bad.push(k+' 道のりが短い '+JSON.stringify(g));if(g.prevEdge<50)bad.push(k+' 前の波の画面の中 '+JSON.stringify(g));if(g.toNext<400)bad.push(k+' 次の波の画面に近い '+JSON.stringify(g));}}
 if(r.demoN!==0)bad.push('デモに柵がある '+r.demoN);
 if(r.crossed.some(x=>x>=0))bad.push('柵を抜けた '+r.crossed);
 if(r.crossed.some(x=>Math.abs(Math.abs(x)-30)>1))bad.push('柵の手前の位置 '+r.crossed);
 if(r.enemyX<30)bad.push('右の敵が左へ抜けた '+r.enemyX);
 if(r.hits.some(h=>h<1))bad.push('レーンによって攻撃が当たらない '+r.hits);
 if(r.projHit<1)bad.push('自分の飛び道具が当たらない '+r.projHit);
 if(!r.enemyProj.removed||r.enemyProj.hpLost<1)bad.push('敵の飛び道具が柵を通る '+JSON.stringify(r.enemyProj));
 if(!r.d0||r.d0.f!==0||r.d1.f!==1||r.d1b.f!==1||!r.d2||r.d2.f!==2)bad.push('絵の選択 '+JSON.stringify([r.d0,r.d1,r.d1b,r.d2]));
 if(r.d0&&(r.d0.dy<340||r.d0.dy+r.d0.h<670||r.d0.dy+r.d0.h>700||r.d0.h>340))bad.push('柵がゲームの奥行きに収まっていない(空まで伸びる/高すぎる) '+JSON.stringify(r.d0));
 if(!r.broken||r.breakHits<4||r.breakHits>16)bad.push('壊れるまでの回数 '+r.breakHits+' '+r.broken);
 if(r.afterBreakX<0)bad.push('倒壊後も通れない '+r.afterBreakX);
 if(r.walk.waveOn||Math.abs(r.walk.x+30)>2||r.walk.camMaxGap<300)bad.push('歩き続けても柵の手前で止まらない '+JSON.stringify(r.walk));
 if(!r.auto.broken||!r.auto.waveOn)bad.push('自動プレイが柵を壊せない '+JSON.stringify(r.auto));
 if(!r.walk2.waveOn||r.walk2.x<30)bad.push('柵を壊しても先へ進めない '+JSON.stringify(r.walk2));
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,hp] of [['healthy',12],['damaged',5],['broken',0]]){await p.evaluate(hp=>{startStage(2,'yuki',false);G.waveOn=false;G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.parts=[];G.decals=[];G.items=[];G.deco=[];
   const w=G.props.find(q=>q.k==='umabo'),P=G.player;P.hp=P.maxhp=9999;P.inv=999;G.camx=w.x-640+120;G.camMax=1e9;P.x=w.x-150;P.y=580;P.face=1;
   for(const q of G.props)if(q!==w)q.x=-9999;
   w.hp=hp;w.broken=hp<=0;G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},hp);await p.screenshot({path:`${process.env.QA_OUT}/umabo_${name}.png`});}}
 console.log(JSON.stringify({bad,errors,summary:r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
