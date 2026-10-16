// 2026-10-15 大筒の砲弾: 着弾の爆風に巻き込まれたら大きく吹っ飛ぶ(オーナー「全然痛くない」)。範囲は着弾の印(楕円 横120・縦40)と同じくらい
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const BASE=process.argv[2]||process.env.GAME_URL;
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[];let r;
 try{const p=await(await b.newContext({viewport:{width:915,height:412}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE);await p.waitForFunction(()=>sprAllReady(),null,{timeout:180000});
  r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;startGame('yuki',null);startStage(6,'yuki',false);G.mode='play';G.banner=null;G.story=null;G.fighters=G.fighters.filter(f=>f.team===0);window.ctlKeys=()=>({});
   const P=G.player,out={};
   const shot=(dx,dy,air)=>{P.hp=P.maxhp;P.inv=0;P.state='idle';P.z=0;P.vx=0;const tx=P.x+dx,ty=P.y+dy,sx=G.camx-80,T=60;addProj({x:sx,y:ty,z:260,vx:(tx-sx)/T,vy:0,vz:0.5*0.6*T-260/T,tx,ty,team:-1,dmg:24,face:1,owner:null,k:'bomb',w:0,life:T+30,kb:8,launch:true,nohit:true,big:true,cannon:true});
    let maxZ=0,x0=P.x,hp0=P.hp,down=false;for(let i=0;i<110;i++){if(air&&i>=50&&i<=68){P.state='jump';P.z=50;P.vz=0;}G.t++;stepGame();if(air&&i===68){out.jumpHp=P.hp;}maxZ=Math.max(maxZ,P.z);if(P.state==='down')down=true;}return{down,maxZ:Math.round(maxZ),fly:Math.round(Math.abs(P.x-x0)),dmg:Math.round(hp0-P.hp)};};
   out.center=shot(0,0);out.edge=shot(250,60);out.far=shot(340,0);out.jump=shot(0,0,true);out.dir=P.vx;
   const e=spawnEn('sword',1);e.x=P.x+60;e.y=P.y;e.entered=true;e.hp=999;P.x-=400;const ex=e.x;const tx=e.x,sx=G.camx-80,T=60;addProj({x:sx,y:e.y,z:260,vx:(tx-sx)/T,vy:0,vz:0.5*0.6*T-260/T,tx,ty:e.y,team:-1,dmg:24,face:1,owner:null,k:'bomb',w:0,life:T+30,kb:8,launch:true,nohit:true,big:true,cannon:true});
   for(let i=0;i<100;i++){G.t++;stepGame();}out.enemy={fly:Math.round(Math.abs(e.x-ex)),hpLost:999-e.hp};
   out.bossWind=['boss1','boss2','boss3','boss7','boss9','masamune'].map(k=>k+':'+TY[k].atk.map(a=>a.hs).join('/'));return out;});
  r.errors=errors;
  if(!r.center.down||r.center.fly<120||r.center.maxZ<40)bad.push('中心で吹っ飛ばない '+JSON.stringify(r.center));
  if(!r.edge.down)bad.push('印の端で巻き込まれない '+JSON.stringify(r.edge));
  if(r.far.down)bad.push('印の外でも当たる '+JSON.stringify(r.far));
  /* 2026-10-16 オーナー「ジャンプしないと避けられない。ジャンプしないと吹っ飛ばされる」 */if(r.jump.dmg>0)bad.push('跳んでいても当たる '+JSON.stringify(r.jump));
  if(r.enemy.fly<80)bad.push('敵も吹っ飛ばない '+JSON.stringify(r.enemy));
  if(errors.length)bad.push('エラー '+errors[0]);
 }catch(e){bad.push('例外 '+e.message);}
 console.log(JSON.stringify(r));if(bad.length){console.log('NG\n'+bad.join('\n'));process.exitCode=1;}else console.log('OK tcannon');await b.close();})();
