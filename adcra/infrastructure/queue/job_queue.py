"""
ADCRA v2.1 — Job Queue Infrastructure Abstraction
Decouples job scheduling and asynchronous task dispatch from specific broker implementations.
Default implementation provides thread-safe in-memory priority queue with retry and status tracking.
"""

import time
import uuid
import queue
import threading
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import IntEnum
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("adcra.infrastructure.queue")



class JobPriority(IntEnum):
    CRITICAL = 1
    HIGH = 5
    NORMAL = 10
    LOW = 20

class JobQueue(ABC):
    @abstractmethod
    def enqueue(self, task_type: str, payload: Dict[str, Any], priority: int = 10) -> str:
        """Enqueue a job and return its job_id."""
        pass

    @abstractmethod
    def dequeue(self, timeout_seconds: float = 1.0) -> Optional[Dict[str, Any]]:
        """Retrieve next job to process or None if empty."""
        pass

    @abstractmethod
    def acknowledge(self, job_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark job as COMPLETED."""
        pass

    @abstractmethod
    def fail(self, job_id: str, error: str) -> bool:
        """Mark job as FAILED or schedule retry."""
        pass

    @abstractmethod
    def cancel(self, job_id: str) -> bool:
        """Cancel a pending or running job."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current job state."""
        pass

    @abstractmethod
    def size(self) -> int:
        return self._q.qsize()

    def list_jobs(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent jobs."""
        pass


class InMemoryJobQueue(JobQueue):
    def __init__(self):
        self._lock = threading.Lock()
        self._q = queue.PriorityQueue()
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def enqueue(self, task_type: str, payload: Dict[str, Any], priority: int = 10) -> str:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job_record = {
            "job_id": job_id,
            "task_type": task_type,
            "priority": priority,
            "payload": payload,
            "status": "QUEUED",
            "retries": 0,
            "max_retries": 3,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result": None
        }
        with self._lock:
            self._jobs[job_id] = job_record
            # PriorityQueue sorts ascending: lower number = higher priority
            self._q.put((priority, job_id))

        logger.info(f"Enqueued job '{job_id}' [{task_type}] with priority {priority}")
        return job_id

    def dequeue(self, timeout_seconds: float = 1.0) -> Optional[Dict[str, Any]]:
        try:
            _, job_id = self._q.get(timeout=timeout_seconds)
            with self._lock:
                job = self._jobs.get(job_id)
                if not job or job["status"] == "CANCELLED":
                    return None
                job["status"] = "RUNNING"
                job["started_at"] = datetime.now(timezone.utc).isoformat()
                return dict(job)
        except queue.Empty:
            return None

    def acknowledge(self, job_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            job["status"] = "COMPLETED"
            job["completed_at"] = datetime.now(timezone.utc).isoformat()
            job["result"] = result or {}
            return True

    def fail(self, job_id: str, error: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            job["retries"] += 1
            if job["retries"] < job["max_retries"]:
                job["status"] = "RETRYING"
                job["error"] = error
                # Re-enqueue with lower priority
                self._q.put((job["priority"] + 5, job_id))
            else:
                job["status"] = "FAILED"
                job["completed_at"] = datetime.now(timezone.utc).isoformat()
                job["error"] = error
            return True

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            job["status"] = "CANCELLED"
            job["completed_at"] = datetime.now(timezone.utc).isoformat()
            return True

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def size(self) -> int:
        return self._q.qsize()

    def list_jobs(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            jobs = list(self._jobs.values())
            if status:
                jobs = [j for j in jobs if j["status"] == status]
            return sorted(jobs, key=lambda j: j["created_at"], reverse=True)[:limit]


_GLOBAL_JOB_QUEUE: Optional[JobQueue] = None

def get_job_queue() -> JobQueue:
    global _GLOBAL_JOB_QUEUE
    if _GLOBAL_JOB_QUEUE is None:
        _GLOBAL_JOB_QUEUE = InMemoryJobQueue()
    return _GLOBAL_JOB_QUEUE
