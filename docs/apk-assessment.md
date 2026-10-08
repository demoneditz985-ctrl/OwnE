# APK assessment and remaining licensing blocker

> **UI-only update:** v0.2.0 adds a new local `SHADOWMODZ` launcher lock and suppresses the legacy licence dialog. It does not replace native entitlements or fix native startup. See [local key gate scope](local-key-gate.md). The native activation paths assessed below remain unchanged.

> **Runtime update:** the user reported that the first branding-test APK crashes; the Android version, crash point and exception have not been supplied. A resource-only diagnostic candidate now preserves the entire original DEX byte-for-byte. See [crash diagnosis](crash-diagnosis.md). Neither a startup fix nor a replacement licence is verified.

## Available input

The repository contains `KOS_3.7-VStable.apk` and no original Gradle/Android project, native C/C++ sources, licence-server project, or original signing keystore. The owner's requested new fixed key is `SHADOWMODZ`.

Static inspection of the original APK found:

| Property | Value |
| --- | --- |
| App label | `KOS` |
| Android package | `com.kos` |
| Version name/code | `3.7-VStable` / `28` |
| Minimum Android | API 24 / Android 7.0 |
| Target SDK | 36 |
| Included ABI | `arm64-v8a` only |
| Launcher | `com.kos.MainActivity` |
| Main native library | `lib/arm64-v8a/libkos.so` |
| Original APK SHA-256 | `07900492ca1a730ee37d7acac900fde25bde8dc0299253665935b743b1a677cb` |
| Native library SHA-256 | `34ff48596bddfedf841b269b2c2ae00ab46418dcf735da957ec82490686fc10d` |

`libkos.so` is an AArch64 native binary with very limited section metadata and a `.riotvanguard` section. Java string accessors in `a/a/a/b` and `a/a/a/c` call native functions. Apktool decoding supplies readable resources and smali; **it does not recover the native project's source or signing private key**.

## Licence call path observed

The names below are the obfuscated names from this exact APK, not original source names.

1. `androidx.emoji2.text.c3.a()` trims the licence input and validates a four-group format resembling `XXXXX-XXXXX-XXXXX-XXXXX`.
2. The activation coroutine in `androidx.emoji2.text.h3.l()` checks network connectivity and calls `NativeBridge.d([context, key], 0x3f1)`. `0x3f1` is decimal **1009**.
3. `NativeBridge.d()` dispatches to the private native `doTask(Object[])` and expects a byte payload. Java code parses that payload into the activation result.
4. The success toast in `androidx.emoji2.text.i3` follows that result; it is not the licence authority.
5. App-launch eligibility in `androidx.emoji2.text.ao0` also calls native functions such as `NativeBridge.a(context)`, `NativeBridge.c(packageName)`, and `NativeBridge.e()`.

Therefore, merely accepting `SHADOWMODZ` in the text field, invoking the success callback, or forcing a Java boolean to `true` would not establish that the native engine grants valid entitlements. No such fake activation changes were made.

The underlying native/server protocol was not recovered or replaced. The old key was not recovered. The requested fixed key is recorded as **pending**, not advertised as functional.

## Cosmetic patches actually applied

- Resource app label and natural-language `KOS` words become **Shadow Modz**, including localized notices.
- Plain-text Compose rendering gets a display-only word replacement. It is **not** attached to the native string decoder, filesystem code, or network/protocol data.
- The app's explicit Android/Compose palette literals become black and purple, while success/warning/error colours and Google's identity-blue icon stay intact.
- Launcher, round and adaptive foreground icons receive a purple geometric shadow/S emblem. The splash uses the new emblem.
- The activation dialog's **secondary contact action** opens `https://t.me/+BBimnHMiSvpiYTBl`; it does not change the activation button.
- The APK keeps package `com.kos`, JNI interfaces, engine classes, the original licence-format check, activation coroutine and native libraries. Renaming every internal `com.kos` symbol without native source risks breaking class loading, JNI registration, providers and runtime engine references.

Protected native/server-rendered text, image assets not used by the patched launcher/splash, rich-text spans and virtualized apps' own branding have not been verified as fully rebranded.

## Verification completed

The build pipeline runs 13 regression tests, assembles the smali/resources, and checks:

- Compiled app label, package identity, Android metadata and unchanged permission set.
- Presence of the new display/contact helper classes.
- Exact native-library byte equality with the original APK.
- Equivalent DEX method instructions/access flags for the native bridge, encrypted string decoders, licence input validation, activation coroutine and app-launch checks.
- Uncompressed `resources.arsc`, uncompressed native libraries and ZIP data-offset alignment (16 KiB for `.so`, 4 bytes for other stored entries).
- Valid v2 and v3 APK signatures using a **new local test certificate**.

Results, certificate public digests and checksums are in `artifacts/branding-test-report.json`. Aligning ZIP entries does not rebuild or change native ELF segment alignment.

## Verification NOT completed

There is no attached Android device or emulator. Installation, startup, splash appearance, layouts, invite opening and native-engine/virtual-app operation have **not** been runtime-tested.

The original signing private key is not available. The new APK cannot update an installed APK signed with the original certificate. The native library may also reject repackaging or the new certificate. **A successful rebuild/signature check is not a promise that the protected app runs.**

Do not uninstall the existing app without backing up its data. Prefer a separate test device.

## Ways forward

- Recover the original native/Android sources from another backup or development machine, then implement and test the `SHADOWMODZ` policy in the actual entitlement authority.
- Recover authorized owner/admin access to the existing licence service and issue/reset a real entitlement. Whether that service supports the exact short key `SHADOWMODZ` is not known; the current client format would also need adjustment.
- A further binary-only replacement would require native reverse engineering plus Android runtime testing, beyond the cosmetic patch completed here.

A single shared offline key has no meaningful secret protection once distributed in an APK. Server-enforced device limits and activation-based expiry require a trusted backend; a static GitHub Pages site cannot enforce them by itself.
