"""Agent 产品运营数据：能力评测、Badcase、竞品实验与可观测性。"""

from __future__ import annotations

from typing import Any


CAPABILITY_REPORT = {
    "version": "v2.5-rc2",
    "dataset_version": "agent-eval-v2.5",
    "total_cases": 236,
    "pass_rate": 0.918,
    "severe_error_recall": 0.964,
    "average_case_cost": 0.071,
    "dimensions": [
        {
            "name": "规划能力",
            "score": 86.4,
            "metrics": {
                "task_decomposition_accuracy": 0.91,
                "step_order_accuracy": 0.88,
                "replan_success_rate": 0.79,
                "constraint_compliance": 0.87,
            },
        },
        {
            "name": "工具调用",
            "score": 92.1,
            "metrics": {
                "tool_selection_accuracy": 0.96,
                "parameter_accuracy": 0.91,
                "retry_success_rate": 0.84,
                "result_citation_accuracy": 0.97,
            },
        },
        {
            "name": "记忆能力",
            "score": 88.7,
            "metrics": {
                "cross_turn_consistency": 0.94,
                "preference_memory_accuracy": 0.90,
                "stale_memory_detection": 0.78,
                "merchant_isolation_accuracy": 0.99,
            },
        },
        {
            "name": "对话体验",
            "score": 89.5,
            "metrics": {
                "intent_accuracy": 0.95,
                "clarification_quality": 0.83,
                "actionability": 0.91,
                "merchant_satisfaction": 0.89,
            },
        },
    ],
}


BADCASES: list[dict[str, Any]] = [
    {
        "case_id": "BC-0241",
        "scenario": "零售 · 库存积压",
        "title": "折扣建议突破最低毛利约束",
        "category": "planning.constraint_omission",
        "severity": "S1",
        "status": "open",
        "owner": "Agent 策略",
        "model_version": "v2.5-rc1",
        "failed_node": "guardrail",
        "root_cause": "Planner 未把最低毛利约束传递给生成和风控节点。",
        "fix": "Planner 增加 required_constraints，并新增折扣后毛利校验器。",
        "regression_suite": ["inventory_margin_18", "tool_parameter_24"],
    },
    {
        "case_id": "BC-0237",
        "scenario": "餐饮 · 评价回复",
        "title": "批量回复工具参数缺少评价 ID",
        "category": "tool.parameter_missing",
        "severity": "S2",
        "status": "regression",
        "owner": "Agent 工程",
        "model_version": "v2.4",
        "failed_node": "tool_executor",
        "root_cause": "Planner 选择正确工具，但未补齐评价 ID 且重试沿用错误参数。",
        "fix": "调用前执行 Pydantic Schema 校验，缺参时回到检索节点。",
        "regression_suite": ["review_reply_parameter_24"],
    },
    {
        "case_id": "BC-0229",
        "scenario": "多轮对话 · 预算调整",
        "title": "沿用已过期的上月预算上限",
        "category": "memory.stale_conflict",
        "severity": "S2",
        "status": "fixed",
        "owner": "模型评测",
        "model_version": "v2.4",
        "failed_node": "memory_resolution",
        "root_cause": "冲突消解错误地让历史记忆覆盖了本轮明确输入。",
        "fix": "当前轮事实 > 已确认记忆 > 历史推断，并加入冲突回归集。",
        "regression_suite": ["memory_conflict_12"],
    },
]


COMPETITOR_REPORT = {
    "disclaimer": "匿名竞品与模拟体验测试，不代表竞品官方数据",
    "task_count": 12,
    "agents": [
        {"name": "商智 Agent", "planning": 86, "tools": 92, "memory": 89, "dialogue": 90, "safety": 96},
        {"name": "行业 Agent A", "planning": 91, "tools": 88, "memory": 82, "dialogue": 86, "safety": 90},
        {"name": "行业 Agent B", "planning": 83, "tools": 94, "memory": 76, "dialogue": 81, "safety": 87},
    ],
    "opportunities": [
        "保持价格、预算和批量操作的安全确认优势",
        "增加中途目标变化后的 Re-plan 专项评测",
        "通过参数 Schema 自校验补强工具失败恢复",
    ],
}


OBSERVABILITY_REPORT = {
    "window": "24h",
    "calls": 18_642,
    "p95_latency_seconds": 4.8,
    "tool_success_rate": 0.967,
    "average_cost_cny": 0.084,
    "fallback_rate": 0.018,
    "confirmation_coverage": 1.0,
    "tool_health": [
        {"tool": "get_metric_snapshot", "success_rate": 0.994, "p95_latency_seconds": 1.2},
        {"tool": "get_review_topics", "success_rate": 0.978, "p95_latency_seconds": 1.8},
        {"tool": "create_campaign", "success_rate": 0.942, "p95_latency_seconds": 2.6},
        {"tool": "reply_reviews", "success_rate": 0.917, "p95_latency_seconds": 2.1},
        {"tool": "adjust_ad_budget", "success_rate": 0.981, "p95_latency_seconds": 1.5},
    ],
    "alerts": [
        {"event": "tool_retry", "level": "warning", "detail": "reply_reviews 参数校验失败，重试后成功"},
        {"event": "guardrail_block", "level": "info", "detail": "预算翻倍请求已拦截并要求确认"},
        {"event": "memory_conflict", "level": "warning", "detail": "检测到本轮预算与历史记忆冲突"},
    ],
}


def list_badcases(status: str | None = None) -> list[dict[str, Any]]:
    if not status:
        return BADCASES
    return [item for item in BADCASES if item["status"] == status]


def run_badcase_regression(case_id: str) -> dict[str, Any]:
    matched = next((item for item in BADCASES if item["case_id"] == case_id), None)
    if not matched:
        raise KeyError(case_id)
    return {
        "case_id": case_id,
        "model_version": "v2.5-rc2",
        "status": "passed",
        "suite": matched["regression_suite"],
        "passed": 12,
        "total": 12,
        "remaining_risk": "low",
    }
