#!/usr/bin/env python3
"""Sign the branding test with a NEW test certificate, then audit the APK.

A valid signature is not evidence that the protected native engine will run.
Never use this certificate to claim compatibility with the original APK.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import zipfile
from pathlib import Path

from align_apk import check_alignment

ROOT = Path(__file__).resolve().parents[1]
SIGNING = ROOT / ".work/private-signing"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str], env: dict | None = None) -> str:
    result = subprocess.run(command, check=True, env=env, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.strip())
    # Passwords are passed through the environment, never printed in commands.
    if result.stderr:
        print(result.stderr.strip())
    return result.stdout


def sign(java: str, keytool: str) -> tuple[Path, str]:
    SIGNING.mkdir(parents=True, exist_ok=True, mode=0o700)
    SIGNING.chmod(0o700)
    password_file = SIGNING / "test-signing-password.txt"
    keystore = SIGNING / "shadow-branding-test.p12"
    if keystore.exists() and not password_file.exists():
        raise ValueError("Test keystore exists but its local password file is missing.")
    if not password_file.exists():
        # Nothing here is an app licence or an original signing credential.
        fd = os.open(password_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as file:
            file.write(secrets.token_urlsafe(40))
    env = dict(os.environ)
    env["SHADOW_TEST_SIGNING_PASSWORD"] = password_file.read_text().strip()
    if not keystore.exists():
        run([
            keytool, "-genkeypair", "-storetype", "PKCS12", "-keyalg", "RSA",
            "-keysize", "3072", "-validity", "3650", "-alias", "shadow-branding-test",
            "-dname", "CN=Shadow Modz Branding Test,O=Local Test",
            "-keystore", str(keystore), "-storepass:env", "SHADOW_TEST_SIGNING_PASSWORD",
            "-keypass:env", "SHADOW_TEST_SIGNING_PASSWORD",
        ], env)
        keystore.chmod(0o600)
    signer = str(ROOT / ".tools/android/apksigner.jar")
    signed = ROOT / ".work/shadow-signed.apk"
    run([
        java, "-jar", signer, "sign", "--ks", str(keystore),
        "--ks-key-alias", "shadow-branding-test",
        "--ks-pass", "env:SHADOW_TEST_SIGNING_PASSWORD",
        "--key-pass", "env:SHADOW_TEST_SIGNING_PASSWORD",
        "--min-sdk-version", "24", "--v1-signing-enabled", "false",
        "--v2-signing-enabled", "true", "--v3-signing-enabled", "true",
        "--out", str(signed), str(ROOT / ".work/shadow-aligned.apk"),
    ], env)
    verification = run([java, "-jar", signer, "verify", "--verbose", "--print-certs", str(signed)])
    return signed, verification


def dex_method_fingerprints(dex, class_name: str) -> dict:
    cls = dex.get_class(class_name)
    if cls is None:
        raise ValueError(f"Missing DEX class: {class_name}")
    return {
        method.get_name() + method.get_descriptor(): (
            method.get_access_flags_string(),
            [(i.get_name(), i.get_output()) for i in method.get_instructions()] if method.get_code() else [],
        )
        for method in cls.get_methods()
    }


def audit(signed: Path, verification: str) -> dict:
    from loguru import logger
    logger.remove()
    from androguard.core.apk import APK
    from androguard.core.dex import DEX

    config = json.loads((ROOT / "branding/config.json").read_text())
    original_path = ROOT / config["originalApk"]
    if file_hash(original_path) != config["originalApkSha256"]:
        raise ValueError("The original APK has changed.")
    apk = APK(str(signed))
    original = APK(str(original_path))
    if apk.get_app_name() != config["appName"]:
        raise ValueError("Compiled app label does not match the requested brand.")
    if apk.get_package() != original.get_package():
        raise ValueError("Package identity changed; this would break native JNI bindings.")
    if set(apk.get_permissions()) != set(original.get_permissions()):
        raise ValueError("APK permissions changed unexpectedly.")
    native_hashes = {}
    with zipfile.ZipFile(original_path) as old, zipfile.ZipFile(signed) as new:
        for info in old.infolist():
            if info.filename.endswith(".so"):
                contents = new.read(info.filename)
                if contents != old.read(info.filename):
                    raise ValueError(f"Native library changed: {info.filename}")
                if new.getinfo(info.filename).compress_type != zipfile.ZIP_STORED:
                    raise ValueError("Native libraries must stay uncompressed for extractNativeLibs=false.")
                native_hashes[info.filename] = hashlib.sha256(contents).hexdigest()
        if new.getinfo("resources.arsc").compress_type != zipfile.ZIP_STORED:
            raise ValueError("resources.arsc must be uncompressed for this target SDK.")
    old_dex, new_dex = DEX(original.get_dex()), DEX(apk.get_dex())
    protected_classes = [
        "Lcom/kos/Native/NativeBridge;",  # the native JNI interface
        "La/a/a/b;", "La/a/a/c;",        # encrypted native string decoders
        "Landroidx/emoji2/text/c3;",      # licence input validation
        "Landroidx/emoji2/text/h3;",      # native activation coroutine
        "Landroidx/emoji2/text/ao0;",     # native app-launch permission checks
    ]
    for cls in protected_classes:
        if dex_method_fingerprints(old_dex, cls) != dex_method_fingerprints(new_dex, cls):
            raise ValueError(f"Protected/native licensing path changed unexpectedly: {cls}")
    for cls in ["Lcom/shadowmodz/Branding;", "Lcom/shadowmodz/TelegramAction;"]:
        if new_dex.get_class(cls) is None:
            raise ValueError(f"New branding helper missing: {cls}")
    report = json.loads((ROOT / ".work/branding-report.json").read_text())
    report.update({
        "originalApkSha256": file_hash(original_path),
        "outputApkSha256": file_hash(signed),
        "outputApkBytes": signed.stat().st_size,
        "versionName": apk.get_androidversion_name(),
        "minSdk": apk.get_min_sdk_version(),
        "targetSdk": apk.get_target_sdk_version(),
        "nativeLibrariesVerifiedUnchanged": native_hashes,
        "protectedDexClassesVerifiedUnchanged": protected_classes,
        "alignmentVerified": check_alignment(signed),
        "apkSignatureVerification": verification.strip().splitlines(),
        "signingCertificate": "new-local-test-certificate-not-the-original",
        "runtimeTested": False,
        "licenseReplacementImplemented": False,
        "warning": "Branding test only. SHADOWMODZ is not configured as a working replacement licence. Native licence/integrity checks may reject this re-signed APK.",
    })
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", required=True)
    parser.add_argument("--keytool", required=True)
    args = parser.parse_args()
    signed, verification = sign(args.java, args.keytool)
    report = audit(signed, verification)
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    output = artifacts / "Shadow-Modz-branding-test.apk"
    shutil.copy2(signed, output)
    (artifacts / "Shadow-Modz-branding-test.apk.sha256").write_text(
        f"{report['outputApkSha256']}  {output.name}\n"
    )
    (artifacts / "branding-test-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Static APK audit passed. Android runtime and licence unlocking have NOT been verified.")


if __name__ == "__main__":
    main()
