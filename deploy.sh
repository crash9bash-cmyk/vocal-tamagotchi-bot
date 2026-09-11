#!/usr/bin/env bash
# Деплой Mini App (bot/mini_app) на GitHub Pages через git subtree.
# Источник правды — bot/mini_app/index.html (файл НЕ дублируется).
# Токен запрашивается интерактивно и НЕ сохраняется в git config.
#
# Запуск (Git Bash / WSL):  bash deploy.sh
set -euo pipefail

REPO="crash9bash-cmyk/vocal-tamagotchi-web"
PREFIX="bot/mini_app"
BRANCH="main"

# проверяем, что мы в корне репо
if [ ! -f "$PREFIX/index.html" ]; then
  echo "✗ Не найден $PREFIX/index.html — запускай из корня проекта (Тамагочи/)."
  exit 1
fi

read -s -p "GitHub PAT (scope repo): " TOKEN
echo

REMOTE_URL="https://${TOKEN}@github.com/${REPO}.git"

# временный remote, чтобы токен не остался в git config
git remote remove _deploy_tmp 2>/dev/null || true
git remote add _deploy_tmp "$REMOTE_URL"

echo "→ subtree push ${PREFIX} → ${REPO}:${BRANCH}"
git subtree push --prefix "$PREFIX" _deploy_tmp "$BRANCH"

git remote remove _deploy_tmp
echo "✓ Deployed. Token scrubbed from git config."
echo "  URL: https://${REPO%/*}.github.io/${REPO#*/}/"
