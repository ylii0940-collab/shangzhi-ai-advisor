"""LangChain 工具：把业务数据查询能力暴露给 Agent。"""

from __future__ import annotations

from langchain_core.tools import tool

from . import data


@tool
def get_merchant_profile(merchant_id: str) -> dict:
    """查询商家行业、门店和可执行约束；制定建议前必须先调用。"""
    return data.merchant_profile(merchant_id)


@tool
def get_metric_snapshot(merchant_id: str) -> dict:
    """查询商家最近经营指标、转化变化与损失估算。"""
    return data.metric_snapshot(merchant_id)


@tool
def get_review_topics(merchant_id: str) -> dict:
    """查询近30天评价数量、负向率和主要负向主题。"""
    return data.review_snapshot(merchant_id)


@tool
def get_campaign_history(merchant_id: str) -> list[dict]:
    """查询历史营销活动及曝光、领取、核销和增量订单表现。"""
    return data.campaign_snapshot(merchant_id)


@tool
def get_industry_benchmark(merchant_id: str) -> dict:
    """查询同城市、同商圈、同行业的可比基准。"""
    return data.benchmark_snapshot(merchant_id)


@tool
def get_inventory_risk(merchant_id: str) -> dict:
    """查询库存天数和SKU毛利风险，用于判断折扣或清仓建议。"""
    return data.inventory_snapshot(merchant_id)


TOOL_REGISTRY = {
    item.name: item
    for item in [
        get_merchant_profile,
        get_metric_snapshot,
        get_review_topics,
        get_campaign_history,
        get_industry_benchmark,
        get_inventory_risk,
    ]
}

