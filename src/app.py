"""High School Management System API."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from storage import ActivityStore

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

database_path = os.getenv("ACTIVITY_DB_PATH", str(current_dir / "data" / "activities.db"))
activity_store = ActivityStore(database_path)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activity_store.list_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        activity_store.signup(activity_name, email)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        activity_store.unregister(activity_name, email)
    except KeyError as error:
        message = str(error)
        status_code = 404 if message == "Activity not found" else 400
        raise HTTPException(status_code=status_code, detail=message) from error
    return {"message": f"Unregistered {email} from {activity_name}"}
