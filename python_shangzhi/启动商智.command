#!/bin/zsh
set -e
cd "$(dirname "$0")"

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "$candidate")"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "需要 Python 3.10 或更高版本。请先安装 Python 后重试。"
  read -k 1 "?按任意键退出..."
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo "首次运行：正在创建独立 Python 环境..."
  "$PYTHON_BIN" -m venv .venv
fi

if [[ ! -f ".venv/.deps-installed" || "requirements.txt" -nt ".venv/.deps-installed" ]]; then
  echo "正在安装/更新 LangChain、LangGraph 和 Web 服务依赖..."
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
  touch .venv/.deps-installed
fi

exec .venv/bin/python app.py

