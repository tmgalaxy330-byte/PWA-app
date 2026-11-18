#!/usr/bin/env bash
# ロジトレ 自動テスト一式。リポジトリ直下で `bash tests/run.sh` を実行する。
# 事前準備: pip install playwright && python -m playwright install chromium
# 既存のChromeを使う場合: CHROME_PATH=/usr/bin/google-chrome bash tests/run.sh
set -e
cd "$(dirname "$0")/.."
python3 -m http.server 8765 >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV' EXIT
sleep 1
for t in e2e_mobile e2e_desktop e2e_templates; do
  echo "=== $t ==="
  python3 tests/$t.py
done
echo "ALL TESTS PASSED"
