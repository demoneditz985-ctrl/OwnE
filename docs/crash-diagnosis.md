# Crash report and conservative diagnostic build

## What is known

The user reported that the first Shadow Modz branding-test APK crashes. No exception, native tombstone, Android version, device ABI or precise crash point has been supplied. The cause is **not established**.

That first build reassembled the complete DEX and injected two cosmetic helpers. Its DEX was 8,443,852 bytes; the original DEX is 7,008,432 bytes. Equivalent method fingerprints in selected licensing classes do not prove that a packed native library tolerates different DEX layout, metadata or signing identity. Size/layout differences are an investigation lead, **not a proven cause**.

The native library loads in `StartupAppComponentFactory` and the `App` static initializer before the activity's Compose UI. A native loader/signature/integrity rejection can therefore occur before any branding helper runs.

## Compatibility-test strategy

`bash scripts/build_compatibility_test.sh`:

1. Decodes resources using Apktool `--no-src`.
2. Verifies and copies the **entire original DEX byte-for-byte**, without smali reassembly.
3. Removes the injected Compose text/colour changes and the Telegram callback by preserving the original DEX.
4. Keeps the Shadow Modz Android label, launcher icons and resource colours.
5. Keeps the original `AnimatedVectorDrawable` splash resource/type and animator target; replaces only its vector artwork.
6. Preserves native library bytes, package, launcher, version, SDK requirements and permissions.
7. Reuses the local test keystore when available, signs v2/v3 and verifies the final DEX bytes and native ZIP alignment.
8. Records whether the certificate actually matches the previous branding test.

This removes possible cosmetic bytecode/layout regressions but does **not** prove a startup fix. The packed library can still reject the test certificate or other resource/APK changes.

## Trade-offs

- Some Compose/native text still says KOS, and the original Compose palette can still contain blue.
- There is no injected Telegram button in this candidate. The invite remains in the release notes: https://t.me/+BBimnHMiSvpiYTBl
- Licensing remains original. `SHADOWMODZ` and "any random key works" have **not** been implemented.
- The earlier branding-test release is marked as user-reported crashing; do not describe either APK as a confirmed crash fix.

## Next evidence needed if it still crashes

The phone model, Android version and when it closes (startup, licence activation or virtual-app launch) are sufficient to begin narrowing the failure. An error screenshot is useful; an Android exception/native crash trace is better.

If a computer with adb is available, collect only the app's relevant crash:

```bash
adb logcat -c
adb shell am force-stop com.kos
adb shell am start -n com.kos/com.kos.MainActivity
adb logcat -d -b crash
```

Share the exception/native signal and stack frames relevant to `com.kos`. Do not send passwords, account tokens or an unfiltered full-device bug report. No device data is cleared by these commands.

No Android device/emulator is attached to the workspace. The diagnostic candidate has passed compilation and static audits, but has **not** been executed on Android.
