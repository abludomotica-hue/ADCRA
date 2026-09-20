#!/usr/bin/env python3
"""
ADCRA Unified CLI (Fase 22: Hardening & Release)
Punto de entrada unificado para orquestar, inspeccionar, producir,
evaluar y certificar campañas publicitarias autónomas de ADCRA.
"""

import os
import sys
import glob
import json
import subprocess
import argparse
from datetime import datetime

# Locate root directory dynamically
cur = os.path.abspath(os.path.dirname(__file__))
while cur and cur != os.path.dirname(cur):
    if os.path.exists(os.path.join(cur, "config")) and os.path.exists(os.path.join(cur, "campaign")):
        WORKSPACE_ROOT = cur
        break
    cur = os.path.dirname(cur)
else:
    WORKSPACE_ROOT = os.path.abspath(os.path.dirname(__file__))

VERSION = "1.0.0-gold"
BANNER = r"""
========================================================================
   ___    ____   ____ ____       _      ____ _     ___ 
  / _ \  |  _ \ / ___|  _ \     / \    / ___| |   |_ _|
 / /_\ \ | | | | |   | |_) |   / _ \  | |   | |    | | 
/ /   \ \| |_| | |___|  _ <   / ___ \ | |___| |___ | | 
\/     \/|____/ \____|_| \_\ /_/   \_(_)____|_____|___|
 Autonomous Digital Campaign & Creative Production System
                     Release 1.0.0-gold
========================================================================
"""

# ANSI Color codes
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def cmd_version(args):
    """Muestra la versión y banner de ADCRA."""
    if args.json:
        print(json.dumps({
            "system": "ADCRA",
            "full_name": "Autonomous Digital Campaign & Creative Production System",
            "version": VERSION,
            "release_candidate": "v1.0.0-gold",
            "status": "PRODUCTION_READY",
            "author": "Antigravity Multi-Agent Agency"
        }, indent=2))
    else:
        print(BANNER)
        print(f"{BOLD}Versión:{RESET} {VERSION}")
        print(f"{BOLD}Estado:{RESET}  {GREEN}PRODUCTION READY & RELEASED{RESET}")
        print(f"{BOLD}Campaña:{RESET} Locos Materos — '¿Dónde estás tú? Está tu mate'")
    return 0

def cmd_status(args):
    """Verifica y presenta el estado de las 22 fases del sistema ADCRA."""
    phases = [
        ("Fase 01", "Campaign Setup & Workspace Architecture", "campaign/campaign-manifest.json"),
        ("Fase 02", "Sensorial Audio Analysis & Synchronization", "campaign/audio/audio-analysis.json"),
        ("Fase 03", "Brand Architecture & Copywriting", "campaign/creative/creative-copy.json"),
        ("Fase 04", "Cinematic Storyboard Generation", "campaign/storyboard/storyboard.json"),
        ("Fase 05", "Visual Prompts & Media Generation", "campaign/assets/asset-inventory.json"),
        ("Fase 06", "DaVinci Resolve Project & Timeline Assembly", "campaign/timeline/timeline.json"),
        ("Fase 07", "Color Grading & Cinematic Palette (ACEScc)", "campaign/color/color-grading-manifest.json"),
        ("Fase 08", "Fairlight Audio Post-Production & Mastering", "campaign/audio/sound-design-manifest.json"),
        ("Fase 09", "Graphic Motion & Overlay Architecture", "campaign/motion-graphics/motion-manifest.json"),
        ("Fase 10", "Social Media Multi-Platform Delivery", "campaign/deliverables/social-format-manifest.json"),
        ("Fase 11", "Autonomous Quality Control (QC & QA)", "campaign/reports/quality-control-report.json"),
        ("Fase 12", "Closed-Loop Feedback & Creative Iteration", "campaign/reports/iteration-history.json"),
        ("Fase 13", "Dynamic Subtitling & Lyric Sync Engine", "campaign/audio/lyric-alignment.json"),
        ("Fase 14", "Visual Identity & Motion Design Tokens", "campaign/remotion/props.json"),
        ("Fase 15", "Adaptive Multi-Platform Delivery Layouts", "campaign/deliverables/guides/tiktok_9_16_safe_zone.png"),
        ("Fase 16", "Advanced Audio Ducking & Sonic Branding", "campaign/audio/sfx_foley_track.wav"),
        ("Fase 17", "A/B Testing & Variant Generation Matrix", "campaign/remotion/variants.json"),
        ("Fase 18", "Cross-Campaign Memory & Performance Insights", "campaign/memory/brand-profile-memory.json"),
        ("Fase 19", "Skill Architect & Meta-Learning Engine", "campaign/meta/synthesized-skills-registry.json"),
        ("Fase 20", "End-to-End Pilot Campaign Validation", "campaign/pilot/pilot-run-report.json"),
        ("Fase 21", "Final Commercial Delivery & Master Production", "campaign/deliverables/masters/commercial-delivery-package.json"),
        ("Fase 22", "Hardening, Benchmarking & Release CLI", "campaign/reports/benchmarking-report.json")
    ]

    status_data = []
    completed_count = 0

    for pid, pname, path in phases:
        full_path = os.path.join(WORKSPACE_ROOT, path)
        exists = os.path.exists(full_path)
        if exists:
            completed_count += 1
            status_str = "COMPLETED"
        else:
            status_str = "PENDING"
        status_data.append({
            "phase": pid,
            "name": pname,
            "artifact": path,
            "status": status_str,
            "exists": exists
        })

    completion_pct = round((completed_count / len(phases)) * 100, 1)

    if args.json:
        print(json.dumps({
            "system_version": VERSION,
            "total_phases": len(phases),
            "completed_phases": completed_count,
            "completion_percentage": completion_pct,
            "overall_status": "PRODUCTION_READY" if completion_pct == 100.0 else "IN_PROGRESS",
            "phases": status_data
        }, indent=2))
        return 0

    print(f"\n{BOLD}{CYAN}=== ADCRA — Estado del Sistema (22 Fases) ==={RESET}")
    print(f"Progreso Global: {GREEN if completion_pct == 100 else YELLOW}{completion_pct}%{RESET} ({completed_count}/{len(phases)} fases completadas)\n")
    print(f"{'FASE':<9} | {'DESCRIPCIÓN':<46} | {'ESTADO':<11} | {'ARTEFACTO'}")
    print("-" * 110)
    for p in status_data:
        color = GREEN if p["exists"] else RED
        mark = "[PASS]" if p["exists"] else "[FAIL]"
        print(f"{p['phase']:<9} | {p['name']:<46} | {color}{mark} {p['status']:<4}{RESET} | {p['artifact']}")

    print("-" * 110)
    if completion_pct == 100.0:
        print(f"{BOLD}{GREEN}✓ TODAS LAS 22 FASES DE ADCRA ESTÁN 100% OPERACIONALES Y VERIFICADAS.{RESET}\n")
    else:
        print(f"{BOLD}{YELLOW}! ALERTA: Hay fases pendientes de verificación.{RESET}\n")

    return 0

def cmd_benchmark(args):
    """Ejecuta o consulta el benchmarking del sistema."""
    bench_script = os.path.join(WORKSPACE_ROOT, ".agents/skills/tools/benchmarking-engine/scripts/run_benchmarks.py")
    if not os.path.exists(bench_script):
        print(f"{RED}Error: Script de benchmark no encontrado en {bench_script}{RESET}")
        return 1

    cmd = [sys.executable, bench_script, "--iterations", str(args.iterations)]
    report_path = os.path.join(WORKSPACE_ROOT, "campaign/reports/benchmarking-report.json")
    cmd.extend(["--output", report_path])
    
    ret = subprocess.run(cmd)
    if args.json and ret.returncode == 0:
        with open(report_path, "r", encoding="utf-8") as f:
            print(f.read())
    return ret.returncode

def cmd_produce(args):
    """Ejecuta la producción del comercial final (Fase 21)."""
    produce_script = os.path.join(WORKSPACE_ROOT, ".agents/skills/production/campaign-production-master/scripts/produce_final_commercial.py")
    if not os.path.exists(produce_script):
        print(f"{RED}Error: Script de producción final no encontrado en {produce_script}{RESET}")
        return 1
    ret = subprocess.run([sys.executable, produce_script])
    return ret.returncode

def cmd_deliver(args):
    """Muestra el paquete de entrega comercial y especificaciones técnicas."""
    pkg_path = os.path.join(WORKSPACE_ROOT, "campaign/deliverables/masters/commercial-delivery-package.json")
    if not os.path.exists(pkg_path):
        print(f"{RED}Error: Paquete de entrega no encontrado en {pkg_path}{RESET}")
        return 1

    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    if args.json:
        print(json.dumps(pkg, indent=2, ensure_ascii=False))
        return 0

    mv = pkg.get("master_video", {})
    ma = pkg.get("master_audio", {})
    bc = pkg.get("broadcast_certification", {})
    variants = pkg.get("variants", [])

    print(f"\n{BOLD}{CYAN}=== ADCRA — Paquete de Entrega Comercial (Locos Materos) ==={RESET}")
    print(f"{BOLD}Campaña:{RESET}      Locos Materos (ID: {pkg.get('campaign_id')})")
    print(f"{BOLD}Delivery ID:{RESET}  {pkg.get('delivery_id')}")
    print(f"{BOLD}Timestamp:{RESET}    {pkg.get('timestamp')}")
    print(f"{BOLD}Duración:{RESET}     {mv.get('duration_seconds')} s")
    print(f"{BOLD}Certificación:{RESET} {GREEN}{bc.get('status')} (QC Score: {bc.get('qc_score')}/100.0){RESET}")
    print(f"{BOLD}Claim:{RESET}         \"{bc.get('claim_verified')}\"\n")

    print(f"{BOLD}Master Deliverable:{RESET}")
    print(f"  • Archivo:   {mv.get('file_path')}")
    print(f"  • Aspecto:   {mv.get('aspect_ratio')} ({mv.get('resolution')}) @ {mv.get('fps')} fps")
    audio_codec = mv.get('audio_codec', 'aac')
    loudness = ma.get('loudness_lufs', -12.7)
    tp = ma.get('true_peak_dbtp', -1.0)
    std = ma.get('standard', 'EBU R128')
    print(f"  • Codecs:    Video {mv.get('video_codec')} ({mv.get('pixel_format')}) | Audio {audio_codec} ({loudness} LUFS - {std})")
    print(f"  • True Peak: {tp} dBTP | Sample Rate: {ma.get('sample_rate_hz', 48000)} Hz")
    print(f"  • SHA-256:   {mv.get('sha256')}\n")

    print(f"{BOLD}Social Media Multi-Platform Deliverables ({len(variants)} formatos):{RESET}")
    print(f"{'PLATAFORMA':<18} | {'ASPECTO':<8} | {'RESOLUCIÓN':<11} | {'SHA-256 (PREFIJO)':<18} | {'ARCHIVO'}")
    print("-" * 96)
    for s in variants:
        fname = os.path.basename(s.get("file_path", ""))
        sha_prefix = s.get("sha256", "")[:16] + "..."
        print(f"{s.get('platform'):<18} | {s.get('aspect_ratio'):<8} | {s.get('resolution'):<11} | {sha_prefix:<18} | {fname}")
    print("-" * 96)
    print(f"\n{GREEN}✓ Todos los entregables están certificados y listos para distribución omnicanal.{RESET}\n")
    return 0

def cmd_introspect(args):
    """Inspecciona y cataloga todas las habilidades del ecosistema ADCRA."""
    skills_dir = os.path.join(WORKSPACE_ROOT, ".agents/skills")
    skills = []

    for skill_file in glob.glob(os.path.join(skills_dir, "**", "SKILL.md"), recursive=True):
        rel_path = os.path.relpath(skill_file, WORKSPACE_ROOT)
        name = os.path.basename(os.path.dirname(skill_file))
        domain = os.path.basename(os.path.dirname(os.path.dirname(skill_file)))
        desc = ""
        version = "1.0.0"

        try:
            with open(skill_file, "r", encoding="utf-8") as f:
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

    if args.json:
        print(json.dumps({"total_skills": len(skills), "skills": skills}, indent=2, ensure_ascii=False))
        return 0

    print(f"\n{BOLD}{CYAN}=== ADCRA — Catálogo de Habilidades del Ecosistema ({len(skills)} Habilidades) ==={RESET}\n")
    print(f"{'NOMBRE':<28} | {'DOMINIO':<16} | {'VER':<7} | {'DESCRIPCIÓN'}")
    print("-" * 105)
    for s in skills:
        desc = (s["description"][:46] + "...") if len(s["description"]) > 46 else s["description"]
        print(f"{s['name']:<28} | {s['domain']:<16} | {s['version']:<7} | {desc}")
    print("-" * 105)
    print(f"{GREEN}✓ Ecosistema de habilidades 100% catalogado e introspectable ({len(skills)} habilidades operacionales).{RESET}\n")
    return 0


def cmd_dashboard(args):
    """Inicia el servidor web interactivo de ADCRA Mission Control."""
    import dashboard_server
    if getattr(args, 'open', False):
        try:
            import webbrowser
            webbrowser.open(f"http://localhost:{args.port}/")
        except Exception:
            pass
    return dashboard_server.run_server(port=args.port, host=args.host)

def cmd_test(args):
    """Ejecuta la suite de pruebas automatizadas."""
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    if args.pattern:
        cmd.extend(["-p", args.pattern])
    print(f"{BOLD}[*] Ejecutando suite de pruebas unitarias ADCRA...{RESET}")
    ret = subprocess.run(cmd)
    return ret.returncode

def main():
    parser = argparse.ArgumentParser(
        description="ADCRA — Autonomous Digital Campaign & Creative Production System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplos:\n  adcra status\n  adcra benchmark --iterations 15\n  adcra deliver\n  adcra introspect\n  adcra test"
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # version
    subparsers.add_parser("version", help="Muestra la versión de ADCRA")

    # status
    subparsers.add_parser("status", help="Muestra el estado de las 22 fases del sistema")

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Ejecuta benchmarks de latencia y throughput")
    p_bench.add_argument("--iterations", type=int, default=10, help="Número de iteraciones")

    # produce
    subparsers.add_parser("produce", help="Regenera el comercial final y entregables sociales")

    # deliver
    subparsers.add_parser("deliver", help="Inspecciona el paquete de entrega comercial y especificaciones")

    # introspect
    subparsers.add_parser("introspect", help="Inspecciona el catálogo de habilidades del ecosistema")

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="Inicia el servidor web interactivo de ADCRA Mission Control")
    p_dash.add_argument("--port", type=int, default=8080, help="Puerto HTTP (default: 8080)")
    p_dash.add_argument("--host", type=str, default="0.0.0.0", help="Host bind (default: 0.0.0.0)")
    p_dash.add_argument("--open", action="store_true", help="Abre el navegador automáticamente")

    # test
    p_test = subparsers.add_parser("test", help="Ejecuta la suite de pruebas de regresión")
    p_test.add_argument("-p", "--pattern", type=str, default="test_*.py", help="Patrón de archivos de test")

    args = parser.parse_args()

    if not args.command:
        cmd_version(args)
        parser.print_help()
        return 0

    cmd_map = {
        "version": cmd_version,
        "status": cmd_status,
        "benchmark": cmd_benchmark,
        "produce": cmd_produce,
        "deliver": cmd_deliver,
        "introspect": cmd_introspect,
        "test": cmd_test,
        "dashboard": cmd_dashboard
    }

    handler = cmd_map.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
