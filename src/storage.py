"""SQLite persistence for extracurricular activity data."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


INITIAL_ACTIVITIES = (
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ("michael@mergington.edu", "daniel@mergington.edu"),
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ("emma@mergington.edu", "sophia@mergington.edu"),
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ("john@mergington.edu", "olivia@mergington.edu"),
    },
    {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ("liam@mergington.edu", "noah@mergington.edu"),
    },
    {
        "name": "Basketball Team",
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ("ava@mergington.edu", "mia@mergington.edu"),
    },
    {
        "name": "Art Club",
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ("amelia@mergington.edu", "harper@mergington.edu"),
    },
    {
        "name": "Drama Club",
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ("ella@mergington.edu", "scarlett@mergington.edu"),
    },
    {
        "name": "Math Club",
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ("james@mergington.edu", "benjamin@mergington.edu"),
    },
    {
        "name": "Debate Team",
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ("charlotte@mergington.edu", "henry@mergington.edu"),
    },
)


class ActivityStore:
    """Own the database schema and persistence operations for activities."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    role TEXT NOT NULL DEFAULT 'student'
                );
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
                    name TEXT,
                    grade TEXT
                );
                CREATE TABLE IF NOT EXISTS parents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
                    name TEXT
                );
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE
                );
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    max_participants INTEGER NOT NULL,
                    provider_id INTEGER REFERENCES providers(id)
                );
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL REFERENCES activities(id),
                    student_id INTEGER NOT NULL REFERENCES students(id),
                    status TEXT NOT NULL DEFAULT 'accepted',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(activity_id, student_id)
                );
                """
            )
            activity_count = connection.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
            if activity_count == 0:
                self._seed(connection)

    def _seed(self, connection: sqlite3.Connection) -> None:
        provider_id = connection.execute(
            "INSERT INTO providers (name) VALUES (?) RETURNING id",
            ("Mergington High School",),
        ).fetchone()[0]
        for activity in INITIAL_ACTIVITIES:
            activity_id = connection.execute(
                """
                INSERT INTO activities
                    (name, description, schedule, max_participants, provider_id)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
                """,
                (
                    activity["name"],
                    activity["description"],
                    activity["schedule"],
                    activity["max_participants"],
                    provider_id,
                ),
            ).fetchone()[0]
            for email in activity["participants"]:
                student_id = self._ensure_student(connection, email)
                connection.execute(
                    "INSERT INTO applications (activity_id, student_id) VALUES (?, ?)",
                    (activity_id, student_id),
                )

    @staticmethod
    def _ensure_student(connection: sqlite3.Connection, email: str) -> int:
        connection.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
        user_id = connection.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()[0]
        connection.execute(
            "INSERT OR IGNORE INTO students (user_id) VALUES (?)", (user_id,)
        )
        return connection.execute(
            "SELECT id FROM students WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

    def list_activities(self) -> dict[str, dict[str, Any]]:
        with self._connect() as connection:
            activity_rows = connection.execute(
                "SELECT name, description, schedule, max_participants, id FROM activities ORDER BY id"
            ).fetchall()
            result = {}
            for activity in activity_rows:
                participants = connection.execute(
                    """
                    SELECT users.email
                    FROM applications
                    JOIN students ON students.id = applications.student_id
                    JOIN users ON users.id = students.user_id
                    WHERE applications.activity_id = ? AND applications.status = 'accepted'
                    ORDER BY applications.id
                    """,
                    (activity["id"],),
                ).fetchall()
                result[activity["name"]] = {
                    "description": activity["description"],
                    "schedule": activity["schedule"],
                    "max_participants": activity["max_participants"],
                    "participants": [row["email"] for row in participants],
                }
            return result

    def signup(self, activity_name: str, email: str) -> None:
        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            if activity is None:
                raise KeyError("Activity not found")
            student_id = self._ensure_student(connection, email)
            existing = connection.execute(
                """
                SELECT id, status FROM applications
                WHERE activity_id = ? AND student_id = ?
                """,
                (activity["id"], student_id),
            ).fetchone()
            if existing is not None and existing["status"] == "accepted":
                raise ValueError("Student is already signed up")
            if existing is not None:
                connection.execute(
                    "UPDATE applications SET status = 'accepted' WHERE id = ?",
                    (existing["id"],),
                )
            else:
                connection.execute(
                    "INSERT INTO applications (activity_id, student_id) VALUES (?, ?)",
                    (activity["id"], student_id),
                )

    def unregister(self, activity_name: str, email: str) -> None:
        with self._connect() as connection:
            activity = connection.execute(
                "SELECT id FROM activities WHERE name = ?", (activity_name,)
            ).fetchone()
            if activity is None:
                raise KeyError("Activity not found")
            application = connection.execute(
                """
                SELECT applications.id
                FROM applications
                JOIN students ON students.id = applications.student_id
                JOIN users ON users.id = students.user_id
                WHERE applications.activity_id = ? AND users.email = ?
                    AND applications.status = 'accepted'
                """,
                (activity["id"], email),
            ).fetchone()
            if application is None:
                raise KeyError("Student is not signed up for this activity")
            connection.execute(
                "UPDATE applications SET status = 'withdrawn' WHERE id = ?",
                (application["id"],),
            )