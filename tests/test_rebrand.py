"""Regression tests for cosmetic-only patches and APK ZIP alignment."""
import importlib.util
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


patch = load("rebrand_apk")
alignment = load("align_apk")


class BrandingTests(unittest.TestCase):
    def test_rebrand_visible_text_preserves_internal_package(self):
        source = '<resources><string name="app_name">KOS</string><string name="help">Open KOS; log: com.kos.txt; KOS_APP_SETTINGS_PREFS</string></resources>'
        output, count = patch.rebrand_strings(source, "Shadow Modz", "Join Telegram")
        self.assertEqual(count, 2)
        self.assertIn('name="app_name">Shadow Modz</string>', output)
        self.assertIn("Open Shadow Modz", output)
        self.assertIn("com.kos.txt", output)
        self.assertIn("KOS_APP_SETTINGS_PREFS", output)

    def test_license_format_and_activation_messages_remain_truthful(self):
        source = '<resources><string name="license_buy_prompt">Buy one</string><string name="license_invalid_format">XXXXX-XXXXX-XXXXX-XXXXX</string><string name="license_activation_failed">Failed</string></resources>'
        output, count = patch.rebrand_strings(source, "Shadow Modz", "Join Shadow Modz on Telegram")
        self.assertEqual(count, 1)
        self.assertIn("Join Shadow Modz on Telegram", output)
        self.assertIn("XXXXX-XXXXX-XXXXX-XXXXX", output)
        self.assertIn('name="license_activation_failed">Failed', output)
        self.assertNotIn("SHADOWMODZ", output)

    def test_localized_text_and_unrelated_language_words(self):
        source = '<resources><string name="notice">KOS يحتاج إلى إذن</string><string name="state_empty">Kosong</string></resources>'
        output, count = patch.rebrand_strings(source, "Shadow Modz", "Telegram")
        self.assertEqual(count, 1)
        self.assertIn("Shadow Modz يحتاج", output)
        self.assertIn("Kosong", output)

    def test_color_literals_not_random_strings_or_masks(self):
        source = '    const-wide v0, 0xff14b8f4L\n    const-wide v2, 0xff14b8f400000000L\n    const-wide v4, 0xffffffffL\n    const-string v6, "0xff14b8f4L"\n'
        output, count = patch.replace_compose_colors(source, {"ff14b8f4": "ffa855f7"})
        self.assertEqual(count, 2)
        self.assertIn("0xffa855f7L", output)
        self.assertIn("0xffa855f700000000L", output)
        self.assertIn("0xffffffffL", output)
        self.assertIn('const-string v6, "0xff14b8f4L"', output)

    def test_named_color_replacement_does_not_touch_library_resources(self):
        source = '<resources><color name="app_background">#ff111111</color><color name="google_blue">#ff4286f4</color></resources>'
        output, count = patch.replace_named_colors(source, {"app_background": "#ff09070d"})
        self.assertEqual(count, 1)
        self.assertIn("#ff09070d", output)
        self.assertIn("#ff4286f4", output)

    def test_text_hook_is_at_render_boundary_only_and_uses_range(self):
        source = '.method public static final b(Ljava/lang/String;I)V\n    .locals 40\n    return-void\n.end method\n'
        output = patch.patch_text_renderer(source)
        self.assertIn("invoke-static/range {p0 .. p0}", output)
        self.assertIn("move-result-object p0", output)
        self.assertNotIn("NativeBridge", output)
        with self.assertRaises(ValueError):
            patch.patch_text_renderer(output)
        with self.assertRaises(ValueError):
            patch.patch_text_renderer("")
        with self.assertRaises(ValueError):
            patch.patch_text_renderer(source + source)

    def test_telegram_replaces_only_contact_constructor(self):
        source = '    invoke-static {v0, v3}, Lcom/kos/Native/NativeBridge;->d([Ljava/lang/Object;I)[B\n    new-instance v5, Landroidx/emoji2/text/e3;\n    .line 12\n    const/4 v14, 0x0\n    invoke-direct {v5, v4, v3, v14}, Landroidx/emoji2/text/e3;-><init>(Landroidx/emoji2/text/wm0;Landroidx/emoji2/text/wm0;I)V\n    return-void\n'
        output = patch.patch_telegram_cta(source)
        self.assertIn("Lcom/shadowmodz/TelegramAction;", output)
        self.assertIn("Lcom/kos/Native/NativeBridge;->d([Ljava/lang/Object;I)[B", output)
        self.assertNotIn("onSuccess", output)
        self.assertNotIn("SHADOWMODZ", output)
        with self.assertRaises(ValueError):
            patch.patch_telegram_cta(output)

    def test_styles_keep_resource_identity_and_change_splash(self):
        source = '<resources><style name="Theme.KOS" parent="@style/Base"><item name="colorPrimary">@color/accent_purple</item></style><style name="Theme.App.Starting"><item name="windowSplashScreenAnimatedIcon">@drawable/old</item><item name="windowSplashScreenBackground">@color/old</item></style></resources>'
        output = patch.patch_styles(source)
        self.assertIn('name="Theme.KOS"', output)
        self.assertIn("@mipmap/ic_launcher_foreground", output)
        self.assertIn('name="android:navigationBarColor">@color/app_background', output)

    def test_config_does_not_claim_replacement_key(self):
        config = json.loads((ROOT / "branding/config.json").read_text())
        self.assertEqual(config["requestedFixedKey"], "SHADOWMODZ")
        self.assertFalse(config["licenseReplacementImplemented"])
        self.assertEqual(config["licenseMode"], "original-native-licensing-unchanged")
        self.assertEqual(config["packageName"], "com.kos")
        self.assertEqual(config["telegramUrl"], "https://t.me/+BBimnHMiSvpiYTBl")

    def test_icons_have_correct_size_and_safe_transparent_foreground(self):
        standard = patch.make_icon((48, 48))
        foreground = patch.make_icon((108, 108), "foreground")
        self.assertEqual(standard.size, (48, 48))
        self.assertEqual(foreground.size, (108, 108))
        self.assertEqual(standard.getpixel((0, 0))[3], 0)
        self.assertEqual(standard.getpixel((24, 24))[3], 255)
        self.assertEqual(foreground.getpixel((0, 0))[3], 0)
        self.assertEqual(foreground.getpixel((54, 54))[3], 255)


class AlignmentTests(unittest.TestCase):
    def test_alignment_roundtrip_and_stale_signatures_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            src, dst = Path(directory) / "input.apk", Path(directory) / "output.apk"
            entries = {
                "AndroidManifest.xml": b"manifest",
                "lib/arm64-v8a/libkos.so": b"native-bytes" * 17,
                "resources.arsc": b"resources",
                "résumé.txt": b"unicode-name",
                "META-INF/androidx.version": b"keep-me",
                "META-INF/CERT.RSA": b"drop-me",
                "META-INF/MANIFEST.MF": b"drop-me",
            }
            with zipfile.ZipFile(src, "w") as archive:
                for name, data in entries.items():
                    archive.writestr(name, data, compress_type=zipfile.ZIP_STORED)
                archive.writestr("classes.dex", b"bytecode", compress_type=zipfile.ZIP_DEFLATED)
            offsets = alignment.align_apk(src, dst)
            self.assertEqual(offsets["lib/arm64-v8a/libkos.so"] % 16384, 0)
            self.assertEqual(offsets["resources.arsc"] % 4, 0)
            with zipfile.ZipFile(dst) as archive:
                self.assertNotIn("META-INF/CERT.RSA", archive.namelist())
                self.assertNotIn("META-INF/MANIFEST.MF", archive.namelist())
                for name, data in entries.items():
                    if name not in ["META-INF/CERT.RSA", "META-INF/MANIFEST.MF"]:
                        self.assertEqual(archive.read(name), data)
                self.assertEqual(archive.read("classes.dex"), b"bytecode")

    def test_alignment_extra_parser_preserves_other_fields(self):
        original = struct.pack("<HH", 0x1234, 2) + b"ab"
        padding = struct.pack("<HHH", 0xD935, 5, 4) + b"\0" * 3
        self.assertEqual(alignment.without_alignment_extra(original + padding), original)
        with self.assertRaises(ValueError):
            alignment.without_alignment_extra(b"x")

    def test_never_overwrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.apk"
            source.write_bytes(b"untouched")
            with self.assertRaises(ValueError):
                alignment.align_apk(source, source)
            self.assertEqual(source.read_bytes(), b"untouched")


if __name__ == "__main__":
    unittest.main()
