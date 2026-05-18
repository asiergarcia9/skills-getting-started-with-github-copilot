"""
Tests for Mergington High School API

Tests cover the core functionality of the FastAPI application using the
AAA (Arrange-Act-Assert) testing pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture that provides a TestClient for the FastAPI app."""
    return TestClient(app)


class TestActivities:
    """Test cases for activities endpoints."""

    def test_get_activities(self, client):
        """
        Test GET /activities endpoint.
        
        Arrange: No setup needed - activities are predefined in app.py
        Act: Send GET request to /activities
        Assert: Verify response contains all activities with correct structure
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Swimming Club",
            "Drama Club",
            "Art Studio",
            "Math Olympiad",
            "Science Fair Prep"
        ]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities
            activity = activities[activity_name]
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_signup_success(self, client):
        """
        Test POST /activities/{activity_name}/signup endpoint.
        
        Arrange: Define test activity and email
        Act: Send POST request to signup endpoint
        Assert: Verify response indicates successful signup (status 200)
        """
        # Arrange
        activity_name = "Programming Class"
        test_email = "testuser@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data.get("message", "").lower()

    def test_unregister_success(self, client):
        """
        Test DELETE /activities/{activity_name}/unregister endpoint.
        
        Arrange: Sign up a student first, then unregister them
        Act: Send DELETE request to unregister endpoint
        Assert: Verify response indicates successful unregistration (status 200)
        """
        # Arrange
        activity_name = "Chess Club"
        # Use an existing participant from the app
        test_email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data.get("message", "").lower()

    def test_activities_list_updated_after_signup(self, client):
        """
        Test that GET /activities reflects signup changes.
        
        Arrange: Define test activity and new email (not yet signed up)
        Act: Sign up the student, then fetch activities
        Assert: Verify the new student appears in the activity's participants list
        """
        # Arrange
        activity_name = "Gym Class"
        new_student_email = "newstudent@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )
        
        # Act - Get updated activities
        updated_response = client.get("/activities")
        
        # Assert
        assert signup_response.status_code == 200
        assert updated_response.status_code == 200
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert new_student_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1
