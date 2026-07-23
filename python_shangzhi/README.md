# 商智 AI 商家经营顾问（真实 Agent 版）

面向本地生活商家的 AI 经营诊断作品集项目。后端使用 Python、LangChain、
LangGraph 和 OpenAI Responses API，前端展示经营看板、证据链、Agent 执行轨迹、
高风险操作确认、A/B 实验和人工评测。

## 一键启动

双击：

```text
启动商智.command
```

首次运行会自动：

1. 查找 Python 3.10 或更高版本；
2. 创建项目自己的 `.venv`；
3. 安装 `requirements.txt`；
4. 启动 `http://127.0.0.1:8000`。

停止程序：回到终端按 `Control + C`。

## 启用真实大模型

1. 双击 `配置模型.command`；
2. 在打开的 `.env` 中填写：

```dotenv
OPENAI_API_KEY=你的_API_Key
OPENAI_MODEL=gpt-5.6-luna
SHANGZHI_AGENT_MODE=auto
```

3. 保存并重新双击 `启动商智.command`。

页面右上角会显示：

- `LIVE AGENT · 模型名`：正在调用真实模型；
- `DEMO AGENT · OFFLINE`：没有 Key，使用明确标识的离线演示推理；
- `FALLBACK`：模型调用失败，本轮自动降级并在 Trace 中记录原因。

公开部署时，把 `OPENAI_API_KEY` 配置为服务器环境变量。访客不需要登录 GPT，
也不能从前端看到密钥。

## Agent 架构

```text
商家问题
  → 意图识别
  → LangChain 经营数据工具
  → LangGraph 检索节点
  → OpenAI 结构化诊断
  → 确定性证据/风险审核
  → 人工确认门
  → SQLite 记忆、行动与 Trace
```

### 已实现能力

- 真实 `ChatOpenAI` 模型调用，并启用 Responses API；
- Pydantic/JSON Schema 结构化输出；
- 6 个 LangChain 业务工具；
- LangGraph 四节点工作流；
- 经营事实、行业基准、评价、活动和库存检索；
- 事实/假设/建议分层与证据编号；
- 效果承诺、折扣、预算、活动、批量回复风险审核；
- 高风险行动必须由商家确认，默认不自动执行；
- SQLite 多轮对话记忆、行动状态与完整 Trace；
- SSE 流式返回 Agent 节点进度；
- 内置离线回退和可运行评测集；
- 请求限流、输入长度限制和后端密钥隔离。
- Agent 四类能力评测：规划、工具调用、记忆与对话体验；
- Badcase 分类、根因、修复方案和专项回归接口；
- 当前版本、历史版本与无工具基线的统一任务对比；
- 调用量、延迟、成本、工具健康、回退和确认覆盖率监控。

## 主要目录

```text
app.py                     FastAPI 接口、SSE、静态页面
agent/
  graph.py                 LangGraph 工作流
  llm.py                   ChatOpenAI 与离线回退
  tools.py                 LangChain 业务工具
  prompts.py               Agent Prompt
  guardrails.py            确定性风险审核
  memory.py                SQLite 记忆、行动、Trace
  schemas.py               结构化输入输出
  evals.py                 内置评测集
web/
  index.html               页面结构
  styles.css               Y2K 未来主义视觉
  app.js                   SSE 对话、证据链与确认交互
tests/                     单元与集成测试
```

## API

- `GET /api/health`
- `GET /api/config/status`
- `POST /api/agent/chat`
- `POST /api/agent/stream`
- `POST /api/agent/confirm`
- `GET /api/agent/history`
- `GET /api/agent/traces`
- `POST /api/evals/run`
- `GET /api/evals/summary`
- `GET /api/evals/capabilities`
- `GET /api/badcases`
- `POST /api/badcases/{case_id}/regression`
- `GET /api/competitors`
- `GET /api/observability`
- `GET /api/dashboard`
- `POST /api/experiment/calculate`
- `POST /api/annotations`
- `GET /api/docs`：交互式接口文档

## 公开部署

项目包含 `Dockerfile`、`.dockerignore` 和 `Procfile`。完整部署步骤见
`DEPLOYMENT.md`。生产环境必须把 `OPENAI_API_KEY` 配置为服务器 Secret，
不要上传 `.env`。

## 测试

```bash
.venv/bin/python -m unittest discover -s tests -v
```

所有经营数据均为模拟数据。真实业务落地时，将 `agent/data.py` 替换为数仓或商家
中心查询即可，Agent 编排、风控和前端无需重写。
