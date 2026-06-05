from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_original_activities = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(_original_activities))


def test_root_redirects_to_static_index():
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "teststudent@example.com"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "duplicate@example.com"
    activities[activity_name]["participants"] = [email]

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_successfully():
    activity_name = "Swimming Club"
    email = "removal@mergington.edu"

    if email not in activities[activity_name]["participants"]:
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete(
        "/activities/Gym Class/participants",
        params={"email": "missing@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
