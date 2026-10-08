#!/usr/bin/env python3
"""Apply a conservative resource-only branding patch with exact original DEX.

This is a crash-isolation candidate, not a verified crash fix or new licence.
It deliberately removes all bytecode patches and leaves native setup intact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from rebrand_apk import ROOT, CONFIG, make_icon, rebrand_strings, replace_named_colors, patch_styles, sha256

DEX_NAME = re.compile(r"classes(?:[0-9]+)?\.dex\Z")


def verify_original_dex(decoded: Path, original: Path) -> dict[str, str]:
    if any(decoded.glob("smali*")):
        raise ValueError("Use apktool --no-src: smali must not be reassembled in this build.")
    actual = {p.name for p in decoded.glob("classes*.dex") if DEX_NAME.fullmatch(p.name)}
    with zipfile.ZipFile(original) as archive:
        expected = {n for n in archive.namelist() if DEX_NAME.fullmatch(n)}
        if not expected or actual != expected:
            raise ValueError("Original DEX inventory does not match the decoded APK.")
        hashes = {}
        for name in sorted(expected):
            contents = (decoded / name).read_bytes()
            if contents != archive.read(name):
                raise ValueError(f"Original DEX bytes changed: {name}")
            hashes[name] = hashlib.sha256(contents).hexdigest()
    return hashes


def apply(decoded: Path, config: dict) -> dict:
    from PIL import Image

    original = ROOT / config["originalApk"]
    dex_hashes = verify_original_dex(decoded, original)
    native = decoded / "lib/arm64-v8a/libkos.so"
    native_hash = sha256(native)
    changed_strings = changed_colors = icons = 0
    for path in sorted((decoded / "res").glob("values*/strings.xml")):
        # No injected Telegram callback exists in this mode. Do not falsely
        # relabel the original buy action as an action that opens our invite.
        contents, count = rebrand_strings(path.read_text(), config["appName"], None)
        if count:
            path.write_text(contents)
            changed_strings += count
    for path in sorted((decoded / "res").glob("values*/colors.xml")):
        contents, count = replace_named_colors(path.read_text(), config["resourceColors"])
        if count:
            path.write_text(contents)
            changed_colors += count
    for path in sorted((decoded / "res").glob("values*/styles.xml")):
        contents = patch_styles(path.read_text(), preserve_animated_splash=True)
        path.write_text(contents)
    for path in sorted((decoded / "res").glob("mipmap*/ic_launcher*.png")):
        with Image.open(path) as image:
            size = image.size
        variant = "foreground" if "foreground" in path.stem else "round" if "round" in path.stem else "standard"
        make_icon(size, variant).save(path)
        icons += 1
    if icons != 15:
        raise ValueError(f"Expected 15 launcher PNGs, found {icons}.")
    # Preserve the original splash drawable class and animator target. Changing
    # the vector's art is enough; a bitmap is not needed in the splash theme.
    splash = decoded / "res/drawable/ic_8_ball.xml"
    animation = decoded / "res/drawable/avd_8_ball_spin.xml"
    if not splash.exists() or not animation.exists():
        raise ValueError("Original animated splash resources are missing.")
    splash.write_text((ROOT / "branding/Shadow-Modz-splash-vector.xml").read_text())
    verify_original_dex(decoded, original)
    if sha256(native) != native_hash:
        raise ValueError("Native library changed unexpectedly.")
    return {
        "purpose": "resource-only-crash-isolation-test",
        "appName": config["appName"],
        "packageName": config["packageName"],
        "requestedFixedKey": config["requestedFixedKey"],
        "licenseReplacementImplemented": False,
        "anyKeyModeImplemented": False,
        "nativeLicensingUnchanged": True,
        "runtimeTested": False,
        "userReportedPreviousBuildCrash": True,
        "startupCrashFixed": None,
        "resourceStringsChanged": changed_strings,
        "resourceColorsChanged": changed_colors,
        "composeColorLiteralsChanged": 0,
        "launcherIconsChanged": icons,
        "displayTextHookAdded": False,
        "telegramContactCallbackAdded": False,
        "retainedAnimatedSplash": True,
        "originalDexSha256": dex_hashes,
        "nativeLibrarySha256": native_hash,
        "telegramUrl": config["telegramUrl"],
        "telegramUrlLocation": "release-notes-only-no-new-in-app-callback",
        "warning": "Diagnostic candidate only. Original DEX and native licensing are unchanged. No Android startup fix or licence unlocking has been verified.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decoded", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    decoded = args.decoded.resolve()
    if decoded == ROOT or not decoded.is_relative_to(ROOT / ".work"):
        raise SystemExit("Only patch a child of .work/; never the repository root.")
    config = json.loads(CONFIG.read_text())
    if sha256(ROOT / config["originalApk"]) != config["originalApkSha256"]:
        raise SystemExit("Original APK checksum mismatch.")
    report = apply(decoded, config)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
