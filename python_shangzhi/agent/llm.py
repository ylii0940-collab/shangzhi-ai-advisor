"""真实模型网关与可测试的离线推理。"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .prompts import SYSTEM_PROMPT, build_diagnosis_prompt
from .schemas import DiagnosisOutput, Evidence, Recommendation
from .settings import Settings


class ModelGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.last_error = ""
        self._mode = "demo"
        self._structured_model = None
        if settings.live_enabled:
            model = ChatOpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                use_responses_api=True,
                reasoning_effort=settings.reasoning_effort,
                max_retries=2,
                timeout=60,
            )
            self._structured_model = model.with_structured_output(
                DiagnosisOutput,
                method="json_schema",
            )
            self._mode = "live"

    @property
    def mode(self) -> str:
        return self._mode

    def diagnose(
        self,
        message: str,
        history: list[dict[str, str]],
        tool_results: dict[str, Any],
    ) -> tuple[DiagnosisOutput, str]:
        if self._structured_model is None:
            return offline_diagnosis(message, tool_results), "demo"

        try:
            result = self._structured_model.invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(
                        content=build_diagnosis_prompt(message, history, tool_results)
                    ),
                ]
            )
            self.last_error = ""
            self._mode = "live"
            return result, "live"
        except Exception as error:
            # 公共状态只暴露错误类型，避免第三方 SDK 的异常文本带出密钥片段。
            self.last_error = type(error).__name__
            self._mode = "fallback"
            if self.settings.agent_mode == "live":
                raise
            return offline_diagnosis(message, tool_results), "fallback"


def offline_diagnosis(message: str, tool_results: dict[str, Any]) -> DiagnosisOutput:
    """无 Key 时的确定性演示推理；不会伪装成真实模型调用。"""
    metrics = tool_results.get("metrics", {})
    reviews = tool_results.get("reviews", {})
    campaigns = tool_results.get("campaigns", [])
    inventory = tool_results.get("inventory", {})
    benchmarks = tool_results.get("benchmark", {})
    profile = tool_results.get("profile", {})

    evidence = [
        Evidence(
            evidence_id="E1",
            metric="套餐曝光",
            observed=f"{metrics.get('package_impressions_7d', 18420):,}",
            comparison=f"近7日变化 {metrics.get('package_impressions_change', 0.12):+.0%}",
            source="get_metric_snapshot",
        ),
        Evidence(
            evidence_id="E2",
            metric="套餐支付转化率",
            observed=f"{metrics.get('package_conversion_7d', 0.078):.1%}",
            comparison=(
                f"环比 {metrics.get('package_conversion_change', -0.18):+.0%}；"
                f"同商圈中位数 {benchmarks.get('package_conversion_median', 0.091):.1%}"
            ),
            source="get_metric_snapshot + get_industry_benchmark",
        ),
    ]

    if reviews:
        top_topic = (reviews.get("topics") or [{"topic": "暂无", "count": 0}])[0]
        evidence.append(
            Evidence(
                evidence_id="E3",
                metric="负向评价",
                observed=f"近30日 {reviews.get('negative_30d', 0)} 条",
                comparison=(
                    f"负向率 {reviews.get('negative_rate', 0):.1%}；"
                    f"首要主题“{top_topic.get('topic')}”{top_topic.get('count')}条"
                ),
                source="get_review_topics",
            )
        )

    constraints = profile.get("constraints", {})
    if "差评" in message or "评价" in message:
        conclusion = "评价侧最值得优先处理的是“分量不足”和“套餐说明不清”，它们与套餐转化下降同时出现，但尚不能直接证明因果。"
        action_type = "reply"
        title = "先修正套餐表达，再小范围验证评价回复"
        rationale = "E3 显示负向评价主要集中在分量与套餐说明，先修正文案并抽样回复，可以验证问题是否来自信息预期。"
        steps = [
            "将负向评价按分量、出餐和套餐说明分组，人工抽查原文",
            "为三类问题分别起草回复模板，不承诺退款或确定效果",
            "先由商家审核 10 条，再决定是否扩大批量回复范围",
        ]
        expected_signal = "观察评价回复率、二次投诉率和套餐页咨询主题是否改善"
    elif "预算" in message or "推广" in message:
        campaign = campaigns[0] if campaigns else {}
        evidence.append(
            Evidence(
                evidence_id=f"E{len(evidence) + 1}",
                metric="历史推广活动",
                observed=campaign.get("name", "暂无可用活动"),
                comparison=(
                    f"领取率 {campaign.get('claim_rate', 0):.1%}；"
                    f"核销率 {campaign.get('redeem_rate', 0):.1%}；"
                    f"增量订单 {campaign.get('incremental_orders', 0)}"
                ),
                source="get_campaign_history",
            )
        )
        conclusion = "历史活动有增量信号，但当前证据不足以支持直接扩大预算，应先设置预算上限并进行小流量验证。"
        action_type = "budget"
        title = "建立小流量预算实验"
        rationale = (
            f"历史活动存在核销和增量订单信号，但商家日预算上限为 "
            f"¥{constraints.get('max_daily_ad_budget', 800)}，不能直接翻倍。"
        )
        steps = [
            "保持对照组预算不变，实验组仅提高 10%，且不超过商家日预算上限",
            "仅分配 20% 可投放流量，运行 7 天后再判断是否扩量",
            "同时监控获客成本、增量订单、退款率和边际 ROI",
        ]
        expected_signal = "实验组边际 ROI 为正、获客成本未恶化且退款率稳定时再申请扩量"
    elif any(word in message for word in ["库存", "缺货", "滞销", "清仓"]):
        skus = inventory.get("high_risk_skus", [])
        sku = skus[0] if skus else {"name": "暂无SKU", "stock_days": 0, "gross_margin_rate": 0}
        evidence.append(
            Evidence(
                evidence_id=f"E{len(evidence) + 1}",
                metric="库存与毛利",
                observed=f"{sku.get('name')} · 库存 {sku.get('stock_days')} 天",
                comparison=(
                    f"毛利率 {sku.get('gross_margin_rate', 0):.1%}；"
                    f"最低约束 {constraints.get('minimum_margin_rate', 0.12):.1%}"
                ),
                source="get_inventory_risk + get_merchant_profile",
            )
        )
        conclusion = "当前库存数据不足以支持全店清仓；应先按 SKU 的库存天数和毛利空间分层，任何折扣发布前都要确认最低毛利约束。"
        action_type = "inventory"
        title = "创建 SKU 分层去库存实验"
        rationale = "库存风险和毛利空间在 SKU 间不同，统一降价会放大毛利损失。"
        steps = [
            "按库存天数、近14日销量和毛利率划分高/中/低风险 SKU",
            "只对高库存且毛利空间足够的 SKU 测试 5% 与 10% 两档权益",
            "发布前重新计算活动后毛利率，并由商家确认商品范围与截止时间",
        ]
        expected_signal = "库存周转改善且活动后毛利率持续高于商家最低约束"
    else:
        conclusion = "套餐曝光上涨但支付转化下降，优先检查价格感知、分量表达和近期负向评价；当前只能判断关联，不能直接归因。"
        action_type = "content"
        title = "优化双人套餐信息表达"
        rationale = "E1 显示曝光增长，而 E2 显示转化下降；先调整低风险的信息表达可以验证用户理解问题。"
        steps = [
            "保持价格不变，仅补充分量、适用人数和核心菜品图片",
            "随机分配 20% 流量进入实验组，运行 7 天",
            "比较套餐详情到支付转化、退款率和差评率",
        ]
        expected_signal = "若假设成立，实验组详情到支付转化率应改善，且退款率不恶化"

    return DiagnosisOutput(
        intent="经营诊断",
        conclusion=conclusion,
        evidence=evidence,
        hypotheses=[
            "套餐曝光人群扩大后，新增流量的购买意愿可能较弱",
            "分量与套餐说明相关负向评价可能影响价格感知",
        ],
        recommendations=[
            Recommendation(
                title=title,
                rationale=rationale,
                steps=steps,
                expected_signal=expected_signal,
                action_type=action_type,
                risk_level="medium" if action_type != "content" else "low",
                requires_confirmation=action_type != "content",
            ),
            Recommendation(
                title="补充原因验证数据",
                rationale="现有数据只能证明转化下降与评价变化同时发生。",
                steps=[
                    "按新老客、来源渠道和时段拆分套餐转化",
                    "记录套餐页停留、退出位置与客服咨询主题",
                ],
                expected_signal="定位转化下降最集中的人群与页面环节",
                action_type="analysis",
                risk_level="low",
                requires_confirmation=False,
            ),
        ],
        confidence=0.82,
        assumptions=["当前模拟数据口径一致", "同商圈基准具有可比性"],
        missing_data=[
            "套餐详情页行为事件",
            f"折扣方案执行前需满足最低毛利率 {constraints.get('minimum_margin_rate', 0.12):.0%}",
        ],
    )
