# Shadow Modz — compatibility test v0.1.1

**Startup crash-isolation candidate, NOT a confirmed crash fix. `SHADOWMODZ` and "any key works" are NOT implemented. The original native licensing remains unchanged.**

The user reported a crash in v0.1.0. This candidate removes all injected/reassembled bytecode and restores the exact original DEX to isolate possible code/layout regressions. No crash trace or device/Android details were supplied, and no Android device is available for runtime testing.

## Downloads

- **[Download compatibility-test APK — 20.6 MiB](https://github.com/demoneditz985-ctrl/OwnE/raw/shadow-modz-compatibility-test-v0.1.1/artifacts/Shadow-Modz-compatibility-test.apk)**
- [SHA-256 checksum](https://github.com/demoneditz985-ctrl/OwnE/blob/shadow-modz-compatibility-test-v0.1.1/artifacts/Shadow-Modz-compatibility-test.apk.sha256)
- [Static audit report](https://github.com/demoneditz985-ctrl/OwnE/blob/shadow-modz-compatibility-test-v0.1.1/artifacts/compatibility-test-report.json)

The APK is stored in the repository at this release tag and linked here, not attached as a binary release asset. The workspace cannot reach GitHub's release-asset upload endpoint.

## Changes and verified checks

- Exact original `classes.dex` bytes retained: 7,008,432 bytes; no smali reassembly or new Java helpers.
- Original native-library bytes retained.
- Original animated-vector splash resource/type and animator target retained; new Shadow Modz vector emblem.
- Shadow Modz Android label, launcher icons and black/purple resource colours.
- Same test signing certificate as v0.1.0, verified by certificate SHA-256. This can update the already-installed Shadow Modz **test** APK without an uninstall, subject to normal Android installation checks. It does not match the original KOS certificate.
- 22 unit/regression tests passed. APK compilation, v2/v3 signatures, manifest metadata and native ZIP alignment passed static audits.

## Deliberate trade-offs

- Original Compose colours/text are retained. Some blue and KOS branding can remain.
- The injected Telegram callback is removed. Telegram invite: https://t.me/+BBimnHMiSvpiYTBl
- Original licence format, activation authority, native setup and engine checks are retained. No replacement key or unconditional success callback was added.
- ARM64 Android 7.0/API 24+ only; package remains `com.kos` and version code remains 28.
- The packed library may still reject re-signing or other APK changes. **A successful static audit does not prove the crash is fixed.**

APK SHA-256:

```text
8f788d27be121093cc252d4174f491511d982c62955054838367b335067cdfe3
```

If this candidate still closes, provide the phone model, Android version and crash screenshot/exception. See `docs/crash-diagnosis.md` for optional adb crash-log commands. Do not send passwords, tokens or a full unfiltered device report.
