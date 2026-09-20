#!/usr/bin/env bash
# ADCRA — Beat-Synced FFmpeg Assembly Script
set -e

WORKSPACE_ROOT="/data/usuario/Documentos/davinci resolve"
cd "$WORKSPACE_ROOT"

ffmpeg -y \
  -t 3.500 -i "Recursos/videos/Escena 01 Ya está sonando el hervidor.mp4" -t 3.292 -i "Recursos/videos/Escena 02 Macro de yerba y bombilla.mp4" -t 3.417 -i "Recursos/videos/Escena 03 El sol asoma en la cordillera.mp4" -t 3.292 -i "Recursos/videos/Escena 04 Cebando arranca todo Chile.mp4" -t 3.292 -i "Recursos/videos/Escena 05 Caminando por el barrio..mp4" -t 3.208 -i "Recursos/videos/Escena 06 Transición trabajohogar..mp4" -t 3.208 -i "Recursos/videos/Escena 07 Estudiantes en la universidad..mp4" -t 2.792 -i "Recursos/videos/Escena 08 Primer plano de mate y sorbo..mp4" -t 3.167 -i "Recursos/videos/Escena 09 Dónde estás tú.mp4" \
  -i "Recursos/Audios/Entre_mates_y_sol.mp3" \
  -filter_complex "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v0];[1:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v1];[2:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v2];[3:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v3];[4:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v4];[5:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v5];[6:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v6];[7:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v7];[8:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[v8];[v0][v1][v2][v3][v4][v5][v6][v7][v8]concat=n=9:v=1:a=0[vconcat]" \
  -map "[vconcat]" -map 9:a \
  -c:v libx264 -preset fast -crf 20 -r 24 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -t 29.167 \
  campaign/timeline/locos_materos_assembly_preview.mp4

echo "[SUCCESS] Video ensamblado generado: campaign/timeline/locos_materos_assembly_preview.mp4"
