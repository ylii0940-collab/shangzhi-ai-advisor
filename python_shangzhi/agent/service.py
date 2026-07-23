"""Agent 应用服务：封装图运行、SSE 事件、记忆和行动确认。"""

from __future__ import annotations

import uuid
from typing import Any, Iterator

from .evals import run_evals
from .graph import build_agent_graph
from .llm import ModelGateway
from .memory import MemoryStore
from .schemas import AgentResponse
from .settings import Settings


NODE_LABELS = {
    "retrieve": "检索商家经营数据",
    "diagnose": "生成结构化经营诊断",
    "guardrail": "检查证据、承诺与操作风险",
    "persist": "保存记忆与待确认行动",
}


class AgentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.memory = MemoryStore(settings.db_path)
        self.gateway = ModelGateway(settings)
        self.graph = build_agent_graph(self.gateway, self.memory)

    def status(self) -> dict[str, Any]:
        return {
            "configured": bool(self.settings.openai_api_key),
            "requested_mode": self.settings.agent_mode,
            "mode": self.gateway.mode,
            "model": (
                self.settings.openai_model
                if self.settings.live_enabled
                else "offline-rule-engine"
            ),
            "framework": "LangChain + LangGraph",
            "responses_api": self.settings.live_enabled,
            "memory": "SQLite",
            "confirmation_gate": True,
            "last_model_error": self.gateway.last_error,
        }

    def stream(
        self,
        message: str,
        thread_id: str | None = None,
        merchant_id: str = "merchant_demo",
    ) -> Iterator[dict[str, Any]]:
        thread_id = thread_id or f"thread_{uuid.uuid4().hex[:12]}"
        history = self.memory.history(thread_id)
        self.memory.add_message(thread_id, merchant_id, "user", message)
        initial_state = {
            "thread_id": thread_id,
            "merchant_id": merchant_id,
            "message": message,
            "history": history,
            "trace": [],
        }
        yield {
            "type": "start",
            "thread_id": thread_id,
            "mode": self.gateway.mode,
            "model": (
                self.settings.openai_model
                if self.settings.live_enabled
                else "offline-rule-engine"
            ),
        }
        final_response: AgentResponse | None = None
        try:
            for update in self.graph.stream(initial_state, stream_mode="updates"):
                for node_name, payload in update.items():
                    if payload.get("response"):
                        final_response = payload["response"]
                    yield {
                        "type": "step",
                        "node": node_name,
                        "label": NODE_LABELS.get(node_name, node_name),
                        "status": "completed",
                    }
            if final_response is None:
                raise RuntimeError("Agent 未生成最终结果")
            yield {
                "type": "final",
                "data": final_response.model_dump(mode="json"),
            }
        except Exception as error:
            self.memory.add_trace(
                thread_id,
                "error",
                {"error_type": type(error).__name__, "message": str(error)[:500]},
            )
            yield {
                "type": "error",
                "error": "Agent 运行失败，请检查模型配置或稍后重试。",
                "detail": f"{type(error).__name__}: {str(error)[:300]}",
            }

    def run(self, message: str, thread_id: str | None, merchant_id: str) -> AgentResponse:
        final: AgentResponse | None = None
        error: str | None = None
        for event in self.stream(message, thread_id, merchant_id):
            if event["type"] == "final":
                final = AgentResponse.model_validate(event["data"])
            elif event["type"] == "error":
                error = event["error"]
        if final:
            return final
        raise RuntimeError(error or "Agent 未返回结果")

    def confirm_action(self, action_id: str, approved: bool) -> dict[str, Any]:
        existing = self.memory.get_action(action_id)
        if not existing:
            raise KeyError("行动不存在")
        if existing["status"] != "pending":
            return existing
        updated = self.memory.update_action(action_id, approved)
        if not updated:
            raise RuntimeError("行动状态更新失败")
        self.memory.add_trace(
            updated["thread_id"],
            "human_confirmation",
            {
                "action_id": action_id,
                "approved": approved,
                "status": updated["status"],
            },
        )
        return updated

    def history(self, thread_id: str) -> list[dict[str, str]]:
        return self.memory.history(thread_id)

    def traces(self, thread_id: str) -> list[dict[str, Any]]:
        return self.memory.traces(thread_id)

    def run_evals(self) -> dict:
        return run_evals(self.memory)

    def eval_summary(self) -> dict:
        return self.memory.eval_summary()
