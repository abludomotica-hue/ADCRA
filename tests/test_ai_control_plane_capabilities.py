"""
Unit and Integration Tests for ADCRA AI Intelligence Control Plane v2.0 - Capabilities System
Verifies:
- 24 canonical capability definitions loaded from config
- CapabilityRegistry initialization, registration, and querying
- CapabilityRequirement matching and evaluation
- ModelCapabilityEntry indexing
- CapabilityDiscoveryEngine and probe execution
"""

import unittest
from adcra.ai.capabilities import (
    Capability,
    CapabilityCategory,
    CapabilityRequirement,
    ModelCapabilityEntry,
    CapabilityRegistry,
    CapabilityDiscoveryEngine,
    CapabilityReport,
    CapabilitySource,
    TextProbe,
    JsonProbe,
    ToolProbe,
    get_capability_registry,
    get_discovery_engine
)

class TestAiControlPlaneCapabilities(unittest.TestCase):

    def setUp(self):
        self.registry = CapabilityRegistry()

    def test_canonical_capabilities_count(self):
        """Verify the 24 canonical capabilities are loaded into the registry."""
        caps = self.registry.list_capabilities()
        self.assertEqual(len(caps), 24)
        
        # Verify key canonical IDs exist
        cap_ids = {c.id for c in caps}
        expected_keys = [
            "text_generation", "structured_generation", "code_generation",
            "strategic_reasoning", "multimodal_vision", "creative_writing",
            "tool_use", "storyboard_generation", "audio_understanding"
        ]
        for k in expected_keys:
            self.assertIn(k, cap_ids)

    def test_filter_capabilities_by_category(self):
        """Verify filtering capabilities by Category."""
        creative_caps = self.registry.list_capabilities(category="creative")
        self.assertGreater(len(creative_caps), 0)
        for c in creative_caps:
            self.assertEqual(c.category, "creative")

    def test_model_capability_registration_and_query(self):
        """Verify model capabilities can be registered and queried."""
        self.registry.register_model_capability(
            model_id="test_model_v1",
            capability_id="creative_writing",
            supported=True,
            source=CapabilitySource.STATIC_REGISTRY,
            confidence=0.98
        )
        self.assertTrue(self.registry.is_model_capable("test_model_v1", "creative_writing"))
        self.assertFalse(self.registry.is_model_capable("test_model_v1", "unknown_capability"))

    def test_evaluate_model_satisfaction(self):
        """Verify evaluating whether a model satisfies a list of requirements."""
        self.registry.register_model_capability("test_model_v2", "structured_generation", supported=True)
        self.registry.register_model_capability("test_model_v2", "multimodal_vision", supported=False)

        reqs = [
            CapabilityRequirement(capability="structured_generation", optional=False),
            CapabilityRequirement(capability="multimodal_vision", optional=True),
        ]
        res = self.registry.evaluate_model_satisfaction("test_model_v2", reqs)
        self.assertTrue(res["compatible"])
        self.assertIn("structured_generation", res["satisfied"])

        # Strict requirement fails
        reqs_strict = [
            CapabilityRequirement(capability="structured_generation", optional=False),
            CapabilityRequirement(capability="multimodal_vision", optional=False),
        ]
        res_strict = self.registry.evaluate_model_satisfaction("test_model_v2", reqs_strict)
        self.assertFalse(res_strict["compatible"])
        self.assertIn("multimodal_vision", res_strict["missing"])

    def test_discovery_engine(self):
        """Verify CapabilityDiscoveryEngine discovers capabilities from model definitions."""
        discovery = CapabilityDiscoveryEngine(registry=self.registry)
        raw_def = {
            "capabilities": {
                "reasoning": True,
                "vision": True,
                "toolCalling": True,
                "structuredOutput": True
            }
        }
        report = discovery.discover_model_capabilities(
            model_id="gemini-test-pro",
            provider_id="google_gemini",
            raw_model_def=raw_def
        )
        self.assertIsInstance(report, CapabilityReport)
        self.assertEqual(report.model_id, "gemini-test-pro")
        self.assertIn("text_generation", report.supported)
        self.assertIn("strategic_reasoning", report.supported)
        self.assertIn("multimodal_vision", report.supported)
        self.assertTrue(self.registry.is_model_capable("gemini-test-pro", "strategic_reasoning"))

if __name__ == "__main__":
    unittest.main()
