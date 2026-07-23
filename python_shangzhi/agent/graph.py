"""LangGraph 工作流：检索 → 诊断 → 风险审核 → 持久化。"""

from __future__ import annotations

import uuid
from typing import Any

from langgraph.graph import END, START, StateGraph

from .guardrails import review_diagnosis
from .llm import ModelGateway
from .memory import MemoryStore
from .schemas import ActionProposal, AgentResponse, AgentState
from .tools import TOOL_REGISTRY


def _detect_intent(message: str) -> str:
    if any(word in message for word in ["差评", "评价", "回复"]):
        return "review"
    if any(word in message for word in ["库存", "缺货", "滞销", "清仓"]):
        return "inventory"
    if any(word in message for word in ["预算", "推广", "投放", "活动", "券"]):
        return "campaign"
    return "overview"


def _call_tool(name: str, merchant_id: str) -> Any:
    return TOOL_REGISTRY[name].invoke({"merchant_id": merchant_id})


def build_agent_graph(gateway: ModelGateway, memory: MemoryStore):
    def retrieve_node(state: AgentState) -> dict:
        intent = _detect_intent(state["message"])
        merchant_id = state["merchant_id"]
        tool_names = [
            "get_merchant_profile",
            "get_metric_snapshot",
            "get_industry_benchmark",
        ]
        if intent in {"review", "overview"}:
            tool_names.append("get_review_topics")
        if intent in {"campaign", "overview"}:
            tool_names.append("get_campaign_history")
        if intent == "inventory":
            tool_names.append("get_inventory_risk")

        aliases = {
            "get_merchant_profile": "profile",
            "get_metric_snapshot": "metrics",
            "get_industry_benchmark": "benchmark",
            "get_review_topics": "reviews",
            "get_campaign_history": "campaigns",
            "get_inventory_risk": "inventory",
        }
        results = {
            aliases[name]: _call_tool(name, merchant_id)
            for name in tool_names
        }
        trace = list(state.get("trace", []))
        trace.append(
            {
                "node": "retrieve",
                "label": "经营数据检索",
                "status": "completed",
                "tools": tool_names,
            }
        )
        return {"intent": intent, "tool_results": results, "trace": trace}

    def diagnose_node(state: AgentState) -> dict:
        diagnosis, mode = gateway.diagnose(
            state["message"],
            state.get("history", []),
            state["tool_results"],
        )
        trace = list(state.get("trace", []))
        trace.append(
            {
                "node": "diagnose",
                "label": "大模型结构化诊断" if mode == "live" else "离线可审计诊断",
                "status": "completed",
                "mode": mode,
                "model": (
                    gateway.settings.openai_model
                    if mode == "live"
                    else (
                        f"{gateway.settings.openai_model} → offline-rule-engine"
                        if mode == "fallback"
                        else "offline-rule-engine"
                    )
                ),
            }
        )
        result = {"diagnosis": diagnosis, "mode": mode, "trace": trace}
        if gateway.last_error:
            result["model_error"] = gateway.last_error
        return result

    def guardrail_node(state: AgentState) -> dict:
        diagnosis, safety = review_diagnosis(state["diagnosis"])
        trace = list(state.get("trace", []))
        trace.append(
            {
                "node": "guardrail",
                "label": "证据与风险审核",
                "status": "completed",
                "risk_level": safety.level,
                "requires_confirmation": safety.requires_confirmation,
            }
        )
        return {"diagnosis": diagnosis, "safety": safety, "trace": trace}

    def persist_node(state: AgentState) -> dict:
        diagnosis = state["diagnosis"]
        safety = state["safety"]
        actions: list[ActionProposal] = []
        for recommendation in diagnosis.recommendations:
            if not recommendation.requires_confirmation:
                continue
            record = memory.create_action(
                thread_id=state["thread_id"],
                merchant_id=state["merchant_id"],
                title=recommendation.title,
                action_type=recommendation.action_type,
                risk_level=recommendation.risk_level,
                payload={
                    "steps": recommendation.steps,
                    "expected_signal": recommendation.expected_signal,
                    "auto_execute": False,
                },
            )
            actions.append(
                ActionProposal(
                    action_id=record["id"],
                    title=record["title"],
                    action_type=record["action_type"],
                    status=record["status"],
                    risk_level=record["risk_level"],
                    payload=record["payload"],
                )
            )

        trace = list(state.get("trace", []))
        trace.append(
            {
                "node": "persist",
                "label": "记忆与行动记录",
                "status": "completed",
                "pending_actions": len(actions),
            }
        )
        mode = state.get("mode", "demo")
        answer = diagnosis.conclusion
        if safety.blocked_reasons:
            answer = "本次建议未通过安全审核：" + "；".join(safety.blocked_reasons)

        response = AgentResponse(
            thread_id=state["thread_id"],
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            mode=mode if mode in {"live", "demo", "fallback"} else "demo",
            model=(
                gateway.settings.openai_model
                if mode == "live"
                else (
                    f"{gateway.settings.openai_model} → offline-rule-engine"
                    if mode == "fallback"
                    else "offline-rule-engine"
                )
            ),
            intent=diagnosis.intent,
            answer=answer,
            evidence=diagnosis.evidence,
            hypotheses=diagnosis.hypotheses,
            recommendations=diagnosis.recommendations,
            safety=safety,
            actions=actions,
            confidence=diagnosis.confidence,
            assumptions=diagnosis.assumptions,
            missing_data=diagnosis.missing_data,
            trace=trace,
        )
        memory.add_message(
            state["thread_id"],
            state["merchant_id"],
            "assistant",
            answer,
            {
                "mode": response.mode,
                "model": response.model,
                "evidence_count": len(response.evidence),
                "action_count": len(actions),
            },
        )
        for event in trace:
            memory.add_trace(state["thread_id"], event["node"], event)
        return {"response": response, "trace": trace}

    builder = StateGraph(AgentState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("diagnose", diagnose_node)
    builder.add_node("guardrail", guardrail_node)
    builder.add_node("persist", persist_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "diagnose")
    builder.add_edge("diagnose", "guardrail")
    builder.add_edge("guardrail", "persist")
    builder.add_edge("persist", END)
    return builder.compile()
