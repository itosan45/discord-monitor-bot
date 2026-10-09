const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch();
 const p=await (await b.newContext({viewport:{width:1280,height:720}})).newPage();
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8765/index.html');
 await p.waitForTimeout(2500);
 const r=await p.evaluate(()=>{
  G.heroPick='yuki';G.selStep=1;
  const yuki=partnerOpts();
  G.heroPick='kage';const kage=partnerOpts();
  G.noStory=true;startGame('yuki','nezu');const q=G.partner,S=SPR.nezu;
  const frames=new Set();let drawn=true;
  if(q&&S&&S.ready){q.x=640;q.y=590;q.face=1;for(let i=0;i<TY.nezu.atk[0].dur;i++){
   q.state='atk';q.cur=TY.nezu.atk[0];q.st=i;const sp=sprPos(q,S);frames.add(Math.floor(sp.pos));drawn=drawSprite(q)&&drawn;
  }}else drawn=false;
  return {yukiHasNezu:yuki.includes('nezu'),kageHasNezu:kage.includes('nezu'),
   nezuName:TY.nezu&&TY.nezu.name,nezuSprite:!!(S&&S.ready),partner:{type:q&&q.type,team:q&&q.team,isPartner:q&&q.isPartner,inFighters:q&&G.fighters.includes(q)},
   attackFrames:frames.size,attackFrameTotal:S&&S.a.a1&&S.a.a1.length,attackDrawn:drawn};
 });
 if(!r.yukiHasNezu||r.kageHasNezu||r.nezuName!=='根津甚八'||!r.nezuSprite||r.partner.type!=='nezu'||r.partner.team!==0||!r.partner.isPartner||!r.partner.inFighters||r.attackFrames!==r.attackFrameTotal||!r.attackDrawn||errors.length){
  console.error(JSON.stringify({result:r,pageErrors:errors}));process.exitCode=1;
 }else console.log(JSON.stringify({result:r,pageErrors:errors}));
 await b.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
