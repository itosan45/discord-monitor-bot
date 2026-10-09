// BGM: 全曲が読み込めて長さが妥当か、ステージ→曲の対応、ボス曲・ラスボス曲・エンディング曲の切り替え、古い曲の解放を確認する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--autoplay-policy=no-user-gesture-required']});
 const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');
 const r=await p.evaluate(async()=>{
  const bad=[],out={};AU.init();await AU.load();
  const wait=async(f,ms=15000)=>{const t=Date.now();while(!f()&&Date.now()-t<ms)await new Promise(r=>setTimeout(r,50));return f();};
  out.stageBgm=STG.map(s=>s.bgm);
  const expectStage=[0,1,5,6,7,2];if(JSON.stringify(out.stageBgm)!==JSON.stringify(expectStage))bad.push({stageBgm:out.stageBgm});
  out.len={};
  for(const i of [1,2,3,5,6,7,10,11]){AU.bgm(i);const ok=await wait(()=>AU.bgmBuf[i]);if(!ok){bad.push({load:i});continue;}const d=AU.bgmBuf[i].duration;out.len[i]=+d.toFixed(1);if(d<30||d>90)bad.push({dur:i,d});if(AU.bgmBuf[i].numberOfChannels!==2)bad.push({ch:i});await wait(()=>AU.cur===i,5000);if(AU.cur!==i)bad.push({notPlaying:i});}
  out.decoded=AU.bgmBuf.map((x,i)=>x?i:null).filter(x=>x!==null);if(out.decoded.length>5)bad.push({memory:out.decoded});
  // ボス曲の選択
  G.stage=1;if(bossBgm({T:{type:'boss4'}})!==3)bad.push('boss!=3');if(bossBgm({T:{type:'boss3'}})!==3)bad.push('stage2 boss3 should be 3');
  G.stage=5;if(bossBgm({T:{type:'boss3'}})!==10)bad.push('final!=10');if(bossBgm({T:{type:'boss1'}})!==3)bad.push('stage6 boss1 should be 3');
  return{bad,out};});
 console.log(JSON.stringify(r),errors);await b.close();if(r.bad.length||errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
