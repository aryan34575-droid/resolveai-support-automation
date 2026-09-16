import json
import unittest

from resolveai.pipeline import ResolveAI, process_json


class ResolveAITests(unittest.TestCase):
    def setUp(self):
        self.engine = ResolveAI()
        self.ticket = {"ticket_id": "T-1", "customer_message": "I was charged twice for my invoice.", "created_at": "2026-01-01T00:00:00Z", "product": "Demo", "channel": "email"}

    def test_complete_workflow_and_safe_default(self):
        result = self.engine.process(self.ticket)
        self.assertEqual(result.status, "awaiting_approval")
        self.assertEqual(result.analysis.category, "billing")
        self.assertEqual(result.analysis.priority, "high")
        self.assertTrue(result.approval_required)
        self.assertFalse(result.update["safe_to_send"])
        self.assertTrue(result.knowledge_articles)

    def test_approval_does_not_bypass_risk(self):
        ticket = dict(self.ticket, customer_message="There is an unauthorized security breach.")
        result = self.engine.process(ticket, approved=True)
        self.assertNotEqual(result.status, "approved")
        self.assertFalse(result.update["safe_to_send"])

    def test_errors(self):
        self.assertEqual(process_json("{bad")["status"], "invalid")
        self.assertEqual(self.engine.process({"ticket_id": "x"}).status, "invalid")
        self.assertEqual(self.engine.process(dict(self.ticket, customer_message=" ")).status, "invalid")


if __name__ == "__main__":
    unittest.main()
