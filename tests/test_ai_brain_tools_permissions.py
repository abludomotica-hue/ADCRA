"""
Unit Tests for Tool Registry, Tool Permissions, and Human Approval Engine
"""

import unittest
from adcra.ai.tools import get_tool_registry
from adcra.ai.permissions import get_permission_engine
from adcra.ai.approval import ApprovalEngine
from adcra.ai.types import (
    PermissionLevel, RiskLevel, AutonomyLevel, ToolExecutionStatus
)


class TestAIBrainToolsAndPermissions(unittest.TestCase):
    def setUp(self):
        self.registry = get_tool_registry()
        self.perm_engine = get_permission_engine()

    def test_default_tools_registration(self):
        tools = self.registry.list_tools()
        self.assertGreaterEqual(len(tools), 8)
        tool_ids = [t["tool_id"] for t in tools]
        self.assertIn("audio_analysis", tool_ids)
        self.assertIn("ffprobe_metadata", tool_ids)
        self.assertIn("qc_evaluator", tool_ids)
        self.assertIn("hyperframes_render", tool_ids)
        self.assertIn("remotion_render", tool_ids)

    def test_tool_execution_allowed_role(self):
        res = self.registry.execute_tool(
            tool_id="audio_analysis",
            arguments={"audio_path": "campaign/audio/locos_materos_master_mix.wav"},
            context={"agent_role": "Audio Analyst"}
        )
        self.assertTrue(res["success"])
        self.assertIn("bpm", res["data"])
        self.assertEqual(res["data"]["bpm"], 107.7)

    def test_tool_permission_denial(self):
        # Role 'Research Analyst' only has READ & EXTERNAL, lacks WRITE & EXECUTE
        res = self.registry.execute_tool(
            tool_id="hyperframes_render",
            arguments={"template": "scene_01.html"},
            context={"agent_role": "Research Analyst"}
        )
        self.assertFalse(res["success"])
        self.assertEqual(res["error"]["code"], ToolExecutionStatus.PERMISSION_DENIED.value)

    def test_approval_engine_gating_critical_action(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        approval_engine = ApprovalEngine(approvals_file=temp_path)

        # 1. Critical publish action must require approval
        needs_appr = approval_engine.requires_approval(
            action="publish_campaign",
            risk_level=RiskLevel.HIGH,
            autonomy_level=AutonomyLevel.AUTONOMOUS
        )
        self.assertTrue(needs_appr)

        # 2. Create approval request
        appr_req = approval_engine.create_approval_request(
            run_id="test_run_123",
            action="publish_campaign",
            why="Releasing finalized spot to Meta & TikTok",
            impact="Public ad spend and live release",
            cost_usd=10.0,
            risk_level=RiskLevel.HIGH,
            campaign_id="camp_locos_materos_2026"
        )
        self.assertEqual(appr_req["status"], "PENDING")
        self.assertEqual(len(approval_engine.get_pending()), 1)

        # 3. Decide approval
        decided = approval_engine.decide(appr_req["approval_id"], approved=True, user="creative_director_user")
        self.assertEqual(decided["status"], "APPROVED")
        self.assertEqual(len(approval_engine.get_pending()), 0)


if __name__ == "__main__":
    unittest.main()
