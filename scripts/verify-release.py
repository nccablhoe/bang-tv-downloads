"""Verify a staged original-key BANG TV (tv.bang.next) APK against the owner's committed approval.

next.json is the new app's manifest. update.json stays the old tv.bang.preview 0.10.0 manifest
so installed copies of the old app keep reporting 'up to date' instead of failing on another package."""
import hashlib,json,pathlib,re,subprocess,sys

def verify(apk,approval,policy,current,tag,apksigner,aapt2):
    if policy.get('configured') is not True:
        raise ValueError('Original BANG TV signing policy is not configured')
    if not re.fullmatch(r'v\d+\.\d+\.\d+',tag):raise ValueError('Stable release tag required')
    if approval.get('tag')!=tag or approval.get('versionName')!=tag[1:]:raise ValueError('Release approval mismatch')
    if approval.get('packageName')!=policy.get('packageName'):raise ValueError('Wrong application ID')
    expected=policy.get('certificateSha256','')
    if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('Original certificate missing')
    if not re.fullmatch('[0-9a-f]{40}',approval.get('sourceCommit','')):raise ValueError('Exact source provenance required')
    version=approval.get('versionCode',0);previous=approval.get('previousVersionCode',0)
    if type(version) is not int or type(previous) is not int or not 0<previous<version<=2100000000:raise ValueError('Non-increasing version')
    if current.get('releaseAvailable') is not False and version<=current.get('versionCode',0):raise ValueError('Published downgrade')
    if current.get('releaseAvailable') is not False and previous!=current.get('versionCode'):raise ValueError('Published baseline mismatch')
    file=pathlib.Path(apk)
    if not 0<file.stat().st_size<=256*1024*1024 or file.stat().st_size!=approval.get('sizeBytes'):raise ValueError('Size mismatch')
    with file.open('rb') as data:digest=hashlib.file_digest(data,'sha256').hexdigest()
    if digest!=approval.get('sha256'):raise ValueError('SHA-256 mismatch')
    output=subprocess.run([apksigner,'verify','--verbose','--print-certs',str(file)],check=True,capture_output=True,text=True).stdout
    certs=re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([0-9a-f]+)$',output,re.M)
    if certs!=[expected]:raise ValueError('Original signing certificate mismatch')
    output=subprocess.run([aapt2,'dump','badging',str(file)],check=True,capture_output=True,text=True).stdout
    identity=re.search(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'",output,re.M)
    sdk=re.search(r"^(?:minSdkVersion|sdkVersion):'(\d+)'",output,re.M)
    if not identity or (identity[1],int(identity[2]),identity[3])!=(policy['packageName'],version,approval['versionName']):raise ValueError('APK identity mismatch')
    if not sdk or int(sdk[1])!=approval.get('minSdk') or int(sdk[1])<26:raise ValueError('SDK mismatch')
    if 'application-debuggable' in output or "testOnly='true'" in output:raise ValueError('Debug/test APK prohibited')
    if type(approval.get('mandatory',False)) is not bool:raise ValueError('Invalid mandatory flag')
    minimum=approval.get('minimumSupportedVersionCode',0)
    if type(minimum) is not int or not 0<=minimum<=version:raise ValueError('Invalid update floor')
    notes=approval.get('releaseNotes','')
    if not isinstance(notes,str) or len(notes)>16000:raise ValueError('Invalid release notes')
    return dict(schemaVersion=1,releaseAvailable=True,packageName=policy['packageName'],versionCode=version,
        versionName=approval['versionName'],apkUrl=f'https://github.com/nccablhoe/bang-tv-downloads/releases/download/{tag}/BANG-TV.apk',
        sha256=digest,sizeBytes=file.stat().st_size,minSdk=int(sdk[1]),releaseNotes=notes,
        mandatory=approval.get('mandatory',False),minimumSupportedVersionCode=minimum)

if __name__=='__main__':
    apk,tag,signer,aapt=sys.argv[1:]
    manifest=verify(apk,json.load(open('approved.json')),json.load(open('signing-policy.json')),json.load(open('next.json')),tag,signer,aapt)
    pathlib.Path('candidate-update.json').write_text(json.dumps(manifest,indent=2)+'\n')
    pathlib.Path('candidate-sha256.txt').write_text(manifest['sha256']+'  BANG-TV.apk\n')
