"""
ADCRA v2.1 — Reactive Event Bus Infrastructure Layer
Provides in-process asynchronous and synchronous event distribution for:
- Decoupled observability
- Real-time UI synchronization via Server-Sent Events (SSE)
- Workflow and trigger automation
- Audit trails

Guarantees:
- Zero secrets in event payloads (auto-sanitized via SecretRedaction)
- Canonical schema adherence
- Thread-safe pub/sub dispatching
"""

import fnmatch
import uuid
import queue
import threading
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from adcra.ai.runtime import SecretRedaction

logger = logging.getLogger("adcra.infrastructure.events")


@dataclass
class SystemEvent:
    event_id: str
    event_type: str
    timestamp: str
    source: str
    client_id: str
    campaign_id: str
    payload: Dict[str, Any]
    run_id: Optional[str] = None
    correlation_id: str = field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:8]}")
    schema_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EventBus:
    def __init__(self, history_limit: int = 500):
        self._lock = threading.Lock()
        self._listeners: Dict[str, List[Callable[[SystemEvent], None]]] = {}
        self._subscribers: List[Tuple[str, Callable[[SystemEvent], None]]] = []
        self._history: List[SystemEvent] = []
        self._history_limit = history_limit
        self._queues: List[queue.Queue] = []

    def publish(
        self,
        event_type: str,
        source: str,
        client_id: str = "default_client",
        campaign_id: str = "default_campaign",
        payload: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> SystemEvent:
        # Strictly sanitize payload to eliminate secrets
        safe_payload = SecretRedaction.sanitize_dict(payload or {})

        event = SystemEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=source,
            client_id=client_id,
            campaign_id=campaign_id,
            payload=safe_payload,
            run_id=run_id,
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:8]}"
        )

        with self._lock:
            self._history.append(event)
            if len(self._history) > self._history_limit:
                self._history.pop(0)

            # Dispatch to pattern subscribers
            subscribers_to_notify = []
            for pattern, callback in self._subscribers:
                if fnmatch.fnmatch(event_type, pattern):
                    subscribers_to_notify.append(callback)

            # Dispatch to SSE queues
            for q in list(self._queues):
                try:
                    q.put_nowait(event)
                except queue.Full:
                    pass

        # Execute callbacks outside the lock to prevent deadlocks
        for cb in subscribers_to_notify:
            try:
                cb(event)
            except Exception as e:
                logger.warning(f"Error executing event listener for '{event_type}': {e}")

        return event

    def subscribe(self, pattern: str, callback: Callable[[SystemEvent], None]) -> None:
        with self._lock:
            self._subscribers.append((pattern, callback))
        logger.debug(f"Subscribed to event pattern: '{pattern}'")

    def unsubscribe(self, callback: Callable[[SystemEvent], None]) -> None:
        with self._lock:
            self._subscribers = [s for s in self._subscribers if s[1] != callback]

    def create_sse_queue(self, maxsize: int = 100) -> queue.Queue:
        q = queue.Queue(maxsize=maxsize)
        with self._lock:
            self._queues.append(q)
        return q

    def remove_sse_queue(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._queues:
                self._queues.remove(q)

    def get_events(
        self,
        limit: int = 50,
        event_type: Optional[str] = None,
        campaign_id: Optional[str] = None,
        client_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._lock:
            events = list(self._history)

        if event_type:
            events = [e for e in events if fnmatch.fnmatch(e.event_type, event_type)]
        if campaign_id:
            events = [e for e in events if e.campaign_id == campaign_id]
        if client_id:
            events = [e for e in events if e.client_id == client_id]
        if run_id:
            events = [e for e in events if e.run_id == run_id]

        return [e.to_dict() for e in events[-limit:]]


_GLOBAL_EVENT_BUS: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    global _GLOBAL_EVENT_BUS
    if _GLOBAL_EVENT_BUS is None:
        _GLOBAL_EVENT_BUS = EventBus()
    return _GLOBAL_EVENT_BUS
