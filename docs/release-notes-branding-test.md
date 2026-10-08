# Shadow Modz — branding test v0.1.0

**Branding-only testing prerelease. `SHADOWMODZ` is NOT a working replacement licence key. The original native licensing is unchanged.**

## Included

- Shadow Modz app label, new launcher/round/adaptive icons, and splash emblem.
- Black/purple Android resource and Compose colours.
- Visible KOS words in resource strings and plain-text Compose rendering rebranded.
- Telegram contact button: https://t.me/+BBimnHMiSvpiYTBl
- Signed APK, SHA-256 checksum and static audit report.

## Verification and limitations

- 13 regression tests passed when building this APK.
- APK v2/v3 signatures and native-library ZIP alignment verified.
- Original native-library bytes and licensing paths verified unchanged.
- Installation, startup and native engine functionality have **not** been tested on Android.
- This is **not** a fully unlocked or production-ready release. The protected native library may reject the new test signing certificate.
- Existing native/server-controlled branding may remain.

## Before installing

- Requires ARM64 Android 7.0/API 24 or newer.
- Retains the original Android package ID `com.kos` to preserve JNI/engine references.
- Uses a **new local test certificate**, not the original certificate. It cannot install as an in-place update over an APK signed with the original key.
- **Prefer a spare/test device. Do not uninstall the original app without backing up important app/profile data.**

APK SHA-256:

```text
3629a2a4db1ad112565ed6cf63ec65b6a2fb52312e68e29ac2fe0edffa853fdc
```

See the repository README and `docs/apk-assessment.md` for the reproducible build and remaining licensing blocker. The original `KOS_3.7-VStable.apk` is preserved unchanged.
