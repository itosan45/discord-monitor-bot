// ゲーム進行でのBGM切り替え: 各ステージの曲、ボス出現で3、最終幕の家康でラスボス曲10、エンディングで11。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--autoplay-policy=no-user-gesture-required']});
 const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 let r;try{r=await p.evaluate(async()=>{
  window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const bad=[],rows=[];
  for(let si=0;si<6;si++){startStage(si,'yuki',false);if(AU.want!==STG[si].bgm)bad.push({stage:si,want:AU.want});
   const bosses=[];for(const w of LV[si].waves)if(w.boss)bosses.push(w.boss);
   for(const k of bosses){G.state='run';const e=spawnEn(k,1);const exp=(si===5&&k==='boss3')?10:3;if(AU.want!==exp)bad.push({stage:si,boss:k,want:AU.want,exp});rows.push({si,k,want:AU.want});}}
  return{bad,rows};});}catch(e){console.error(e.message);await b.close();process.exit(1);}
 const src=require('fs').readFileSync(require('path').join(__dirname,'..','game_src.html'),'utf8');
 const endOk=/AU\.bgm\(11\);const fin=/.test(src);if(!endOk)r.bad.push('ending bgm not 11');
 console.log(JSON.stringify(r),errors);await b.close();if(r.bad.length||errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
