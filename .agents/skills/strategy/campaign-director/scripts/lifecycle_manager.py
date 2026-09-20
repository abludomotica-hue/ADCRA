#!/usr/bin/env python3
"""
ADCRA Campaign Director — Lifecycle Manager
Administra la máquina de estados de la campaña, transiciones de fase y control
estricto de iteraciones (máximo 3 automáticas).
"""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import jsonschema

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

VALID_PHASES = [
    "BRIEF_INGESTION",
    "STRATEGIC_ALIGNMENT",
    "ASSET_INTELLIGENCE",
    "STORYBOARDING",
    "TOOL_ROUTING",
    "PRODUCTION",
    "QUALITY_CONTROL",
    "ITERATION_ENGINE",
    "HALT_FOR_USER_REVIEW",
    "DELIVERY"
]

def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifiesto no encontrado: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_manifest(manifest: dict, manifest_path: Path):
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    schema_path = WORKSPACE_ROOT / "config" / "campaign-schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=manifest, schema=schema)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def cmd_status(manifest: dict):
    wf = manifest.get("workflow_status", {})
    print("\n=== ESTADO DE CICLO DE VIDA ADCRA ===")
    print(f"Campaña:        {manifest.get('campaign_name')} ({manifest.get('campaign_id')})")
    print(f"Fase Actual:    {wf.get('current_phase')}")
    print(f"Iteración:      {wf.get('iteration_count')} / {wf.get('max_iterations', 3)}")
    print(f"Aprobada:       {'SÍ' if wf.get('is_approved') else 'NO'}")
    print("=====================================\n")

def cmd_transition(manifest: dict, target_phase: str, manifest_path: Path):
    if target_phase not in VALID_PHASES:
        print(f"[ERROR] Fase no válida: {target_phase}. Fases permitidas: {VALID_PHASES}", file=sys.stderr)
        sys.exit(1)
    
    prev = manifest["workflow_status"]["current_phase"]
    manifest["workflow_status"]["current_phase"] = target_phase
    save_manifest(manifest, manifest_path)
    print(f"[TRANSITION] Fase actualizada con éxito: {prev} -> {target_phase}")

def cmd_request_iteration(manifest: dict, reason: str, manifest_path: Path):
    wf = manifest["workflow_status"]
    current_iter = wf.get("iteration_count", 0)
    max_iter = wf.get("max_iterations", 3)
    
    new_iter = current_iter + 1
    if new_iter > max_iter:
        wf["current_phase"] = "HALT_FOR_USER_REVIEW"
        wf["iteration_count"] = max_iter
        save_manifest(manifest, manifest_path)
        print(f"[HALT] Límite de {max_iter} iteraciones alcanzado. El sistema se detiene para revisión humana obligatoria.")
        print(f"Motivo del último intento: {reason}")
        return False
    else:
        wf["iteration_count"] = new_iter
        wf["current_phase"] = "ITERATION_ENGINE"
        save_manifest(manifest, manifest_path)
        print(f"[ITERATION] Iniciando iteración {new_iter} de {max_iter}. Motivo: {reason}")
        return True

def cmd_approve(manifest: dict, manifest_path: Path):
    manifest["workflow_status"]["is_approved"] = True
    manifest["workflow_status"]["current_phase"] = "DELIVERY"
    save_manifest(manifest, manifest_path)
    print("[APPROVED] Campaña aprobada oficialmente para entrega final.")

def main():
    parser = argparse.ArgumentParser(description="Gestor de ciclo de vida e iteraciones de campaña ADCRA")
    parser.add_argument("--manifest", "-m", default="campaign/campaign-manifest.json", help="Ruta al manifiesto de campaña")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    subparsers.add_parser("status", help="Muestra el estado actual de la campaña")

    # transition
    trans_parser = subparsers.add_parser("transition", help="Transiciona la fase del workflow")
    trans_parser.add_argument("--to", required=True, help="Nombre de la fase destino")

    # iterate
    iter_parser = subparsers.add_parser("iterate", help="Solicita una nueva iteración de mejora")
    iter_parser.add_argument("--reason", required=True, help="Motivo técnico o creativo de la iteración")

    # approve
    subparsers.add_parser("approve", help="Marca la campaña como aprobada")

    args = parser.parse_args()
    manifest_path = WORKSPACE_ROOT / args.manifest
    manifest = load_manifest(manifest_path)

    if args.command == "status":
        cmd_status(manifest)
    elif args.command == "transition":
        cmd_transition(manifest, args.to, manifest_path)
    elif args.command == "iterate":
        cmd_request_iteration(manifest, args.reason, manifest_path)
    elif args.command == "approve":
        cmd_approve(manifest, manifest_path)

if __name__ == "__main__":
    main()
