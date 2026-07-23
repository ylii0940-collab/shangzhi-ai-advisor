from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent.service import AgentService
from agent.settings import Settings


class AgentServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = str(Path(self.temp_dir.name) / "test.db")
        self.service = AgentService(
            Settings(
                openai_api_key="",
                openai_model="gpt-5.6-luna",
                agent_mode="demo",
                db_path=db_path,
            )
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_graph_returns_evidence_and_trace(self) -> None:
        events = list(
            self.service.stream(
                "为什么最近套餐转化下降？",
                "thread_test",
                "merchant_demo",
            )
        )
        final = [event for event in events if event["type"] == "final"][0]["data"]
        self.assertEqual(final["mode"], "demo")
        self.assertGreaterEqual(len(final["evidence"]), 2)
        self.assertEqual(
            [item["node"] for item in final["trace"]],
            ["retrieve", "diagnose", "guardrail", "persist"],
        )

    def test_high_risk_action_waits_for_human(self) -> None:
        result = self.service.run(
            "把推广预算直接提高一倍",
            "thread_budget",
            "merchant_demo",
        )
        self.assertTrue(result.safety.requires_confirmation)
        self.assertEqual(result.actions[0].status, "pending")
        action = self.service.confirm_action(result.actions[0].action_id, True)
        self.assertEqual(action["status"], "executed")

    def test_builtin_evals(self) -> None:
        result = self.service.run_evals()
        self.assertEqual(result["passed"], result["total"])


if __name__ == "__main__":
    unittest.main()
