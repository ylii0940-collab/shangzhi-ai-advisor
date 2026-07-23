#!/bin/zsh
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/python_shangzhi"
cd "$PROJECT_DIR"

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "$candidate")"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "需要 Python 3.10 或更高版本。"
  read -k 1 "?按任意键退出..."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "需要 Node.js 22.13 或更高版本。"
  read -k 1 "?按任意键退出..."
  exit 1
fi

if [[ ! -x "$BACKEND_DIR/.venv/bin/python" ]]; then
  echo "首次运行：创建 Python 独立环境..."
  "$PYTHON_BIN" -m venv "$BACKEND_DIR/.venv"
fi

if [[ ! -f "$BACKEND_DIR/.venv/.deps-installed" || "$BACKEND_DIR/requirements.txt" -nt "$BACKEND_DIR/.venv/.deps-installed" ]]; then
  echo "安装 Python Agent 依赖..."
  "$BACKEND_DIR/.venv/bin/python" -m pip install --upgrade pip
  "$BACKEND_DIR/.venv/bin/python" -m pip install -r "$BACKEND_DIR/requirements.txt"
  touch "$BACKEND_DIR/.venv/.deps-installed"
fi

if [[ ! -d "$PROJECT_DIR/node_modules" ]]; then
  echo "安装完整前端依赖..."
  npm install
fi

cleanup() {
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "启动 Python LangGraph Agent：http://127.0.0.1:8000"
(
  cd "$BACKEND_DIR"
  exec .venv/bin/python app.py --host 127.0.0.1 --port 8000 --no-browser
) &
BACKEND_PID=$!

echo "启动完整产品前端：http://127.0.0.1:3000"
AGENT_API_URL=http://127.0.0.1:8000 npm run dev &
FRONTEND_PID=$!

sleep 3
open "http://127.0.0.1:3000"

echo ""
echo "商智完整前后端已启动。关闭本窗口或按 Control + C 可同时停止服务。"
wait
