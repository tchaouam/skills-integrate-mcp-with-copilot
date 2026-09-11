import unittest

from fastapi.testclient import TestClient

from app import app, activities


class ApprovalWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        activities.clear()
        activities.update({
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu"],
                "approved": True,
                "status": "approved",
                "reason": "",
            },
            "Science Fair Prep": {
                "description": "Prepare a science fair project",
                "schedule": "Mondays, 3:30 PM - 4:30 PM",
                "max_participants": 10,
                "participants": [],
                "approved": False,
                "status": "pending",
                "reason": "",
            },
        })

    def test_pending_activities_are_hidden_from_students(self):
        response = self.client.get("/activities")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("Chess Club", payload)
        self.assertNotIn("Science Fair Prep", payload)

    def test_admin_can_approve_pending_activity(self):
        response = self.client.post("/admin/activities/Science Fair Prep/approve")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(activities["Science Fair Prep"]["status"], "approved")
        self.assertTrue(activities["Science Fair Prep"]["approved"])

    def test_admin_can_reject_pending_activity_with_reason(self):
        response = self.client.post(
            "/admin/activities/Science Fair Prep/reject",
            json={"reason": "Needs more staffing"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(activities["Science Fair Prep"]["status"], "rejected")
        self.assertEqual(activities["Science Fair Prep"]["reason"], "Needs more staffing")


if __name__ == "__main__":
    unittest.main()
