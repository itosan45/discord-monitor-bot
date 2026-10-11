// 2026-10-11 納品の新素材: 馬上旋風8コマ(全6人)、景勝の居合・踏み込み一文字、武蔵の二刀連撃、信玄の軍配押し打ち、信長の片手大薙ぎ、三成の鉄扇空中回転。
// 主武器だけに使い、拾得武器(別の絵)・他の攻撃では使わない。画面端でも欠けない(描画矩形が画面内)。QA_OUTで命中の瞬間の画面を保存。
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_BIN});
 try{const p=await(await b.newContext({viewport:{width:802,height:360}})).newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(process.argv[2]||process.env.GAME_URL);await p.waitForFunction(()=>sprAllReady(),null,{timeout:120000});
 const r=await p.evaluate(()=>{window.requestAnimationFrame=()=>0;AU.muted=true;G.noStory=true;const out={};
  const used=new Map();const od=CanvasRenderingContext2D.prototype.drawImage;let off=null;
  CanvasRenderingContext2D.prototype.drawImage=function(img,...a){if(used.has(img)){const m=this.getTransform();const sx=a[0],sy=a[1];used.get(img).add(sx+','+sy);if(a.length>=8){const x=m.a*a[4]+m.e,w=m.a*a[6];const L=Math.min(x,x+w),R=Math.max(x,x+w);const rec=used.get(img);rec.minX=Math.min(rec.minX??1e9,L);rec.maxX=Math.max(rec.maxX??-1e9,R);}}return od.call(this,img,...a);};
  const setup=(hero,mount,edge)=>{startGame(hero,null);G.waveOn=false;G.waves=[{x:999999,en:[]}];G.fighters=G.fighters.filter(f=>f.team===0);G.banner=null;const P=G.player;P.wpn=null;P.mount=mount?{hp:6,max:6,col:'red'}:null;P.x=edge===0?G.camx+640:edge<0?G.camx+fighterScreenMargin(P):G.camx+W-fighterScreenMargin(P);P.y=570;P.face=edge>0?-1:1;P.inv=999;P.state='idle';return P;};
  const track=k=>{const S=SPR[k];const set=new Set();used.set(S.img,set);return set;};
  // 1. 馬上旋風(8コマ): 6人×左右
  out.whirl=[];for(const hero of ['yuki','kage','mitsu','nobu','shin','musashi'])for(const face of [1,-1]){const s=track('mountwhirl2_'+hero);const P=setup(hero,true,0);P.face=face;const e=mk('sword',P.x+face*150,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);G.t++;updMount(P,{gdP:true});for(let i=0;i<80&&P.state==='matk';i++){G.t++;updMount(P,{});ctx.setTransform(RS,0,0,RS,0,0);drawFighter(P);}out.whirl.push({hero,face,frames:s.size});used.delete(SPR['mountwhirl2_'+hero].img);}
  // 2. 徒歩の新しい攻撃
  const cases=[['kage','iai',P=>{startCharge(P);},true],['kage','ichi',P=>{P.state='atk';P.st=0;P.cur=Object.assign({},TY.kage.atk[3],{});P.cur.base=TY.kage.atk[3];P.hit.clear();},true],['musashi','nito',P=>{P.state='atk';P.st=0;P.cur=TY.musashi.atk[1];P.hit.clear();},true],['shin','push',P=>{P.state='atk';P.st=0;P.cur=TY.shin.atk[2];P.hit.clear();},true],['nobu','sweep',P=>{P.state='atk';P.st=0;P.cur=TY.nobu.atk[1];P.hit.clear();},true]];
  out.atk=[];for(const [hero,nm,start] of cases)for(const edge of [0,-1,1]){const s=track('atk3_'+hero);const P=setup(hero,false,edge);const e=mk('sword',P.x+P.face*120,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);start(P);let n=0,minX=1e9,maxX=-1e9;const rec=s;
   for(;n<80&&P.state==='atk';n++){G.t++;updPlayer(P,{});ctx.setTransform(RS,0,0,RS,0,0);drawFighter(P);}
   out.atk.push({hero,nm,edge,frames:s.size,minX:Math.round(s.minX??0),maxX:Math.round(s.maxX??0),n});used.delete(SPR['atk3_'+hero].img);}
  // 3. 拾得武器・他の攻撃では使わない
  out.other=[];for(const [hero,idx] of [['kage',0],['kage',1],['musashi',0],['shin',0],['nobu',0]]){const s=track('atk3_'+hero);const P=setup(hero,false,0);P.state='atk';P.st=0;P.cur=TY[hero].atk[idx];P.hit.clear();for(let i=0;i<20;i++){G.t++;updPlayer(P,{});drawFighter(P);}
   const P2=setup(hero,false,0);P2.wpn={k:'odachi',uses:99};P2.state='atk';P2.st=0;P2.cur=TY[hero].atk[idx===0?3:1]||TY[hero].atk[0];P2.hit.clear();for(let i=0;i<20;i++){G.t++;updPlayer(P2,{});drawFighter(P2);}out.other.push({hero,idx,frames:s.size});used.delete(SPR['atk3_'+hero].img);}
  // 4. 三成の鉄扇ブーメラン
  {const s=track('atk3_mitsu');const P=setup('mitsu',false,0);const e=mk('sword',P.x+200,570,1);e.entered=true;e.hp=e.maxhp=9999;e.cool=9999;G.fighters.push(e);P.state='atk';P.st=0;P.cur=TY.mitsu.atk[2];P.hit.clear();for(let i=0;i<60;i++){G.t++;updPlayer(P,{});stepGame();ctx.setTransform(RS,0,0,RS,0,0);renderWorld();}out.fan=s.size;}
  CanvasRenderingContext2D.prototype.drawImage=od;out.cw=ctx.canvas.width;return out;});
 console.log(JSON.stringify(r));
 const bad=[];for(const o of r.whirl)if(o.frames<8)bad.push('whirl'+o.hero+o.face+':'+o.frames);
 for(const o of r.atk){if(o.frames<4)bad.push('atk'+o.hero+o.nm+o.edge+':'+o.frames);if(o.minX<-1||o.maxX>r.cw+1)bad.push('edge'+o.hero+o.nm+o.edge+':'+o.minX+'/'+o.maxX);}
 for(const o of r.other)if(o.frames>0)bad.push('used-other:'+o.hero+o.idx);
 if(r.fan<4)bad.push('fan'+r.fan);
 console.log(JSON.stringify({bad,errors}));if(bad.length||errors.length)process.exitCode=1;
 }finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
