#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

bash build_web.sh

rm -rf docs
mkdir -p docs
cp -R build/web/* docs/

touch docs/.nojekyll

echo "已生成 docs/，请提交并推送到 GitHub，然后在仓库设置开启 Pages（Source 选 main 分支 /docs）"
