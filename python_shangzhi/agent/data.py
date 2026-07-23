"""可替换的数据访问层。

作品集默认使用一组可审计的模拟经营数据。真实落地时只需把这些函数替换为
数仓、商家中心或指标平台查询，不需要改 Agent 编排。
"""

from __future__ import annotations

from copy import deepcopy


MERCHANTS = {
    "merchant_demo": {
        "merchant_id": "merchant_demo",
        "name": "李记小馆",
        "industry": "餐饮",
        "city": "杭州",
        "store": "湖滨店",
        "constraints": {
            "minimum_margin_rate": 0.12,
            "max_daily_ad_budget": 800,
            "auto_execute_allowed": False,
        },
        "metrics": {
            "today_revenue": 12680,
            "today_paid_orders": 186,
            "store_rating": 4.63,
            "package_impressions_7d": 18420,
            "package_impressions_change": 0.12,
            "package_conversion_7d": 0.078,
            "package_conversion_change": -0.18,
            "estimated_lost_orders_daily": 8,
            "repeat_purchase_rate_30d": 0.214,
            "evening_utilization": 0.51,
            "benchmark_evening_utilization": 0.72,
        },
        "reviews": {
            "total_30d": 286,
            "negative_30d": 31,
            "negative_rate": 0.108,
            "topics": [
                {"topic": "分量不足", "count": 13, "change": 0.44},
                {"topic": "上菜慢", "count": 9, "change": 0.18},
                {"topic": "套餐说明不清", "count": 6, "change": 0.50},
            ],
        },
        "campaigns": [
            {
                "name": "工作日晚市券",
                "period": "最近 14 天",
                "exposure": 6300,
                "claim_rate": 0.092,
                "redeem_rate": 0.281,
                "incremental_orders": 37,
            },
            {
                "name": "老客召回",
                "period": "上月",
                "target_users": 1200,
                "open_rate": 0.36,
                "redeem_rate": 0.118,
                "incremental_orders": 82,
            },
        ],
        "benchmarks": {
            "industry": "杭州同商圈中式正餐",
            "package_conversion_median": 0.091,
            "negative_review_rate_median": 0.074,
            "repeat_purchase_rate_median": 0.238,
        },
        "inventory": {
            "high_risk_skus": [
                {"name": "招牌双人餐", "stock_days": 5, "gross_margin_rate": 0.31},
                {"name": "夏日酸梅汤", "stock_days": 18, "gross_margin_rate": 0.54},
            ]
        },
    }
}


def merchant_profile(merchant_id: str) -> dict:
    merchant = MERCHANTS.get(merchant_id) or MERCHANTS["merchant_demo"]
    return {
        "merchant_id": merchant["merchant_id"],
        "name": merchant["name"],
        "industry": merchant["industry"],
        "city": merchant["city"],
        "store": merchant["store"],
        "constraints": deepcopy(merchant["constraints"]),
    }


def metric_snapshot(merchant_id: str) -> dict:
    merchant = MERCHANTS.get(merchant_id) or MERCHANTS["merchant_demo"]
    return deepcopy(merchant["metrics"])


def review_snapshot(merchant_id: str) -> dict:
    merchant = MERCHANTS.get(merchant_id) or MERCHANTS["merchant_demo"]
    return deepcopy(merchant["reviews"])


def campaign_snapshot(merchant_id: str) -> list[dict]:
    merchant = MERCHANTS.get(merchant_id) or MERCHANTS["merchant_demo"]
    return deepcopy(merchant["campaigns"])


def benchmark_snapshot(merchant_id: str) -> dict:
    merchant = MERCHANTS.get(merchant_id) or MERCHANTS["merchant_demo"]
    return deepcopy(merchant["benchmarks"])


def inventory_snapshot(merchant_id: str) -> dict:
    merchant = MERCHANTS.get(merchant_id) or MERCHANTS["merchant_demo"]
    return deepcopy(merchant["inventory"])

