#!/usr/bin/env bash
# Crash-isolation candidate: original executable code; no licence replacement.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
bash scripts/build_branding_test.sh --bootstrap-only
export PYTHONPATH="$ROOT/.tools/python${PYTHONPATH:+:$PYTHONPATH}"
JAVA="$(python3 -c 'import jdk4py; print(jdk4py.JAVA)')"
KEYTOOL="$(dirname "$JAVA")/keytool"
"$JAVA" -jar .tools/android/apktool.jar d -f --no-src KOS_3.7-VStable.apk -o .work/compatibility
python3 scripts/rebrand_resources.py .work/compatibility --report .work/compatibility-report.json
"$JAVA" -jar .tools/android/apktool.jar b .work/compatibility -o .work/compatibility-unsigned.apk
python3 scripts/align_apk.py .work/compatibility-unsigned.apk .work/compatibility-aligned.apk
python3 scripts/sign_and_audit.py --java "$JAVA" --keytool "$KEYTOOL" \
  --mode resource-only --aligned .work/compatibility-aligned.apk \
  --signed-intermediate .work/compatibility-signed.apk \
  --report-file .work/compatibility-report.json \
  --output artifacts/Shadow-Modz-compatibility-test.apk \
  --report-output artifacts/compatibility-test-report.json
printf '\nBuilt a crash-isolation candidate; not an Android-verified crash fix.\n'
printf 'Original DEX/native licensing unchanged. SHADOWMODZ and any-key mode are not implemented.\n'
