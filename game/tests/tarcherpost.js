// 2026-10-15 飛び道具のボス(最上義光・徳川秀忠)の陣取り(オーナー「飛び道具が武器なのに距離を取る戦法になっていません。対角線上の画面端に移動して攻撃」)
// ①主人公から見て対角線上(横は反対の端・縦は反対側の列)に陣取る ②そこから遠距離技(矢・雨・兵を呼ぶ)を出す ③主人公が反対側へ動くと反対の隅へ移る ④詰め寄ると跳び越える・近接技の割合が少ない
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;window.dropItem=()=>{};const out={},bad=[];
  const idle={l:0,r:0,u:0,d:0,atkP:0,jumpP:0,spcP:0};
  const setup=(px,py)=>{startGame('yuki',null);startStage(0,'yuki',false);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0&&f===G.player);G.partner=null;G.props=[];G.parts=[];G.proj=[];G.camMax=G.camx;const P=G.player;P.x=G.camx+px;P.y=py;P.face=1;P.hp=P.maxhp=99999;P.inv=0;window.ctlKeys=()=>idle;return P;};
  const mkE=(type,x,y)=>{const e=mk(type,x,y,1);e.entered=true;e.hp=e.maxhp=99999;e.face=-1;e.cool=30;G.fighters.push(e);return e;};
  const tick=()=>{G.t++;stepGame();};
  const mid=(YMIN+YMAX)/2;
  for(const type of ['boss2','boss5']){
   const nm=type==='boss2'?'最上':'秀忠';
   // ①② 主人公は左・上の列に立つ→ボスは右端・下の列へ。そこから遠距離技
   {const P=setup(330,YMIN+40);const e=mkE(type,G.camx+640,(YMIN+YMAX)/2);let far=0,near=0,diag=0,n=0,atks={};const cx=G.camx+W/2;
    for(let i=0;i<1500;i++){P.hp=P.maxhp;P.inv=999;const st0=e.state;tick();e.hp=e.maxhp;
     if(i>500){n++;if(e.x>cx+120&&e.y>mid)diag++;}
     if(e.state==='atk'&&st0!=='atk'&&e.cur){const k=e.cur.k||e.cur.pz;atks[k]=(atks[k]||0)+1;if(Math.abs(P.x-e.x)>420)far++;else near++;}}
    out[nm+'陣取り']={diagRate:+(diag/n).toFixed(2),far,near,atks,boss:[Math.round(e.x-G.camx),Math.round(e.y)]};
    if(!(diag/n>0.6))bad.push(nm+'が対角線上(右端・下の列)に陣取らない '+diag/n);
    if(!(far>=3))bad.push(nm+'が遠くから撃たない far='+far);if(near>far)bad.push(nm+'が近距離の技ばかり '+near+'>'+far);}
   // ③ 主人公が右・下の列へ移ると、ボスは左端・上の列へ移る
   {const P=setup(330,YMIN+40);const e=mkE(type,G.camx+1000,YMAX-10);
    for(let i=0;i<300;i++){P.hp=P.maxhp;P.inv=999;tick();e.hp=e.maxhp;}
    P.x=G.camx+W-330;P.y=YMAX-40;let moved=0,n=0;
    for(let i=0;i<1400;i++){P.hp=P.maxhp;P.inv=999;tick();e.hp=e.maxhp;if(i>900){n++;if(e.x<G.camx+W/2-120&&e.y<mid)moved++;}}
    out[nm+'反対の隅']={rate:+(moved/n).toFixed(2),boss:[Math.round(e.x-G.camx),Math.round(e.y)]};
    if(!(moved/n>0.5))bad.push(nm+'が反対側へ動いた主人公に合わせて反対の隅へ移らない '+moved/n);}
   // ④ 詰め寄る→跳び越える(BHOP)か退く
   {const P=setup(330,YMIN+40);const e=mkE(type,G.camx+1000,YMAX-10);let hop=0,seenHop=false;
    for(let i=0;i<500;i++){P.hp=P.maxhp;P.inv=999;if(i>300)window.ctlKeys=()=>({l:0,r:(P.x<e.x-30)?1:0,u:0,d:(P.y<e.y-10)?1:0,atkP:0,jumpP:0,spcP:0});tick();e.hp=e.maxhp;
     if(e.cur&&(e.cur.k==='hop'||e.cur.k==='step')&&!seenHop){hop++;seenHop=true;}if(!e.cur||(e.cur.k!=='hop'&&e.cur.k!=='step'))seenHop=false;}
    out[nm+'詰め寄り']={hop};if(!(hop>=1))bad.push(nm+'が詰め寄られても跳ばない');}
  }
  return {out,bad,err:0};});
 console.log(JSON.stringify(r.out));
 if(errors.length)r.bad.push('エラー '+errors[0]);
 if(r.bad.length){console.log('NG',r.bad);process.exitCode=1;}else console.log('OK tarcherpost');
 }finally{await b.close();}})();
