// Final boss flow: stop BGM -> call -> chant -> fanfare -> score screen.
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForTimeout(3000);
 const run=async kdLen=>p.evaluate(kdLen=>{window.requestAnimationFrame=()=>0;G.noStory=true;startGame('yuki',null);G.demo=false;
  const events=[];Object.defineProperty(AU,'on',{value:true,configurable:true});AU.ac={currentTime:0};AU.tick=()=>{};AU.taiko=()=>{};AU.sfx=()=>{};
  AU.voBuf.yuki={duration:2.5};AU.bossLine=()=>2.93;AU.voice=k=>events.push([G.stateT,'defeat',k]);AU.stopBgm=()=>events.push([0,'stopBgm']);AU.kc=k=>{events.push([G.stateT,'kc',k]);return true;};AU.kachi=()=>{events.push([G.stateT,'kachi']);AU.kdLen=kdLen;return true;};
  AU.ffBuf={duration:4};AU.fanfare=()=>events.push([G.stateT,'fanfare']);G.wi=G.waves.length-1;bossDown(mk('boss1',640,590,1),G.player);G.slow=0;
  let frames=0;while(G.state==='bossdown'&&frames<1200){stepGame();frames++;}events.push([frames,'score']);return {events,state:G.state};},kdLen);
 // 討ち取ったり→勝鬨の音頭まで1秒(60フレーム)以上あける。敵将の最期のセリフ(2.93秒想定)の後に討ち取ったり
 // 勝鬨の声の長さ(末尾の無音を除く): 実際の2種類 3.12秒・4.73秒。ファンファーレは声の終わる0.3秒前〜直後に始まること
 let fail=false;for(const kdLen of [3.12,4.73]){const r=await run(kdLen);console.log(JSON.stringify({kdLen,r,errors}));
 const ev=r.events,call=ev.find(e=>e[1]==='kc'),chant=ev.find(e=>e[1]==='kachi'),fan=ev.find(e=>e[1]==='fanfare'),score=ev.find(e=>e[1]==='score');
 const defeat=ev.filter(e=>e[1]==='defeat');
 if(errors.length||defeat[0]&&defeat[0][0]<Math.ceil(2.93*60)+24||ev[0][1]!=='stopBgm'||defeat.length!==1||!call||call[0]<defeat[0][0]+2.5*60+60||!chant||chant[0]-call[0]!==192||!fan||fan[0]<chant[0]+(kdLen-0.3)*60-1||fan[0]>chant[0]+kdLen*60+6||score[0]<=fan[0]+4*60||r.state!=='clear')fail=true;}
 await b.close();if(fail)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1);});
