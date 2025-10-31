import pytest


def test_create_issue(client, auth_headers, test_project):
    """Test issue creation"""
    response = client.post(
        f"/projects/{test_project.id}/issues",
        json={
            "title": "New Issue",
            "description": "Issue description",
            "status": "Open",
            "priority": "Medium"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Issue"
    assert data["status"] == "Open"
    assert data["priority"] == "Medium"


def test_get_project_issues(client, auth_headers, test_project, db_session):
    """Test getting project issues"""
    from app.models.issue import Issue
    
    # Create test issue
    issue = Issue(
        project_id=test_project.id,
        title="Test Issue",
        description="Test Description",
        status="Open",
        priority="High",
        created_by=test_project.created_by
    )
    db_session.add(issue)
    db_session.commit()
    
    response = client.get(f"/projects/{test_project.id}/issues", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_filter_issues_by_status(client, auth_headers, test_project, db_session):
    """Test filtering issues by status"""
    from app.models.issue import Issue
    
    # Create issues with different statuses
    issue1 = Issue(
        project_id=test_project.id,
        title="Open Issue",
        status="Open",
        priority="Medium",
        created_by=test_project.created_by
    )
    issue2 = Issue(
        project_id=test_project.id,
        title="Closed Issue",
        status="Closed",
        priority="Medium",
        created_by=test_project.created_by
    )
    db_session.add_all([issue1, issue2])
    db_session.commit()
    
    response = client.get(
        f"/projects/{test_project.id}/issues?status=Open",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(issue["status"] == "Open" for issue in data)


def test_update_issue(client, auth_headers, test_project, db_session):
    """Test updating an issue"""
    from app.models.issue import Issue
    
    issue = Issue(
        project_id=test_project.id,
        title="Test Issue",
        status="Open",
        priority="Low",
        created_by=test_project.created_by
    )
    db_session.add(issue)
    db_session.commit()
    
    response = client.patch(
        f"/issues/{issue.id}",
        json={"status": "Closed"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Closed"


def test_delete_issue(client, auth_headers, test_project, db_session):
    """Test deleting an issue"""
    from app.models.issue import Issue
    
    issue = Issue(
        project_id=test_project.id,
        title="Test Issue",
        status="Open",
        priority="Medium",
        created_by=test_project.created_by
    )
    db_session.add(issue)
    db_session.commit()
    
    response = client.delete(f"/issues/{issue.id}", headers=auth_headers)
    assert response.status_code == 204

def test_filter_issues_by_priority(client, auth_headers, test_project, db_session):
    """Test filtering issues by priority"""
    from app.models.issue import Issue
    
    issue1 = Issue(
        project_id=test_project.id,
        title="High Priority",
        status="Open",
        priority="High",
        created_by=test_project.created_by
    )
    issue2 = Issue(
        project_id=test_project.id,
        title="Low Priority",
        status="Open",
        priority="Low",
        created_by=test_project.created_by
    )
    db_session.add_all([issue1, issue2])
    db_session.commit()
    
    response = client.get(
        f"/projects/{test_project.id}/issues?priority=High",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(issue["priority"] == "High" for issue in data)


def test_create_issue_missing_title(client, auth_headers, test_project):
    """Test issue creation without title"""
    response = client.post(
        f"/projects/{test_project.id}/issues",
        json={
            "description": "Missing title",
            "status": "Open",
            "priority": "Medium"
        },
        headers=auth_headers
    )
    assert response.status_code == 422 