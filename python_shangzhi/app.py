#!/usr/bin/env python3
"""商智 AI 商家经营顾问。

FastAPI 提供页面与接口，LangGraph 编排真实 Agent。没有 OpenAI Key 时会明确
运行 DEMO 模式；配置 Key 后自动切换到真实模型调用。
"""

from __future__ import annotations

import argparse
import json
import threading
import time
import webbrowser
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterator

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import AgentService, Settings


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
DATA_ROOT = ROOT / "data"

settings = Settings.from_env()
agent_service = AgentService(settings)

app = FastAPI(
    title="商智 AI 商家经营顾问",
    description="LangChain + LangGraph 商家经营诊断 Agent",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


DASHBOARD = {
    "score": 82,
    "metrics": [
        {"label": "今日实收", "value": 12680, "display": "¥12,680", "trend": "+8.6%"},
        {"label": "支付订单", "value": 186, "display": "186", "trend": "+12.3%"},
        {"label": "到店转化率", "value": 7.8, "display": "7.8%", "trend": "-1.4%"},
        {"label": "店铺评分", "value": 4.63, "display": "4.63", "trend": "+0.06"},
    ],
    "funnel": [
        {"label": "消息送达", "value": 48260, "rate": "100%"},
        {"label": "商家阅读", "value": 31849, "rate": "66.0%"},
        {"label": "商家回复", "value": 12421, "rate": "39.0%"},
        {"label": "接受建议", "value": 6583, "rate": "53.0%"},
        {"label": "执行操作", "value": 4147, "rate": "63.0%"},
        {"label": "经营改善", "value": 2364, "rate": "57.0%"},
    ],
    "opportunities": [
        {
            "level": "高优先级",
            "title": "套餐转化率连续 7 日下降",
            "detail": "曝光上涨 12%，支付转化率下降 18%",
            "impact": "预计少成交 56 单",
        },
        {
            "level": "可优化",
            "title": "晚市仍有空闲产能",
            "detail": "20:00 后到店率低于同商圈 21%",
            "impact": "预计可增收 ¥3,200",
        },
        {
            "level": "新机会",
            "title": "老客复购信号增强",
            "detail": "238 位收藏用户尚未再次到店",
            "impact": "建议定向召回",
        },
    ],
}


class SlidingWindowRateLimiter:
    """单机演示限流；生产环境可替换为 Redis。"""

    def __init__(self, limit: int = 30, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            events = self._events[key]
            while events and events[0] <= now - self.window_seconds:
                events.popleft()
            if len(events) >= self.limit:
                return False
            events.append(now)
            return True


rate_limiter = SlidingWindowRateLimiter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    thread_id: str | None = Field(default=None, max_length=100)
    merchant_id: str = Field(default="merchant_demo", max_length=100)


class ConfirmRequest(BaseModel):
    action_id: str = Field(min_length=5, max_length=100)
    approved: bool


class ExperimentRequest(BaseModel):
    traffic: int = Field(default=50, ge=10, le=90)


class AnnotationRequest(BaseModel):
    case_id: str = Field(default="CASE-0086", max_length=100)
    scores: dict[str, int] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list, max_length=20)
    note: str = Field(default="", max_length=2000)


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request) -> None:
    if not rate_limiter.allow(client_key(request)):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")


def sse(events: Iterator[dict[str, Any]]) -> Iterator[str]:
    for event in events:
        event_type = event.get("type", "message")
        payload = json.dumps(event, ensure_ascii=False)
        yield f"event: {event_type}\ndata: {payload}\n\n"


@app.exception_handler(Exception)
async def unhandled_exception(_: Request, error: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": "服务暂时不可用",
            "error_type": type(error).__name__,
        },
    )


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "商智 AI Agent",
        "version": "2.0.0",
        "agent": agent_service.status(),
    }


@app.get("/api/config/status")
def config_status() -> dict[str, Any]:
    """只返回配置状态，永远不返回密钥。"""
    return {"ok": True, **agent_service.status()}


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    return {"ok": True, "data": DASHBOARD, "updated_at": int(time.time())}


@app.post("/api/agent/chat")
def agent_chat(payload: ChatRequest, request: Request) -> dict[str, Any]:
    check_rate_limit(request)
    result = agent_service.run(
        payload.message.strip(),
        payload.thread_id,
        payload.merchant_id,
    )
    return {"ok": True, "data": result.model_dump(mode="json")}


@app.post("/api/agent/stream")
def agent_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    check_rate_limit(request)
    events = agent_service.stream(
        payload.message.strip(),
        payload.thread_id,
        payload.merchant_id,
    )
    return StreamingResponse(
        sse(events),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat")
def backwards_compatible_chat(
    payload: ChatRequest, request: Request
) -> dict[str, Any]:
    """兼容旧前端，同时返回 Agent 结构化结果。"""
    check_rate_limit(request)
    result = agent_service.run(
        payload.message.strip(),
        payload.thread_id,
        payload.merchant_id,
    )
    return {
        "ok": True,
        "reply": result.answer,
        "thread_id": result.thread_id,
        "agent": result.model_dump(mode="json"),
    }


@app.post("/api/agent/confirm")
def confirm_action(payload: ConfirmRequest, request: Request) -> dict[str, Any]:
    check_rate_limit(request)
    try:
        action = agent_service.confirm_action(payload.action_id, payload.approved)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "ok": True,
        "action": action,
        "message": (
            "已记录商家确认，模拟执行完成"
            if payload.approved
            else "已拒绝该行动，不会执行任何变更"
        ),
    }


@app.get("/api/agent/history")
def agent_history(
    thread_id: str = Query(min_length=5, max_length=100),
) -> dict[str, Any]:
    return {"ok": True, "messages": agent_service.history(thread_id)}


@app.get("/api/agent/traces")
def agent_traces(
    thread_id: str = Query(min_length=5, max_length=100),
) -> dict[str, Any]:
    return {"ok": True, "traces": agent_service.traces(thread_id)}


@app.post("/api/evals/run")
def run_evaluation(request: Request) -> dict[str, Any]:
    check_rate_limit(request)
    return {"ok": True, "result": agent_service.run_evals()}


@app.get("/api/evals/summary")
def evaluation_summary() -> dict[str, Any]:
    return {"ok": True, "summary": agent_service.eval_summary()}


@app.post("/api/experiment/calculate")
def calculate_experiment(payload: ExperimentRequest) -> dict[str, Any]:
    traffic = payload.traffic
    total = 48_000
    b_samples = round(total * traffic / 100)
    a_samples = total - b_samples
    days = max(7, round(14 * 50 / min(traffic, 100 - traffic)))
    power = 92 if 35 <= traffic <= 65 else 78
    return {
        "ok": True,
        "traffic": traffic,
        "a_samples": a_samples,
        "b_samples": b_samples,
        "estimated_days": days,
        "power": power,
    }


@app.post("/api/annotations")
def save_annotation(payload: AnnotationRequest) -> dict[str, Any]:
    DATA_ROOT.mkdir(exist_ok=True)
    record = {
        "created_at": int(time.time()),
        "case_id": payload.case_id,
        "scores": payload.scores,
        "errors": payload.errors,
        "note": payload.note,
    }
    with (DATA_ROOT / "annotations.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"ok": True, "message": "标注已保存", "next_case": "CASE-0087"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


app.mount("/", StaticFiles(directory=WEB_ROOT, html=True), name="web")


def main() -> None:
    parser = argparse.ArgumentParser(description="运行商智 AI Agent")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print("=" * 66)
    print("商智 AI 商家经营顾问 · LangChain + LangGraph")
    print(f"访问地址：{url}")
    print(f"Agent 模式：{agent_service.status()['mode'].upper()}")
    print(f"模型：{agent_service.status()['model']}")
    if agent_service.status()["mode"] != "live":
        print("提示：复制 .env.example 为 .env 并填写 OPENAI_API_KEY 可启用真实模型。")
    print("停止程序：在终端按 Control + C")
    print("=" * 66)
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
