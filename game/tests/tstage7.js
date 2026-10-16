// 2026-10-16 第七幕の最後の砦: 家康は奥で構え、家来が3度押し寄せる→突破すると家康が前に出て一騎打ち。体力75/50/25%で掛け合い、50/25%で身代わり。倒すと最期のセリフ
// ステージデモ(全編自動)で最後まで進むかも見る(オーナーはデモで判断する)
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const BASE=process.argv[2]||process.env.GAME_URL;
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});const bad=[];let out;
 try{const p=await(await b.newContext({viewport:{width:915,height:412}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE);await p.waitForFunction(()=>sprAllReady(),null,{timeout:180000});
  out=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;demoView.motion='auto';startAuto('yuki',6);if(G.mode==='story')endStory();
   const wi=G.waves.length-1;G.wi=wi;G.camMax=G.waves[wi].x;G.camx=G.camMax-5;G.fighters=G.fighters.filter(f=>f.team===0);G.props=[];
   const o={ev:[],says:[]},seen=new Set(),ev=(k)=>{if(!seen.has(k)){seen.add(k);o.ev.push(k+'@'+G.t);}};let ieInvHit=0;
   for(let i=0;i<60*60*12;i++){if(G.mode==='story'&&G.story){endStory();continue;}const P=G.player;if(P)P.hp=Math.max(P.hp,P.maxhp*0.5);
    G.t++;stepGame();const S=G.s7;if(S){ev('ph:'+S.ph);if(S.ph==='surge')ev('surge'+S.surge);if(S.hold)ev('hold');if(S.ie&&S.ph!=='fight'&&S.ie.hp<S.ie.maxhp)ieInvHit++;}
    for(const f of G.fighters)if(f.say&&!o.says.includes(f.say.s))o.says.push(f.say.s);
    if(G.state==='bossdown'){ev('bossdown');if(G.stateT>30)break;}}
   o.ieInvHit=ieInvHit;o.final={state:G.state,mode:G.mode};return o;});
  out.errors=errors;
  for(const k of ['ph:intro','hold','surge0','surge1','surge2','ph:call','ph:fight','bossdown'])if(!out.ev.some(e=>e.startsWith(k+'@')))bad.push('出ない: '+k);
  for(const w of ['しかと見届けた','最後の砦','殿をお守り','よう戦ってくれた','散った者たち','この身を盾','最後の旗本','見事じゃ'])if(!out.says.some(s=>s.includes(w)))bad.push('セリフ無し: '+w);
  if(out.ieInvHit)bad.push('突破前に家康の体力が減った');
  if(errors.length)bad.push('エラー '+errors[0]);
 }catch(e){bad.push('例外 '+e.message);}
 console.log(JSON.stringify(out));if(bad.length){console.log('NG\n'+bad.join('\n'));process.exitCode=1;}else console.log('OK tstage7');await b.close();})();
