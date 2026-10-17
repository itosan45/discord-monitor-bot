// からくり武者の専用必殺(2026-10-17)の検査。
// 2026-10-17 オーナー指示で突進をゆっくり(1コマ約6px)にしたため、突進は約2秒かかる(ループ上限を460コマに)。
// Lv1=独楽の突進: 回転(kspin)が有限で、前へ進み、通り道の敵が多段で削られ、最後に弾き飛ばされる。時間は突進中だけ止まり、終わりに動く。
// Lv2=突進のあと砲弾: 砲弾(k:'shell')が飛んで爆発し、敵が吹き飛ぶ。爆発で時間の停止が解ける。
// 左右両向き。描画エラー・有限でない粒(PT)の警告が出ない。カットイン(顔のアップ)が描かれる。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:915,height:412}});const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='warning'&&/PT |drawParts/.test(m.text()))errors.push(m.text().slice(0,160));});
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForTimeout(1500);
 await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;startAuto('karakuri',2);if(G.mode==='story')endStory();G.waveOn=false;G.camMax=1e9;G.auto=false;});
 await p.waitForFunction(()=>{frame();return sprAllReady();},null,{timeout:120000,polling:300});
 const out=[];
 for(const lv of [1,2])for(const side of [1,-1]){
  const r=await p.evaluate(([lv,side])=>{G.mode='play';G.state='run';G.banner=null;G.fighters=G.fighters.filter(f=>f===G.player);G.partner=null;G.proj=[];const P=G.player;const X0=G.camx+(side>0?240:W-240);P.x=X0;P.y=570;P.face=side;P.inv=0;P.hp=P.maxhp;P.ki=lv*100;
   const en=[];for(let i=0;i<3;i++){const e=mk('spear',X0+side*(320+i*110),556+i*14,1);e.entered=true;e.face=-side;e.cool=9999;e.wakeInv=0;e.hp=e.maxhp=300;G.fighters.push(e);en.push(e);}
   startSpecial(P);const o={lv,side,spinOK:true,cutSeen:false,shell:false,boom:false,frozeDuringRush:false,unfroze:false,spun:false,x0:X0,xMax:0,minHp:300,bounced:false};
   const hp0=en.map(e=>e.hp);const far=mk('spear',X0-side*260,500,1);far.entered=true;far.face=side;far.wakeInv=0;far.hp=far.maxhp=300;G.fighters.push(far);let lastFar=-1;
   for(let k=0;k<460;k++){frame();if(G.cut&&G.cut.type==='karakuri'&&G.cut.t>2)o.cutSeen=true;if(P.kspin!==undefined){o.spun=true;if(!Number.isFinite(P.kspin))o.spinOK=false;}
    if(P.state==='spc'&&G.spcScene)o.frozeDuringRush=true;/* 時間は止めない */if(P.state==='spc'&&!G.spcScene&&P.st>20)o.unfroze=true;if(P.state==='spc'&&P.kspin!==undefined&&far.state!=='dead'&&(far.st!==lastFar)){o.farMoved=true;}lastFar=far.st;
    if(G.proj.some(q=>q.k==='shell'))o.shell=true;o.xMax=Math.max(o.xMax,Math.abs(P.x-X0));if(en.some(e=>e.state==='down'||e.dying))o.bounced=true;
    if(P.state!=='spc'&&k>20)break;}
   o.dmg=en.map((e,i)=>Math.round(hp0[i]-e.hp));o.moved=Math.round(o.xMax);o.endState=P.state;return o;},[lv,side]);
  out.push(r);}
 const bad=[];for(const r of out){if(!r.spinOK)bad.push('spin NaN '+r.lv+'/'+r.side);if(!r.spun)bad.push('no spin');if(!r.cutSeen)bad.push('no cut-in');if(r.moved<300)bad.push('rush short '+r.moved);if(!r.dmg.some(d=>d>=12))bad.push('no multi hit '+r.dmg);if(!r.bounced)bad.push('no knockback');if(r.frozeDuringRush)bad.push('time was frozen (enemies must keep moving)');if(!r.farMoved)bad.push('free enemy did not act during the spin');if(r.lv===2&&!r.shell)bad.push('no shell');if(r.lv===1&&r.shell)bad.push('Lv1 fired shell');if(r.endState==='spc')bad.push('special did not end');}
 console.log(JSON.stringify({out,bad,errors}));if(bad.length||errors.length)process.exitCode=1;
}finally{await b.close();}})();
