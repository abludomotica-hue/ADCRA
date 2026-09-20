#!/usr/bin/env python3
"""
ADCRA — Dynamic Tool Router
Mapea necesidades creativas y técnicas hacia la herramienta primaria adecuada
o activa alternativas declaradas con base en la disponibilidad en tiempo real.
"""

import sys
import os
import json
import argparse
from pathlib import Path

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

# Agregar tool-discovery al PATH para reutilizar chequeos
DISCOVERY_SCRIPTS = WORKSPACE_ROOT / ".agents" / "skills" / "tools" / "tool-discovery" / "scripts"
if str(DISCOVERY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(DISCOVERY_SCRIPTS))

try:
    from discover_tools import discover_all_tools, is_tool_available
except ImportError:
    # Fallback si se ejecuta de forma aislada
    def discover_all_tools():
        return {"tools": {}}
    def is_tool_available(t, cache=None):
        return False

def load_router_matrix() -> dict:
    router_path = WORKSPACE_ROOT / "config" / "tool-router.json"
    if not router_path.is_file():
        raise FileNotFoundError(f"Matriz de enrutador no encontrada: {router_path}")
    with open(router_path, "r", encoding="utf-8") as f:
        return json.load(f)

def route_need(need: str, discovery_cache: dict = None) -> dict:
    matrix = load_router_matrix()
    routes = matrix.get("routes", [])
    
    # Normalización para búsqueda case-insensitive y flexible
    target_need = need.strip().lower()
    matched_route = None
    for r in routes:
        if r["necesidad"].strip().lower() == target_need:
            matched_route = r
            break

    if not matched_route:
        # Búsqueda por contención
        for r in routes:
            if target_need in r["necesidad"].strip().lower() or r["necesidad"].strip().lower() in target_need:
                matched_route = r
                break

    if not matched_route:
        return {
            "necesidad": need,
            "status": "NOT_FOUND",
            "error": f"No existe una regla de enrutamiento para la necesidad: '{need}'"
        }

    primary = matched_route["herramienta_primaria"]
    alt = matched_route.get("alternativa")
    req_gpu = matched_route.get("requiere_gpu", False)
    rationale = matched_route.get("criterio_decision", "")

    cache = discovery_cache or discover_all_tools()

    primary_ok = is_tool_available(primary, cache)
    if primary_ok:
        return {
            "necesidad": matched_route["necesidad"],
            "selected_tool": primary,
            "is_fallback": False,
            "status": "ROUTED_PRIMARY",
            "primary_tool": primary,
            "primary_available": True,
            "alternative_tool": alt,
            "alternative_available": is_tool_available(alt, cache) if alt else False,
            "requires_gpu": req_gpu,
            "decision_rationale": rationale
        }

    # Primary no disponible: evaluar alternativa
    if alt:
        alt_ok = is_tool_available(alt, cache)
        if alt_ok:
            return {
                "necesidad": matched_route["necesidad"],
                "selected_tool": alt,
                "is_fallback": True,
                "status": "ROUTED_FALLBACK",
                "primary_tool": primary,
                "primary_available": False,
                "alternative_tool": alt,
                "alternative_available": True,
                "requires_gpu": req_gpu,
                "decision_rationale": f"[FALLBACK] Herramienta primaria '{primary}' no disponible. Despachando alternativa '{alt}' para: {rationale}"
            }

    # Ni primaria ni alternativa disponibles
    return {
        "necesidad": matched_route["necesidad"],
        "selected_tool": None,
        "is_fallback": False,
        "status": "UNAVAILABLE",
        "primary_tool": primary,
        "primary_available": False,
        "alternative_tool": alt,
        "alternative_available": False,
        "requires_gpu": req_gpu,
        "decision_rationale": rationale,
        "resolution_action": f"Se requiere instalar '{primary}'" + (f" o '{alt}'" if alt else "")
    }

def audit_all_routes(discovery_cache: dict = None) -> list:
    matrix = load_router_matrix()
    routes = matrix.get("routes", [])
    cache = discovery_cache or discover_all_tools()
    
    results = []
    for r in routes:
        res = route_need(r["necesidad"], cache)
        results.append(res)
    return results

def main():
    parser = argparse.ArgumentParser(description="ADCRA Dynamic Tool Router")
    parser.add_argument("--need", "-n", help="Nombre de la necesidad creativa o técnica a enrutar")
    parser.add_argument("--list-routes", action="store_true", help="Lista las necesidades soportadas")
    parser.add_argument("--audit-routes", action="store_true", help="Audita la resolución de todas las rutas en el entorno actual")
    parser.add_argument("--json", action="store_true", help="Salida en JSON estructurado")
    args = parser.parse_args()

    if args.list_routes:
        matrix = load_router_matrix()
        print("\n=== MATRIZ DE RUTAS ADCRA ===")
        for r in matrix.get("routes", []):
            alt_str = f"(Alternativa: {r['alternativa']})" if r.get("alternativa") else "(Sin alternativa)"
            print(f" - {r['necesidad']:<26} -> {r['herramienta_primaria']:<18} {alt_str}")
        print("==============================\n")
        return

    if args.audit_routes:
        cache = discover_all_tools()
        audit = audit_all_routes(cache)
        if args.json:
            print(json.dumps(audit, indent=2, ensure_ascii=False))
        else:
            print("\n=== AUDITORÍA DE ENRUTAMIENTO DE HERRAMIENTAS ADCRA ===")
            print(f"{'Necesidad':<26} | {'Primaria':<16} | {'Seleccionada':<16} | {'Estado':<16}")
            print("-" * 82)
            primary_count = 0
            fallback_count = 0
            unavail_count = 0
            for item in audit:
                sel = item.get("selected_tool") or "NINGUNA"
                stat = item.get("status")
                if stat == "ROUTED_PRIMARY":
                    primary_count += 1
                elif stat == "ROUTED_FALLBACK":
                    fallback_count += 1
                else:
                    unavail_count += 1
                print(f"{item['necesidad']:<26} | {item.get('primary_tool', 'N/A'):<16} | {sel:<16} | {stat:<16}")
            print("-" * 82)
            print(f"Total Rutas: {len(audit)} | Primarias Operativas: {primary_count} | En Fallback: {fallback_count} | Requieren Instalación: {unavail_count}\n")
        return

    if args.need:
        result = route_need(args.need)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n=== RESULTADO DE ENRUTAMIENTO ===")
            print(f"Necesidad:      {result.get('necesidad')}")
            print(f"Estado:         {result.get('status')}")
            print(f"Herramienta:    {result.get('selected_tool') or 'NO DISPONIBLE'}")
            print(f"Es Fallback:    {'SÍ' if result.get('is_fallback') else 'NO'}")
            print(f"Requiere GPU:   {'SÍ' if result.get('requires_gpu') else 'NO'}")
            print(f"Justificación:  {result.get('decision_rationale')}")
            if result.get("resolution_action"):
                print(f"Acción:         {result.get('resolution_action')}")
            print("=================================\n")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
