import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200  # Success, as we're serving the file directly

def test_get_activities(client):
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Check structure of an activity
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity

def test_signup_success(client):
    """Test successful activity signup"""
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up test@mergington.edu for Chess Club"
    
    # Verify the student was actually added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate(client):
    """Test that a student cannot sign up for multiple activities"""
    # First signup
    email = "duplicate@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Try to sign up for another activity
    response = client.post(f"/activities/Programming Class/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for an activity"

def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success(client):
    """Test successful activity unregistration"""
    # First sign up a student
    email = "unregister@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then unregister them
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from Chess Club"
    
    # Verify the student was actually removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who isn't registered"""
    response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"

def test_unregister_nonexistent_activity(client):
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonExistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"