// 2026-10-13 武田信玄の通常2(軍配返し打ち、新キー atk3b_shin)。主武器・徒歩の2段目だけで使う(拾得武器・馬上・1/3段目・敵では使わない)。
// 全5コマが出る・命中の瞬間(hs)が接触のコマ(3コマ目)・両端でも描画が画面内・旧い切れた絵(通常2の欠片)を使わない。QA_OUTがあれば命中の瞬間の画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.__noGuard=true;const out={};
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage=function(img,...a){const rec=used.get(img);if(rec){rec.add(a[0]+','+a[1]);if(a.length>=8){const m=this.getTransform(),x=m.a*a[4]+m.e,w=m.a*a[6],L=Math.min(x,x+w),R=Math.max(x,x+w);rec.minX=Math.min(rec.minX??1e9,L);rec.maxX=Math.max(rec.maxX??-1e9,R);}}return od.call(this,img,...a);};
  const setup=(edge,wpn,mount)=>{startGame('shin',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=wpn||null;P.mount=mount?{hp:6,max:6,col:'red'}:null;P.x=edge===0?G.camx+640:edge<0?G.camx+fighterScreenMargin(P):G.camx+W-fighterScreenMargin(P);P.y=570;P.face=edge>0?-1:1;P.inv=999;P.state='idle';return P;};
  const run=(idx,edge,wpn)=>{const k='atk3b_shin',S=SPR[k],set=new Set();used.set(S.img,set);const P=setup(edge,wpn);const e=mk('sword',P.x+P.face*120,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);
   P.state='atk';P.st=0;P.cur=TY.shin.atk[idx];P.hit.clear();const seq=[];let hitSt=null,hp0=e.hp,n=0;
   for(;n<80&&P.state==='atk';n++){G.t++;updPlayer(P,{});ctx.setTransform(RS,0,0,RS,0,0);const before=new Set(set);drawFighter(P);const added=[...set].filter(x=>!before.has(x));seq.push(set.size);if(hitSt===null&&e.hp<hp0)hitSt=P.st;}
   const o={idx,edge,wpn:!!wpn,frames:set.size,minX:Math.round(set.minX??0),maxX:Math.round(set.maxX??0),hitSt,n};used.delete(S.img);return o;};
  out.turn=[];for(const edge of [0,-1,1])out.turn.push(run(1,edge));
  out.other=[run(0,0),run(2,0),run(1,0,{k:'odachi',uses:99})];
  // 描画の順序: 構え(0,1コマ)→命中(hs=7で2コマ目)→3,4コマ
  {const S=SPR.atk3b_shin,set=new Set();used.set(S.img,set);const P=setup(0);const e=mk('sword',P.x+P.face*120,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);P.state='atk';P.st=0;P.cur=TY.shin.atk[1];P.hit.clear();const fr=[];
   for(let i=0;i<22&&P.state==='atk';i++){G.t++;updPlayer(P,{});const sp=sprPos(P,SPR[P.type]);const U=SPR.atk3b_shin;ctx.setTransform(RS,0,0,RS,0,0);const b4=set.size;drawFighter(P);fr.push([P.st,set.size]);}
   out.order=fr;used.delete(S.img);}
  out.meta={frames:SPR.atk3b_shin.a.turn.length,h:SPR.atk3b_shin.a.turn[0][3],a1h:SPR.shin.a.a1[0][3]*SPR.shin.a.a1[0][6]};
  out.cw=W*RS;return out;});
 const bad=[];
 for(const o of r.turn){if(o.frames!==5)bad.push('コマ数 '+JSON.stringify(o));if(o.minX<0||o.maxX>r.cw)bad.push('画面外 '+JSON.stringify(o)+' cw '+r.cw);if(!(o.hitSt>=7&&o.hitSt<=13))bad.push('命中時刻 '+JSON.stringify(o));}
 if(r.other[0].frames||r.other[1].frames)bad.push('1段目/3段目で使っている '+JSON.stringify(r.other));
 if(r.other[2].frames)bad.push('拾得武器で使っている '+JSON.stringify(r.other[2]));
 if(Math.abs(r.meta.h-r.meta.a1h)>r.meta.a1h*0.5)bad.push('大きさ '+JSON.stringify(r.meta));
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,st] of [['shin_turn_0',2],['shin_turn_1',5],['shin_turn_hit',8],['shin_turn_3',12],['shin_turn_4',17]]){await p.evaluate(([st])=>{startGame('shin',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=null;P.x=G.camx+380;P.y=570;P.face=1;P.inv=999;const e=mk('sword',P.x+110,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;e.face=-1;G.fighters.push(e);P.state='atk';P.st=0;P.cur=TY.shin.atk[1];P.hit.clear();G.parts=[];G.flashT=0;G.hitstop=0;G.shake=0;G.items=[];G.decals=[];for(let i=0;i<st;i++){G.t++;P.inv=999;updPlayer(P,{});G.hitstop=0;}G.flashT=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();drawHUD();},[st]);await p.screenshot({path:`${process.env.QA_OUT}/${name}.png`});}}
 console.log(JSON.stringify({bad,errors,turn:r.turn,other:r.other,order:r.order.map(x=>x.join(':')).join(' '),meta:r.meta}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
