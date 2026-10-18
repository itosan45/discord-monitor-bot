// 現在のゲーム内描画から馬・主人公・武器を一枚に合成した馬上攻撃コマを採取する。
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
const root=path.resolve(__dirname,'../..');
const heroes={yuki:'真田幸村',kage:'上杉景勝',mitsu:'石田三成',nobu:'織田信長',shin:'武田信玄',musashi:'宮本武蔵'};
const profiles={default:'主武器',odachi:'長剣',naginata:'薙刀',teppo:'火縄銃',yoto:'妖刀',ono:'斧',konbou:'棍棒',takeyari:'竹槍',kusari:'鎖鎌',yumi:'弓矢'};
const weapon=Object.fromEntries(Object.keys(profiles).filter(k=>k!=='default').map(k=>[k,k]));
const frames=[0,6,10,16,22],W=576,H=416;
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||'http://127.0.0.1:8876/index.html');await p.waitForFunction(()=>sprAllReady());
 const sheets=await p.evaluate(({heroes,profiles,weapon,frames,W,H})=>{
  window.requestAnimationFrame=()=>0;G.noStory=true;G.lowq=true;const out=[];
  for(const [hero] of Object.entries(heroes)){if(hero!=='musashi')continue;
   startGame(hero,null);for(let n=0;n<50&&!Object.values(SPR).every(s=>s.ready||s.failed);n++){};
   const mount=SPR['mount_'+({yuki:'red',kage:'blue',mitsu:'purple',nobu:'red',shin:'red',musashi:'iron'}[hero])];
   if(!mount?.ready||!SPR[hero]?.ready)throw Error('sprite load failed: '+hero);
   for(const k of ['mountatk_','mountatk2_','mountfull3_'])if(SPR[k+hero])SPR[k+hero].ready=false;
   // Reuse the clean attack pose sequence; the alternate a3 art contains baked-in slash arcs.
   for(const k of [hero,hero+'_u'])if(SPR[k]?.a?.a1)SPR[k].a.a3=SPR[k].a.a1;
   for(const [profile] of Object.entries(profiles)){
    const c=document.createElement('canvas');c.width=W*frames.length;c.height=H;const x=c.getContext('2d');
    const f=mk(hero,640,400,0);f.mount={hp:6,max:6,col:({yuki:'red',kage:'blue',mitsu:'purple',nobu:'red',shin:'red',musashi:'iron'}[hero])};f.face=1;f.sc=1;f.z=0;f.flash=0;f.t=0;f.wp=0;f.state='matk';f.cur=MATK;f.hit=new Set();f.mountedDefault=profile==='default';f.wpn=weapon[profile]?{k:weapon[profile],uses:30}:null;
    const distinct=[];
    frames.forEach((st,i)=>{f.st=st;f.t=i*2;ctx.clearRect(0,0,1280,720);if(!drawRiderPlayer(f))throw Error('draw failed: '+hero+'/'+profile);x.drawImage(ctx.canvas,352,16,W,H,i*W,0,W,H);distinct.push(i);});
    out.push({hero,profile,png:c.toDataURL('image/png')});
   }
  }
  return out;
 },{heroes,profiles,weapon,frames,W,H});
 if(errors.length)throw Error(errors.join('\n'));
 const dest=process.env.OUT;if(!dest)throw Error('OUT is required; never overwrite original sprites');fs.mkdirSync(dest,{recursive:true});
 for(const s of sheets){const filename=`馬上攻撃_${heroes[s.hero]}_${profiles[s.profile]}_5コマ_v3.png`;fs.writeFileSync(path.join(dest,filename),Buffer.from(s.png.split(',')[1],'base64'),{flag:'wx'});}
 console.log(JSON.stringify({sheets:sheets.length,dimensions:[W*frames.length,H],output:dest,errors}));await b.close();
})().catch(e=>{console.error(e);process.exit(1);});
