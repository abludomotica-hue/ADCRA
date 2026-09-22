import unittest
from adcra.infrastructure.events.event_bus import EventBus, SystemEvent


class TestEventBus(unittest.TestCase):
    """
    ADCRA v2.1 Event Bus Specification Tests.
    Tests publish/subscribe, wildcard matching, history retention, secret sanitization, and SSE queue distribution.
    """

    def setUp(self):
        self.bus = EventBus(history_limit=10)

    def test_publish_and_subscribe_exact_match(self):
        """Verify exact event type subscriber receives published events."""
        received = []
        self.bus.subscribe("campaign.created", lambda e: received.append(e))

        evt = self.bus.publish(
            event_type="campaign.created",
            source="CampaignService",
            campaign_id="camp_99",
            payload={"name": "Summer Launch"}
        )

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].event_id, evt.event_id)
        self.assertEqual(received[0].payload["name"], "Summer Launch")

    def test_wildcard_topic_subscription(self):
        """Verify wildcard patterns (e.g. 'run.*') match all relevant child event types."""
        run_events = []
        self.bus.subscribe("run.*", lambda e: run_events.append(e))

        self.bus.publish("run.started", source="Executor")
        self.bus.publish("run.checkpoint", source="Executor")
        self.bus.publish("run.completed", source="Executor")
        self.bus.publish("campaign.updated", source="CampaignService")  # Should not match

        self.assertEqual(len(run_events), 3)
        types = [e.event_type for e in run_events]
        self.assertEqual(types, ["run.started", "run.checkpoint", "run.completed"])

    def test_history_limit_and_filtering(self):
        """Verify event history buffer respects limit and filters by campaign/type."""
        for i in range(15):
            self.bus.publish(
                event_type="item.added" if i % 2 == 0 else "item.removed",
                source="Inventory",
                campaign_id="camp_a" if i < 10 else "camp_b",
                payload={"index": i}
            )

        # Bus limit is 10
        all_events = self.bus.get_events(limit=50)
        self.assertEqual(len(all_events), 10)

        # Filter by campaign
        camp_b_events = self.bus.get_events(campaign_id="camp_b")
        self.assertEqual(len(camp_b_events), 5)

        # Filter by type
        removed_events = self.bus.get_events(event_type="item.removed")
        self.assertTrue(all(e["event_type"] == "item.removed" for e in removed_events))

    def test_secret_sanitization_in_event_payloads(self):
        """Verify API keys and sensitive tokens are automatically redacted upon publish."""
        captured = []
        self.bus.subscribe("security.audit", lambda e: captured.append(e))

        self.bus.publish(
            event_type="security.audit",
            source="SecurityService",
            payload={
                "openai_key": "sk-1234567890abcdef1234567890abcdef",
                "api_key": "secret_api_key_val",
                "normal_field": "public_data"
            }
        )

        self.assertEqual(len(captured), 1)
        p = captured[0].payload
        self.assertEqual(p["api_key"], "[REDACTED]")
        self.assertEqual(p["normal_field"], "public_data")

    def test_sse_queue_streaming(self):
        """Verify real-time SSE queues receive broadcast events."""
        sse_q = self.bus.create_sse_queue(maxsize=10)

        self.bus.publish("sse.test", source="Test", payload={"msg": "hello sse"})

        self.assertFalse(sse_q.empty())
        item = sse_q.get_nowait()
        self.assertEqual(item.event_type, "sse.test")
        self.assertEqual(item.payload["msg"], "hello sse")

        self.bus.remove_sse_queue(sse_q)


if __name__ == "__main__":
    unittest.main()
