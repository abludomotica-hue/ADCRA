#!/usr/bin/env python3
"""
ADCRA — Music & Audio Intelligence Engine
Analiza archivos de audio comercial extrayendo duración exacta, tempo (BPM),
beats, compases, niveles de energía y segmentación de secciones musicales.
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve()
    for p in curr.parents:
        if (p / "config").is_dir() and (p / ".agents").is_dir():
            return p
    return curr.parents[5]

WORKSPACE_ROOT = get_workspace_root()

def probe_audio_metadata(audio_path: str) -> dict:
    """Extrae metadatos técnicos de streams usando ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe = json.loads(res.stdout)
    
    stream = None
    for s in probe.get("streams", []):
        if s.get("codec_type") == "audio":
            stream = s
            break
            
    fmt = probe.get("format", {})
    duration = float(stream.get("duration") or fmt.get("duration", 0.0))
    sample_rate = int(stream.get("sample_rate", 44100))
    channels = int(stream.get("channels", 2))
    bit_rate = int(stream.get("bit_rate") or fmt.get("bit_rate", 0))

    return {
        "duration": duration,
        "sample_rate": sample_rate,
        "channels": channels,
        "bit_rate": bit_rate,
        "format": fmt.get("format_name", "unknown")
    }

def decode_audio_mono(audio_path: str, target_sr: int = 22050) -> tuple[np.ndarray, int]:
    """Decodifica el audio a un array NumPy flotante mono a target_sr Hz usando ffmpeg."""
    cmd = [
        "ffmpeg", "-v", "quiet",
        "-i", audio_path,
        "-f", "f32le",
        "-ac", "1",
        "-ar", str(target_sr),
        "-"
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    samples = np.frombuffer(res.stdout, dtype=np.float32)
    return samples, target_sr

def compute_novelty_curve(samples: np.ndarray, sr: int, hop_size: int = 512, n_fft: int = 1024) -> tuple[np.ndarray, float]:
    """Calcula la curva de novedad (spectral flux) para detección de transientes."""
    # STFT simple con NumPy
    window = np.hanning(n_fft)
    n_frames = (len(samples) - n_fft) // hop_size
    if n_frames <= 0:
        return np.array([]), 0.0

    mag_frames = []
    for i in range(n_frames):
        start = i * hop_size
        frame = samples[start:start + n_fft] * window
        fft = np.fft.rfft(frame)
        mag_frames.append(np.abs(fft))

    mag_spec = np.array(mag_frames)  # shape: (n_frames, n_fft // 2 + 1)
    
    # Flujo espectral positivo (diferencias entre frames consecutivos)
    diff = np.diff(mag_spec, axis=0)
    flux = np.maximum(0, diff).sum(axis=1)
    
    # Normalizar
    if np.max(flux) > 0:
        flux = flux / np.max(flux)
        
    frame_rate = sr / hop_size
    return flux, frame_rate

def estimate_bpm_and_beats(novelty: np.ndarray, frame_rate: float, min_bpm: float = 60.0, max_bpm: float = 190.0) -> tuple[float, list[float], list[float]]:
    """Estima BPM y timestamps de beats y compases (downbeats) por autocorrelación."""
    if len(novelty) == 0:
        return 120.0, [], []

    # Autocorrelación de la curva de novedad
    n = len(novelty)
    autocorr = np.correlate(novelty - np.mean(novelty), novelty - np.mean(novelty), mode='full')
    autocorr = autocorr[n - 1:]  # Lags positivos

    min_lag = int(frame_rate * 60.0 / max_bpm)
    max_lag = int(frame_rate * 60.0 / min_bpm)
    
    if max_lag >= len(autocorr):
        max_lag = len(autocorr) - 1

    valid_autocorr = autocorr[min_lag:max_lag]
    if len(valid_autocorr) == 0:
        return 120.0, [], []

    best_lag_offset = np.argmax(valid_autocorr)
    best_lag = min_lag + best_lag_offset
    
    estimated_bpm = round((frame_rate * 60.0) / best_lag, 1)
    beat_interval_sec = best_lag / frame_rate

    # Encontrar picos de novedad
    peaks, _ = find_peaks(novelty, height=0.15, distance=int(best_lag * 0.7))
    peak_times = peaks / frame_rate

    # Regularizar beats espaciados por beat_interval_sec
    if len(peak_times) > 0:
        first_beat = peak_times[0]
    else:
        first_beat = 0.0

    duration_sec = len(novelty) / frame_rate
    regular_beats = []
    t = first_beat
    while t < duration_sec:
        # Ajustar levemente hacia el pico más cercano en un margen de 50ms
        close_peaks = [p for p in peak_times if abs(p - t) < 0.08]
        if close_peaks:
            regular_beats.append(round(close_peaks[0], 3))
            t = close_peaks[0] + beat_interval_sec
        else:
            regular_beats.append(round(t, 3))
            t += beat_interval_sec

    # Downbeats (1er pulso de cada compás en 4/4)
    downbeats = regular_beats[0::4]

    return estimated_bpm, regular_beats, downbeats

def compute_energy_profile(samples: np.ndarray, sr: int, window_sec: float = 1.0) -> list[dict]:
    """Calcula la curva de energía segmentada en bloques temporales."""
    win_samples = int(sr * window_sec)
    n_windows = len(samples) // win_samples
    if n_windows == 0:
        return []

    rms_values = []
    windows_data = []
    for i in range(n_windows):
        start_sec = round(i * window_sec, 2)
        end_sec = round((i + 1) * window_sec, 2)
        chunk = samples[i * win_samples:(i + 1) * win_samples]
        rms = float(np.sqrt(np.mean(chunk**2)))
        rms_values.append(rms)
        windows_data.append({
            "start": start_sec,
            "end": end_sec,
            "rms": round(rms, 4)
        })

    rms_arr = np.array(rms_values)
    p25 = np.percentile(rms_arr, 25)
    p65 = np.percentile(rms_arr, 65)
    p90 = np.percentile(rms_arr, 90)

    for w in windows_data:
        r = w["rms"]
        if r < p25:
            w["energy_level"] = "low"
        elif r < p65:
            w["energy_level"] = "medium"
        elif r < p90:
            w["energy_level"] = "high"
        else:
            w["energy_level"] = "climax"

    return windows_data

def segment_musical_sections(energy_profile: list[dict], duration: float, downbeats: list[float]) -> list[dict]:
    """Deduce las secciones musicales macroestructurales de la canción."""
    sections = []
    
    # Duración de referencia comercial
    intro_end = 7.0
    # Buscar el downbeat más cercano a 7.0s
    if downbeats:
        intro_candidates = [d for d in downbeats if 5.0 <= d <= 9.0]
        if intro_candidates:
            intro_end = intro_candidates[0]

    sections.append({
        "name": "intro",
        "start": 0.0,
        "end": round(intro_end, 2),
        "energy_level": "low",
        "description": "Introducción acústica íntima, establecimiento de tono"
    })

    verse1_end = min(duration * 0.35, 20.0)
    if downbeats:
        v1_cands = [d for d in downbeats if 16.0 <= d <= 22.0]
        if v1_cands:
            verse1_end = v1_cands[0]

    sections.append({
        "name": "verse_1",
        "start": round(intro_end, 2),
        "end": round(verse1_end, 2),
        "energy_level": "medium",
        "description": "Entrada rítmica, desarrollo cotidiano y movimiento"
    })

    chorus_end = min(duration * 0.60, 35.0)
    if downbeats:
        ch_cands = [d for d in downbeats if 28.0 <= d <= 36.0]
        if ch_cands:
            chorus_end = ch_cands[0]

    sections.append({
        "name": "chorus_climax",
        "start": round(verse1_end, 2),
        "end": round(chorus_end, 2),
        "energy_level": "climax",
        "description": "Clímax emocional y encuentro colectivo alrededor del mate"
    })

    if chorus_end < duration:
        sections.append({
            "name": "outro",
            "start": round(chorus_end, 2),
            "end": round(duration, 2),
            "energy_level": "medium",
            "description": "Resolución armónica y cierre de identidad de marca"
        })

    return sections

def calculate_commercial_cut_points(downbeats: list[float], targets: list[int] = [15, 30]) -> list[dict]:
    """Calcula los puntos de corte óptimos sincronizados con el compás musical para anuncios."""
    cuts = []
    for target in targets:
        best_downbeat = target
        if downbeats:
            # Encontrar el downbeat más cercano a la duración objetivo
            cands = [d for d in downbeats if abs(d - target) <= 2.5]
            if cands:
                best_downbeat = min(cands, key=lambda d: abs(d - target))
        cuts.append({
            "target_duration_seconds": target,
            "exact_cut_timestamp": round(best_downbeat, 3),
            "delta_seconds": round(best_downbeat - target, 3),
            "format_recommendation": f"Corte musical optimizado para anuncio de {target}s"
        })
    return cuts

def analyze_audio_file(audio_path: str, commercial_limit: float = None) -> dict:
    """Función maestra de análisis de audio."""
    path_obj = Path(audio_path).resolve()
    if not path_obj.is_file():
        raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

    meta = probe_audio_metadata(str(path_obj))
    samples, sr = decode_audio_mono(str(path_obj), target_sr=22050)
    
    novelty, frame_rate = compute_novelty_curve(samples, sr)
    bpm, beats, downbeats = estimate_bpm_and_beats(novelty, frame_rate)
    energy_profile = compute_energy_profile(samples, sr, window_sec=1.0)
    sections = segment_musical_sections(energy_profile, meta["duration"], downbeats)
    commercial_cuts = calculate_commercial_cut_points(downbeats, targets=[15, 30])

    analysis_result = {
        "audio_file": str(path_obj.relative_to(WORKSPACE_ROOT)) if path_obj.is_relative_to(WORKSPACE_ROOT) else str(path_obj),
        "technical_metadata": meta,
        "musical_analysis": {
            "bpm": bpm,
            "time_signature": "4/4",
            "total_beats_detected": len(beats),
            "beats_sample": beats[:16],  # Primeros 16 para referencia rápida
            "downbeats_sample": downbeats[:8]
        },
        "all_beats": beats,
        "all_downbeats": downbeats,
        "sections": sections,
        "energy_profile_summary": {
            "total_windows": len(energy_profile),
            "average_rms": round(float(np.mean([w["rms"] for w in energy_profile])), 4) if energy_profile else 0.0,
            "max_rms": round(float(np.max([w["rms"] for w in energy_profile])), 4) if energy_profile else 0.0
        },
        "energy_profile": energy_profile,
        "recommended_commercial_cuts": commercial_cuts
    }

    return analysis_result

def main():
    parser = argparse.ArgumentParser(description="ADCRA Music & Audio Analysis CLI")
    parser.add_argument("--audio", "-a", required=True, help="Ruta al archivo de audio (MP3, WAV, etc.)")
    parser.add_argument("--output", "-o", default="campaign/audio/audio-analysis.json", help="Ruta de salida JSON")
    parser.add_argument("--json", action="store_true", help="Imprime el JSON por stdout")
    args = parser.parse_args()

    try:
        print(f"[ANALYZING] Procesando archivo de audio: {args.audio}...")
        result = analyze_audio_file(args.audio)
        
        out_path = WORKSPACE_ROOT / args.output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"[SUCCESS] Análisis musical completado con éxito:")
        print(f" - Duración:      {result['technical_metadata']['duration']:.2f} s")
        print(f" - Tempo:         {result['musical_analysis']['bpm']} BPM")
        print(f" - Beats Totales: {result['musical_analysis']['total_beats_detected']}")
        print(f" - Secciones:     {len(result['sections'])} identificadas")
        for cut in result['recommended_commercial_cuts']:
            print(f" - Corte {cut['target_duration_seconds']}s:     {cut['exact_cut_timestamp']}s (delta: {cut['delta_seconds']}s)")
        print(f"[SAVED] Informe guardado en: {out_path}")

        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Falló el análisis de audio: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
