"""Guard the resource-only crash-isolation strategy; not Android runtime tests."""
import hashlib
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from rebrand_apk import rebrand_strings, patch_styles
from rebrand_resources import verify_original_dex
from sign_and_audit import verify_dex_bytes, certificate_digest


class CompatibilityTests(unittest.TestCase):
    def setup_dex_fixture(self, directory):
        decoded = Path(directory) / "decoded"
        decoded.mkdir()
        original = Path(directory) / "original.apk"
        contents = b"exact-original-bytecode"
        with zipfile.ZipFile(original, "w") as archive:
            archive.writestr("classes.dex", contents)
        (decoded / "classes.dex").write_bytes(contents)
        return decoded, original, contents

    def test_preserves_exact_dex(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, original, contents = self.setup_dex_fixture(directory)
            self.assertEqual(verify_original_dex(decoded, original), {"classes.dex": hashlib.sha256(contents).hexdigest()})

    def test_refuses_reassembled_smali(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, original, _ = self.setup_dex_fixture(directory)
            (decoded / "smali").mkdir()
            with self.assertRaisesRegex(ValueError, "no-src"):
                verify_original_dex(decoded, original)

    def test_refuses_modified_dex(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, original, _ = self.setup_dex_fixture(directory)
            (decoded / "classes.dex").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "bytes changed"):
                verify_original_dex(decoded, original)

    def test_refuses_extra_dex(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, original, _ = self.setup_dex_fixture(directory)
            (decoded / "classes2.dex").write_bytes(b"extra")
            with self.assertRaisesRegex(ValueError, "inventory"):
                verify_original_dex(decoded, original)

    def test_final_apk_dex_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, original, contents = self.setup_dex_fixture(directory)
            rebuilt = Path(directory) / "rebuilt.apk"
            with zipfile.ZipFile(rebuilt, "w") as archive:
                archive.writestr("classes.dex", contents)
            with zipfile.ZipFile(original) as old, zipfile.ZipFile(rebuilt) as new:
                self.assertEqual(verify_dex_bytes(old, new)["classes.dex"], hashlib.sha256(contents).hexdigest())
            with zipfile.ZipFile(rebuilt, "w") as archive:
                archive.writestr("classes.dex", b"different")
            with zipfile.ZipFile(original) as old, zipfile.ZipFile(rebuilt) as new:
                with self.assertRaisesRegex(ValueError, "DEX bytes changed"):
                    verify_dex_bytes(old, new)

    def test_final_apk_refuses_extra_dex(self):
        with tempfile.TemporaryDirectory() as directory:
            _, original, contents = self.setup_dex_fixture(directory)
            rebuilt = Path(directory) / "rebuilt.apk"
            with zipfile.ZipFile(rebuilt, "w") as archive:
                archive.writestr("classes.dex", contents)
                archive.writestr("classes2.dex", b"extra")
            with zipfile.ZipFile(original) as old, zipfile.ZipFile(rebuilt) as new:
                with self.assertRaisesRegex(ValueError, "inventory"):
                    verify_dex_bytes(old, new)

    def test_do_not_mislabel_original_contact_action(self):
        xml = '<resources><string name="app_name">KOS</string><string name="license_buy_prompt">Buy a key</string></resources>'
        new, count = rebrand_strings(xml, "Shadow Modz", None)
        self.assertEqual(count, 1)
        self.assertIn("Buy a key", new)
        self.assertNotIn("Telegram", new)

    def test_preserve_animated_splash_type(self):
        xml = '<resources><style name="Theme.App.Starting"><item name="windowSplashScreenAnimatedIcon">@drawable/avd_8_ball_spin</item></style></resources>'
        new = patch_styles(xml, preserve_animated_splash=True)
        self.assertIn("@drawable/avd_8_ball_spin", new)
        self.assertNotIn("@mipmap", new)
        vector = (ROOT / "branding/Shadow-Modz-splash-vector.xml").read_text()
        self.assertIn('android:name="rotation_group"', vector)

    def test_certificate_fingerprint_parser(self):
        digest = "ab" * 32
        self.assertEqual(certificate_digest("Signer #1 certificate SHA-256 digest: " + digest), digest)
        self.assertIsNone(certificate_digest("No certificate"))


if __name__ == "__main__":
    unittest.main()
