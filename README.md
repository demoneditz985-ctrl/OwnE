# Shadow Modz — startup compatibility test

> **The first branding-test build has a user-reported crash. The new compatibility test is a diagnostic candidate, not a confirmed crash fix. `SHADOWMODZ` and "any random key works" are not implemented. Native licensing remains unchanged.**

## Current download

- [Compatibility testing prerelease v0.1.1](https://github.com/demoneditz985-ctrl/OwnE/releases/tag/shadow-modz-compatibility-test-v0.1.1)
- [Download compatibility-test APK — 20.6 MiB](https://github.com/demoneditz985-ctrl/OwnE/raw/shadow-modz-compatibility-test-v0.1.1/artifacts/Shadow-Modz-compatibility-test.apk)
- [Crash investigation and optional logcat instructions](docs/crash-diagnosis.md)

APK downloads are linked from release notes and hosted in this repository. Binary release-asset uploads are blocked by the workspace's network restrictions.

## What changed after the crash report?

The initial cosmetic build reassembled the entire DEX and added two branding/contact helpers. It passed compilation, signature and selected-class static checks, but the user subsequently reported a crash with no error/device details.

The compatibility candidate instead:

- Uses Apktool **`--no-src`**, preserving the **complete original DEX byte-for-byte**.
- Removes the injected Compose text hook, Compose colour edits and Telegram callback.
- Retains the **Shadow Modz** Android label, launcher icons and black/purple Android resource colours.
- Preserves the original animated splash drawable/type and animator target, changing only its vector emblem.
- Preserves native libraries, package, launcher, permissions, version and SDK requirements.
- Reuses the previous local test signing certificate, when present; the published candidate's certificate matches v0.1.0.
- Passes **22** unit/regression tests and APK signature/static audits.

This removes potential bytecode/layout regressions. It does **not** identify the actual crash cause or establish that the packed native library accepts re-signing. There is no attached Android device or emulator.

### Trade-offs

Some Compose/native KOS text and blue colours remain because original code is deliberately preserved. The compatibility candidate does not inject a Telegram action. The requested invite is still documented: https://t.me/+BBimnHMiSvpiYTBl

## Licence status

The original key format, native activation (`NativeBridge.d(..., 1009)`), native setup and engine checks are unchanged. No fake success callback or unconditional "all keys valid" result has been added. A key input comparison alone would not prove that the engine accepts a new entitlement.

The repository contains an APK only; no native source, licence-service project or original signing key was recovered. [APK assessment](docs/apk-assessment.md).

A single shared key also does not securely enforce device limits or first-use expiry. No GitHub Pages generator/backend was built for the latest single-key request.

## Testing

- Requires ARM64 Android 7.0/API 24+.
- Package remains `com.kos`, version code 28, preserving JNI references and native metadata expectations.
- The candidate's certificate matches the earlier **Shadow Modz test APK**, allowing an in-place update of that test installation under normal Android rules. It does **not** match the original KOS signing identity.
- No phone data is cleared by the build scripts.
- If it still closes, send the phone model, Android version and where it closes (startup, activation or game launch). A relevant exception/native crash trace is needed to identify the actual fault. Do not send credentials or a full unfiltered device report.

## Build

Linux, Python 3.11+, npm and first-run npm/PyPI access are required. Pinned tooling is bootstrapped into ignored `.tools/`; npm lifecycle scripts are not executed.

```bash
# Conservative diagnostic candidate: original DEX, resources-only patch
bash scripts/build_compatibility_test.sh

# Historical code-patched build, now user-reported crashing
bash scripts/build_branding_test.sh

# Tests after the tool bootstrap
PYTHONPATH=.tools/python python3 -m unittest discover -s tests -v
```

Both pipelines preserve `KOS_3.7-VStable.apk`, align stored native libraries to 16 KiB, test-sign with a locally generated certificate and verify the output before writing deliverables.

The test keystore and its random password are in ignored `.work/private-signing/` with restricted permissions. They are not an app licence or the original signing key. Never commit them. A fresh workspace without that keystore generates a different test certificate; the report explicitly records whether the previous test certificate matches.

## Artifacts

- `artifacts/Shadow-Modz-compatibility-test.apk`, `.sha256`, `compatibility-test-report.json` — current resource-only diagnostic candidate.
- `artifacts/Shadow-Modz-branding-test.apk`, `.sha256`, `branding-test-report.json` — historical cosmetic build with a user-reported crash; retained for comparison, **not recommended**.
- `KOS_3.7-VStable.apk` — original input, untouched.
