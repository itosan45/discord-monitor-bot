// 2026-10-14 鉄球大僧の歩き16コマ(A-015)。実際の歩きで16コマすべてが順に一巡する/足元(接地線)がコマごとにずれない/人物の高さが待機と大きく違わない。
// QA_OUTがあれば Android相当(802×360) の画面(歩きの16コマを並べた1枚)を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];
  const P=G.player;P.hp=P.maxhp=9999;P.inv=999;P.x=G.camx+200;P.y=570;
  const e=mk('monk',G.camx+640,570,1);e.entered=true;e.hp=e.maxhp=99999;e.cool=999;e.face=-1;G.fighters.push(e);const S=SPR.monk,A=S.a;
  out.walkN=A.walk.length;
  // 歩きの位相を一巡させて、選ばれるコマを数える
  const seq=[];e.state='walk';for(let i=0;i<64;i++){e.wp=i/64*TAU;const sp=sprPos(e,S);seq.push(Math.floor(sp.pos));}
  out.seq=seq.join(',');out.frames=new Set(seq).size;let back=0;for(let i=1;i<seq.length;i++)if(seq[i]<seq[i-1])back++;out.wraps=back;
  // 接地線: 各コマの下端(oy+h)の最大差
  const bots=A.walk.map(q=>q[5]+q[3]*q[6]);out.botSpread=+(Math.max(...bots)-Math.min(...bots)).toFixed(1);
  const idleH=A.idle[0][3]*A.idle[0][6],walkH=A.walk.map(q=>q[3]*q[6]);out.idleH=Math.round(idleH);out.walkH=[Math.round(Math.min(...walkH)),Math.round(Math.max(...walkH))];
  return out;});
 const bad=[];
 if(r.walkN!==16)bad.push('歩きのコマ数 '+r.walkN);
 if(r.frames!==16)bad.push('一巡で16コマが出ない '+r.frames);
 if(r.wraps!==0)bad.push('順番が乱れる(0→15へ順に進む) '+r.wraps);
 if(r.botSpread>6)bad.push('足元がコマごとにずれる '+r.botSpread);
 if(r.walkH[0]<r.idleH*0.85||r.walkH[1]>r.idleH*1.1)bad.push('人物の高さが待機と違いすぎる '+JSON.stringify([r.idleH,r.walkH]));
 if(process.env.QA_OUT){const fs=require('fs');fs.mkdirSync(process.env.QA_OUT,{recursive:true});
  for(const [name,idx] of [['a',[0,2,4,6]],['b',[8,10,12,14]]]){await p.evaluate(idx=>{startGame('yuki',null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;G.props=[];G.deco=[];G.parts=[];G.items=[];G.decals=[];
   const P=G.player;P.x=-9999;P.inv=999;const es=idx.map((n,k)=>{const e=mk('monk',G.camx+120+k*300,570,1);e.entered=true;e.hp=e.maxhp=99999;e.cool=999;e.face=1;e.state='walk';e.wp=n/16*TAU+0.01;G.fighters.push(e);return e;});
   G.flashT=0;G.hitstop=0;G.shake=0;ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;ctx.setTransform(RS,0,0,RS,0,0);renderWorld();},idx);await p.screenshot({path:`${process.env.QA_OUT}/monkwalk_${name}.png`});}}
 console.log(JSON.stringify({bad,errors,summary:r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
