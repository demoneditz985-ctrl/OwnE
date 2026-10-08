# Shadow Modz — APK branding test

> **Important: this is NOT a licence-unlocked app. `SHADOWMODZ` is the requested new key, but it has not been installed as a working replacement licence. The original native licensing remains unchanged.**

## Download

- [GitHub testing prerelease](https://github.com/demoneditz985-ctrl/OwnE/releases/tag/shadow-modz-branding-test-v0.1.0)
- [Direct APK download — 20.9 MiB](https://github.com/demoneditz985-ctrl/OwnE/raw/957a1058f3950c13d984f124b476635aa62c8c56/artifacts/Shadow-Modz-branding-test.apk)

The APK is hosted at a pinned repository commit and linked from the prerelease notes. It is not attached as a binary release asset: the workspace could not reach GitHub's release-asset upload endpoint. The direct link downloads the same signed branding-test APK described below.

This repository originally contained only `KOS_3.7-VStable.apk`, not the Android project or native source. The owner's latest request is a single key named **`SHADOWMODZ`**, plus the **Shadow Modz** name, black/purple styling, and [Telegram invite](https://t.me/+BBimnHMiSvpiYTBl).

## Delivered

- **`artifacts/Shadow-Modz-branding-test.apk`** — a rebuilt, locally test-signed cosmetic APK.
- Shadow Modz app label, launcher/round/adaptive icons and splash emblem.
- Black/purple Android resource and Compose palettes.
- Visible `KOS` words in resource strings and Compose-rendered plain text changed to `Shadow Modz`. Internal package/JNI/protocol identifiers are intentionally preserved.
- The activation dialog's secondary contact button now says **Join Shadow Modz on Telegram** and opens the supplied invite. It does not activate a licence.
- Reproducible patch/build scripts, regression tests, APK SHA-256, and a machine-readable static audit report.
- The original APK is unchanged.

## Not completed / not verified

| Item | Status |
| --- | --- |
| Replace the native licence with `SHADOWMODZ` | **Not implemented** |
| Recover the old key or signing certificate | Not recovered |
| Confirm the APK launches on Android | Not runtime-tested; no Android device/emulator was available |
| Unlock the native engine / original app features | Not implemented or verified |
| Fully remove protected/native/server-rendered KOS branding | Not verified |
| First-use expiry and device limits | Not implemented; the latest request asks for one fixed key |
| GitHub Pages generator | Not built or deployed for this single-key request |

The original activation code calls `NativeBridge.d(..., 1009)`, and app-launch eligibility also calls native functions in `libkos.so`. A text comparison against `SHADOWMODZ`, a fake success toast, or an extra login screen would **not prove the native engine accepts that licence**. Those checks have not been replaced with unconditional success.

**A new signing certificate is unavoidable without the original signing key.** The original native integrity/licensing logic may reject this re-signed test build. See [the APK assessment](docs/apk-assessment.md).

## Before testing on a phone

1. Prefer a spare/test Android device. The input APK supports **ARM64 only**, Android **7.0/API 24 or newer**.
2. Keep the original APK and back up any important app/profile data. This build keeps the package ID `com.kos` to avoid breaking JNI and engine references.
3. **Do not uninstall your existing app just to try this build unless you have backed up its data.** A differently signed APK cannot be installed as an in-place update; Android will report a signature conflict.
4. Installing successfully does not mean licence activation or native-engine operation will work.
5. If you test it, report the screen/error and Android version. Do not send passwords, tokens, or signing credentials in chat.

## Build locally

Requirements: Linux, Python 3.11+, npm, and internet access to npm/PyPI on the first run. Java and the inspection tools are installed under ignored `.tools/`.

```bash
bash scripts/build_branding_test.sh
```

The script:

1. Verifies the original APK and tool JAR checksums.
2. Runs the Python regression tests.
3. Decodes a fresh copy into ignored `.work/shadowmodz/`.
4. Applies the cosmetic-only patches from `branding/` and `apk-patches/`.
5. Rebuilds, aligns uncompressed native-library entries to **16 KiB**, and signs with a **new local test certificate**.
6. Verifies v2/v3 APK signatures, manifest metadata, ZIP alignment, unchanged native library bytes, and unchanged native licensing/activation DEX paths.
7. Writes the test APK, checksum, and report to `artifacts/`.

This uses Apktool 2.9.3 and apksigner 0.9, vendored in the pinned npm package `@postar/apktool-node@0.3.4`. No npm lifecycle scripts are executed. These are build tools only, not recovered app source.

The locally generated test keystore and its random password are in ignored `.work/private-signing/`, with restricted file permissions. They are **not** the original app signing key, the app licence, or a production credential. Never commit them. Rebuilds in the same workspace reuse that test certificate; a fresh workspace generates a different one.

Tests alone, after installing `requirements-tools.txt` under `.tools/python`:

```bash
PYTHONPATH=.tools/python python3 -m unittest discover -s tests -v
```

## What would unblock the real fixed key?

Recover the source that builds `libkos.so` (including its licence/entitlement logic), or recover owner access to the existing licensing service so a valid entitlement can be issued. A reliably tested binary-level replacement would require additional native reverse engineering and Android runtime testing; this build does not claim to provide it.

A shared offline key can be extracted or shared. It does not securely enforce per-device limits or first-use expiration. If those earlier requirements return, a trusted licensing backend is required; GitHub Pages can serve the UI but cannot keep server secrets or enforce those rules itself.
