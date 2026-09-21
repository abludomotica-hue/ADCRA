"""
Unit and Integration Tests for Campaign Knowledge Graph & Epistemology
Validates schema compliance, epistemic node attributes, Brand DNA integrity,
and REST API endpoints.
"""

import unittest
import json
import os
import urllib.request
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


class TestCampaignKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        self.schema_path = WORKSPACE_ROOT / "config" / "campaign-knowledge-graph.schema.json"
        self.graph_path = WORKSPACE_ROOT / "campaign" / "campaign-knowledge-graph.json"

    def test_schema_file_exists_and_valid_json(self):
        self.assertTrue(self.schema_path.is_file(), "campaign-knowledge-graph.schema.json must exist")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertIn("properties", schema)
        self.assertIn("client", schema["properties"])
        self.assertIn("brand_dna", schema["definitions"])

    def test_campaign_graph_validates_against_schema(self):
        self.assertTrue(self.graph_path.is_file(), "campaign-knowledge-graph.json must exist")
        with open(self.schema_path, "r", encoding="utf-8") as sf:
            schema = json.load(sf)
        with open(self.graph_path, "r", encoding="utf-8") as gf:
            graph = json.load(gf)

        # Validate Draft-07 schema
        jsonschema.validate(instance=graph, schema=schema)

    def test_epistemic_node_structure(self):
        with open(self.graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)

        # Sample epistemic nodes from client, objective, audience, audio
        sample_nodes = [
            graph["client"]["brand_colors"],
            graph["client"]["typography"],
            graph["client"]["voice_tone"],
            graph["objective"]["primary_objective"],
            graph["audience"]["primary_audience"],
            graph["audio"]["tempo_bpm"]
        ]

        valid_sources = {"CLIENT_INPUT", "CONFIRMED_FACT", "AI_INFERENCE", "AI_RECOMMENDATION", "RESEARCH", "UNKNOWN"}
        for node in sample_nodes:
            self.assertIn("source", node)
            self.assertIn(node["source"], valid_sources)
            self.assertIn("confidence", node)
            self.assertIn("requires_confirmation", node)
            self.assertIn("status", node)
            self.assertIn("approved", node)

    def test_brand_dna_completeness(self):
        with open(self.graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)

        brand_dna = graph.get("client", {}).get("brand_dna", {})
        required_dimensions = [
            "who_we_are",
            "how_we_speak",
            "how_we_look",
            "how_we_move",
            "how_we_sell",
            "how_we_should_never_behave"
        ]
        for dim in required_dimensions:
            self.assertIn(dim, brand_dna, f"Brand DNA missing dimension {dim}")
            attr = brand_dna[dim]
            self.assertIn("value", attr)
            self.assertIn("source", attr)
            self.assertIn("confidence", attr)

    def test_api_knowledge_graph_endpoints(self):
        url_get = "http://127.0.0.1:8080/api/intake/knowledge-graph"
        try:
            with urllib.request.urlopen(url_get, timeout=3) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertIn("client", data)
                self.assertIn("brand_dna", data["client"])
        except urllib.error.URLError:
            self.skipTest("Dashboard server not running on localhost:8080")


if __name__ == "__main__":
    unittest.main()
