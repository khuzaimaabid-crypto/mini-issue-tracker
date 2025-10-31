import pytest


def test_create_project(client, auth_headers):
    """Test project creation"""
    response = client.post(
        "/projects",
        json={
            "name": "New Project",
            "description": "Project description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "Project description"
    assert "id" in data


def test_create_project_unauthorized(client):
    """Test project creation without authentication"""
    response = client.post(
        "/projects",
        json={
            "name": "New Project",
            "description": "Project description"
        }
    )
    
    assert response.status_code == 403


def test_get_user_projects(client, auth_headers, test_project):
    """Test getting user's projects"""
    response = client.get("/projects", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Test Project"


def test_get_project_by_id(client, auth_headers, test_project):
    """Test getting a specific project"""
    response = client.get(f"/projects/{test_project.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


def test_update_project(client, auth_headers, test_project):
    """Test updating a project"""
    response = client.patch(
        f"/projects/{test_project.id}",
        json={"name": "Updated Project"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"


def test_delete_project(client, auth_headers, test_project):
    """Test deleting a project"""
    response = client.delete(f"/projects/{test_project.id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify project is deleted
    response = client.get(f"/projects/{test_project.id}", headers=auth_headers)
    assert response.status_code == 404


def test_access_other_user_project(client, db_session, auth_headers):
    """Test accessing another user's project"""
    from app.models.user import User
    from app.models.project import Project
    from app.auth.password_handler import password_handler
    
    # Create another user
    other_user = User(
        name="Other User",
        email="other@example.com",
        hashed_password=password_handler.hash("password123")
    )
    db_session.add(other_user)
    db_session.commit()
    
    # Create project for other user
    other_project = Project(
        name="Other Project",
        description="Other Description",
        created_by=other_user.id
    )
    db_session.add(other_project)
    db_session.commit()
    
    # Try to access other user's project
    response = client.get(f"/projects/{other_project.id}", headers=auth_headers)
    assert response.status_code == 403
    
def test_create_project_missing_name(client, auth_headers):
    """Test project creation without name"""
    response = client.post(
        "/projects",
        json={"description": "Missing name"},
        headers=auth_headers
    )
    assert response.status_code == 422