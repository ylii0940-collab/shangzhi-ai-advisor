#!/bin/zsh
set -e
cd "$(dirname "$0")"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
fi

echo "即将打开本地 .env 配置文件。"
echo "只需把 OPENAI_API_KEY= 后面填入你的 API Key，然后保存并重新启动项目。"
echo "密钥不会写进前端，也不会包含在 ZIP 或 Git 中。"
open -e .env

