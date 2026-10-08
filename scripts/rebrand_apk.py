#!/usr/bin/env python3
"""Apply cosmetic patches to the exact APK in this repo, not a licence bypass.

The decoded APK is a build intermediate, never a recovered Android project.
The original native licensing and integrity checks deliberately remain intact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "branding/config.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebrand_strings(xml: str, app_name: str, telegram_cta: str | None) -> tuple[str, int]:
    count = 0

    def update(match: re.Match) -> str:
        nonlocal count
        opening, name, value, closing = match.groups()
        new_value = re.sub(r"\bKOS\b", app_name, value)
        if name == "app_name":
            new_value = app_name
        elif name == "license_buy_prompt" and telegram_cta is not None:
            new_value = telegram_cta
        if value != new_value:
            count += 1
        return opening + new_value + closing

    pattern = r'(<string\s+name="([^"]+)"[^>]*>)(.*?)(</string>)'
    return re.sub(pattern, update, xml, flags=re.DOTALL), count


def replace_named_colors(xml: str, colors: dict[str, str]) -> tuple[str, int]:
    count = 0

    def update(match: re.Match) -> str:
        nonlocal count
        opening, name, value, closing = match.groups()
        new_value = colors.get(name, value)
        if new_value != value:
            count += 1
        return opening + new_value + closing

    pattern = r'(<color\s+name="([^"]+)"[^>]*>)([^<]*)(</color>)'
    return re.sub(pattern, update, xml), count


def replace_compose_colors(smali: str, mapping: dict[str, str]) -> tuple[str, int]:
    """Replace only explicit, known ARGB literals, not arbitrary numeric constants."""
    count = 0

    def update(match: re.Match) -> str:
        nonlocal count
        prefix, value, suffix, ending = match.groups()
        replacement = mapping.get(value.lower())
        if replacement is None:
            return match.group()
        count += 1
        return prefix + replacement + (suffix or "") + ending

    pattern = r"(?m)^(\s*const-wide(?:/32)?\s+[vp]\d+,\s+0x)([fF]{2}[0-9a-fA-F]{6})(00000000)?(L\b)"
    return re.sub(pattern, update, smali), count


def patch_text_renderer(smali: str) -> str:
    # The original parameter registers are >15, so invoke-static/range is required.
    pattern = r"(?m)(^\.method public static final b\(Ljava/lang/String;[^\n]+\n\s*\.locals \d+\n)"
    hook = (
        "\n    # Display-only branding; native strings/protocols are not changed.\n"
        "    invoke-static/range {p0 .. p0}, Lcom/shadowmodz/Branding;->displayText(Ljava/lang/String;)Ljava/lang/String;\n"
        "    move-result-object p0\n"
    )
    if "Lcom/shadowmodz/Branding;->displayText" in smali:
        raise ValueError("Text renderer is already patched; decode a fresh APK first.")
    updated, count = re.subn(pattern, lambda m: m.group(1) + hook, smali)
    if count != 1:
        raise ValueError(f"Expected exactly one Text renderer, found {count}.")
    return updated


def patch_telegram_cta(smali: str) -> str:
    # f3 is this exact APK's activation-dialog UI. Its last TextButton is the
    # secondary 'buy a key' action. No activation or success callback is touched.
    pattern = (
        r"(?ms)^    new-instance v5, Landroidx/emoji2/text/e3;\n.*?"
        r"^    invoke-direct \{v5, v4, v3, v14\}, Landroidx/emoji2/text/e3;-><init>"
        r"\(Landroidx/emoji2/text/wm0;Landroidx/emoji2/text/wm0;I\)V\n"
    )
    replacement = (
        "    # Shadow Modz Telegram contact; licensing is unchanged.\n"
        "    new-instance v5, Lcom/shadowmodz/TelegramAction;\n"
        "    iget-object v14, v0, Landroidx/emoji2/text/f3;->f:Landroid/content/Context;\n"
        "    invoke-direct {v5, v14}, Lcom/shadowmodz/TelegramAction;-><init>(Landroid/content/Context;)V\n"
    )
    updated, count = re.subn(pattern, replacement, smali)
    if count != 1:
        raise ValueError(f"Expected exactly one contact CTA, found {count}.")
    return updated


def patch_styles(xml: str, *, preserve_animated_splash: bool = False) -> str:
    def update(match: re.Match) -> str:
        opening, name, body, closing = match.groups()
        if name == "Theme.App.Starting":
            body = re.sub(
                r'(<item name="windowSplashScreenAnimatedIcon">)[^<]+',
                (r"\1@drawable/avd_8_ball_spin" if preserve_animated_splash
                 else r"\1@mipmap/ic_launcher_foreground"), body,
            )
            body = re.sub(
                r'(<item name="windowSplashScreenBackground">)[^<]+',
                r"\1@color/app_background", body,
            )
        elif name == "Theme.KOS":
            items = {
                "android:navigationBarColor": "@color/app_background",
                "android:windowLightNavigationBar": "false",
                "colorAccent": "@color/accent_purple",
            }
            for key, value in items.items():
                pattern = rf'(<item name="{re.escape(key)}">)[^<]+'
                if re.search(pattern, body):
                    body = re.sub(pattern, lambda m: m.group(1) + value, body)
                else:
                    body = body.rstrip() + f'\n        <item name="{key}">{value}</item>\n    '
        return opening + body + closing

    return re.sub(
        r'(<style name="(Theme\.KOS|Theme\.App\.Starting)"[^>]*>)(.*?)(</style>)',
        update, xml, flags=re.DOTALL,
    )


def make_icon(size: tuple[int, int], variant: str = "standard"):
    """Render the same geometric emblem as branding/Shadow-Modz-icon.svg."""
    from PIL import Image, ImageDraw

    scale = 2
    canvas = 512 * scale
    foreground = variant == "foreground"
    image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if not foreground:
        shape = draw.ellipse if variant == "round" else draw.rounded_rectangle
        if variant == "round":
            shape((0, 0, canvas - 1, canvas - 1), fill="#09070d")
            shape((10, 10, canvas - 11, canvas - 11), outline="#25172f", width=8)
        else:
            shape((0, 0, canvas - 1, canvas - 1), radius=224, fill="#09070d")
            shape((10, 10, canvas - 11, canvas - 11), radius=216, outline="#25172f", width=8)
        # Restrained purple glow, contained inside the opaque launcher background.
        glow = Image.new("RGBA", image.size)
        gd = ImageDraw.Draw(glow)
        for radius in range(210, 15, -4):
            alpha = int(1 + (210 - radius) / 16)
            gd.ellipse(((256-radius)*scale, (256-radius)*scale,
                        (256+radius)*scale, (256+radius)*scale), fill=(109, 40, 217, alpha))
        image = Image.alpha_composite(image, glow)
        draw = ImageDraw.Draw(image)

    factor = 0.88 if foreground else 1.0

    def points(coords):
        return [((256 + (x-256)*factor)*scale, (256 + (y-256)*factor)*scale)
                for x, y in coords]

    shield = points([(256,82), (394,148), (368,327), (256,430), (144,327), (118,148)])
    draw.polygon(shield, fill="#130c1e")
    draw.line(shield + [shield[0]], fill="#56338d", width=12, joint="curve")
    mask = Image.new("L", image.size)
    md = ImageDraw.Draw(mask)
    emblem = points([(188,168), (332,168), (310,208), (210,208), (192,242),
                     (294,242), (328,276), (288,344), (152,344), (176,304),
                     (266,304), (284,272), (186,272), (152,238)])
    md.polygon(emblem, fill=255)
    gradient = Image.new("RGBA", image.size)
    gr = ImageDraw.Draw(gradient)
    for y in range(canvas):
        t = min(1, max(0, (y/scale - 168) / 176))
        color = tuple(round(a + (b-a)*t) for a, b in zip((216,180,254), (124,58,237)))
        gr.line((0,y,canvas,y), fill=(*color,255))
    image.paste(gradient, (0,0), mask)
    draw = ImageDraw.Draw(image)
    draw.line(points([(210,208),(310,208)]), fill="#e2c9ff", width=2)
    draw.line(points([(176,304),(266,304)]), fill="#cba7ff", width=2)
    return image.resize(size, Image.Resampling.LANCZOS)


def apply(decoded: Path, config: dict) -> dict:
    from PIL import Image

    required = [
        "apktool.yml", "AndroidManifest.xml",
        "smali/androidx/emoji2/text/hl2.smali",
        "smali/androidx/emoji2/text/f3.smali",
        "smali/com/kos/Native/NativeBridge.smali",
        "lib/arm64-v8a/libkos.so", "res/values/strings.xml",
    ]
    for name in required:
        if not (decoded / name).is_file():
            raise ValueError(f"Missing decoded input: {name}")
    # Refuse to conceal or relabel a licence bypass as a branding-only patch.
    if config["licenseReplacementImplemented"] is not False:
        raise ValueError("This tool implements branding only, not replacement licensing.")
    native_file = decoded / "lib/arm64-v8a/libkos.so"
    bridge_file = decoded / "smali/com/kos/Native/NativeBridge.smali"
    before_native, before_bridge = sha256(native_file), sha256(bridge_file)

    # Preflight the fragile, exact-version patches before writing any files.
    renderer = decoded / "smali/androidx/emoji2/text/hl2.smali"
    dialog = decoded / "smali/androidx/emoji2/text/f3.smali"
    renderer_new = patch_text_renderer(renderer.read_text())
    dialog_new = patch_telegram_cta(dialog.read_text())

    changed_strings = changed_resources = changed_compose = 0
    for path in sorted((decoded / "res").glob("values*/strings.xml")):
        locale = path.parent.name
        cta = "Join Shadow Modz on Telegram"
        if locale.startswith("values-ar"):
            cta = "انضم إلى Shadow Modz على Telegram"
        elif locale.startswith("values-pt"):
            cta = "Entre no Telegram da Shadow Modz"
        contents, count = rebrand_strings(path.read_text(), config["appName"], cta)
        if count:
            path.write_text(contents)
            changed_strings += count
    for path in sorted((decoded / "res").glob("values*/colors.xml")):
        contents, count = replace_named_colors(path.read_text(), config["resourceColors"])
        if count:
            path.write_text(contents)
            changed_resources += count
    for path in sorted((decoded / "res").glob("values*/styles.xml")):
        contents = path.read_text()
        updated = patch_styles(contents)
        if updated != contents:
            path.write_text(updated)
    for path in sorted((decoded / "smali").rglob("*.smali")):
        # Never edit native interfaces or encrypted-string decoders.
        if path.is_relative_to(decoded / "smali/com/kos") or path.is_relative_to(decoded / "smali/a"):
            continue
        contents, count = replace_compose_colors(path.read_text(), config["composeColorMap"])
        if count:
            path.write_text(contents)
            changed_compose += count
    renderer.write_text(renderer_new)
    dialog.write_text(dialog_new)
    patches = decoded / "smali/com/shadowmodz"
    patches.mkdir(parents=True, exist_ok=True)
    for name in ["Branding.smali", "TelegramAction.smali"]:
        contents = (ROOT / "apk-patches" / name).read_text()
        contents = contents.replace("https://t.me/+BBimnHMiSvpiYTBl", config["telegramUrl"])
        (patches / name).write_text(contents)

    icons = 0
    for path in sorted((decoded / "res").glob("mipmap*/ic_launcher*.png")):
        with Image.open(path) as original:
            size = original.size
        variant = "foreground" if "foreground" in path.stem else "round" if "round" in path.stem else "standard"
        make_icon(size, variant).save(path)
        icons += 1
    if icons != 15:
        raise ValueError(f"Expected 15 launcher PNGs, found {icons}.")
    if before_native != sha256(native_file) or before_bridge != sha256(bridge_file):
        raise ValueError("Native code/interfaces changed unexpectedly.")
    return {
        "purpose": "branding-test-only",
        "appName": config["appName"],
        "telegramUrl": config["telegramUrl"],
        "requestedFixedKey": config["requestedFixedKey"],
        "licenseReplacementImplemented": False,
        "nativeLicensingUnchanged": True,
        "runtimeTested": False,
        "packageName": config["packageName"],
        "resourceStringsChanged": changed_strings,
        "resourceColorsChanged": changed_resources,
        "composeColorLiteralsChanged": changed_compose,
        "launcherIconsChanged": icons,
        "displayTextHookAdded": True,
        "telegramContactCallbackAdded": True,
        "nativeLibrarySha256": before_native,
        "nativeBridgeSourceSha256": before_bridge,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decoded", type=Path, help="Fresh apktool decode of the original APK")
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--report", type=Path, default=ROOT / ".work/branding-report.json")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if sha256(ROOT / config["originalApk"]) != config["originalApkSha256"]:
        raise SystemExit("Original APK checksum mismatch; this patch targets one exact version.")
    decoded = args.decoded.resolve()
    if decoded == ROOT or not decoded.is_relative_to(ROOT / ".work"):
        raise SystemExit("Decode into a child of .work/; never patch the repository root.")
    report = apply(decoded, config)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
