import os
import shutil
import tempfile
import unittest
from pathlib import Path

from adcra.domain.execution.durable_run import (
    DurableRun,
    RunStatus,
    RunCheckpoint
)
from adcra.infrastructure.persistence.run_repository import RunRepository
from adcra.infrastructure.queue.job_queue import InMemoryJobQueue, JobPriority


class TestDurableExecution(unittest.TestCase):
    """
    ADCRA v2.1 Durable Execution & Execution Plane Tests.
    Tests job queuing, priority scheduling, step checkpointing, failure resumption, and cancellation.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.run_repo = RunRepository(base_dir=Path(self.temp_dir) / "runs")
        self.queue = InMemoryJobQueue()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_lifecycle_and_persistence(self):
        """Test creating, saving, updating, and retrieving a DurableRun."""
        run = DurableRun(
            run_id="run_test_001",
            campaign_id="camp_test_001",
            client_id="client_test_001",
            intent_id="intent_001",
            task_type="campaign_production_pipeline",
            total_steps=5
        )
        self.assertEqual(run.status, RunStatus.QUEUED)
        self.assertEqual(len(run.checkpoints), 0)

        # Save to repository
        self.run_repo.save(run)

        # Retrieve and verify
        loaded = self.run_repo.get(run.run_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.campaign_id, "camp_test_001")
        self.assertEqual(loaded.client_id, "client_test_001")
        self.assertEqual(loaded.status, RunStatus.QUEUED)

    def test_checkpointing_and_step_progress(self):
        """Test step checkpoint creation and state preservation."""
        run = DurableRun(
            run_id="run_test_002",
            campaign_id="camp_test_002",
            client_id="client_test_002",
            intent_id="intent_002",
            task_type="ai_ideation_run",
            total_steps=3
        )
        run.start()
        self.assertEqual(run.status, RunStatus.RUNNING)

        # Record step 1 checkpoint
        run.record_checkpoint(
            step_id="step_1",
            step_name="brand_intake_validation",
            output_key="brand_data",
            data={"brand_name": "Test Yerba", "valid": True}
        )
        self.assertEqual(len(run.checkpoints), 1)
        self.assertEqual(run.current_step_index, 1)

        # Record step 2 checkpoint
        run.record_checkpoint(
            step_id="step_2",
            step_name="creative_copy_generation",
            output_key="copy_variants",
            data={"headlines": ["Headline A", "Headline B"]}
        )
        self.assertEqual(len(run.checkpoints), 2)
        self.assertEqual(run.current_step_index, 2)

        self.run_repo.save(run)
        reloaded = self.run_repo.get(run.run_id)
        self.assertEqual(len(reloaded.checkpoints), 2)
        self.assertEqual(reloaded.checkpoints["step_1"]["step_name"], "brand_intake_validation")
        self.assertEqual(reloaded.checkpoints["step_2"]["step_name"], "creative_copy_generation")

    def test_run_failure_and_resumption(self):
        """Test that a failed run can resume from its last completed checkpoint."""
        run = DurableRun(
            run_id="run_test_003",
            campaign_id="camp_test_003",
            client_id="client_test_003",
            intent_id="intent_003",
            task_type="pipeline_resumption_test",
            total_steps=4
        )
        run.start()

        # Step 1 succeeded
        run.record_checkpoint(
            step_id="step_1",
            step_name="step_one",
            output_key="res1",
            data={"result": "step1_ok"}
        )

        # Step 2 failed
        run.fail(error="Simulated network failure during step 2")
        self.assertEqual(run.status, RunStatus.FAILED)
        self.assertEqual(run.error, "Simulated network failure during step 2")

        # Resume run
        self.assertTrue(run.can_resume())
        resumed = run.resume()
        self.assertTrue(resumed)
        self.assertEqual(run.status, RunStatus.RUNNING)
        self.assertIsNone(run.error)
        self.assertEqual(run.current_step_index, 1)  # Preserved step 1 progress

    def test_run_cancellation(self):
        """Test that an active run can be cancelled cleanly."""
        run = DurableRun(
            run_id="run_test_004",
            campaign_id="camp_test_004",
            client_id="client_test_004",
            intent_id="intent_004",
            task_type="cancellation_test",
            total_steps=2
        )
        run.start()
        run.cancel()
        self.assertEqual(run.status, RunStatus.CANCELLED)
        self.assertFalse(run.can_resume())

    def test_job_queue_priority_dispatch(self):
        """Test job enqueueing with priority ordering."""
        # Enqueue NORMAL then HIGH then CRITICAL
        j1 = self.queue.enqueue(task_type="task_normal", payload={"p": 1}, priority=JobPriority.NORMAL)
        j2 = self.queue.enqueue(task_type="task_high", payload={"p": 2}, priority=JobPriority.HIGH)
        j3 = self.queue.enqueue(task_type="task_critical", payload={"p": 3}, priority=JobPriority.CRITICAL)

        self.assertEqual(self.queue.size(), 3)

        # Dequeue must return CRITICAL first, then HIGH, then NORMAL
        d1 = self.queue.dequeue()
        self.assertEqual(d1["job_id"], j3)
        d2 = self.queue.dequeue()
        self.assertEqual(d2["job_id"], j2)
        d3 = self.queue.dequeue()
        self.assertEqual(d3["job_id"], j1)
        self.assertEqual(self.queue.size(), 0)


if __name__ == "__main__":
    unittest.main()
