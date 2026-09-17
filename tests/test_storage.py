import tempfile
import unittest
from pathlib import Path

from src.storage import ActivityStore


class ActivityStoreTests(unittest.TestCase):
    def test_activity_and_signup_data_survive_a_new_store_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "activities.db"
            first_store = ActivityStore(database_path)
            first_store.signup("Chess Club", "new.student@mergington.edu")

            second_store = ActivityStore(database_path)
            chess_club = second_store.list_activities()["Chess Club"]

            self.assertIn("new.student@mergington.edu", chess_club["participants"])
            self.assertEqual(chess_club["max_participants"], 12)

    def test_unregistration_is_persisted_as_an_inactive_application(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "activities.db"
            first_store = ActivityStore(database_path)
            first_store.unregister("Chess Club", "michael@mergington.edu")

            second_store = ActivityStore(database_path)

            self.assertNotIn(
                "michael@mergington.edu",
                second_store.list_activities()["Chess Club"]["participants"],
            )


if __name__ == "__main__":
    unittest.main()