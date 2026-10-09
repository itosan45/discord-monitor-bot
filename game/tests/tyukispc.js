// 幸村の必殺「赤備え突貫」(Lv1・Lv2): 突進で雑兵を槍に掛けて運びながら多段ヒット→最後の一突きでまとめて遠くへ吹き飛ばす。
// 運んだ人数・多段の回数・吹き飛びの速さ・Lv2の十文字の炎の命中を数値で確かめ、各段階の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const bad=[],rows=[],shots=[];
  for(const lv of [1,2]){startGame('yuki',null);G.state='run';G.waveOn=false;G.waves=[{x:1e9,en:[]}];G.wi=0;G.items=[];G.props=[];G.proj=[];G.steeds=[];G.hzT=99999;G.partner=null;
   const f=G.player;f.x=G.camx+220;f.y=570;f.face=1;f.inv=0;f.hp=f.maxhp=999;
   const es=[0,1,2,3].map(i=>{const e=mk(i%2?'spear':'sword',f.x+130+i*70,570+((i%3)-1)*14,1);e.hp=e.maxhp=400;e.entered=true;e.face=-1;e.cool=9999;return e;});
   const back=mk('sword',f.x-120,570,1);back.hp=back.maxhp=400;back.entered=true;back.cool=9999;G.fighters=[f,...es,back];
   f.ki=lv*100;startSpecial(f);const hits=es.map(()=>0),hp=es.map(e=>e.hp);let carried=0,maxV=0,fire=0,shotAt={20:'rush',40:'rush2'};
   let fin=-1;for(let t=0;t<200;t++){G.t++;stepGame();if(f.state==='spc'&&f.st===f.rushEnd+1&&fin<0)fin=t;if(fin>=0&&(t===fin+1||t===fin+16||t===fin+26||t===fin+40)){renderWorld();drawHUD();drawOverlays();shots.push({name:'yukispc-lv'+lv+'-fly'+(t-fin),png:cv.toDataURL('image/png').split(',')[1]});}es.forEach((e,i)=>{if(e.hp<hp[i]){hits[i]++;hp[i]=e.hp;}});
    if(f.state==='spc'&&f.st===f.rushEnd)carried=(f.spcHeld||[]).length;
    if(f.state==='spc'&&f.st>=f.rushEnd+1&&f.st<=f.rushEnd+6)for(const e of es)maxV=Math.max(maxV,Math.abs(e.vx||0));
    if(f.state==='spc'&&shotAt[f.st]&&f.st<=f.rushEnd){renderWorld();drawHUD();drawOverlays();shots.push({name:'yukispc-lv'+lv+'-'+shotAt[f.st],png:cv.toDataURL('image/png').split(',')[1]});delete shotAt[f.st];}}
   const row={lv,rushEnd:f.rushEnd,yukiX:Math.round(f.x-G.camx),enemyX:es.map(e=>Math.round(e.x-G.camx)),carried,hits,maxV:+maxV.toFixed(1),dmg:es.map(e=>400-Math.max(0,e.hp)),behind:400-back.hp,launched:G.yspcN};rows.push(row);
   if(carried<2)bad.push({lv,fewCarried:carried});if(Math.min(...hits.slice(0,2))<6)bad.push({lv,fewMultiHits:hits});if(maxV<9)bad.push({lv,weakLaunch:maxV});}
  return {bad,rows,shots};});
 const dir=(process.env.QA_OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006')+'/qa/yukispc';fs.mkdirSync(dir,{recursive:true});for(const s of r.shots)fs.writeFileSync(dir+'/'+s.name+'.png',Buffer.from(s.png,'base64'));delete r.shots;
 console.log(JSON.stringify({r,errors}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
