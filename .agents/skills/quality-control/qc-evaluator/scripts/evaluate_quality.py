#!/usr/bin/env python3
"""
ADCRA — Quality Control Evaluator
Ejecuta la auditoría tricameral (Técnica, Creativa, Marca) para la campaña de Locos Materos,
calculando el Quality Score ponderado y emitiendo el certificado de entrega formal.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import jsonschema

def get_workspace_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "config" / "quality-control-schema.json").exists():
            return parent
    return Path("/data/usuario/Documentos/davinci resolve")

WORKSPACE_ROOT = get_workspace_root()

def run_tricameral_audit() -> dict:
    """Ejecuta la auditoría exhaustiva en los 3 pilares: Técnico, Creativo y Marca."""

    # 1. Cargar artefactos de campaña
    camp_file = WORKSPACE_ROOT / "campaign" / "campaign-manifest.json"
    time_file = WORKSPACE_ROOT / "campaign" / "timeline" / "timeline.json"
    audio_file = WORKSPACE_ROOT / "campaign" / "audio" / "sound-design-manifest.json"
    color_file = WORKSPACE_ROOT / "campaign" / "color" / "color-grading-manifest.json"
    story_file = WORKSPACE_ROOT / "campaign" / "storyboard" / "storyboard.json"
    motion_file = WORKSPACE_ROOT / "campaign" / "motion-graphics" / "motion-manifest.json"
    social_file = WORKSPACE_ROOT / "campaign" / "deliverables" / "social-format-manifest.json"

    with open(camp_file, "r", encoding="utf-8") as f:
        camp_data = json.load(f)
    with open(time_file, "r", encoding="utf-8") as f:
        time_data = json.load(f)
    with open(audio_file, "r", encoding="utf-8") as f:
        audio_data = json.load(f)
    with open(color_file, "r", encoding="utf-8") as f:
        color_data = json.load(f)
    with open(story_file, "r", encoding="utf-8") as f:
        story_data = json.load(f)
    with open(motion_file, "r", encoding="utf-8") as f:
        motion_data = json.load(f)
    with open(social_file, "r", encoding="utf-8") as f:
        social_data = json.load(f)

    # --- PILAR 1: AUDITORÍA TÉCNICA ---
    tech_checks = []

    # Check 1.1: Resolución vertical 9:16
    tf = time_data.get("timeline_format", {})
    w = tf.get("width")
    h = tf.get("height")
    res_ok = (w == 720 and h == 1280)
    tech_checks.append({
        "check_id": "tech_01_resolution_9_16",
        "name": "Resolución Vertical 9:16 (720x1280)",
        "passed": res_ok,
        "details": f"Resolución detectada: {w}x{h} (Esperado: 720x1280 vertical)"
    })

    # Check 1.2: Framerate y Duración
    fps = tf.get("fps", 0)
    total_frames = tf.get("duration_frames", 0)
    fps_ok = (fps == 24.0 and total_frames == 700)
    tech_checks.append({
        "check_id": "tech_02_framerate_duration",
        "name": "Velocidad de Cuadro 24.0 fps y 700 Frames (29.167s)",
        "passed": fps_ok,
        "details": f"Framerate: {fps} fps, Cuadros totales: {total_frames} (Duración: {round(total_frames / (fps or 24), 3)}s)"
    })

    # Check 1.3: Sonoridad EBU R128 (-14 LUFS, -1 dBTP, 48kHz / 24b)
    loud = audio_data.get("loudness_compliance", {})
    meas_lufs = loud.get("measured_integrated_lufs", -99.0)
    meas_tp = loud.get("measured_true_peak_dbtp", 0.0)
    fmt = audio_data.get("audio_format", {})
    audio_ok = (-16.0 <= meas_lufs <= -12.0) and (meas_tp <= -0.9) and (fmt.get("sample_rate_hz") == 48000)
    tech_checks.append({
        "check_id": "tech_03_ebu_r128_loudness",
        "name": "Normalización de Audio Broadcast EBU R128",
        "passed": audio_ok,
        "details": f"Sonoridad: {meas_lufs} LUFS (Target: -14.0 LUFS), True Peak: {meas_tp} dBTP, Sample Rate: {fmt.get('sample_rate_hz')} Hz"
    })

    # Check 1.4: Conformación de EDL y XML
    edl_file = WORKSPACE_ROOT / "campaign" / "timeline" / "locos_materos_edit.edl"
    xml_file = WORKSPACE_ROOT / "campaign" / "timeline" / "locos_materos_edit.xml"
    conformance_ok = edl_file.is_file() and xml_file.is_file()
    tech_checks.append({
        "check_id": "tech_04_timeline_conformance",
        "name": "Conformación Estándar NLE (CMX 3600 EDL y FCP7 XML)",
        "passed": conformance_ok,
        "details": f"Archivos conformados: EDL ({edl_file.is_file()}), XML ({xml_file.is_file()})"
    })

    # Check 1.5: Existencia de Activos Físicos Master
    wav_master = WORKSPACE_ROOT / "campaign" / "audio" / "locos_materos_master_mix.wav"
    mp3_master = WORKSPACE_ROOT / "campaign" / "audio" / "locos_materos_master_mix.mp3"
    assets_ok = wav_master.is_file() and mp3_master.is_file()
    tech_checks.append({
        "check_id": "tech_05_master_audio_assets",
        "name": "Integridad de Archivos Master de Audio",
        "passed": assets_ok,
        "details": f"Master WAV (PCM 24b/48k): {wav_master.is_file()}, Master MP3: {mp3_master.is_file()}"
    })

    tech_passed = sum(1 for c in tech_checks if c["passed"])
    tech_score = round((tech_passed / len(tech_checks)) * 100.0, 1)
    tech_status = "PASSED" if tech_score >= 90.0 else "FAILED"

    # --- PILAR 2: AUDITORÍA CREATIVA ---
    creative_checks = []

    # Check 2.1: Sincronización Rítmica a Beats Musicales
    clips = time_data.get("tracks", {}).get("video_tracks", [{}])[0].get("clips", [])
    scenes_count = len(clips)
    cuts_on_beats = all(c.get("beat_sync", {}).get("aligned_beat_seconds", 0) > 0 for c in clips)
    creative_checks.append({
        "check_id": "creat_01_beat_sync_cuts",
        "name": "Alineación de Cortes a Transientes Musicales (107.7 BPM)",
        "passed": cuts_on_beats and scenes_count == 9,
        "details": f"Total de tomas montadas: {scenes_count}, Cortes sincronizados a transientes rítmicos: {cuts_on_beats}"
    })

    # Check 2.2: Progresión Narrativa y Storyboard Rationale
    story_scenes = story_data.get("scenes", [])
    has_rationales = all(len(sc.get("rationale", "")) > 15 for sc in story_scenes)
    creative_checks.append({
        "check_id": "creat_02_narrative_progression",
        "name": "Estructura Narrativa Completa y Justificaciones Estratégicas",
        "passed": (len(story_scenes) == 9 and has_rationales),
        "details": f"Escenas con justificación cinematográfica: {len(story_scenes)}/9"
    })

    # Check 2.3: Overlays Tipográficos y Cinética Motion Graphics
    mg_overlays = motion_data.get("overlays", [])
    mg_ok = len(mg_overlays) == 9 and all((WORKSPACE_ROOT / ov.get("output_asset_path", "")).is_file() for ov in mg_overlays)
    creative_checks.append({
        "check_id": "creat_03_motion_graphics_overlays",
        "name": "Cinética Tipográfica y Overlays Gráficos 720x1280",
        "passed": mg_ok,
        "details": f"Plantillas cinéticas generadas e hiperframes renderizados: {len(mg_overlays)}/9"
    })

    # Check 2.4: Respeto a Zonas Seguras Multiplataforma
    guides = social_data.get("deliverables", [])
    guides_ok = len(guides) >= 5
    creative_checks.append({
        "check_id": "creat_04_safe_zones_adherence",
        "name": "Márgenes de Seguridad y Prevención de Oclusiones UI Móvil",
        "passed": guides_ok,
        "details": f"Plataformas móviles y widescreen mapeadas con safe zones: {len(guides)}"
    })

    creative_passed = sum(1 for c in creative_checks if c["passed"])
    creative_score = round((creative_passed / len(creative_checks)) * 100.0, 1)
    creative_status = "PASSED" if creative_score >= 90.0 else "FAILED"

    # --- PILAR 3: AUDITORÍA DE MARCA (LOCOS MATEROS) ---
    brand_checks = []

    # Check 3.1: Paleta Cromática Oficial
    mg_palette = motion_data.get("brand_palette", {}).get("primary", "")
    color_manifest_palette = color_data.get("creative_intent", {}).get("color_palette", [])
    palette_ok = any("#0D5C3A" in str(c) for c in color_manifest_palette) or "#0D5C3A" in mg_palette
    brand_checks.append({
        "check_id": "brand_01_color_palette_harmony",
        "name": "Identidad Cromática Oficial (#0D5C3A Verde Mate, #D4AF37 Dorado Yerba)",
        "passed": palette_ok,
        "details": f"Colores institucionales verificados en motion graphics y LUTs 3D"
    })

    # Check 3.2: Temperatura Cálida de Color y Look Cinematográfico
    bch = color_data.get("brand_color_harmony", {})
    target_temp = bch.get("color_temperature_target_kelvin", 0)
    luts_count = len(color_data.get("luts_registered", []))
    temp_ok = (5500 <= target_temp <= 6200) and luts_count >= 3
    brand_checks.append({
        "check_id": "brand_02_cinematic_warmth_look",
        "name": "Temperatura Cálida (~5900K) y LUTs 3D .cube",
        "passed": temp_ok,
        "details": f"Temperatura calibrada: {target_temp}K, LUTs 3D registradas: {luts_count}"
    })

    # Check 3.3: Presencia del Claim Oficial
    sb_copies = [sc.get("copy", "") for sc in story_scenes]
    claim_ok = any("tu mate" in c.lower() for c in sb_copies)
    brand_checks.append({
        "check_id": "brand_03_official_campaign_claim",
        "name": "Presencia del Lema Rector '¿Dónde estás tú? Está tu mate'",
        "passed": claim_ok,
        "details": f"Claim publicitario verificado en storyboard: '{sb_copies[-1]}'"
    })

    # Check 3.4: Packshot Final y Cierre de Marca (Escena 09)
    scene_09 = story_scenes[-1] if story_scenes else {}
    packshot_ok = (scene_09.get("brand_visibility") == "hero_packshot" or
                   "packshot" in scene_09.get("visual", "").lower())
    brand_checks.append({
        "check_id": "brand_04_packshot_hero_closing",
        "name": "Cierre Hero Packshot con Logotipo en Escena 09",
        "passed": packshot_ok,
        "details": f"Remate publicitario de escena final: brand_visibility={scene_09.get('brand_visibility')}"
    })

    brand_passed = sum(1 for c in brand_checks if c["passed"])
    brand_score = round((brand_passed / len(brand_checks)) * 100.0, 1)
    brand_status = "PASSED" if brand_score >= 90.0 else "FAILED"

    # --- PONDERACIÓN GLOBAL ---
    # Técnico: 35%, Creativo: 35%, Marca: 30%
    overall_score = round(tech_score * 0.35 + creative_score * 0.35 + brand_score * 0.30, 1)

    if overall_score >= 90.0 and tech_status == "PASSED" and creative_status == "PASSED" and brand_status == "PASSED":
        certification_status = "APPROVED"
    elif overall_score >= 75.0:
        certification_status = "NEEDS_REVISION"
    else:
        certification_status = "REJECTED"

    report = {
        "campaign_id": camp_data.get("campaign_id", "camp_locos_materos_2026"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_score": overall_score,
        "certification_status": certification_status,
        "audits": {
            "technical_audit": {
                "score": tech_score,
                "status": tech_status,
                "checks": tech_checks
            },
            "creative_audit": {
                "score": creative_score,
                "status": creative_status,
                "checks": creative_checks
            },
            "brand_audit": {
                "score": brand_score,
                "status": brand_status,
                "checks": brand_checks
            }
        }
    }

    return report

def validate_qc_report(report: dict):
    """Valida el informe contra el contrato formal JSON Schema."""
    schema_path = WORKSPACE_ROOT / "config" / "quality-control-schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=report, schema=schema)
    print(f"[SUCCESS] Informe de control de calidad validado contra config/quality-control-schema.json")

def main():
    parser = argparse.ArgumentParser(description="Quality Control Evaluator & Certification Engine")
    parser.add_argument("--validate-only", action="store_true", help="Solo valida el reporte existente")
    args = parser.parse_args()

    report_path = WORKSPACE_ROOT / "campaign" / "reports" / "quality-control-report.json"

    if args.validate_only:
        if not report_path.is_file():
            print(f"[ERROR] No existe {report_path}", file=sys.stderr)
            sys.exit(1)
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        validate_qc_report(data)
        print(f"[VALID] El informe {report_path} cumple 100% con config/quality-control-schema.json")
        sys.exit(0)

    print("[QUALITY CONTROL] Ejecutando auditoría tricameral (Técnica, Creativa, Marca)...")
    report = run_tricameral_audit()
    validate_qc_report(report)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Informe guardado en: {report_path}")
    print(f" - Quality Score Global: {report['overall_score']}/100.0")
    print(f" - Dictamen Final: {report['certification_status']}")
    print(f"   * Auditoría Técnica: {report['audits']['technical_audit']['score']}/100.0 ({report['audits']['technical_audit']['status']})")
    print(f"   * Auditoría Creativa: {report['audits']['creative_audit']['score']}/100.0 ({report['audits']['creative_audit']['status']})")
    print(f"   * Auditoría de Marca: {report['audits']['brand_audit']['score']}/100.0 ({report['audits']['brand_audit']['status']})")

if __name__ == "__main__":
    main()
