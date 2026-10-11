// 馬上の旋風突撃(突撃ボタン): 6人×左右。前へ進み、前の敵と後ろの敵の両方に複数回当たり、最後の一撃で打ち上げる。1.5秒は連続で出せない。弓・鉄砲・鎖鎌では出ない
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const rows=[];
  for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const face of [1,-1]){
   startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.mount={hp:6,max:6,col:'red'};P.wpn=null;P.x=G.camx+640;P.y=570;P.face=face;P.state='idle';P.inv=999;P.ki=0;
   const front=mk('sword',P.x+face*150,570,1),back=mk('sword',P.x-face*90,570,1);for(const e of [front,back]){e.entered=true;e.hp=e.maxhp=999;e.cool=999;G.fighters.push(e);}
   const x0=P.x;window._lh=0;if(!window._hw){window._hw=1;const oh=window.hurt;window.hurt=function(t,a,d){if(d&&d.launch&&a===G.player&&a.cur&&a.cur.whirl)window._lh++;return oh(t,a,d);};}
   const far=mk('sword',P.x+face*400,570,1);far.entered=true;far.hp=far.maxhp=999;far.cool=999;G.fighters.push(far);let hitsF=0,hitsB=0,lf=front.hp,lb=back.hp,launched=false;
   G.t++;updMount(P,{gdP:true});const used=P.cur&&P.cur.whirl;
   for(let i=0;i<80&&P.state==='matk';i++){G.t++;updMount(P,{});for(const e of [front,back]){e.cool=999;}if(front.hp<lf){hitsF++;lf=front.hp;}if(back.hp<lb){hitsB++;lb=back.hp;}}launched=window._lh>0;
   const moved=Math.round((P.x-x0)*face);G.t++;updMount(P,{gdP:true});const again=P.state==='matk';
   rows.push({hero,face,used:!!used,moved,hitsF,hitsB,launched,again,ki:Math.round(P.ki)});}
  const no=[];for(const w of ['yumi','teppo','kusari']){startGame('yuki',null);const P=G.player;P.mount={hp:6,max:6,col:'red'};P.wpn={k:w,uses:9};P.state='idle';G.t++;updMount(P,{gdP:true});no.push(!!(P.cur&&P.cur.whirl));}
  return {rows,no};});
 for(const x of r.rows)console.log(JSON.stringify(x));
 const bad=r.rows.filter(o=>!o.used||o.moved<250||o.hitsF<2||o.hitsB<1||!o.launched||o.again||o.ki<1);
 console.log(JSON.stringify({bad:bad.map(o=>o.hero+o.face),noWhirlWith:r.no,errors}));if(bad.length||r.no.some(Boolean)||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
