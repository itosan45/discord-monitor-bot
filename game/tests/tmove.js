// 主人公6人の歩行テンポを抑え、停止時に低い構えへ移ることを確認
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));await p.goto('http://127.0.0.1:8765/index.html');await p.waitForTimeout(3000);
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;window.dropItem=()=>{};const out=[];for(const h of ['yuki','kage','mitsu','nobu','shin','musashi']){G.noStory=true;startGame(h,null);for(let i=0;i<8;i++)stepGame();const p=G.player;p.wp=0;window.ctlKeys=()=>({r:true});for(let i=0;i<60;i++)stepGame();const moving={state:p.state,wp:+p.wp.toFixed(2),frame:sprPos(p,SPR[p.T.spr||p.T.type]).pos};window.ctlKeys=()=>({});for(let i=0;i<3;i++)stepGame();const stopped={state:p.state,frame:sprPos(p,SPR[p.T.spr||p.T.type]).pos};out.push({hero:h,moving,stopped,ready:SPR[p.T.spr||p.T.type].ready});}return out;});
 console.log(JSON.stringify({r,errors:er}));await b.close();if(er.length||r.some(x=>!x.ready||x.moving.state!=='walk'||x.moving.wp<1||x.moving.wp>20||x.stopped.state!=='idle'))process.exit(1);
})();
