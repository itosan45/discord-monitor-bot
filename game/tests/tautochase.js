// 2026-10-15 ステージデモ(全編自動)で、第六幕の家康が馬で逃げる追撃戦→家来の盾→天海→第七幕(政宗→家康)まで進むか
// オーナーはデモを流して判断するので、自動プレイで全部の演出が見えることを確かめる。体力は減らさない(自動の主人公は死なない設定と同じ)
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const BASE=process.argv[2]||process.env.GAME_URL;
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[];let out;
 try{const p=await(await b.newContext({viewport:{width:915,height:412}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE);await p.waitForFunction(()=>sprAllReady(),null,{timeout:180000});
  out=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;demoView.motion='auto';startAuto('yuki',5);
   const o={ev:[]},seen=new Set(),ev=(k,x)=>{if(!seen.has(k)){seen.add(k);o.ev.push(Object.assign({k,t:G.t},x||{}));}};
   for(let i=0;i<60*60*25;i++){if(G.mode==='story'&&G.story){endStory();continue;}const P=G.player;if(P)P.hp=Math.max(P.hp,P.maxhp*0.5);
    G.t++;stepGame();
    const C=G.chase;if(C){ev('chase:'+C.phase);if(C.hold)ev('hold');}
    for(const f of G.fighters){if(f.say)ev('say:'+f.T.name);if(f.T.type==='boss3'&&f.mount)ev('ieyasuMounted');if(f.T.type==='tenkai')ev('tenkai');if(f.T.type==='masamune')ev('masamune');}
    ev('stage'+G.stage);if(G.state==='bossdown'&&G.stage===6)ev('stage7clear');if(G.mode!=='play'){ev('mode:'+G.mode);break;}
    if(seen.has('stage7clear')&&G.stateT>200)break;}
   o.final={stage:G.stage,state:G.state,mode:G.mode,wi:G.wi,nw:G.waves.length,boss:G.boss&&G.boss.T.type};return o;});
  out.errors=errors;
  for(const k of ['ieyasuMounted','chase:run','chase:shield','hold','tenkai','stage6','masamune','say:伊達政宗'])if(!out.ev.some(e=>e.k===k))bad.push('自動で出ない: '+k);
  if(errors.length)bad.push('エラー '+errors[0]);
 }catch(e){bad.push('例外 '+e.message);}
 console.log(JSON.stringify(out));if(bad.length){console.log('NG\n'+bad.join('\n'));process.exitCode=1;}else console.log('OK tautochase');await b.close();})();
