"use strict";
const manifestUrl="https://raw.githubusercontent.com/nccablhoe/bang-tv-downloads/main/next.json";
async function check(){
 const status=document.getElementById("status"),details=document.getElementById("details"),link=document.getElementById("download"),notes=document.getElementById("notes");
 link.hidden=true;notes.hidden=true;status.textContent="Checking release availability…";
 try{
  const controller=typeof AbortController==="function"?new AbortController():null;
  const timeout=setTimeout(function(){if(controller)controller.abort();},15000);
  let response;try{response=await fetch(manifestUrl,{cache:"no-store",signal:controller?controller.signal:undefined});}finally{clearTimeout(timeout);}
  if(!response.ok)throw Error("manifest");const release=await response.json();
  if(release.schemaVersion!==1)throw Error("schema");
  if(release.releaseAvailable===false){status.textContent="Compatible signed release coming soon";details.textContent="The download channel is ready. The first original-key APK is completing release verification. No test APK is offered here.";return;}
  const url=new URL(release.apkUrl);
  if(url.origin!=="https://github.com" || !/^\/nccablhoe\/bang-tv-downloads\/releases\/download\/[A-Za-z0-9._-]+\/BANG-TV\.apk$/.test(url.pathname) || url.search || url.hash || url.username || url.password || !Number.isSafeInteger(release.versionCode) || release.versionCode<1 || !Number.isSafeInteger(release.sizeBytes) || release.sizeBytes<1 || !/^[a-f0-9]{64}$/i.test(release.sha256))throw Error("release");
  status.textContent="BANG TV "+release.versionName;details.textContent=(release.sizeBytes/1048576).toFixed(1)+" MB · Android API "+release.minSdk+" or newer. Choose Download APK, then approve installation.";
  link.href=url.href;link.hidden=false;notes.textContent=String(release.releaseNotes||"");notes.hidden=false;
 }catch(_){status.textContent="Unable to check right now";details.textContent="Check your connection and try again. Your installed BANG TV app is unaffected.";}
}
document.getElementById("retry").addEventListener("click",check);check();
