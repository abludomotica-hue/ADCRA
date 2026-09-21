"""
Unit tests for ADCRA AI Brain — Hardware Probe & Video Engine Router
"""

import unittest
from adcra.ai.hardware import (
    get_hardware_probe, VideoEngineMode, GPUInfo, HardwareEnvironmentReport
)


class TestHardwareProbe(unittest.TestCase):
    def setUp(self):
        self.probe = get_hardware_probe()

    def test_probe_gpu_returns_info(self):
        gpu = self.probe.probe_gpu()
        self.assertIsInstance(gpu, GPUInfo)
        self.assertIsInstance(gpu.detected, bool)
        self.assertIsInstance(gpu.name, str)
        self.assertIsInstance(gpu.vram_mb, int)

    def test_probe_environment(self):
        env = self.probe.probe_environment()
        self.assertIsInstance(env, HardwareEnvironmentReport)
        self.assertIn(env.selected_engine, [VideoEngineMode.DAVINCI_NATIVE, VideoEngineMode.REMOTION_FFMPEG_HYBRID, VideoEngineMode.FFMPEG_DIRECT])
        self.assertIsInstance(env.reason, str)
        self.assertIsInstance(env.ffmpeg_installed, bool)
        self.assertIsInstance(env.node_installed, bool)

    def test_execute_video_conform_returns_valid_result(self):
        result = self.probe.execute_video_conform(
            project_name="Test_Conform_Project",
            timeline_manifest={"timeline": "dummy"}
        )
        self.assertEqual(result["status"], "CONFORMED")
        self.assertIn("engine", result)
        self.assertIn("master_path", result)
        self.assertIsInstance(result["fallback_used"], bool)


if __name__ == "__main__":
    unittest.main()
