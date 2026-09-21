# ADCRA AI Brain — Verbal Economy & Readability Enforcement Engine
# Ensures on-screen and voiceover text respects the cognitive pacing of modern digital video,
# particularly for vertical 9:16 reels/TikTok where viewer drop-off is immediate.
# Calculates reading rate (words/second, WPM), hook density (first 3s), and flags copy overload (>2.8 wps).

import re
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict


class VerbalEconomyStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    ACCEPTABLE = "ACCEPTABLE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class SceneCopyMetric:
    scene_id: str
    copy: str
    word_count: int
    char_count: int
    duration_sec: float
    wps: float
    wpm: float
    status: VerbalEconomyStatus
    flag: Optional[str]
    is_hook: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


class VerbalEconomyEngine:
    MAX_VERTICAL_WPS = 2.8
    MAX_HORIZONTAL_WPS = 3.2
    MAX_HOOK_WORDS = 8
    TARGET_WPS_RANGE = (1.4, 2.4)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text.strip())

    def count_words(self, text: str) -> int:
        cleaned = self.clean_text(text)
        if not cleaned:
            return 0
        words = re.findall(r"\b[\w\u00C0-\u017F]+\b", cleaned)
        return len(words)

    def evaluate_rate(self, wps: float, is_hook: bool = False, aspect_ratio: str = "9:16") -> VerbalEconomyStatus:
        max_allowed = self.MAX_VERTICAL_WPS if aspect_ratio == "9:16" else self.MAX_HORIZONTAL_WPS
        if wps <= 2.2:
            return VerbalEconomyStatus.OPTIMAL
        elif wps <= max_allowed:
            return VerbalEconomyStatus.ACCEPTABLE
        elif wps <= max_allowed + 0.6:
            return VerbalEconomyStatus.WARNING
        else:
            return VerbalEconomyStatus.CRITICAL

    def analyze_scene(
        self,
        scene_id: str,
        copy_text: str,
        duration_sec: float,
        is_hook: bool = False,
        aspect_ratio: str = "9:16"
    ) -> SceneCopyMetric:
        duration = max(0.5, float(duration_sec or 3.0))
        words = self.count_words(copy_text)
        chars = len(copy_text or "")
        wps = round(words / duration, 2)
        wpm = round(wps * 60, 1)

        status = self.evaluate_rate(wps, is_hook=is_hook, aspect_ratio=aspect_ratio)
        flag = None

        if is_hook and words > self.MAX_HOOK_WORDS:
            flag = f"HOOK_DENSITY_HIGH ({words} words > {self.MAX_HOOK_WORDS} max recommended for first 3s)"
            if status == VerbalEconomyStatus.OPTIMAL:
                status = VerbalEconomyStatus.ACCEPTABLE
        elif wps > self.MAX_VERTICAL_WPS and aspect_ratio == "9:16":
            flag = f"EXCEEDS_VERTICAL_RATE ({wps} wps > {self.MAX_VERTICAL_WPS} max)"
        elif wps > self.MAX_HORIZONTAL_WPS:
            flag = f"EXCEEDS_READING_RATE ({wps} wps > {self.MAX_HORIZONTAL_WPS} max)"

        return SceneCopyMetric(
            scene_id=scene_id,
            copy=copy_text or "",
            word_count=words,
            char_count=chars,
            duration_sec=duration,
            wps=wps,
            wpm=wpm,
            status=status,
            flag=flag,
            is_hook=is_hook
        )

    def analyze_campaign(
        self,
        scenes: List[Dict[str, Any]],
        aspect_ratio: str = "9:16",
        campaign_id: str = "default"
    ) -> Dict[str, Any]:
        metrics: List[SceneCopyMetric] = []
        total_words = 0
        total_duration = 0.0
        flags: List[str] = []

        for idx, sc in enumerate(scenes):
            scene_id = sc.get("scene_id", f"scene_{idx+1:02d}")
            copy_text = sc.get("copy", "")
            duration = float(sc.get("duration", sc.get("duration_seconds", 3.0)) or 3.0)
            is_hook = (idx == 0) or (sc.get("start", 0.0) < 3.0)

            metric = self.analyze_scene(
                scene_id=scene_id,
                copy_text=copy_text,
                duration_sec=duration,
                is_hook=is_hook,
                aspect_ratio=aspect_ratio
            )
            metrics.append(metric)
            total_words += metric.word_count
            total_duration += metric.duration_sec
            if metric.flag:
                flags.append(f"[{scene_id}] {metric.flag}")

        overall_wps = round(total_words / max(1.0, total_duration), 2)
        overall_wpm = round(overall_wps * 60, 1)

        hook_metric = metrics[0] if metrics else None
        hook_data = hook_metric.to_dict() if hook_metric else {}

        has_critical = any(m.status == VerbalEconomyStatus.CRITICAL for m in metrics)
        has_warning = any(m.status == VerbalEconomyStatus.WARNING for m in metrics) or overall_wps > self.MAX_VERTICAL_WPS

        if has_critical:
            overall_status = VerbalEconomyStatus.CRITICAL
        elif has_warning:
            overall_status = VerbalEconomyStatus.WARNING
        elif any(m.status == VerbalEconomyStatus.ACCEPTABLE for m in metrics):
            overall_status = VerbalEconomyStatus.ACCEPTABLE
        else:
            overall_status = VerbalEconomyStatus.OPTIMAL

        recommendations = []
        if overall_wps > self.MAX_VERTICAL_WPS:
            recommendations.append(
                f"Reducir densidad global de texto: {overall_wps} palabras/seg supera el límite recomendado de {self.MAX_VERTICAL_WPS} para video vertical."
            )
        if hook_metric and hook_metric.word_count > self.MAX_HOOK_WORDS:
            recommendations.append(
                f"Hook inicial sobrecargado ({hook_metric.word_count} palabras). Se aconseja condensar a máximo {self.MAX_HOOK_WORDS} palabras para retención en los primeros 3s."
            )
        for m in metrics:
            if m.status in (VerbalEconomyStatus.WARNING, VerbalEconomyStatus.CRITICAL):
                rec_dur = round(m.word_count / 2.2, 1)
                recommendations.append(
                    f"Escena {m.scene_id}: Considerar podar {m.copy} o alargar duración en timeline de {m.duration_sec}s a {rec_dur}s."
                )

        if not recommendations:
            recommendations.append("Ritmo y economía verbal óptimos. La cadencia permite lectura fluida sincronizada con la música.")

        return {
            "campaign_id": campaign_id,
            "status": overall_status.value,
            "aspect_ratio": aspect_ratio,
            "overall_wps": overall_wps,
            "overall_wpm": overall_wpm,
            "total_words": total_words,
            "total_duration_sec": round(total_duration, 2),
            "scenes_count": len(scenes),
            "hook_metric": hook_data,
            "scenes_analysis": [m.to_dict() for m in metrics],
            "flags": flags,
            "recommendations": recommendations,
            "passed_qc": overall_status in (VerbalEconomyStatus.OPTIMAL, VerbalEconomyStatus.ACCEPTABLE)
        }


_GLOBAL_VERBAL_ENGINE = VerbalEconomyEngine()

def get_verbal_economy_engine() -> VerbalEconomyEngine:
    return _GLOBAL_VERBAL_ENGINE
