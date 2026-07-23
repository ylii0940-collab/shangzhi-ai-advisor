"""Agent 输入、输出和状态的数据结构。"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class Evidence(BaseModel):
    evidence_id: str = Field(description="证据唯一编号，例如 E1")
    metric: str = Field(description="指标或事实名称")
    observed: str = Field(description="当前观测值")
    comparison: str = Field(description="对比基线或变化")
    source: str = Field(description="证据来源，只能引用工具返回的数据")


class Recommendation(BaseModel):
    title: str
    rationale: str
    steps: list[str] = Field(min_length=1, max_length=5)
    expected_signal: str = Field(description="验证建议有效性的指标，不承诺确定效果")
    action_type: str = Field(description="analysis/content/discount/budget/campaign/inventory/reply")
    risk_level: RiskLevel = "low"
    requires_confirmation: bool = False


class DiagnosisOutput(BaseModel):
    intent: str
    conclusion: str
    evidence: list[Evidence] = Field(min_length=1, max_length=6)
    hypotheses: list[str] = Field(default_factory=list, max_length=5)
    recommendations: list[Recommendation] = Field(min_length=1, max_length=4)
    confidence: float = Field(ge=0, le=1)
    assumptions: list[str] = Field(default_factory=list, max_length=5)
    missing_data: list[str] = Field(default_factory=list, max_length=5)


class SafetyReview(BaseModel):
    level: RiskLevel
    passed: bool
    requires_confirmation: bool
    warnings: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)


class ActionProposal(BaseModel):
    action_id: str
    title: str
    action_type: str
    status: Literal["pending", "approved", "rejected", "executed"]
    risk_level: RiskLevel
    payload: dict[str, Any]


class AgentResponse(BaseModel):
    thread_id: str
    message_id: str
    mode: Literal["live", "demo", "fallback"]
    model: str
    intent: str
    answer: str
    evidence: list[Evidence]
    hypotheses: list[str]
    recommendations: list[Recommendation]
    safety: SafetyReview
    actions: list[ActionProposal]
    confidence: float
    assumptions: list[str]
    missing_data: list[str]
    trace: list[dict[str, Any]]


class AgentState(TypedDict, total=False):
    thread_id: str
    merchant_id: str
    message: str
    history: list[dict[str, str]]
    intent: str
    tool_results: dict[str, Any]
    diagnosis: DiagnosisOutput
    safety: SafetyReview
    response: AgentResponse
    trace: list[dict[str, Any]]
    mode: str
    model_error: str

