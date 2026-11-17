const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const script=fs.readFileSync(require('node:path').join(__dirname,'../download.js'),'utf8').replace('document.getElementById("retry").addEventListener("click",check);check();','');
async function run(release,fail=false){const elements={};const context={URL,setTimeout,clearTimeout,AbortController,fetch:async()=>{if(fail)throw Error('offline');return{ok:true,json:async()=>release}},document:{getElementById:id=>elements[id]??(elements[id]={hidden:false,textContent:'',href:'',addEventListener(){}})}};vm.createContext(context);vm.runInContext(script,context);await context.check();return elements;}
(async()=>{
let dom=await run({schemaVersion:1,releaseAvailable:false});assert.equal(dom.download.hidden,true);assert.match(dom.status.textContent,/coming soon/);
const valid={schemaVersion:1,versionName:'1.0.0',versionCode:24,apkUrl:'https://github.com/nccablhoe/bang-tv-downloads/releases/download/v1.0.0/BANG-TV.apk',sizeBytes:1024,sha256:'a'.repeat(64),minSdk:26,releaseNotes:'Fixes'};
dom=await run(valid);assert.equal(dom.download.hidden,false);assert.equal(dom.download.href,valid.apkUrl);
dom=await run({...valid,apkUrl:'https://malicious.example/app.apk'});assert.equal(dom.download.hidden,true);assert.match(dom.status.textContent,/Unable/);
dom=await run(valid,true);assert.equal(dom.download.hidden,true);assert.match(dom.status.textContent,/Unable/);
console.log('4 landing-page checks passed: pending, valid release, rejected foreign URL, offline recovery.');
})().catch(e=>{console.error(e);process.exit(1)});
