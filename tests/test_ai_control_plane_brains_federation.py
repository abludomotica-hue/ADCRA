"""
Unit and Integration Tests for ADCRA AI Intelligence Control Plane v2.0 - Brain Profiles & Federation
Verifies:
- 14 cognitive brain profiles loaded from config/ai-brains.json
- BrainProfile capability requirements generation
- BrainHandoff creation and validation
- BrainFederationEngine handoff lifecycle and history tracking
- Backward compatibility bridge with adcra.ai.profiles.ProfileManager
"""

import unittest
from adcra.ai.brains import (
    BrainProfile,
    BrainHandoff,
    BrainRegistry,
    BrainFederationEngine,
    get_brain_registry,
    get_federation_engine
)
from adcra.ai.profiles import ProfileManager
from adcra.ai.types import SourceEpistemology

class TestAiControlPlaneBrainsFederation(unittest.TestCase):

    def setUp(self):
        self.registry = BrainRegistry()
        self.federation = BrainFederationEngine(registry=self.registry)

    def test_canonical_brains_count(self):
        """Verify the 14 cognitive Brain Profiles are loaded from config/ai-brains.json."""
        brains = self.registry.list_brains()
        self.assertEqual(len(brains), 14)

        brain_ids = {b.id for b in brains}
        expected = [
            "creative_director", "brand_strategist", "copy_director",
            "storyboard_director", "visual_director", "audio_director",
            "production_director", "qc_director", "delivery_director",
            "market_researcher", "audience_analyst", "strategic_planner",
            "editorial_director", "post_mortem_analyst"
        ]
        for bid in expected:
            self.assertIn(bid, brain_ids)

    def test_brain_profile_capability_requirements(self):
        """Verify BrainProfile extracts typed CapabilityRequirements."""
        creative = self.registry.get_brain("creative_director")
        self.assertIsNotNone(creative)
        reqs = creative.get_capability_requirements()
        self.assertGreater(len(reqs), 0)

        # Ensure required capabilities are marked non-optional
        req_map = {r.capability: r for r in reqs}
        for cap in creative.required_capabilities:
            self.assertIn(cap, req_map)
            self.assertFalse(req_map[cap].optional)

    def test_brain_handoff_creation_and_history(self):
        """Verify BrainFederationEngine records structured handoffs between brains."""
        handoff = self.federation.create_handoff(
            source_brain="brand_strategist",
            target_brain="creative_director",
            campaign_id="camp_test_01",
            task_id="brand_essence_formulation",
            input_context={"brand_name": "Locos Materos", "audience": "Gen Z"},
            artifacts=[{"type": "brief", "uri": "artifact://brief.json"}],
            decisions=["Core theme: ritual, connection, everyday authenticity"],
            constraints=["Budget max $500", "Rec.709 color space"],
            confidence=0.96,
            epistemology=SourceEpistemology.AI_RECOMMENDATION
        )

        self.assertIsInstance(handoff, BrainHandoff)
        self.assertTrue(handoff.handoff_id.startswith("handoff_"))
        self.assertEqual(handoff.source_brain, "brand_strategist")
        self.assertEqual(handoff.target_brain, "creative_director")

        # Verify history filtering
        history = self.federation.list_handoffs(campaign_id="camp_test_01")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].handoff_id, handoff.handoff_id)

        # Empty result for unknown campaign
        self.assertEqual(len(self.federation.list_handoffs(campaign_id="non_existent")), 0)

    def test_backward_compatibility_profiles_bridge(self):
        """Verify adcra.ai.profiles exports BrainRegistry profiles seamlessly via ProfileManager."""
        legacy_manager = ProfileManager()
        profiles = legacy_manager.list_profiles()
        self.assertGreaterEqual(len(profiles), 14)
        cd = legacy_manager.get_profile("creative_director")
        self.assertIsNotNone(cd)
        self.assertEqual(cd.get("profile_id"), "creative_director")

if __name__ == "__main__":
    unittest.main()
