# Shadow Modz — local key gate UI test

> **The new local entry screen supports `SHADOWMODZ`, and the old licence dialog renderer is suppressed. This is NOT a native-engine licence unlock or a verified crash fix. Native startup and entitlements remain unchanged.**

## Current download

- [Local-gate testing prerelease v0.2.0](https://github.com/demoneditz985-ctrl/OwnE/releases/tag/shadow-modz-local-gate-test-v0.2.0)
- [Download local-gate test APK — 20.6 MiB](https://github.com/demoneditz985-ctrl/OwnE/raw/shadow-modz-local-gate-test-v0.2.0/artifacts/Shadow-Modz-local-gate-test.apk)
- Key for this **local entry screen**: **`SHADOWMODZ`**
- [How the new gate works, and what it does not unlock](docs/local-key-gate.md)

APK downloads are linked from release notes and hosted in the repository. Binary release-asset uploads are blocked by the workspace's network restrictions.

## New UI-only implementation

The latest request permits replacing the old licence/login page with a new Shadow Modz key page. This test rebuild starts from the untouched original APK, fully decompiles it for inspection, and implements:

- A new black/purple launcher entry screen, Shadow Modz name/emblem and Telegram button.
- Case-sensitive `SHADOWMODZ` validation, rejecting wrong/random/empty keys.
- Private preference storage of local acceptance; opening the original main activity requires a successful save and a rechecked local proof.
- Suppression of only the legacy licence-dialog renderer, with a **four-byte** in-place primary-DEX patch and recomputed header digests.
- Four new classes in a supplemental DEX, not wholesale reassembly of the original code.
- A private original main activity and, on API 28+, component-factory routing for unaccepted attempts to instantiate it.
- Shadow Modz Android label, launcher icons, animated splash vector and resource colours.
- Exact Telegram invite: https://t.me/+BBimnHMiSvpiYTBl

**Native initialization still happens before any activity.** A native signing/integrity fault can still prevent the new screen appearing. The original native activation, bootstrap and game/virtual-app entitlement checks remain intact. Even a successful local entry does not prove protected features work.

This embedded shared-key lock is not a secure DRM service: the key/proof can be extracted, shared, restored or modified. No expiry, device limit or server enforcement is implemented. On API 24–27 AppComponentFactory routing is unavailable; the new launcher route still uses the form.

Some original Compose/native KOS branding and blue colours remain because that code is deliberately not globally rewritten.

## Checks completed

**32** unit/regression tests passed. The pure-string key validator is tested against actual compiled instructions using a deliberately limited interpreter; this is **not** Android/JNI emulation. Audits check the exact permitted original-DEX change, unchanged native/licensing method fingerprints and `.so` bytes, new classes, compiled manifest routing, name/package/SDK/permissions, v2/v3 signatures and ZIP alignment.

No Android device/emulator is attached. Activity lifecycle, phone persistence, startup, original main UI and native features are untested. The initial branding build had a user-reported crash, with no crash trace or Android details supplied. [Crash investigation](docs/crash-diagnosis.md).

## Installing/testing

- ARM64 Android 7/API 24+; package `com.kos`, version code 28.
- The published test uses the same test certificate as prior Shadow Modz test APKs and can update those under normal Android rules. It does not match the original KOS certificate.
- Build scripts do not clear phone data.
- If it closes, report the phone model, Android version, crash point and relevant exception/native signal. Do not send credentials or a full unfiltered device report.

## Build

Linux, Python 3.11+, npm and first-run npm/PyPI access are required. Tooling is pinned and installed into ignored `.tools/`; npm lifecycle scripts are not executed.

```bash
# Latest: local key form + legacy UI suppression; native engine unchanged
bash scripts/build_local_gate_test.sh

# Diagnostic alternative: completely untouched DEX, resources-only rebrand
bash scripts/build_compatibility_test.sh

# Historical code-reassembled build, user-reported crashing
bash scripts/build_branding_test.sh

PYTHONPATH=.tools/python python3 -m unittest discover -s tests -v
```

The keystore/password remain private under ignored `.work/private-signing/`; never commit them. A fresh workspace without that keystore generates a different certificate. The audit explicitly checks whether it matches the previous test.

Full decompile/build intermediates are ignored; they are not recovered native C/C++ source. The repository contains no recovered native project, licence-service project or original signing key. [Original APK assessment](docs/apk-assessment.md). No GitHub Pages generator/backend was built for the single-key request.

## Artifact history

- `artifacts/Shadow-Modz-local-gate-test.apk`, `.sha256`, `local-gate-test-report.json` — new local entry gate, native entitlement replacement **not** implemented.
- `artifacts/Shadow-Modz-compatibility-test.apk`, `.sha256`, `compatibility-test-report.json` — resource-only startup diagnostic, full original DEX retained.
- `artifacts/Shadow-Modz-branding-test.apk`, `.sha256`, `branding-test-report.json` — initial cosmetic build, user-reported crash; **not recommended**.
- `KOS_3.7-VStable.apk` — original input, untouched.
