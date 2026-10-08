#!/usr/bin/env bash
# Rebuild from the original APK with a new local key UI. NOT a native unlock.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
bash scripts/build_branding_test.sh --bootstrap-only
export PYTHONPATH="$ROOT/.tools/python${PYTHONPATH:+:$PYTHONPATH}"
JAVA="$(python3 -c 'import jdk4py; print(jdk4py.JAVA)')"
KEYTOOL="$(dirname "$JAVA")/keytool"
# Full source/resource decompilation for inspection, separate from packaging.
# Do not reassemble the original encrypted/native-bound classes wholesale.
"$JAVA" -jar .tools/android/apktool.jar d -f KOS_3.7-VStable.apk -o .work/local-gate-inspection
"$JAVA" -jar .tools/android/apktool.jar d -f --no-src KOS_3.7-VStable.apk -o .work/local-gate
python3 scripts/assemble_gate.py --java "$JAVA" apk-patches/gate .work/local-gate-classes2.dex
python3 scripts/local_gate.py .work/local-gate --gate-dex .work/local-gate-classes2.dex --report .work/local-gate-report.json
"$JAVA" -jar .tools/android/apktool.jar b .work/local-gate -o .work/local-gate-unsigned.apk
python3 scripts/align_apk.py .work/local-gate-unsigned.apk .work/local-gate-aligned.apk
python3 scripts/sign_and_audit.py --java "$JAVA" --keytool "$KEYTOOL" \
  --mode local-gate --aligned .work/local-gate-aligned.apk \
  --signed-intermediate .work/local-gate-signed.apk \
  --report-file .work/local-gate-report.json \
  --output artifacts/Shadow-Modz-local-gate-test.apk \
  --report-output artifacts/local-gate-test-report.json
printf '\nNew local entry key: SHADOWMODZ. Original licence dialog UI suppressed.\n'
printf 'NATIVE ENGINE ENTITLEMENTS/STARTUP ARE UNCHANGED AND UNVERIFIED.\n'
