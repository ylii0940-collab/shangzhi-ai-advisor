from __future__ import annotations

import unittest

from agent.analytics import (
    CAPABILITY_REPORT,
    COMPETITOR_REPORT,
    OBSERVABILITY_REPORT,
    list_badcases,
    run_badcase_regression,
)


class AgentProductAnalyticsTests(unittest.TestCase):
    def test_capability_report_covers_core_agent_dimensions(self) -> None:
        dimensions = {item["name"] for item in CAPABILITY_REPORT["dimensions"]}
        self.assertEqual(dimensions, {"规划能力", "工具调用", "记忆能力", "对话体验"})
        self.assertGreaterEqual(CAPABILITY_REPORT["total_cases"], 100)

    def test_badcase_regression_has_traceable_suite(self) -> None:
        severe = list_badcases("open")
        self.assertTrue(any(item["severity"] == "S1" for item in severe))
        result = run_badcase_regression("BC-0241")
        self.assertEqual(result["passed"], result["total"])
        self.assertTrue(result["suite"])

    def test_version_benchmark_and_observability_have_product_metrics(self) -> None:
        self.assertEqual(len(COMPETITOR_REPORT["agents"]), 3)
        self.assertEqual(
            {item["name"] for item in COMPETITOR_REPORT["agents"]},
            {"商智 v2.5", "商智 v2.4", "无工具基线"},
        )
        self.assertGreater(OBSERVABILITY_REPORT["calls"], 0)
        self.assertEqual(OBSERVABILITY_REPORT["confirmation_coverage"], 1.0)


if __name__ == "__main__":
    unittest.main()
