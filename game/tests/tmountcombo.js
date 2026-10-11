// 馬上の通常3連撃: 攻撃ボタンを重ねて押すと1→2→3段目へつながり、3段目で打ち上げる。押さなければ1段で終わる。6人×左右。主武器は専用の3種(mountnorm)の全コマを描く。弓・鉄砲・鎖鎌・突撃・旋風は従来どおり。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const rows=[];
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(used.has(img)){used.get(img).add(a[0]+','+a[1]);}return od.call(this,img,...a);};
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const face of [1,-1])for(const mode of ['combo','single','weapon']){
   startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.mount={hp:6,max:6,col:'red'};P.wpn=mode==='weapon'?{k:'odachi',uses:9}:null;P.x=G.camx+640;P.y=570;P.face=face;P.inv=999;P.state='idle';
   const e=mk('sword',P.x+face*120,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);
   const S=SPR['mountnorm_'+hero];const set=new Set();used.set(S.img,set);let lh=0;const oh=window.hurt;window.hurt=function(t,a,d){if(a===G.player&&d&&d.launch)lh++;return oh(t,a,d);};
   const stages=[];let first=true,hits=0,lasthp=e.hp;
   G.t++;updMount(P,{atkP:true});stages.push(P.cur&&P.cur.stage||0);
   for(let i=0;i<120&&P.state==='matk';i++){G.t++;const press=mode!=='single'&&[8,9,10,24,25,26,42].includes(i);updMount(P,{atkP:press});if(P.cur&&P.cur.stage&&stages[stages.length-1]!==P.cur.stage)stages.push(P.cur.stage);if(e.hp<lasthp){hits++;lasthp=e.hp;}ctx.setTransform(RS,0,0,RS,0,0);drawFighter(P);}
   window.hurt=oh;rows.push({hero,face,mode,stages:stages.join('>'),hits,launch:lh,frames:set.size,end:P.state});used.delete(S.img);}
  CanvasRenderingContext2D.prototype.drawImage=od;return rows;});
 const bad=[];for(const o of r){if(o.mode==='combo'){if(o.stages!=='1>2>3'||o.hits<3||o.launch!==1||o.frames<12)bad.push(o);}else if(o.mode==='single'){if(o.stages!=='1'||o.hits<1||o.launch!==0||o.frames<3)bad.push(o);}else{if(o.frames!==0)bad.push(o);}}
 console.log(JSON.stringify({n:r.length,sample:r.slice(0,3),bad:bad.slice(0,5)}),JSON.stringify(errors));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
