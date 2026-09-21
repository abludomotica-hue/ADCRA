#!/usr/bin/env python3
"""
Pruebas Unitarias Automatizadas — FASE UI-08: Audio Intake + Visualization
Campaign Intake Studio (ADCRA)

Verifica:
1. Componentes visuales y estilos en web/intake.css (audio-dropzone, audio-hud-grid,
   audio-hud-card, waveform-controls, audio-player-btn, section-markers-track, lyrics-guard-card).
2. Lógica del Audio Intake Studio en web/intake.js (renderStep08_Audio, bindStep08_Events,
   analyzeAudioFile, waveform player, marcadores EDL y blindaje de letra).
3. Endpoint de análisis espectral y musical POST /api/intake/analyze-audio (detección de BPM 107.7,
   tonalidad Am, compás 4/4, intervalos de corte y 5 secciones de montaje).
4. Persistencia integral del perfil musical y letra en /api/intake/draft.
5. Reglas de diagnóstico pre-flight (bloqueante crítico) para Paso 08 en evaluateAllStepStatuses.
"""

import os
import sys
import json
import socket
import threading
import urllib.request
import urllib.error
import unittest

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, WORKSPACE_ROOT)

import dashboard_server

def get_free_port():
    """Encuentra un puerto TCP libre efímero para pruebas."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


class TestPhaseUI08AudioIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_port = get_free_port()
        cls.server_address = ('127.0.0.1', cls.test_port)
        cls.httpd = dashboard_server.ThreadedHTTPServer(cls.server_address, dashboard_server.DashboardRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.test_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.server_thread.join(timeout=2.0)

    def test_01_audio_css_classes(self):
        """01. Valida estilos de Audio & Musical HUD en intake.css."""
        css_path = os.path.join(WORKSPACE_ROOT, "web", "intake.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        required = [
            ".audio-dropzone",
            ".audio-hud-grid",
            ".audio-hud-card",
            ".audio-hud-val",
            ".audio-hud-lbl",
            ".waveform-controls",
            ".audio-player-btn",
            ".section-markers-track",
            ".section-marker-pill",
            ".lyrics-guard-card"
        ]
        for c in required:
            self.assertIn(c, css, f"Falta {c} en web/intake.css")

    def test_02_audio_js_logic(self):
        """02. Valida métodos del Audio Intake Studio en intake.js."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        expected = [
            "renderStep08_Audio()",
            "bindStep08_Events()",
            "analyzeAudioFile(",
            "audioDropzone",
            "audioFileInput",
            "btnPlayAudio",
            "btnReanalyzeAudio",
            "inpAudioLyrics",
            "/api/intake/analyze-audio"
        ]
        for item in expected:
            self.assertIn(item, js, f"Falta '{item}' en web/intake.js")

    def test_03_api_analyze_audio_endpoint(self):
        """03. Valida análisis musical vía POST /api/intake/analyze-audio."""
        url = f"{self.base_url}/api/intake/analyze-audio"

        payload = {"filename": "locos_materos_track.mp3"}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res.get("status"), "SUCCESS")
            audio = res.get("audio", {})
            self.assertEqual(audio.get("bpm"), 107.7)
            self.assertEqual(audio.get("time_signature"), "4/4")
            self.assertIn("Am", audio.get("musical_key", ""))
            self.assertEqual(audio.get("cut_interval_seconds"), 2.22)
            self.assertEqual(len(audio.get("sections", [])), 5)

        # Error cuando falta filename
        empty_req = urllib.request.Request(url, data=json.dumps({}).encode("utf-8"), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(empty_req) as resp:
                self.fail("Debió retornar HTTP 400")
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 400)

    def test_04_audio_data_persistence(self):
        """04. Valida persistencia y round-trip de audio en /api/intake/draft."""
        payload = {
            "clientMode": "EXISTING_CLIENT",
            "activeStep": 8,
            "draft": {
                "client": {"brand_name": "Locos Materos"},
                "audio": {
                    "filename": "locos_materos_master_cut.wav",
                    "bpm": 107.7,
                    "time_signature": "4/4",
                    "musical_key": "Am (La menor)",
                    "energy_vibe": "ALTA / ENÉRGICA",
                    "cut_interval_seconds": 2.22,
                    "duration_seconds": 30.0,
                    "lyrics": "El ritual matero que nos une cada tarde de invierno...",
                    "sections": [
                        {"name": "Hook / Intro", "start_s": 0.0, "end_s": 3.0, "vibe": "Apertura"},
                        {"name": "Climax", "start_s": 20.0, "end_s": 26.0, "vibe": "Packshot"}
                    ]
                }
            },
            "updated_at": "2026-09-20T13:45:00Z"
        }

        # Guardar POST
        url = f"{self.base_url}/api/intake/draft"
        post_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=post_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)

        # Leer GET
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))

        data = res.get("draft", {}).get("draft", {})
        audio = data.get("audio", {})

        self.assertEqual(audio.get("filename"), "locos_materos_master_cut.wav")
        self.assertEqual(audio.get("bpm"), 107.7)
        self.assertEqual(audio.get("musical_key"), "Am (La menor)")
        self.assertIn("ritual matero", audio.get("lyrics", ""))

    def test_05_diagnostic_evaluation_step08(self):
        """05. Valida reglas diagnósticas críticas de Paso 08 en evaluateAllStepStatuses."""
        js_path = os.path.join(WORKSPACE_ROOT, "web", "intake.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("this.draft.audio.filename", js)
        self.assertIn("this.updateStepStatus(8, 'COMPLETE')", js)
        self.assertIn("this.updateStepStatus(8, 'MISSING')", js)


if __name__ == "__main__":
    unittest.main()
