# Official BANG TV downloads

This repository hosts public distribution metadata and website tooling. BANG TV application source, credentials, signing keys, and user playlists are not stored here.

- Website: https://nccablhoe.github.io/bang-tv-downloads/
- Permanent installation page: https://nccablhoe.github.io/bang-tv-downloads/download/
- Live manifest (new BANG TV, `tv.bang.next`): https://raw.githubusercontent.com/nccablhoe/bang-tv-downloads/main/next.json
- Old app manifest (`tv.bang.preview`, frozen at 0.10.0 so installed copies stay quiet): https://raw.githubusercontent.com/nccablhoe/bang-tv-downloads/main/update.json
- Stable direct APK endpoint after the first approved release: https://github.com/nccablhoe/bang-tv-downloads/releases/latest/download/BANG-TV.apk

**From 1.0.0 this channel serves the new BANG TV (`tv.bang.next`, owner decision 2026-11-25).** The Downloader code and `releases/latest/download/BANG-TV.apk` follow the newest release, so they move to the new app when 1.0.0 is published. `update.json` is no longer written; it stays at the old app's 0.10.0 so that app's updater does not offer a different package.

Previous published release: **0.10.0 (versionCode 24)**, old app `tv.bang.preview`. The original-key, non-debuggable APK passed integrity and original-certificate checks and a cloud in-place upgrade from build 22. The permanent APK URL and manifest were anonymously downloaded and their exact size/SHA-256 verified. No disposable-signer validation APK is published.

The installation page reads the live manifest instead of hardcoding a version. APK URLs in manifests are immutable versioned release assets. Verified Downloader code: **9286403** — https://aftv.news/9286403. It points to the permanent direct APK endpoint (`releases/latest/download/BANG-TV.apk`). The official shortener returned this code; a cloud browser followed its redirect and downloaded the exact published APK (8,512,935 bytes, matching SHA-256). Physical installation through the Downloader app has not yet been tested.

Release workflow: stage the original-key signed APK as `BANG-TV.apk` in a draft release; commit an owner-reviewed `approved.json` binding its source, certificate, version, byte size and SHA-256; manually run Publish approved release behind the `bang-tv-public-release` environment approval. GitHub exposes draft releases only to push-capable tokens, so the environment gates validation before its short-lived contents-write token is issued. Publication depends on successful validation and revalidates the same staged bytes and unchanged approval commit. No source push triggers a release. The signer stays in its established cloud environment.

GitHub Pages serves only the small website. APKs use GitHub Releases. No paid hosting, LFS, custom domain or analytics is configured.

The release environment requires approval by the owner (`nccablhoe`), disallows administrator bypass, and restricts deployment to `main`. Published releases are configured immutable. The signing policy pins the original package and public certificate, independently verified against previously delivered build 22. The private signing key remains in its original cloud environment. At setup, no APK had been published; `update.json` is the current release authority.

Validation: `python3 scripts/test_release.py` (10 controlled tool-output checks) and `node scripts/test_download.cjs` (4 landing-state checks). These tests do not establish Android installation compatibility.
