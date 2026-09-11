"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


def normalize_activity(activity):
    """Ensure legacy activities include approval metadata."""
    activity.setdefault("approved", True)
    activity.setdefault("status", "approved" if activity["approved"] else "pending")
    activity.setdefault("reason", "")
    if activity["status"] == "approved":
        activity["approved"] = True
    if activity["status"] in {"pending", "rejected"}:
        activity["approved"] = False
    return activity


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "approved": True,
        "status": "approved",
        "reason": "",
    },
}

for activity in activities.values():
    normalize_activity(activity)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return {
        name: activity
        for name, activity in activities.items()
        if activity.get("status") == "approved"
    }


def get_activity_or_404(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity = activities[activity_name]
    normalize_activity(activity)
    if activity.get("status") != "approved":
        raise HTTPException(status_code=403, detail="Activity is not approved yet")
    return activity


@app.post("/admin/activities")
def create_activity(payload: dict):
    """Create a new activity in pending review."""
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Activity name is required")
    if name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    activity = {
        "description": payload.get("description", ""),
        "schedule": payload.get("schedule", ""),
        "max_participants": int(payload.get("max_participants", 0)),
        "participants": [],
        "approved": False,
        "status": "pending",
        "reason": "",
    }
    activities[name] = activity
    return {"message": f"Submitted {name} for approval", "activity": activity}


@app.get("/admin/activities")
def get_admin_activities():
    return {
        "pending": {
            name: activity
            for name, activity in activities.items()
            if activity.get("status") == "pending"
        },
        "rejected": {
            name: activity
            for name, activity in activities.items()
            if activity.get("status") == "rejected"
        },
        "approved": {
            name: activity
            for name, activity in activities.items()
            if activity.get("status") == "approved"
        },
    }


@app.post("/admin/activities/{activity_name}/approve")
def approve_activity(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    activity["approved"] = True
    activity["status"] = "approved"
    activity["reason"] = ""
    return {"message": f"Approved {activity_name}", "activity": activity}


@app.post("/admin/activities/{activity_name}/reject")
async def reject_activity(activity_name: str, request: Request):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    payload = await request.json()
    reason = payload.get("reason", "") if isinstance(payload, dict) else ""

    activity = activities[activity_name]
    activity["approved"] = False
    activity["status"] = "rejected"
    activity["reason"] = reason
    return {"message": f"Rejected {activity_name}", "activity": activity}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activity = get_activity_or_404(activity_name)

    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activity = get_activity_or_404(activity_name)

    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
