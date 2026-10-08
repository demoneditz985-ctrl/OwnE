# New Shadow Modz local entry screen

## Scope

The latest request explicitly permits replacing only the old licence/login UI and adding a new screen for `SHADOWMODZ`. This build implements that **local UI/entry lock**, not a native-engine entitlement replacement.

- Exact key: **`SHADOWMODZ`**, case-sensitive; Java ASCII `trim()` is applied.
- Empty, null, lower-case, suffixed and arbitrary random values are rejected.
- A valid key is saved in private Android SharedPreferences; the original main activity is opened only after that save reports success and the saved proof is rechecked.
- Existing saved local acceptance skips the form on later launches.
- The new launcher is `com.shadowmodz.KeyActivity`, with black/purple styling, Shadow Modz name/emblem and the exact Telegram invite.
- The original `com.kos.MainActivity` is no longer exported. On Android 9/API 28+ the new AppComponentFactory additionally redirects unauthorised attempts to instantiate that activity back to the local form.
- On Android 7/8/API 24–27 the launcher route still uses the form, but AppComponentFactory routing is unavailable. This is not a secure/secret DRM boundary against code running under the same app UID, root, APK modification or preference restoration.

A single shared key embedded in an APK can be extracted or shared. There is no server enforcement, device cap or expiration. This does not constitute a production licensing service.

## Original APK handling

The original APK is fully decompiled for inspection into ignored `.work/local-gate-inspection/`. Packaging uses a separate resource decode and the original primary DEX, not wholesale smali reassembly.

Only the **four bytes** of the first instruction in the exact `zx0.a(wm0,wm0,wm0,sw,int)` legacy dialog renderer change:

```text
Original: 08001600  (move-object/from16)
New:      0e000000  (return-void; nop)
```

Both code units are replaced so operand words are not accidentally decoded as stray instructions. DEX signature/checksum fields are recomputed. The primary DEX length, string/method tables, offsets and all other code bytes are verified unchanged. Four new classes are assembled into `classes2.dex`.

Suppressing that Compose renderer hides the original licence dialog. It does **not** synthesise the native activation payload or grant native permissions; a caller's old UI state can still exist while the dialog is hidden.

## Native startup and functionality

The original `com.kos.App`, encrypted-string decoders, `NativeBridge`, activation coroutine, native bootstrap and app-launch engine checks are retained. Every original `.so` byte is unchanged. No unconditional native success result is substituted.

**Native library initialization still runs before any activity, including the new key screen.** A signature/integrity rejection or other native startup fault can still close the APK before the form appears. The new screen does not fix or bypass that problem.

Even if the form accepts `SHADOWMODZ` and opens the original main activity, protected native features may still reject the original licence or fail. The report therefore separately records:

- `localKeyGateImplemented = true`
- `legacyLicenceDialogSuppressed = true`
- `nativeEntitlementReplacementImplemented = false`
- `licenseReplacementImplemented = false`
- `runtimeTested = false`

Some original Compose/native KOS text and blue colours remain because that code is deliberately not reassembled or globally rewritten.

## Verification

The compiled **pure string validator** is exercised with a small, explicitly limited Dalvik instruction interpreter: positive and negative key inputs are tested against the actual compiled method. This is not an Android/JNI emulator.

Regression tests also verify the limited primary-DEX patch, checksums, rejection of unrelated code changes, manifest routing and helper presence. The final APK is checked for compiled label/launcher/package/SDK/permissions, unchanged native libraries and native-method fingerprints, exact permitted primary-DEX changes, added classes, v2/v3 signatures and ZIP alignment.

No Android device/emulator is connected. Activity lifecycle, preference persistence on a phone, startup, original main UI and native features have not been runtime-tested. Compilation/static checks are not evidence of a full app unlock or crash fix.

Build:

```bash
bash scripts/build_local_gate_test.sh
```

The pinned Apktool JAR exposes SmaliBuilder but not a standalone smali CLI main method. `scripts/assemble_gate.py` emits a tiny Java classfile bridge to that existing API, avoiding compiler downloads and untrusted package scripts. Its generated classfile and all decompile/build intermediates are ignored.
