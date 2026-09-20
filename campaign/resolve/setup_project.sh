#!/usr/bin/env bash
# ADCRA — Setup DaVinci Resolve Project Launcher
set -e
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting/Modules"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API"

python3 "/data/usuario/Documentos/davinci resolve/campaign/resolve/import_to_resolve.py"
