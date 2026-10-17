// 槍回し(2026-10-17)の検査: 幸村の防御と、竹槍を持った防御で、(1)前から来た矢を弾き返して相手の方へ飛ばす(team 0・逆向き)
// (2) 防御の間 槍の絵(drawPoleProp)が描かれる (3) 竹槍の溜め攻撃は頭上で回して全方位に多段ヒット、最後に吹き飛ばす。描画エラーなし。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const p=await b.newPage({viewport:{width:915,height:412}});const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>typeof sprAllReady==='function'&&sprAllReady(),null,{timeout:120000});
 const out=[];
 for(const wpn of ['','takeyari']){
  out.push(await p.evaluate((wpn)=>{window.requestAnimationFrame=()=>0;AU.muted=true;startAuto('yuki',2);if(G.mode==='story')endStory();G.waveOn=false;G.camMax=1e9;G.auto=false;
   G.mode='play';G.state='run';G.banner=null;G.fighters=G.fighters.filter(f=>f===G.player);G.partner=null;G.proj=[];const P=G.player;P.x=G.camx+400;P.y=570;P.face=1;P.inv=0;P.hp=P.maxhp=500;P.wpn=wpn?{k:wpn,uses:99}:null;
   const orig=drawPoleProp;let drawn=0;drawPoleProp=function(...a){drawn++;return orig.apply(this,a);};
   const src=mk('archer',P.x+360,P.y,1);src.entered=true;src.cool=9999;src.face=-1;G.fighters.push(src);
   let refl=0;
   for(let i=0;i<120;i++){if(i%40===5)addProj({x:P.x+300,y:P.y,z:P.z+80,vx:-11,vz:0,team:1,dmg:6,face:-1,owner:src,k:'arrow',w:14,life:60,kb:2});
    keys.KeyV=true;frame();
    if(G.proj.some(q=>q.team===0&&q.owner===P&&q.k==='arrow'&&q.vx>0))refl++;}
   keys.KeyV=false;let spinHits=0,launched=0;
   if(wpn){P.state='idle';P.cur=null;P.st=0;const en=[];for(const dx of[-90,90,-140]){const e=mk('spear',P.x+dx,P.y,1);e.entered=true;e.cool=9999;e.hp=e.maxhp=400;e.wakeInv=0;G.fighters.push(e);en.push(e);}
    const h0=en.map(e=>e.hp);startCharge(P);for(let i=0;i<120;i++){frame();}spinHits=en.filter((e,i)=>e.hp<h0[i]).length;launched=en.filter(e=>e.state==='down'||e.dying||e.hp<=0).length;}
   return {wpn,drawn,reflected:refl,spinHits,launched};},wpn));}
 const bad=[];for(const r of out){if(r.drawn<5)bad.push('spear not drawn '+r.wpn);if(r.reflected<1)bad.push('arrow not reflected '+r.wpn);}
 if(out[1]&&(out[1].spinHits<2||out[1].launched<1))bad.push('overhead spin did not hit around '+JSON.stringify(out[1]));
 console.log(JSON.stringify({out,bad,errors}));if(bad.length||errors.length)process.exitCode=1;
}finally{await b.close();}})();
