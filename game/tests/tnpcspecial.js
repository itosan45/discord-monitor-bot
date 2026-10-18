// 全編デモで敵の武将を主人公に選んだ時(npcHero)、政宗は奥義・柳生宗矩は必殺を実際に撃つ(2026-10-17 オーナー指摘)。
// 各キャラで幕2を最大7000コマ流し、撃った回数と描画エラー・有限でない粒の警告を数える。政宗は奥義が最後まで終わって待機に戻ること。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const out=[],bad=[],errors=[];
 for(const who of ['masamune','munenori']){
  const p=await b.newPage({viewport:{width:915,height:412}});p.on('pageerror',e=>errors.push(who+':'+e.message));p.on('console',m=>{if(m.type()==='warning'&&/PT |drawParts/.test(m.text()))errors.push(who+':'+m.text().slice(0,120));});
  await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForTimeout(1500);
  await p.evaluate(who=>{window.requestAnimationFrame=()=>0;AU.muted=true;startAuto(who,2);if(G.mode==='story')endStory();},who);
  await p.waitForFunction(()=>{frame();return sprAllReady();},null,{timeout:120000,polling:300});
  const r=await p.evaluate(who=>{let ult=0,spc=0,maxki=0,ended=0;const u0=startUlt,s0=startSpecial;startUlt=function(p){ult++;return u0(p);};startSpecial=function(p){spc++;return s0(p);};
   for(let k=0;k<7000;k++){const P=G.player;if(P){P.hp=P.maxhp;maxki=Math.max(maxki,P.ki||0);}frame();if(ult+spc>=3&&G.player.state==='idle'&&!G.ult&&!G.spcScene)break;}
   return {who,ult,spc,maxki:Math.round(maxki),np:!!G.player.npcHero,state:G.player.state,stuck:!!G.ult||!!G.spcScene};},who);
  out.push(r);
  if(who==='masamune'&&r.ult<1)bad.push('masamune did not use ult');
  if(who==='munenori'&&r.spc<1)bad.push('munenori did not use special');
  if(r.stuck)bad.push(who+' stuck in special/ult');
  await p.close();}
 console.log(JSON.stringify({out,bad,errors}));if(bad.length||errors.length)process.exitCode=1;
}finally{await b.close();}})();
