#!/usr/bin/env python3
"""
ADCRA — Test Suite de Validación de Arquitectura Base (Fase 1)
Valida la integridad de directorios, especificación JSON Schema Draft-07,
cargas útiles válidas e inválidas, consistencia del enrutador y documentación.
"""

import os
import json
import unittest
from pathlib import Path
import jsonschema

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

class TestPhase1Architecture(unittest.TestCase):

    def test_01_required_skill_directories_exist(self):
        """Verifica que todos los dominios de habilidades requeridos existan en .agents/skills/"""
        expected_domains = [
            "strategy",
            "creative",
            "analysis",
            "production",
            "tools",
            "post-production",
            "quality-control",
            "memory",
            "meta"
        ]
        skills_dir = WORKSPACE_ROOT / ".agents" / "skills"
        self.assertTrue(skills_dir.is_dir(), f"No existe el directorio {skills_dir}")
        for domain in expected_domains:
            domain_path = skills_dir / domain
            self.assertTrue(domain_path.is_dir(), f"Dominio de habilidad faltante: {domain}")

    def test_02_documentation_files_exist(self):
        """Verifica la existencia y contenido no vacío de la documentación base"""
        expected_docs = [
            "docs/ADCRA/ARCHITECTURE.md",
            "docs/ADCRA/IMPLEMENTATION_PLAN.md",
            "docs/ADCRA/DECISION_LOG.md",
            "docs/ADCRA/AUDIT_REPORT.md",
            "docs/ADCRA/PROJECT_STATE.md"
        ]
        for rel_path in expected_docs:
            doc_path = WORKSPACE_ROOT / rel_path
            self.assertTrue(doc_path.is_file(), f"Documento faltante: {rel_path}")
            self.assertGreater(doc_path.stat().st_size, 100, f"El documento {rel_path} está vacío o incompleto")

    def test_03_json_schemas_are_valid(self):
        """Verifica que todos los esquemas JSON en config/ sean esquemas válidos según Draft-07"""
        schema_files = [
            "config/campaign-schema.json",
            "config/storyboard-schema.json",
            "config/creative-copy-schema.json",
            "config/qc-schema.json"
        ]
        for rel_path in schema_files:
            file_path = WORKSPACE_ROOT / rel_path
            with open(file_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            # Verifica que sea un schema válido según el validador de jsonschema
            validator_cls = jsonschema.validators.validator_for(schema)
            validator_cls.check_schema(schema)

    def test_04_campaign_schema_validation(self):
        """Prueba payloads válidos e inválidos contra campaign-schema.json"""
        schema_path = WORKSPACE_ROOT / "config" / "campaign-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        valid_payload = {
            "campaign_id": "camp_ypf_infinito_2026",
            "campaign_name": "YPF Infinito — Energía que Une",
            "version": "1.0.0",
            "client": {
                "name": "YPF",
                "industry": "Energía y Combustibles",
                "brand_values": ["Nacional", "Calidad", "Cercanía", "Futuro"]
            },
            "strategic_brief": {
                "objective": "brand_repositioning",
                "target_audience": {
                    "demographic": "Conductores 25-50 años Argentina",
                    "psychographic": "Valoración del viaje, la familia y la confiabilidad",
                    "context": "Ruta y vida cotidiana"
                },
                "core_message": "Cada kilómetro que recorremos cuenta una historia compartida",
                "tone_of_voice": ["Cálido", "Inspirador", "Épico"],
                "requirements": [
                    {
                        "id": "req_01",
                        "type": "CLIENT_REQUIREMENT",
                        "description": "Presencia del isotipo YPF en el packshot final de 2 segundos",
                        "origin": "Manual de Marca YPF 2026",
                        "is_mandatory": True,
                        "validation_status": "verified"
                    },
                    {
                        "id": "req_02",
                        "type": "USER_REQUIREMENT",
                        "description": "Entregar versión vertical 9:16 para Reels y horizontal 16:9 para Broadcast",
                        "origin": "Prompt del usuario",
                        "is_mandatory": True,
                        "validation_status": "verified"
                    },
                    {
                        "id": "req_03",
                        "type": "TECHNICAL_REQUIREMENT",
                        "description": "El render debe exportarse a 30 FPS exactos y ProRes/H.264",
                        "origin": "Restricción de canal",
                        "is_mandatory": True,
                        "validation_status": "verified"
                    },
                    {
                        "id": "req_04",
                        "type": "CREATIVE_RECOMMENDATION",
                        "description": "Sincronizar el primer corte visual con la entrada de la batería",
                        "origin": "Propuesta del Director Creativo",
                        "is_mandatory": False,
                        "validation_status": "pending"
                    },
                    {
                        "id": "req_05",
                        "type": "AGENT_ASSUMPTION",
                        "description": "Se asume que la duración objetivo no debe superar los 35 segundos",
                        "origin": "Inferencia de formato comercial",
                        "is_mandatory": False,
                        "validation_status": "pending"
                    }
                ]
            },
            "deliverables": [
                {
                    "format_id": "reel_vertical",
                    "aspect_ratio": "9:16",
                    "resolution": {"width": 1080, "height": 1920},
                    "fps": 30.0,
                    "target_channels": ["Instagram", "TikTok"],
                    "duration_target_seconds": 30.0
                }
            ],
            "workflow_status": {
                "current_phase": "FASE 1",
                "iteration_count": 0,
                "max_iterations": 3,
                "is_approved": False
            }
        }

        # Valid payload must pass
        jsonschema.validate(instance=valid_payload, schema=schema)

        # Invalid payload: missing mandatory client requirement field
        invalid_payload = dict(valid_payload)
        del invalid_payload["client"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_payload, schema=schema)

        # Invalid payload: requirement type not in strict taxonomy
        invalid_taxonomy_payload = json.loads(json.dumps(valid_payload))
        invalid_taxonomy_payload["strategic_brief"]["requirements"][0]["type"] = "INVALID_TYPE_TAG"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_taxonomy_payload, schema=schema)

    def test_05_storyboard_schema_validation(self):
        """Prueba payloads válidos e inválidos contra storyboard-schema.json"""
        schema_path = WORKSPACE_ROOT / "config" / "storyboard-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        valid_storyboard = {
            "storyboard_id": "sb_ypf_001",
            "campaign_id": "camp_ypf_infinito_2026",
            "narrative_arc": "Amanecer solitario -> Encuentro en ruta -> Celebración colectiva",
            "total_duration_seconds": 30.0,
            "target_fps": 30.0,
            "scenes": [
                {
                    "scene_id": "scene_01",
                    "start": 0.0,
                    "end": 4.5,
                    "duration": 4.5,
                    "audio_segment": {
                        "beat_start": 0.0,
                        "beat_end": 4.5,
                        "energy_level": "low",
                        "musical_cue": "Intro suave de guitarra acústica"
                    },
                    "lyric_reference": "instrumental",
                    "visual": "Plano general amanecer en la meseta patagónica",
                    "camera": "Plano general estático con suave paneo a la derecha",
                    "lighting": "Luz dorada de primera hora, contrastes suaves",
                    "emotion": "Serenidad y expectativa",
                    "copy": "Donde el camino empieza.",
                    "typography": {
                        "font_family": "Montserrat Bold",
                        "size": "48px",
                        "color": "#FFFFFF",
                        "alignment": "center"
                    },
                    "animation": "fade_up_smooth",
                    "transition": {
                        "type": "cross_dissolve",
                        "duration_seconds": 0.5
                    },
                    "brand_visibility": "subtle",
                    "asset_ids": ["clip_001_patagonia.mp4"],
                    "tool": "DaVinci Resolve",
                    "rationale": "Establece el tono emocional y la inmensidad del territorio argentino"
                }
            ]
        }

        # Valid storyboard passes
        jsonschema.validate(instance=valid_storyboard, schema=schema)

        # Invalid storyboard: missing required rationale
        invalid_storyboard = json.loads(json.dumps(valid_storyboard))
        del invalid_storyboard["scenes"][0]["rationale"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_storyboard, schema=schema)

        # Invalid tool choice
        invalid_tool_storyboard = json.loads(json.dumps(valid_storyboard))
        invalid_tool_storyboard["scenes"][0]["tool"] = "NonExistentVideoEditor"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_tool_storyboard, schema=schema)

    def test_06_creative_copy_schema_validation(self):
        """Prueba payloads válidos e inválidos contra creative-copy-schema.json (5 variantes obligatorias)"""
        schema_path = WORKSPACE_ROOT / "config" / "creative-copy-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        valid_copy_payload = {
            "campaign_id": "camp_ypf_infinito_2026",
            "overall_narrative_thread": "La energía que impulsa las conexiones humanas",
            "scene_copies": [
                {
                    "scene_id": "scene_01",
                    "context_inputs": {
                        "visual_description": "Ruta desierta al amanecer con auto encendiendo luces",
                        "music_cue": "Acorde sostenido de guitarra",
                        "lyric_reference": "instrumental",
                        "emotion_target": "Nostalgia y determinación",
                        "objective": "Captar atención en los primeros 3 segundos",
                        "audience_target": "Conductores frecuentes de ruta",
                        "brand_tone": "Cálido e inspirador",
                        "previous_scene_copy": "none",
                        "next_scene_copy": "El viaje que nos une"
                    },
                    "alternatives": {
                        "emocional": {
                            "text": "Cada viaje guarda una promesa.",
                            "emotional_impact_score": 8.5
                        },
                        "publicitaria": {
                            "text": "Llegá más lejos con Infinia.",
                            "call_to_action_score": 7.0
                        },
                        "conversacional": {
                            "text": "Arrancar temprano tiene su magia.",
                            "naturalness_score": 9.0
                        },
                        "minimalista": {
                            "text": "Comenzar.",
                            "word_count": 1
                        },
                        "identidad_de_marca": {
                            "text": "YPF. Energía que une.",
                            "brand_alignment_score": 9.5
                        }
                    },
                    "selected_variant": "emocional",
                    "selected_text": "Cada viaje guarda una promesa.",
                    "selection_rationale": "El inicio requiere construir conexión empática antes de introducir el llamado comercial de marca"
                }
            ]
        }

        # Valid copy payload passes
        jsonschema.validate(instance=valid_copy_payload, schema=schema)

        # Invalid copy payload: missing one of the 5 required variants (e.g. minimalista)
        invalid_copy_payload = json.loads(json.dumps(valid_copy_payload))
        del invalid_copy_payload["scene_copies"][0]["alternatives"]["minimalista"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_copy_payload, schema=schema)

    def test_07_qc_schema_validation(self):
        """Prueba payloads válidos e inválidos contra qc-schema.json (3 niveles de QC)"""
        schema_path = WORKSPACE_ROOT / "config" / "qc-schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        valid_qc_payload = {
            "qc_id": "qc_report_001",
            "campaign_id": "camp_ypf_infinito_2026",
            "render_target": {
                "file_path": "/data/usuario/Documentos/davinci resolve/assets/export/reel_vertical_v1.mp4",
                "format_aspect_ratio": "9:16",
                "file_hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            },
            "iteration_number": 1,
            "technical_qc": {
                "measured_duration_seconds": 30.02,
                "expected_duration_seconds": 30.00,
                "duration_delta_seconds": 0.02,
                "resolution_actual": {"width": 1080, "height": 1920},
                "fps_actual": 30.0,
                "video_codec": "h264",
                "audio_codec": "aac",
                "audio_clipping_detected": False,
                "accidental_silence_detected": False,
                "black_frames_count": 0,
                "frozen_frames_count": 0,
                "encoding_errors_detected": False,
                "status": "PASS",
                "notes": "Parámetros técnicos conformes a especificación broadcast"
            },
            "creative_qc": {
                "rhythm_sync_score": 9.2,
                "narrative_flow_score": 8.8,
                "emotional_continuity_score": 9.0,
                "copy_legibility_score": 9.5,
                "composition_balance_score": 8.7,
                "status": "PASS",
                "observations": ["Cortes perfectamente alineados con los transientes de percusión"]
            },
            "brand_qc": {
                "logo_presence_verified": True,
                "brand_color_palette_verified": True,
                "typography_guidelines_verified": True,
                "tone_consistency_verified": True,
                "unauthorized_claims_detected": False,
                "product_prominence_verified": True,
                "status": "PASS",
                "brand_compliance_notes": "Logotipo final visible durante 2.5s con safe area de 10%"
            },
            "overall_status": "APPROVED",
            "action_required": "PROCEED_TO_DELIVERY"
        }

        # Valid QC payload passes
        jsonschema.validate(instance=valid_qc_payload, schema=schema)

        # Invalid QC: iteration number exceeding max 3
        invalid_qc_payload = json.loads(json.dumps(valid_qc_payload))
        invalid_qc_payload["iteration_number"] = 4
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_qc_payload, schema=schema)

        # Invalid QC: missing brand_qc
        invalid_qc_missing_brand = json.loads(json.dumps(valid_qc_payload))
        del invalid_qc_missing_brand["brand_qc"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_qc_missing_brand, schema=schema)

    def test_08_tool_router_integrity(self):
        """Verifica la consistencia estructural y lógica de config/tool-router.json"""
        router_path = WORKSPACE_ROOT / "config" / "tool-router.json"
        with open(router_path, "r", encoding="utf-8") as f:
            router = json.load(f)

        self.assertIn("routing_policy", router)
        self.assertIn("routes", router)
        self.assertGreater(len(router["routes"]), 5)

        known_tools = {"DaVinci Resolve", "Remotion", "HyperFrames", "FFmpeg", "FFprobe", "FFprobe/FFmpeg", None}
        for route in router["routes"]:
            self.assertIn("necesidad", route)
            self.assertIn("herramienta_primaria", route)
            self.assertIn("criterio_decision", route)
            self.assertIn("requiere_gpu", route)
            self.assertIn(route["herramienta_primaria"], known_tools, f"Herramienta primaria desconocida: {route['herramienta_primaria']}")
            if route.get("alternativa") is not None:
                self.assertIn(route["alternativa"], known_tools, f"Herramienta alternativa desconocida: {route['alternativa']}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
