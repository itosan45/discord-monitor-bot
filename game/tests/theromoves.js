// 信長(妖刀・散弾・必殺Lv1鉄砲/Lv2火刑)、三成(鉄扇の風の刃・扇ブーメラン)、信玄(風林火山・騎馬隊の幻・軍配受け)の動作検査。
// 各技で敵に当たること、飛び道具が出ること、エラーが無いことを確かめ、攻撃中の画面を保存する。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright'),fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const p=await(await b.newContext({viewport:{width:802,height:360},isMobile:true,hasTouch:true})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const r=await p.evaluate(()=>{requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const bad=[],rows=[],shots=[];
  const setup=(hero,n,dist)=>{startGame(hero,null);G.state='run';G.waveOn=false;G.waves=[{x:1e9,en:[]}];G.wi=0;G.items=[];G.props=[];G.proj=[];G.steeds=[];G.hzT=99999;
   const f=G.player;f.x=G.camx+380;f.y=570;f.face=1;f.hp=f.maxhp=999;f.inv=0;G.partner=null;const es=[];
   for(let i=0;i<n;i++){const e=mk('sword',f.x+dist+i*60,570+((i%3)-1)*30,1);e.hp=e.maxhp=500;e.entered=true;e.face=-1;e.cool=9999;es.push(e);}G.fighters=[f,...es];return {f,es};};
  const run=(n,snapAt,name)=>{for(let t=0;t<n;t++){G.t++;stepGame();if(t===snapAt){renderWorld();shots.push({name,png:cv.toDataURL('image/png').split(',')[1]});}}};
  const dmg=es=>es.reduce((s,e)=>s+(500-Math.max(0,e.hp)),0);
  // 通常攻撃の各段
  for(const hero of ['nobu','mitsu','shin'])for(let i=0;i<4;i++){const {f,es}=setup(hero,3,i===3||hero==='mitsu'?150:90);const kinds=new Set();
   startPAtk(f,i);for(let t=0;t<40;t++){G.t++;stepGame();for(const q of G.proj)kinds.add(q.k);if(t===(f.cur?f.cur.hs+3:8)&&i>=0){renderWorld();shots.push({name:hero+'-atk'+(i+1),png:cv.toDataURL('image/png').split(',')[1]});}}
   const d=dmg(es);rows.push({hero,atk:i+1,damage:Math.round(d),proj:[...kinds],hp:f.hp});if(d<=0)bad.push({hero,atk:i+1,noDamage:true});}
  // 期待する飛び道具
  const want={'nobu-4':'bullet','mitsu-1':'kaze','mitsu-3':'fanboom','shin-1':'kaze','shin-4':'cavghost'};
  for(const [k,v] of Object.entries(want)){const [h,n]=k.split('-');const row=rows.find(x=>x.hero===h&&x.atk==+n);if(!row||!row.proj.includes(v))bad.push({missingProj:k,want:v,got:row&&row.proj});}
  // 信長: 妖刀の吸血(体力が減っている時に回復するか)
  {const {f,es}=setup('nobu',1,90);f.hp=500;startPAtk(f,0);for(let t=0;t<20;t++){G.t++;stepGame();}rows.push({drainHp:f.hp});if(!(f.hp>500))bad.push({noDrain:f.hp});}
  // 三成: 扇ブーメランが手元に戻って消えるか
  {const {f}=setup('mitsu',0,0);startPAtk(f,2);let seen=false,gone=false;for(let t=0;t<140;t++){G.t++;stepGame();const q=G.proj.find(x=>x.k==='fanboom');if(q)seen=true;else if(seen){gone=true;break;}}rows.push({fanReturn:gone});if(!gone)bad.push({fanNotReturned:true});}
  // 信長: 必殺Lv1(鉄砲)とLv2(火刑)
  for(const lv of [1,2]){const {f,es}=setup('nobu',5,200);f.ki=lv*100;startSpecial(f);const cut=G.cut&&G.cut.name;run(130,lv===2?100:30,'nobu-spc'+lv);const d=dmg(es);rows.push({nobuSpc:lv,cut,damage:Math.round(d)});if(d<=0)bad.push({nobuSpc:lv,noDamage:true});if(lv===2&&cut!=='魔王の火刑')bad.push({cutName:cut});}
  // 信玄: 軍配受け(ガード中に正面から斬られたら反撃)
  {const {f,es}=setup('shin',1,70);const e=es[0];f.state='guard';f.st=6;f.gst=0;e.face=-1;const hp0=e.hp;hurt(f,e,{dmg:10,kb:3});rows.push({counterEnemyHp:e.hp});if(!(e.hp<hp0))bad.push({noGunbaiCounter:true});
   const hp1=e.hp;hurt(f,e,{dmg:10,kb:3});if(e.hp<hp1)bad.push({counterNoCooldown:true});}
  return {bad,rows,shots};});
 const dir=(process.env.QA_OUT||'C:/Users/user/Desktop/output/sekigahara-new-20261006')+'/qa/hero-moves';fs.mkdirSync(dir,{recursive:true});for(const s of r.shots)fs.writeFileSync(dir+'/'+s.name+'.png',Buffer.from(s.png,'base64'));delete r.shots;
 console.log(JSON.stringify({r,errors}));if(r.bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
