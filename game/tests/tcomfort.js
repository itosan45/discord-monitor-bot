// 2026-10-14 友達の意見対応: ①「↓で画面ごと下に消える」= 1本指のtouchmoveで画面がスクロールする→preventDefaultされること
// ②「目が疲れる」= ポーズメニューの「目にやさしい表示」で揺れ・白フラッシュが弱まる(既定ON・保存される) ③「味方が強すぎる」= 味方の与ダメ/被ダメの係数
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const bad=[],out={};
  // ① touchmove
  const ev=new Event('touchmove',{bubbles:true,cancelable:true});document.getElementById('zone').dispatchEvent(ev);out.touchPrevented=ev.defaultPrevented;
  if(!ev.defaultPrevented)bad.push('1本指のtouchmoveがpreventDefaultされない(画面が下に動く)');
  const st=getComputedStyle(document.body);out.bodyPos=st.position;if(st.position!=='fixed')bad.push('bodyがfixedでない');
  // ② 目にやさしい表示
  startGame('yuki','nobu');startStage(0,'yuki',false);G.waveOn=false;G.waves=[{x:999999,en:[]}];
  out.comfortDefault=COMFORT;if(!COMFORT)bad.push('既定でON');
  G.pause=true;G.pzSel=1;for(const k of Object.keys(pressed))pressed[k]=false;pressed.Enter=true;frame();
  out.afterToggle=COMFORT;if(COMFORT)bad.push('ポーズ画面でENTERしても切り替わらない');
  out.stored=localStorage.getItem('sekigahara_comfort');if(out.stored!=='0')bad.push('設定が保存されない');
  pressed.Enter=false;G.pzSel=2;pressed.ArrowUp=true;frame();pressed.ArrowUp=false;out.selAfterUp=G.pzSel;if(G.pzSel!==1)bad.push('↑で選択が戻らない '+G.pzSel);
  setComfort(true);G.pause=false;
  // 揺れ: ctx.translateの大きさを記録
  const tr=[];const t0=ctx.translate.bind(ctx);ctx.translate=(x,y)=>{tr.push(Math.abs(x)+Math.abs(y));return t0(x,y);};
  const maxTr=()=>{let m=0;for(let i=0;i<40;i++){tr.length=0;G.shake=30;renderWorld();m=Math.max(m,tr[0]||0);}return m;};
  setComfort(true);const a=maxTr();setComfort(false);const c=maxTr();ctx.translate=t0;setComfort(true);out.shake={on:+a.toFixed(1),off:+c.toFixed(1)};
  if(!(a<c*0.6))bad.push('やさしい表示で揺れが弱まらない '+a+' vs '+c);
  // ③ 味方の係数
  const q=G.partner;out.partner=!!q;if(q){const e=mk('spear',G.camx+400,q.y,1);e.hp=e.maxhp=9999;e.inv=0;G.fighters.push(e);
   const hp0=e.hp;hurt(e,q,{dmg:20,kb:0});const dealt=hp0-e.hp;const hp1=e.hp;e.inv=0;hurt(e,G.player,{dmg:20,kb:0});const dealtP=hp1-e.hp;out.dealt={partner:+dealt.toFixed(1),player:+dealtP.toFixed(1)};
   if(!(dealt<dealtP*0.95))bad.push('味方の与ダメが主人公以下になっていない '+dealt+' vs '+dealtP);}
  return {out,bad};});
 console.log(JSON.stringify(r.out));if(errors.length)console.log('pageerrors',errors);
 if(r.bad.length||errors.length){console.log('NG',r.bad);process.exitCode=1;}else console.log('OK tcomfort');
 }finally{await b.close();}})();
