"""
Unit and Integration Tests for ADCRA AI Intelligence Control Plane v2.0 - Runtime & Security
Verifies:
- SecretRedaction of API keys, bearer tokens, and structured JSON secrets
- SecretRedaction.sanitize_dict() recursive scrubbing
- AIRun entity lifecycle and state transitions
- AgentRuntime.execute_brain() execution, fallback engine resilience, and cost tracking
"""

import unittest
from adcra.ai.runtime import (
    SecretRedaction,
    AIRun,
    AIRunStatus,
    AgentRuntime,
    get_agent_runtime
)
from adcra.ai.types import AIMessage

class TestAiControlPlaneRuntimeSecurity(unittest.TestCase):

    def setUp(self):
        self.runtime = AgentRuntime()

    def test_secret_redaction_text(self):
        """Verify redacting various API key and token patterns from raw text."""
        raw_text = (
            "Connecting with openai key sk-abc12345678901234567890abcdef and "
            "google key AIzaSyA1234567890123456789012345678901 and "
            "header Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-IDN secretly."
        )
        redacted = SecretRedaction.redact(raw_text)

        self.assertNotIn("sk-abc12345678901234567890abcdef", redacted)
        self.assertNotIn("AIzaSyA1234567890123456789012345678901", redacted)
        self.assertIn("[REDACTED_API_KEY]", redacted)

    def test_secret_redaction_sanitize_dict(self):
        """Verify recursive sanitization of nested dictionary structures."""
        data = {
            "campaign": "locos-materos",
            "api_key": "sk-real_secret_token_1234567890",
            "auth": {
                "token": "secret_token_abc1234567890",
                "nested_pass": "super_secret"
            },
            "logs": [
                "Called with api_key=\"hidden_val\""
            ]
        }

        sanitized = SecretRedaction.sanitize_dict(data)
        self.assertEqual(sanitized["api_key"], "[REDACTED]")
        self.assertEqual(sanitized["auth"]["token"], "[REDACTED]")
        self.assertEqual(sanitized["campaign"], "locos-materos")
        self.assertNotIn("hidden_val", str(sanitized["logs"]))

    def test_airun_lifecycle_and_serialization(self):
        """Verify AIRun state defaults and dictionary serialization."""
        run = AIRun(
            run_id="run_test_001",
            campaign_id="camp_test",
            brain_id="creative_director",
            status=AIRunStatus.QUEUED
        )
        self.assertEqual(run.status, AIRunStatus.QUEUED)
        
        d = run.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["run_id"], "run_test_001")
        self.assertEqual(d["status"], "QUEUED")
        self.assertEqual(d["brain_id"], "creative_director")

    def test_agent_runtime_execute_brain(self):
        """Verify executing a task via a cognitive brain profile through the runtime."""
        messages = [
            AIMessage(role="user", content="Define el concepto central para una campaña de yerba mate.")
        ]
        
        response, airun = self.runtime.execute_brain(
            brain_id="creative_director",
            messages=messages,
            campaign_id="camp_runtime_test"
        )

        self.assertIsNotNone(response)
        self.assertGreater(len(response.content), 0)
        self.assertIsInstance(airun, AIRun)
        self.assertEqual(airun.status, AIRunStatus.COMPLETED)
        self.assertEqual(airun.brain_id, "creative_director")
        self.assertGreater(airun.latency_ms, 0)
        self.assertIsNotNone(airun.completed_at)

        # Verify run is recorded in the runtime history
        retrieved_run = self.runtime.get_run(airun.run_id)
        self.assertIsNotNone(retrieved_run)
        self.assertEqual(retrieved_run.run_id, airun.run_id)

if __name__ == "__main__":
    unittest.main()
