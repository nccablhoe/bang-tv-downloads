import hashlib,importlib.util,pathlib,tempfile,types,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('release',pathlib.Path(__file__).with_name('verify-release.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ReleaseTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.apk=pathlib.Path(self.temp.name)/'app.apk';self.apk.write_bytes(b'fixture only, not an APK')
  self.policy=dict(configured=True,packageName='tv.bang.preview',certificateSha256='b'*64)
  self.approval=dict(tag='v1.0.0',versionName='1.0.0',versionCode=24,previousVersionCode=22,packageName='tv.bang.preview',sourceCommit='a'*40,sizeBytes=self.apk.stat().st_size,sha256=hashlib.sha256(self.apk.read_bytes()).hexdigest(),minSdk=26,releaseNotes='Fixes')
  self.current=dict(releaseAvailable=False)
 def run_gate(self,cert=None,badging=None):
  def tool(args,**kw):return types.SimpleNamespace(stdout=('Signer #1 certificate SHA-256 digest: '+(cert or 'b'*64)+'\n') if args[0]=='signer' else (badging or "package: name='tv.bang.preview' versionCode='24' versionName='1.0.0'\nminSdkVersion:'26'\n"))
  with patch.object(m.subprocess,'run',side_effect=tool):return m.verify(self.apk,self.approval,self.policy,self.current,'v1.0.0','signer','aapt2')
 def test_valid_manifest(self):
  result=self.run_gate();self.assertTrue(result['releaseAvailable']);self.assertFalse(result['mandatory']);self.assertEqual(result['sha256'],self.approval['sha256'])
 def test_unconfigured_signer(self):
  self.policy['configured']=False
  with self.assertRaises(ValueError):self.run_gate()
 def test_wrong_certificate(self):
  with self.assertRaises(ValueError):self.run_gate(cert='c'*64)
 def test_tampered_bytes(self):
  self.apk.write_bytes(b'tampered')
  with self.assertRaises(ValueError):self.run_gate()
 def test_wrong_package(self):
  self.approval['packageName']='another.app'
  with self.assertRaises(ValueError):self.run_gate()
 def test_preview(self):
  self.approval['versionName']='1.0.0-preview'
  with self.assertRaises(ValueError):self.run_gate()
 def test_debug(self):
  with self.assertRaises(ValueError):self.run_gate(badging="package: name='tv.bang.preview' versionCode='24' versionName='1.0.0'\nminSdkVersion:'26'\napplication-debuggable\n")
 def test_downgrade(self):
  self.current=dict(releaseAvailable=True,versionCode=24)
  with self.assertRaises(ValueError):self.run_gate()
 def test_baseline_drift(self):
  self.current=dict(releaseAvailable=True,versionCode=23)
  with self.assertRaises(ValueError):self.run_gate()
 def test_mandatory_type(self):
  self.approval['mandatory']='yes'
  with self.assertRaises(ValueError):self.run_gate()
if __name__=='__main__':unittest.main()
