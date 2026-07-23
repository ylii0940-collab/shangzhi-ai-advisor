"""确定性风险审核，避免把安全边界完全交给大模型。"""

from __future__ import annotations

import re

from .schemas import DiagnosisOutput, SafetyReview


HIGH_RISK_ACTIONS = {"discount", "budget", "campaign", "inventory", "reply"}
PROMISE_PATTERNS = [
    r"保证.{0,8}(提升|增长|清理|成交)",
    r"一定.{0,8}(提升|增长|清理|成交)",
    r"\d+\s*天内.{0,12}\d+%",
]


def review_diagnosis(diagnosis: DiagnosisOutput) -> tuple[DiagnosisOutput, SafetyReview]:
    warnings: list[str] = []
    blocked: list[str] = []
    requires_confirmation = False

    evidence_ids = {item.evidence_id for item in diagnosis.evidence}
    if len(evidence_ids) != len(diagnosis.evidence):
        blocked.append("证据编号重复，无法可靠追溯")

    for recommendation in diagnosis.recommendations:
        if recommendation.action_type in HIGH_RISK_ACTIONS:
            recommendation.requires_confirmation = True
            if recommendation.risk_level == "low":
                recommendation.risk_level = "medium"
        if recommendation.requires_confirmation:
            requires_confirmation = True

        joined = " ".join(
            [
                recommendation.title,
                recommendation.rationale,
                recommendation.expected_signal,
                *recommendation.steps,
            ]
        )
        if any(re.search(pattern, joined) for pattern in PROMISE_PATTERNS):
            warnings.append(f"“{recommendation.title}”包含疑似效果承诺，已要求人工确认")
            recommendation.requires_confirmation = True
            recommendation.risk_level = "high"
            requires_confirmation = True

    if diagnosis.confidence > 0.9 and diagnosis.missing_data:
        warnings.append("存在缺失数据但置信度偏高，已下调至 0.85")
        diagnosis.confidence = 0.85

    if not diagnosis.evidence:
        blocked.append("没有可验证证据")

    level = "high" if blocked else ("medium" if requires_confirmation or warnings else "low")
    return diagnosis, SafetyReview(
        level=level,
        passed=not blocked,
        requires_confirmation=requires_confirmation,
        warnings=warnings,
        blocked_reasons=blocked,
    )

