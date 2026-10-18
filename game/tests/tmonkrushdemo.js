// 2026-10-13 鉄球大僧の端から端への突進を、自動デモ(本物のAIの主人公と大僧)で実際に動かす。
// 大僧は画面外へ出ない・突進を使う・突進中の主人公に当たる/かわされる・突進の最中の画面を保存する(QA_OUT)。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;});
 const r=await p.evaluate(()=>{startDemo(0);G.lowq=true;G.titleT=-9999;G.camx=G.camMax=0;G.banner=null;G.vo=null;G.waveOn=true;G.sq=[];G.props=[];G.items=[];G.proj=[];
  const P=G.player;P.x=700;P.y=570;P.hp=P.maxhp=99999;P.inv=0;const m=mk('monk',1000,570,1);m.entered=true;m.hp=m.maxhp=99999;m.face=-1;m.cool=1;G.fighters=[P,m];G.boss=null;
  G.autoSpd=1;demoView.paused=false;demoView.steps=0;demoView.credit=0;acc=0;last=0;
  const o={rushStarts:0,hitsByRush:0,out:0,ticks:0,shot:false,minX:9999,maxX:-9999,types:new Set()};let was=false,hp=P.hp;
  for(let t=1;t<=6000;t++){loop(t*1000/60+0.00001);o.ticks=t;
   const rushing=m.state==='atk'&&m.cur&&m.cur.edge;if(rushing&&!was)o.rushStarts++;was=rushing;
   if(P.hp<hp&&rushing&&m.st>=m.cur.hs&&m.st<=m.cur.he)o.hitsByRush++;hp=P.hp;
   if(m.hp>0){const sx=m.x-G.camx;o.minX=Math.min(o.minX,sx);o.maxX=Math.max(o.maxX,sx);if(sx<0||sx>W)o.out++;}
   if(rushing&&!m.rushDone&&m.st>=m.cur.hs+10&&!o.shot&&o.rushStarts>=1){o.shot=true;demoView.paused=true;autoUI(true);break;}
  }
  o.rushN=G.rushN||0;o.minX=Math.round(o.minX);o.maxX=Math.round(o.maxX);return o;});
 if(process.env.QA_OUT){require('fs').mkdirSync(process.env.QA_OUT,{recursive:true});await p.screenshot({path:process.env.QA_OUT+'/demo_rush_run.png'});}
 const bad=[];if(r.rushStarts<1)bad.push('突進を使わない');if(r.out)bad.push('画面外に出た '+r.out);if(r.minX<150||r.maxX>1280-150)bad.push('範囲 '+r.minX+','+r.maxX);
 console.log(JSON.stringify({bad,errors,r}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
