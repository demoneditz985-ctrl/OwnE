# Shadow Modz — local key gate UI test v0.2.0

**New local entry screen: key `SHADOWMODZ`. The old licence dialog is suppressed. This is NOT a native-engine licence unlock or a confirmed crash fix. Native startup and entitlements remain unchanged and unverified.**

## Downloads

- **[Download local-gate test APK — 20.6 MiB](https://github.com/demoneditz985-ctrl/OwnE/raw/shadow-modz-local-gate-test-v0.2.0/artifacts/Shadow-Modz-local-gate-test.apk)**
- [SHA-256 checksum](https://github.com/demoneditz985-ctrl/OwnE/blob/shadow-modz-local-gate-test-v0.2.0/artifacts/Shadow-Modz-local-gate-test.apk.sha256)
- [Audit report](https://github.com/demoneditz985-ctrl/OwnE/blob/shadow-modz-local-gate-test-v0.2.0/artifacts/local-gate-test-report.json)

The APK is hosted at this release tag in the repository and linked here, not attached as a binary release asset. The workspace cannot reach GitHub's release-asset upload endpoint.

## Implemented

- New black/purple Shadow Modz entry screen, label, launcher icons and splash emblem.
- Exact **`SHADOWMODZ`** local key validation; case-sensitive, with ASCII whitespace trimmed. Random, empty, null and wrong-case keys are rejected.
- Private local preference save; entry to the original main activity requires a valid saved local proof.
- Original licence-dialog rendering suppressed by a four-byte in-place UI entry patch, with DEX checksums updated. No wholesale reassembly of the original encrypted/native-bound code.
- New classes in `classes2.dex`; original native Application, encrypted string decoders, native bridge/activation/startup/engine checks and `.so` bytes retained.
- Telegram action on the new form: https://t.me/+BBimnHMiSvpiYTBl
- Same local test signing certificate as the earlier Shadow Modz test APKs, verified by SHA-256.

## Verification

- **32** unit/regression tests passed, including execution of the compiled pure-string key validator with positive/negative samples in a limited test interpreter.
- Primary DEX changes restricted to the exact four-byte UI patch and header digests; native/licensing method fingerprints verified unchanged.
- Compiled launcher, label, package, manifest routing, SDK, permissions, helper classes, APK v2/v3 signatures and ZIP alignment verified.
- Original APK fully decompiled for inspection, with a separate conservative packaging decode.

## Important limits

- **Native initialization runs before this key screen.** A native signing/integrity/startup fault can still close the app before the form appears.
- Accepting the new local key does **not** grant the original native engine's entitlement. Protected features can still reject the old licence or fail after the form.
- No Android device/emulator was available: activity lifecycle, persistence, startup and native features have not been tested on a phone. This is not a stable release.
- Some original Compose/native KOS branding and blue colours remain.
- Launcher changes apply on Android 7/API 24+. Additional AppComponentFactory routing requires Android 9/API 28+. This embedded shared-key lock is not secure against app modification, root or code under the same UID; no device caps or expiration are implemented.
- ARM64 only. Package remains `com.kos`; version code remains 28. Certificate matches earlier Shadow Modz **test** builds, not the original KOS certificate.

APK SHA-256:

```text
fdbf638abb1ab59d7afad010b7b2ebcf78869bc3bfeb6f2db458c3bfce956f13
```

See `docs/local-key-gate.md` for the UI/engine scope distinction and `docs/crash-diagnosis.md` for relevant crash-log collection if startup still fails.
