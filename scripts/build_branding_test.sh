#!/usr/bin/env bash
# Builds a cosmetic test APK only. It does not set SHADOWMODZ as a licence.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p .tools/android .work artifacts
export PYTHONPATH="$ROOT/.tools/python${PYTHONPATH:+:$PYTHONPATH}"

# Tools remain local/ignored. Community npm package vendors Apktool 2.9.3 and
# Android apksigner 0.9; verify the jar checksums and do not execute npm scripts.
if ! python3 -c 'import jdk4py; from PIL import Image; import androguard' >/dev/null 2>&1; then
  python3 -m pip install --target .tools/python --upgrade -r requirements-tools.txt
fi
JAVA="$(python3 -c 'import jdk4py; print(jdk4py.JAVA)')"
KEYTOOL="$(dirname "$JAVA")/keytool"
if [[ ! -f .tools/android/apktool.jar || ! -f .tools/android/apksigner.jar ]]; then
  npm pack @postar/apktool-node@0.3.4 --ignore-scripts --pack-destination .tools
  tar -xzf .tools/postar-apktool-node-0.3.4.tgz -C .tools/android --strip-components=2 \
    package/lib/apktool.jar package/lib/apksigner.jar
fi
printf '%s\n' \
  '7956eb04194300ce0d0a84ad18771eebc94b89fb8d1ddcce8ea4c056818646f4  .tools/android/apktool.jar' \
  'eefdd6aed9db9fb849e4c98a50d8741e19d1b674ba6547220bcb9c3ed152123a  .tools/android/apksigner.jar' \
  | sha256sum --check --status
printf '%s\n' \
  '07900492ca1a730ee37d7acac900fde25bde8dc0299253665935b743b1a677cb  KOS_3.7-VStable.apk' \
  | sha256sum --check --status

python3 -m unittest discover -s tests -v
"$JAVA" -jar .tools/android/apktool.jar d -f KOS_3.7-VStable.apk -o .work/shadowmodz
python3 scripts/rebrand_apk.py .work/shadowmodz --report .work/branding-report.json
"$JAVA" -jar .tools/android/apktool.jar b .work/shadowmodz -o .work/shadow-unsigned.apk
python3 scripts/align_apk.py .work/shadow-unsigned.apk .work/shadow-aligned.apk
python3 scripts/sign_and_audit.py --java "$JAVA" --keytool "$KEYTOOL"
printf '\nBuilt artifacts/Shadow-Modz-branding-test.apk.\n'
printf 'IMPORTANT: Native licensing is unchanged; SHADOWMODZ is NOT a working replacement key.\n'
