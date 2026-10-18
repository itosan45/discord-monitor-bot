// ユーザー録音4種(掛け声 hey/seiya は オーナー録音 pk があればそちらが優先)の埋め込み、復号、イベント割当て、音量が有効であることを確認
const {chromium}=require(process.env.PLAYWRIGHT||'playwright');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_BIN||'C:/Program Files/Google/Chrome/Application/chrome.exe'});const p=await(await b.newContext({viewport:{width:1280,height:720}})).newPage();const er=[];p.on('pageerror',e=>er.push(e.message));
 await p.goto('http://127.0.0.1:8765/index.html');await p.mouse.click(640,360);await p.waitForTimeout(5000);
 const r=await p.evaluate(async()=>{
  AU.init();if(AU.ac.state==='suspended')await AU.ac.resume();for(let i=0;i<100&&!AU.userVoiceBuf?.victory;i++)await new Promise(r=>setTimeout(r,50));
  const keys=['charge','hey','seiya','victory'],buffers=Object.fromEntries(keys.map(k=>{const b=AU.userVoiceBuf?.[k];if(!b)return[k,null];let sum=0,peak=0;for(let i=0;i<b.length;i+=40){const x=Math.abs(b.getChannelData(0)[i]);sum+=x*x;peak=Math.max(peak,x);}return[k,{duration:+b.duration.toFixed(2),rms:+Math.sqrt(sum/Math.ceil(b.length/40)).toFixed(4),peak:+peak.toFixed(3)}];}));
  const calls=[],orig=AU.userVoice.bind(AU);AU.userVoice=(k,v)=>{calls.push(k);return orig(k,v);};
  const charge=AU.userVoice('charge',1.28);AU.kiai({isPartner:false},true);await new Promise(r=>setTimeout(r,720));AU.kiai({isPartner:false},true);const victory=AU.kc('call',1,1.35);
  return {pk:(AU.pkBuf||[]).length>=6,state:AU.ac.state,on:AU.on,buffers,calls,charge,victory};
 });
 console.log(JSON.stringify({r,errors:er}));await b.close();if(er.length||!r.on||r.calls.join(',')!==(r.pk?'charge,victory':'charge,hey,seiya,victory')||!r.charge||!r.victory||Object.values(r.buffers).some(x=>!x||x.rms<0.01||x.peak>1))process.exit(1);
})();
