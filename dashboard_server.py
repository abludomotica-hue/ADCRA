#!/usr/bin/env python3
"""
ADCRA Mission Control — Servidor HTTP y API REST
Proporciona streaming de video con soporte de byte-ranges (HTTP 206 Partial Content),
servicios REST para estado, entregables, telemetría y catálogo de habilidades,
y sirve los archivos estáticos de la interfaz web en web/.
"""

import os
import sys
import json
import glob
import mimetypes
import argparse
import subprocess
import time
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

# Ubicar raíz del workspace dinámicamente
cur = os.path.abspath(os.path.dirname(__file__))
while cur and cur != os.path.dirname(cur):
    if os.path.exists(os.path.join(cur, "config")) and os.path.exists(os.path.join(cur, "campaign")):
        WORKSPACE_ROOT = cur
        break
    cur = os.path.dirname(cur)
else:
    WORKSPACE_ROOT = os.path.abspath(os.path.dirname(__file__))

WEB_DIR = os.path.join(WORKSPACE_ROOT, "web")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP multi-hilo para streaming concurrente de video y llamadas API."""
    daemon_threads = True

class DashboardRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Silenciar logs verbosos en consola a menos que sea un error."""
        if args and str(args[1]) in ["404", "500"]:
            super().log_message(format, *args)

    def send_json(self, data, status=200):
        """Envía respuesta JSON con encabezados CORS."""
        content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        """Manejo de pre-flight CORS."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")
        self.end_headers()

    def do_POST(self):
        """Manejo de acciones POST (ej. ejecutar benchmark en vivo)."""
        parsed = urlparse(self.path)
        if parsed.path == "/api/intake/draft":
            self.handle_api_intake_draft_post()
            return
        elif parsed.path == "/api/run-benchmark":
            try:
                bench_script = os.path.join(WORKSPACE_ROOT, ".agents/skills/tools/benchmarking-engine/scripts/run_benchmarks.py")
                res = subprocess.run(
                    [sys.executable, bench_script, "--iterations", "5"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=20
                )
                report_path = os.path.join(WORKSPACE_ROOT, "campaign/reports/benchmarking-report.json")
                if os.path.exists(report_path):
                    with open(report_path, "r", encoding="utf-8") as f:
                        report_data = json.load(f)
                    self.send_json({"status": "SUCCESS", "report": report_data})
                else:
                    self.send_json({"status": "ERROR", "message": "Reporte no generado"}, 500)
            except Exception as e:
                self.send_json({"status": "ERROR", "message": str(e)}, 500)
            return

        self.send_error(404, "Endpoint no encontrado")


    def do_HEAD(self):
        """Manejo de peticiones HEAD para verificar tamaño y headers sin cuerpo."""
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ["/", "/index.html"]:
            file_path = os.path.join(WEB_DIR, "index.html")
        elif path in ["/intake", "/intake.html"]:
            file_path = os.path.join(WEB_DIR, "intake.html")
        elif path.startswith("/campaign/"):
            file_path = os.path.join(WORKSPACE_ROOT, path.lstrip("/"))
        else:
            file_path = os.path.join(WEB_DIR, path.lstrip("/"))

        real_file = os.path.realpath(file_path)
        if not real_file.startswith(os.path.realpath(WORKSPACE_ROOT)) or not os.path.exists(real_file):
            self.send_error(404)
            return

        file_size = os.path.getsize(real_file)
        content_type, _ = mimetypes.guess_type(real_file)
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        """Manejo de peticiones GET para API y recursos estáticos con byte-ranges."""
        parsed = urlparse(self.path)
        path = parsed.path

        # ----------------- Rutas REST API -----------------
        if path == "/api/status":
            self.handle_api_status()
            return
        elif path == "/api/deliver":
            self.handle_api_deliver()
            return
        elif path == "/api/benchmark":
            self.handle_api_benchmark()
            return
        elif path == "/api/introspect":
            self.handle_api_introspect()
            return
        elif path == "/api/health":
            self.handle_api_health()
            return
        elif path == "/api/artifact":
            self.handle_api_artifact(parse_qs(parsed.query))
            return
        elif path == "/api/intake/draft":
            self.handle_api_intake_draft_get()
            return
        elif path == "/api/intake/clients":
            self.handle_api_intake_clients()
            return

        # ----------------- Rutas Estáticas -----------------
        # Rutear '/' a 'web/index.html', '/intake' a 'web/intake.html'
        if path in ["/", "/index.html"]:
            file_path = os.path.join(WEB_DIR, "index.html")
        elif path in ["/intake", "/intake.html"]:
            file_path = os.path.join(WEB_DIR, "intake.html")
        elif path.startswith("/campaign/"):
            # Acceso controlado a archivos de video, audio y entregables de campaña
            rel_path = path.lstrip("/")
            file_path = os.path.join(WORKSPACE_ROOT, rel_path)
        else:
            # Archivos estáticos en web/ (css, js, assets)
            rel_path = path.lstrip("/")
            file_path = os.path.join(WEB_DIR, rel_path)

        # Seguridad de path traversal
        real_file = os.path.realpath(file_path)
        if not real_file.startswith(os.path.realpath(WORKSPACE_ROOT)):
            self.send_error(403, "Acceso denegado")
            return

        if not os.path.exists(real_file) or os.path.isdir(real_file):
            self.send_error(404, f"Archivo no encontrado: {path}")
            return

        # Servir archivo con soporte opcional de streaming HTTP 206 (Range)
        self.serve_file_with_ranges(real_file)

    def handle_api_status(self):
        """Devuelve el estado de las 22 fases de ADCRA."""
        phases = [
            ("Fase 01", "Campaign Setup & Workspace Architecture", "campaign/campaign-manifest.json", "Estrategia"),
            ("Fase 02", "Sensorial Audio Analysis & Synchronization", "campaign/audio/audio-analysis.json", "Audio"),
            ("Fase 03", "Brand Architecture & Copywriting", "campaign/creative/creative-copy.json", "Creativo"),
            ("Fase 04", "Cinematic Storyboard Generation", "campaign/storyboard/storyboard.json", "Creativo"),
            ("Fase 05", "Visual Prompts & Media Generation", "campaign/assets/asset-inventory.json", "Producción"),
            ("Fase 06", "DaVinci Resolve Project & Timeline Assembly", "campaign/timeline/timeline.json", "Edición"),
            ("Fase 07", "Color Grading & Cinematic Palette (ACEScc)", "campaign/color/color-grading-manifest.json", "Color"),
            ("Fase 08", "Fairlight Audio Post-Production & Mastering", "campaign/audio/sound-design-manifest.json", "Fairlight"),
            ("Fase 09", "Graphic Motion & Overlay Architecture", "campaign/motion-graphics/motion-manifest.json", "Motion"),
            ("Fase 10", "Social Media Multi-Platform Delivery", "campaign/deliverables/social-format-manifest.json", "Delivery"),
            ("Fase 11", "Autonomous Quality Control (QC & QA)", "campaign/reports/quality-control-report.json", "QA"),
            ("Fase 12", "Closed-Loop Feedback & Creative Iteration", "campaign/reports/iteration-history.json", "Producción"),
            ("Fase 13", "Dynamic Subtitling & Lyric Sync Engine", "campaign/audio/lyric-alignment.json", "Audio"),
            ("Fase 14", "Visual Identity & Motion Design Tokens", "campaign/remotion/props.json", "Diseño"),
            ("Fase 15", "Adaptive Multi-Platform Delivery Layouts", "campaign/deliverables/guides/tiktok_9_16_safe_zone.png", "Delivery"),
            ("Fase 16", "Advanced Audio Ducking & Sonic Branding", "campaign/audio/sfx_foley_track.wav", "Fairlight"),
            ("Fase 17", "A/B Testing & Variant Generation Matrix", "campaign/remotion/variants.json", "Producción"),
            ("Fase 18", "Cross-Campaign Memory & Performance Insights", "campaign/memory/brand-profile-memory.json", "Memoria"),
            ("Fase 19", "Skill Architect & Meta-Learning Engine", "campaign/meta/synthesized-skills-registry.json", "Meta"),
            ("Fase 20", "End-to-End Pilot Campaign Validation", "campaign/pilot/pilot-run-report.json", "Piloto"),
            ("Fase 21", "Final Commercial Delivery & Master Production", "campaign/deliverables/masters/commercial-delivery-package.json", "Producción"),
            ("Fase 22", "Hardening, Benchmarking & Release CLI", "campaign/reports/benchmarking-report.json", "Tools")
        ]

        status_data = []
        completed_count = 0

        for pid, pname, rel_path, category in phases:
            full_path = os.path.join(WORKSPACE_ROOT, rel_path)
            exists = os.path.exists(full_path)
            size_kb = round(os.path.getsize(full_path) / 1024, 1) if exists else 0
            if exists:
                completed_count += 1
            status_data.append({
                "phase_id": pid,
                "name": pname,
                "artifact": rel_path,
                "category": category,
                "status": "COMPLETED" if exists else "PENDING",
                "exists": exists,
                "size_kb": size_kb
            })

        pct = round((completed_count / len(phases)) * 100, 1)
        self.send_json({
            "system": "ADCRA",
            "version": "1.0.0-gold",
            "overall_status": "PRODUCTION_READY" if pct == 100.0 else "IN_PROGRESS",
            "completion_percentage": pct,
            "total_phases": len(phases),
            "completed_phases": completed_count,
            "phases": status_data
        })

    def handle_api_deliver(self):
        """Devuelve el paquete de entrega comercial y especificaciones técnicas."""
        pkg_path = os.path.join(WORKSPACE_ROOT, "campaign/deliverables/masters/commercial-delivery-package.json")
        if os.path.exists(pkg_path):
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            self.send_json(pkg)
        else:
            self.send_json({"error": "Paquete de entrega no encontrado"}, 404)

    def handle_api_benchmark(self):
        """Devuelve el informe de benchmarking más reciente."""
        bench_path = os.path.join(WORKSPACE_ROOT, "campaign/reports/benchmarking-report.json")
        if os.path.exists(bench_path):
            with open(bench_path, "r", encoding="utf-8") as f:
                bench = json.load(f)
            self.send_json(bench)
        else:
            self.send_json({"error": "Reporte de benchmarking no encontrado"}, 404)

    def handle_api_introspect(self):
        """Devuelve el catálogo de las habilidades del ecosistema."""
        skills_dir = os.path.join(WORKSPACE_ROOT, ".agents/skills")
        skills = []
        for sf in glob.glob(os.path.join(skills_dir, "**", "SKILL.md"), recursive=True):
            rel_path = os.path.relpath(sf, WORKSPACE_ROOT)
            name = os.path.basename(os.path.dirname(sf))
            domain = os.path.basename(os.path.dirname(os.path.dirname(sf)))
            desc = ""
            version = "1.0.0"
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        for line in parts[1].splitlines():
                            if line.startswith("name:"):
                                name = line.split(":", 1)[1].strip()
                            elif line.startswith("domain:"):
                                domain = line.split(":", 1)[1].strip()
                            elif line.startswith("version:"):
                                version = line.split(":", 1)[1].strip()
                            elif line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip()
            except Exception:
                pass
            skills.append({
                "name": name,
                "domain": domain,
                "version": version,
                "description": desc,
                "path": rel_path
            })
        skills = sorted(skills, key=lambda x: (x["domain"], x["name"]))
        self.send_json({"total_skills": len(skills), "skills": skills})

    def handle_api_health(self):
        """Devuelve telemetría de hardware y estado del sistema."""
        cpu_count = os.cpu_count() or 4
        ram_gb = 8.0
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        except Exception:
            pass

        gpu_name = None
        try:
            res = subprocess.run(["nvidia-smi", "-L"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
            if res.returncode == 0 and res.stdout.strip():
                gpu_name = res.stdout.strip().split("\n")[0]
        except Exception:
            pass

        self.send_json({
            "status": "HEALTHY",
            "system_version": "1.0.0-gold",
            "cpu_cores": cpu_count,
            "ram_total_gb": ram_gb,
            "gpu_device": gpu_name,
            "server_pid": os.getpid()
        })

    def handle_api_artifact(self, query):
        """Devuelve el contenido de un artefacto de campaña en formato texto o JSON."""
        rel_path = query.get("path", [""])[0]
        if not rel_path:
            self.send_json({"error": "Parámetro 'path' requerido"}, 400)
            return

        target_path = os.path.realpath(os.path.join(WORKSPACE_ROOT, rel_path))
        if not target_path.startswith(os.path.realpath(WORKSPACE_ROOT)) or not os.path.exists(target_path):
            self.send_json({"error": "Artefacto no encontrado o acceso no permitido"}, 404)
            return

        try:
            if target_path.endswith(".json"):
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_json({"path": rel_path, "type": "json", "content": data})
            else:
                with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                self.send_json({"path": rel_path, "type": "text", "content": text})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)


    def handle_api_intake_draft_get(self):
        """Devuelve el estado de la sesión de borrador de campaña si existe."""
        draft_path = os.path.join(WORKSPACE_ROOT, "campaign", "draft-session.json")
        if os.path.exists(draft_path):
            try:
                with open(draft_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_json({"status": "SUCCESS", "draft": data})
            except Exception as e:
                self.send_json({"status": "ERROR", "message": str(e)}, 500)
        else:
            self.send_json({"status": "SUCCESS", "draft": None, "message": "No hay borrador activo"})

    def handle_api_intake_draft_post(self):
        """Guarda o actualiza la sesión de borrador de campaña (autosave)."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            draft_path = os.path.join(WORKSPACE_ROOT, "campaign", "draft-session.json")
            os.makedirs(os.path.dirname(draft_path), exist_ok=True)
            with open(draft_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.send_json({"status": "SUCCESS", "message": "Borrador guardado exitosamente", "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        except Exception as e:
            self.send_json({"status": "ERROR", "message": str(e)}, 500)

    def handle_api_intake_clients(self):
        """Devuelve el listado de clientes existentes en el sistema ADCRA."""
        clients = []
        brand_memory_path = os.path.join(WORKSPACE_ROOT, "campaign", "memory", "brand-profile-memory.json")
        if os.path.exists(brand_memory_path):
            try:
                with open(brand_memory_path, "r", encoding="utf-8") as f:
                    brand_data = json.load(f)
                clients.append({
                    "id": "locos-materos",
                    "name": brand_data.get("brand_name", "Locos Materos"),
                    "industry": "e-commerce / yerba mate",
                    "has_memory": True,
                    "memory": brand_data
                })
            except Exception:
                pass
        self.send_json({"status": "SUCCESS", "clients": clients})

    def serve_file_with_ranges(self, file_path):
        """Sirve archivos estáticos con soporte completo de HTTP 206 Partial Content para video."""
        file_size = os.path.getsize(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        range_header = self.headers.get("Range")

        if not range_header:
            # Respuesta estándar HTTP 200 completa
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.copy_file_chunks(f, self.wfile, file_size)
            return

        # Parsear header Range: bytes=START-END
        try:
            range_match = range_header.strip().replace("bytes=", "")
            parts = range_match.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1

            if start >= file_size or end >= file_size or start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{file_size}")
                self.end_headers()
                return

            chunk_len = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(chunk_len))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                self.copy_file_chunks(f, self.wfile, chunk_len)

        except Exception as e:
            self.send_error(500, f"Error en streaming: {str(e)}")

    def copy_file_chunks(self, source, destination, total_bytes):
        """Transfiere datos en bloques de 64 KB."""
        bytes_left = total_bytes
        chunk_size = 64 * 1024
        while bytes_left > 0:
            to_read = min(chunk_size, bytes_left)
            chunk = source.read(to_read)
            if not chunk:
                break
            try:
                destination.write(chunk)
                bytes_left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                break

def run_server(port=8080, host="0.0.0.0"):
    """Inicia el servidor HTTP multihilo de ADCRA Mission Control."""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, DashboardRequestHandler)
    print(f"\n========================================================================")
    print(f"      ADCRA MISSION CONTROL — CENTRO DE OPERACIONES WEB (v1.0.0)")
    print(f"========================================================================")
    print(f"  • Servidor activo en: http://localhost:{port}/")
    print(f"  • Red local:          http://{host}:{port}/")
    print(f"  • Raíz de activos:    {WEB_DIR}")
    print(f"  • Streaming Video:    Habilitado con HTTP 206 (Byte-Ranges)")
    print(f"========================================================================\n")
    print("Presiona Ctrl+C para detener el servidor.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido ordenadamente.")
        httpd.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ADCRA Mission Control Web Server")
    parser.add_argument("--port", type=int, default=8080, help="Puerto HTTP (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Dirección de bind (default: 0.0.0.0)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
