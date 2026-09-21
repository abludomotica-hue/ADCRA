"""
Unit Tests for Context Engine, Memory Engine & Multi-Tenant Isolation
"""

import unittest
import tempfile
from pathlib import Path
from adcra.ai.context import get_context_engine
from adcra.ai.memory import MemoryEngine, MemoryWriteValidator
from adcra.ai.types import MemoryType, SourceEpistemology


class TestAIBrainContextAndMemory(unittest.TestCase):
    def setUp(self):
        self.context_engine = get_context_engine()

    def test_context_engine_assembly(self):
        pkt = self.context_engine.assemble_context(campaign_id="camp_locos_materos_2026")
        self.assertIn("brand", pkt)
        self.assertIn("audio", pkt)
        self.assertIn("epistemic_sources", pkt)
        self.assertEqual(pkt["brand"]["name"], "Locos Materos")

        prompt_str = self.context_engine.format_context_for_prompt(pkt)
        self.assertIn("Locos Materos", prompt_str)
        self.assertIn("107.7", prompt_str)

    def test_memory_engine_write_and_query(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        engine = MemoryEngine()
        engine._memory_store_file = Path(temp_path)
        engine._entries = []

        # 1. Guardar decisión
        entry = engine.write_entry(
            tenant_id="tenant_alpha",
            scope="campaign",
            memory_type=MemoryType.DECISION,
            source=SourceEpistemology.CONFIRMED_FACT,
            content={"hook_selected": "Ritual y Pertenencia"},
            confidence=0.99,
            confirmed_by_human=True
        )
        self.assertIsNotNone(entry["entry_id"])

        # 2. Consultar con el mismo tenant
        res_alpha = engine.query(tenant_id="tenant_alpha")
        self.assertEqual(len(res_alpha), 1)

        # 3. Multi-tenant isolation: tenant_beta NO debe ver las entradas de tenant_alpha
        res_beta = engine.query(tenant_id="tenant_beta")
        self.assertEqual(len(res_beta), 0, "Cross-tenant memory leakage detected!")

    def test_epistemic_write_validation_rejection(self):
        # Intentar guardar AI_INFERENCE como FACT sin confirmación humana debe lanzar excepción
        validator = MemoryWriteValidator()
        invalid_entry = {
            "tenant_id": "tenant_1",
            "scope": "client",
            "memory_type": MemoryType.FACT.value,
            "source": SourceEpistemology.AI_INFERENCE.value,
            "confidence": 0.65,
            "confirmed_by_human": False,
            "content": {"claim": "Unverified assertion"}
        }
        with self.assertRaises(ValueError) as cm:
            validator.validate_entry(invalid_entry)
        self.assertIn("Epistemic violation", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
