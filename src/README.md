# Mergington High School Activities API

A simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister from activities
- Persist activities, students, providers, and applications in SQLite

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                      |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Stored with a stable database identifier and exposed by name:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Users and students** - A user is identified by email and linked to a student profile:
   - Name
   - Grade level

3. **Providers** - Own activity records and can be expanded with provider management features.

4. **Applications** - Link students to activities and track active or withdrawn participation.

SQLite data is stored in `src/data/activities.db` by default. Set `ACTIVITY_DB_PATH` to use a different database location. The initial activity catalog is seeded automatically when the database is empty.
