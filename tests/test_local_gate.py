"""Tests for the new local UI gate; never claim Android/native-engine testing."""
import hashlib
import shutil
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from local_gate import suppress_dialog, verify_primary_dex, execute_matches, verify_gate_dex, update_manifest, A
from assemble_gate import assemble
import xml.etree.ElementTree as ET


class CompiledKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import jdk4py
        except ImportError:
            raise unittest.SkipTest("Run the pinned tool bootstrap first.")
        if not (ROOT / ".tools/android/apktool.jar").exists():
            raise unittest.SkipTest("Pinned Apktool JAR is not installed.")
        cls.directory = tempfile.TemporaryDirectory()
        cls.output = Path(cls.directory.name) / "classes2.dex"
        assemble(str(jdk4py.JAVA), ROOT / "apk-patches/gate", cls.output)
        cls.dex = cls.output.read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_accepts_exact_key(self):
        self.assertTrue(execute_matches(self.dex, "SHADOWMODZ"))
        self.assertTrue(execute_matches(self.dex, " SHADOWMODZ\n"))

    def test_rejects_wrong_empty_null_and_case_changed_keys(self):
        for key in ["", None, "RANDOM", "shadowmodz", "SHADOWMODZ1", "SHADOW-MODZ"]:
            with self.subTest(key=key):
                self.assertFalse(execute_matches(self.dex, key))

    def test_java_trim_not_unicode_whitespace_normalization(self):
        self.assertFalse(execute_matches(self.dex, "\u00a0SHADOWMODZ\u00a0"))

    def test_expected_new_classes_and_validator_samples(self):
        self.assertEqual(verify_gate_dex(self.dex)["localGateValidatorSamplesPassed"], 8)


class UiPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import androguard
        except ImportError:
            raise unittest.SkipTest("Install pinned inspection tools first.")
        with zipfile.ZipFile(ROOT / "KOS_3.7-VStable.apk") as apk:
            cls.original = apk.read("classes.dex")
        cls.patched, cls.report = suppress_dialog(cls.original)

    def test_only_original_dialog_entry_and_header_checksums_change(self):
        self.assertEqual(len(self.original), len(self.patched))
        result = verify_primary_dex(self.original, self.patched)
        self.assertTrue(result["primaryDexOnlyUiPatch"])
        self.assertEqual(self.report["patchedBytes"], "0e000000")
        self.assertEqual(self.report["originalBytes"], "08001600")

    def test_reject_unrelated_code_changes(self):
        contents = bytearray(self.patched)
        contents[40] ^= 1
        with self.assertRaisesRegex(ValueError, "Unexpected primary DEX change"):
            verify_primary_dex(self.original, bytes(contents))

    def test_reject_bad_header_digest(self):
        contents = bytearray(self.patched)
        contents[12] ^= 1
        with self.assertRaisesRegex(ValueError, "Invalid DEX signature"):
            verify_primary_dex(self.original, bytes(contents))

    def test_new_manifest_launcher_and_private_original_activity(self):
        xml = '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.kos"><application android:name="com.kos.App"><activity android:name="com.kos.MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity></application></manifest>'
        root = ET.fromstring(update_manifest(xml))
        app = root.find("application")
        self.assertEqual(app.get(A+"name"), "com.kos.App")
        self.assertEqual(app.get(A+"appComponentFactory"), "com.shadowmodz.GateComponentFactory")
        activities = {a.get(A+"name"): a for a in app.findall("activity")}
        self.assertEqual(activities["com.kos.MainActivity"].get(A+"exported"), "false")
        self.assertIsNone(activities["com.kos.MainActivity"].find("intent-filter"))
        self.assertEqual(activities["com.shadowmodz.KeyActivity"].get(A+"exported"), "true")

    def test_refuse_already_patched_manifest(self):
        xml = '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:name="com.kos.App"><activity android:name="com.kos.MainActivity"/></application></manifest>'
        with self.assertRaisesRegex(ValueError, "already added"):
            update_manifest(update_manifest(xml))

    def test_no_native_grant_or_always_true_policy(self):
        policy = (ROOT / "apk-patches/gate/KeyPolicy.smali").read_text()
        self.assertNotIn("NativeBridge", policy)
        self.assertIn("KeyPolicy;->matches", policy)
        activity = (ROOT / "apk-patches/gate/KeyActivity.smali").read_text()
        self.assertIn("KeyPolicy;->isAccepted", activity)
        self.assertIn("Invalid Shadow Modz key.", activity)
        self.assertNotIn("Activation successful", activity)


if __name__ == "__main__":
    unittest.main()
