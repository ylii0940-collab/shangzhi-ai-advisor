from __future__ import annotations

import unittest

from agent.guardrails import review_diagnosis
from agent.schemas import DiagnosisOutput, Evidence, Recommendation


class GuardrailTests(unittest.TestCase):
    def test_budget_action_requires_confirmation(self) -> None:
        diagnosis = DiagnosisOutput(
            intent="预算调整",
            conclusion="建议先验证",
            evidence=[
                Evidence(
                    evidence_id="E1",
                    metric="核销率",
                    observed="11.8%",
                    comparison="高于历史活动",
                    source="get_campaign_history",
                )
            ],
            recommendations=[
                Recommendation(
                    title="提高预算",
                    rationale="历史活动有增量信号",
                    steps=["将预算提高 10%"],
                    expected_signal="观察增量订单",
                    action_type="budget",
                    risk_level="low",
                )
            ],
            confidence=0.8,
        )
        reviewed, safety = review_diagnosis(diagnosis)
        self.assertTrue(safety.requires_confirmation)
        self.assertTrue(reviewed.recommendations[0].requires_confirmation)
        self.assertEqual(reviewed.recommendations[0].risk_level, "medium")

    def test_promise_is_upgraded_to_high_risk(self) -> None:
        diagnosis = DiagnosisOutput(
            intent="库存",
            conclusion="需要清理库存",
            evidence=[
                Evidence(
                    evidence_id="E1",
                    metric="库存周转",
                    observed="46天",
                    comparison="上期21天",
                    source="get_inventory_risk",
                )
            ],
            recommendations=[
                Recommendation(
                    title="清仓",
                    rationale="库存上升",
                    steps=["统一降价"],
                    expected_signal="保证7天内清理80%库存",
                    action_type="inventory",
                    risk_level="medium",
                )
            ],
            confidence=0.9,
        )
        reviewed, safety = review_diagnosis(diagnosis)
        self.assertEqual(reviewed.recommendations[0].risk_level, "high")
        self.assertTrue(safety.warnings)


if __name__ == "__main__":
    unittest.main()

