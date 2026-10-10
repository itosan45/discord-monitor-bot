// 回避: スティックを倒しながら防御ボタンを押すと、その方向へ回避する(前方・後方・上下)。倒さずに押すと従来どおり防御(見切りは tfeel.js)。
// 6人の主人公で、回避の向き・移動量・無敵・回避の絵・連続で出せない間(約0.3秒)を確かめる。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const bad=[],rows=[];
  const setup=hero=>{startGame(hero,null);G.state='run';G.waveOn=false;G.waves=[{x:1e9,en:[]}];G.wi=0;G.items=[];G.props=[];G.proj=[];G.steeds=[];G.hzT=99999;G.sq=[];G.slow=0;G.hitstop=0;
   const f=G.player;f.x=G.camx+500;f.y=570;f.face=1;f.hp=f.maxhp=999;f.inv=0;f.dcd=0;G.partner=null;G.fighters=[f];for(const k in keys)keys[k]=false;for(const k in pressed)delete pressed[k];return f;};
  const step=n=>{for(let i=0;i<n;i++){G.t++;stepGame();for(const k in pressed)delete pressed[k];}};
  const press=(dirKey)=>{if(dirKey)keys[dirKey]=true;setKey('KeyV',true);step(1);setKey('KeyV',false);};
  const HEROES=['yuki','kage','mitsu','nobu','shin','musashi'];
  for(const hero of HEROES){
   for(const [dirKey,label] of [['ArrowRight','前'],['ArrowLeft','後'],['ArrowUp','上'],['ArrowDown','下']]){
    const f=setup(hero),x0=f.x,y0=f.y;press(dirKey);const st=f.state,inv=f.inv,anim=f.dback?'dodgeB':'dodgeF',hasArt=!!(SPR[f.T.spr||f.T.type]&&SPR[f.T.spr||f.T.type].a[anim]);
    step(24);keys[dirKey]=false;const dx=Math.round(f.x-x0),dy=Math.round(f.y-y0);
    rows.push({hero,dir:label,st,inv,anim,hasArt,dx,dy,face:f.face});
    if(st!=='dodge'||inv<10||!hasArt)bad.push({hero,label,st,inv,hasArt});
    if(label==='前'&&dx<60)bad.push({hero,label,dx});if(label==='後'&&dx>-60)bad.push({hero,label,dx});
    if(label==='上'&&dy>-40)bad.push({hero,label,dy});if(label==='下'&&dy<40)bad.push({hero,label,dy});}
   // 倒さずに押すと防御(回避しない)
   {const f=setup(hero);keys.KeyV=true;pressed.KeyV=true;step(3);const st=f.state;keys.KeyV=false;step(10);rows.push({hero,neutral:st});if(st!=='guard')bad.push({hero,neutral:st});}
   // 回避直後は約0.3秒(18更新)出せない
   {const f=setup(hero);press('ArrowRight');step(22);const end=f.state;press('ArrowRight');const again=f.state;keys.ArrowRight=false;
    const f2=setup(hero);press('ArrowRight');step(19+18);press('ArrowRight');const later=f2.state;keys.ArrowRight=false;
    rows.push({hero,endState:end,againSoon:again,againLater:later});if(again==='dodge'||later!=='dodge')bad.push({hero,again,later});}
   // 騎乗中は防御ボタンが「突撃」: 止まったまま押しても騎馬突撃が出て前へ突っ込み、敵に当たる
   {const f=setup(hero);f.mount={hp:6,max:6,col:'red'};const e=mk('sword',f.x+150,570,1);e.hp=e.maxhp=500;e.entered=true;e.face=-1;e.cool=9999;G.fighters=[f,e];
    step(1);const label=document.getElementById('bG').textContent,x0=f.x;setKey('KeyV',true);step(1);setKey('KeyV',false);const st=f.state,chg=f.cur===MCHG;step(30);
    const dx=Math.round(f.x-x0),hit=e.hp<500;rows.push({hero,mountLabel:label,st,chg,dx,hit});if(label!=='突撃'||!chg||dx<100||!hit)bad.push({hero,mountLabel:label,st,chg,dx,hit});
    f.mount=null;step(1);if(document.getElementById('bG').textContent!=='防御')bad.push({hero,footLabel:document.getElementById('bG').textContent});}
  }
  return {bad,rows};});
 console.log(JSON.stringify({bad:r.bad,rows:r.rows,errors}));
 }finally{await b.close();}})();
