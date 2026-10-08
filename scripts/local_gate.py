#!/usr/bin/env python3
"""Prepare a new local key screen and suppress the legacy UI dialog.

Only the legacy dialog entry instructions change in the original DEX. Native
activation, setup, engine checks and encrypted strings are NOT replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from rebrand_apk import ROOT, CONFIG, sha256
from rebrand_resources import apply as apply_resources

ANDROID = "http://schemas.android.com/apk/res/android"
A = "{" + ANDROID + "}"
ET.register_namespace("android", ANDROID)
DIALOG_CLASS = "Landroidx/emoji2/text/zx0;"
DIALOG_DESCRIPTOR = "(Landroidx/emoji2/text/wm0;Landroidx/emoji2/text/wm0;Landroidx/emoji2/text/wm0;Landroidx/emoji2/text/sw;I)V"
GATE_CLASSES = {
    "Lcom/shadowmodz/KeyPolicy;", "Lcom/shadowmodz/KeyActivity;",
    "Lcom/shadowmodz/KeyAction;", "Lcom/shadowmodz/GateComponentFactory;",
}


def parse_dex(contents: bytes):
    from loguru import logger
    logger.remove()
    from androguard.core.dex import DEX
    return DEX(contents)


def dialog_entry_offset(contents: bytes) -> int:
    dex = parse_dex(contents)
    cls = dex.get_class(DIALOG_CLASS)
    if cls is None:
        raise ValueError("Original licence-dialog class not found.")
    methods = [m for m in cls.get_methods() if m.get_name() == "a" and m.get_descriptor().replace(" ", "") == DIALOG_DESCRIPTOR]
    if len(methods) != 1:
        raise ValueError("Expected one exact original licence-dialog renderer.")
    first = next(iter(methods[0].get_instructions()))
    if first.get_name() != "move-object/from16" or first.get_length() != 4:
        raise ValueError("Unexpected original dialog entry instructions.")
    offset = methods[0].get_code_off() + 16
    if contents[offset] != 0x08:
        raise ValueError("Expected the exact 22x move-object/from16 opcode.")
    return offset


def suppress_dialog(contents: bytes) -> tuple[bytes, dict]:
    offset = dialog_entry_offset(contents)
    old = contents[offset:offset + 4]
    # Replace BOTH code units of the first instruction. A 1-unit return alone
    # would leave its operands to be decoded as invalid stray instructions.
    new = b"\x0e\x00\x00\x00"  # return-void; nop
    modified = bytearray(contents)
    modified[offset:offset + 4] = new
    modified[12:32] = hashlib.sha1(modified[32:]).digest()
    struct.pack_into("<I", modified, 8, zlib.adler32(modified[12:]) & 0xffffffff)
    patch = {
        "class": DIALOG_CLASS, "method": "a" + DIALOG_DESCRIPTOR,
        "entryOffset": offset, "originalBytes": old.hex(), "patchedBytes": new.hex(),
        "originalDexSha256": hashlib.sha256(contents).hexdigest(),
        "patchedDexSha256": hashlib.sha256(modified).hexdigest(),
        "byteLengthUnchanged": len(modified) == len(contents),
        "description": "Suppress only the old dialog rendering; no native entitlement is created.",
    }
    verify_primary_dex(contents, bytes(modified))
    return bytes(modified), patch


def verify_primary_dex(original: bytes, modified: bytes) -> dict:
    offset = dialog_entry_offset(original)
    if len(modified) != len(original):
        raise ValueError("Primary DEX length changed.")
    if modified[offset:offset + 4] != b"\x0e\x00\x00\x00":
        raise ValueError("Legacy dialog was not suppressed as expected.")
    restored = bytearray(modified)
    restored[8:32] = original[8:32]
    restored[offset:offset + 4] = original[offset:offset + 4]
    if bytes(restored) != original:
        raise ValueError("Unexpected primary DEX change outside the four-byte UI patch and header checksums.")
    if modified[12:32] != hashlib.sha1(modified[32:]).digest():
        raise ValueError("Invalid DEX signature.")
    if struct.unpack_from("<I", modified, 8)[0] != zlib.adler32(modified[12:]) & 0xffffffff:
        raise ValueError("Invalid DEX checksum.")
    dex = parse_dex(modified)
    method = next(m for m in dex.get_class(DIALOG_CLASS).get_methods() if m.get_name() == "a" and m.get_descriptor().replace(" ", "") == DIALOG_DESCRIPTOR)
    names = [i.get_name() for i in method.get_instructions()]
    if names[:2] != ["return-void", "nop"]:
        raise ValueError("Unexpected patched method decoding.")
    return {"entryOffset": offset, "primaryDexOnlyUiPatch": True, "primaryDexLength": len(modified)}


def execute_matches(dex_bytes: bytes, value: str | None) -> bool:
    """Execute just the new compiled pure-string validator, not Android/JNI.

    This tiny test interpreter deliberately permits only its exact instruction
    set and Java String.trim/equals calls. It is NOT a native engine emulator.
    """
    dex = parse_dex(dex_bytes)
    cls = dex.get_class("Lcom/shadowmodz/KeyPolicy;")
    if cls is None:
        raise ValueError("Missing new key policy.")
    method = next(m for m in cls.get_methods() if m.get_name() == "matches")
    code = method.get_code()
    arg_register = code.get_registers_size() - code.get_ins_size()
    registers = {arg_register: value}
    instructions, offset = {}, 0
    for instruction in method.get_instructions():
        instructions[offset] = instruction
        offset += instruction.get_length()
    pc, result = 0, None
    for _ in range(30):
        ins = instructions[pc]
        name = ins.get_name()
        following = pc + ins.get_length()
        if name == "if-eqz":
            if registers.get(ins.AA) is None or registers.get(ins.AA) == 0:
                following = pc + ins.BBBB * 2
        elif name in ["const-string", "const-string/jumbo"]:
            registers[ins.AA] = dex.get_cm_string(ins.get_ref_kind())
        elif name == "invoke-virtual":
            reference = dex.get_cm_method(ins.get_ref_kind())
            owner, member, descriptor = reference
            if owner != "Ljava/lang/String;":
                raise ValueError("Unexpected validator call owner.")
            if member == "trim":
                s = registers[ins.C]
                # Java String.trim removes codepoints <= U+0020, not all Unicode whitespace.
                registers[ins.C] = s.strip("".join(chr(i) for i in range(33)))
                result = registers[ins.C]
            elif member == "equals":
                result = registers[ins.C] == registers[ins.D]
            else:
                raise ValueError("Unexpected validator string call.")
        elif name in ["move-result", "move-result-object"]:
            registers[ins.AA] = result
        elif name == "const/4":
            registers[ins.A] = ins.B
        elif name == "return":
            return bool(registers[ins.AA])
        else:
            raise ValueError(f"Unsupported validator instruction: {name}")
        pc = following
    raise ValueError("Validator did not terminate.")


def verify_gate_dex(contents: bytes) -> dict:
    dex = parse_dex(contents)
    if {cls.get_name() for cls in dex.get_classes()} != GATE_CLASSES:
        raise ValueError("Unexpected helper classes in classes2.dex.")
    samples = {
        "SHADOWMODZ": True, " SHADOWMODZ ": True,
        "shadowmodz": False, "SHADOWMODZ1": False, "RANDOM": False,
        "": False, None: False, "\u00a0SHADOWMODZ\u00a0": False,
    }
    for value, expected in samples.items():
        if execute_matches(contents, value) != expected:
            raise ValueError(f"Compiled key validation failed for {value!r}.")
    return {"localGateValidatorSamplesPassed": len(samples), "gateDexSha256": hashlib.sha256(contents).hexdigest()}


def update_manifest(xml: str) -> str:
    root = ET.fromstring(xml)
    app = root.find("application")
    if app is None or app.get(A + "name") != "com.kos.App":
        raise ValueError("Unexpected original application class.")
    main = next((a for a in app.findall("activity") if a.get(A + "name") == "com.kos.MainActivity"), None)
    if main is None:
        raise ValueError("Original main activity missing.")
    main.set(A + "exported", "false")
    for intent in list(main.findall("intent-filter")):
        if any(a.get(A + "name") == "android.intent.action.MAIN" for a in intent.findall("action")):
            main.remove(intent)
    if any(a.get(A + "name") == "com.shadowmodz.KeyActivity" for a in app.findall("activity")):
        raise ValueError("Local gate already added.")
    app.set(A + "appComponentFactory", "com.shadowmodz.GateComponentFactory")
    gate = ET.SubElement(app, "activity", {A + "name": "com.shadowmodz.KeyActivity", A + "exported": "true", A + "theme": "@style/ShadowGateTheme"})
    intent = ET.SubElement(gate, "intent-filter")
    ET.SubElement(intent, "action", {A + "name": "android.intent.action.MAIN"})
    ET.SubElement(intent, "category", {A + "name": "android.intent.category.LAUNCHER"})
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")


def apply(decoded: Path, gate_dex: Path, config: dict) -> dict:
    report = apply_resources(decoded, config)
    with zipfile.ZipFile(ROOT / config["originalApk"]) as archive:
        original = archive.read("classes.dex")
    modified, patch = suppress_dialog(original)
    (decoded / "classes.dex").write_bytes(modified)
    gate_contents = gate_dex.read_bytes()
    gate_checks = verify_gate_dex(gate_contents)
    (decoded / "classes2.dex").write_bytes(gate_contents)
    manifest = decoded / "AndroidManifest.xml"
    manifest.write_text(update_manifest(manifest.read_text()))
    (decoded / "res/layout/shadow_key_gate.xml").write_text((ROOT / "branding/shadow_key_gate.xml").read_text())
    style = decoded / "res/values/shadow_gate.xml"
    style.write_text('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="ShadowGateTheme" parent="@android:style/Theme.Material.NoActionBar">
        <item name="android:windowBackground">#ff09070d</item>
        <item name="android:statusBarColor">#ff09070d</item>
        <item name="android:navigationBarColor">#ff09070d</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:colorAccent">#ffa855f7</item>
    </style>
</resources>
''')
    report.update({
        "purpose": "local-key-gate-ui-test", "localKeyGateImplemented": True,
        "localKey": "SHADOWMODZ", "legacyLicenceDialogSuppressed": True,
        "licenseReplacementImplemented": False, "nativeEntitlementReplacementImplemented": False,
        "nativeStartupStillBeforeGate": True, "runtimeTested": False,
        "originalDexByteForByteUnchanged": False, "primaryDexUiPatch": patch,
        "localKeyGateScope": "launcher-and-app-component-factory-activity-routing-not-native-engine",
        "telegramContactCallbackAdded": True, "telegramUrlLocation": "new-local-key-screen",
        "warning": "New local SHADOWMODZ entry lock only. The old UI dialog is suppressed, but native engine licensing and startup are unchanged. Not a licence-unlocked or Android-verified build.",
        **gate_checks,
    })
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decoded", type=Path)
    parser.add_argument("--gate-dex", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    decoded = args.decoded.resolve()
    if decoded == ROOT or not decoded.is_relative_to(ROOT / ".work"):
        raise SystemExit("Only patch a child of .work/.")
    config = json.loads(CONFIG.read_text())
    if sha256(ROOT / config["originalApk"]) != config["originalApkSha256"]:
        raise SystemExit("Original APK checksum mismatch.")
    report = apply(decoded, args.gate_dex, config)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
