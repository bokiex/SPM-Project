import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flaskapp.models.teams import TeamsService, TeamsController

@pytest.fixture
def supabase_client():
    return MagicMock()

@pytest.fixture
def teams_service(supabase_client):
    return TeamsService(supabase_client)

@pytest.fixture
def teams_controller(teams_service):
    return TeamsController(teams_service)

# Test the TeamsService class
def test_get_staff_by_department(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', 'Dept': 'IT', 'Position': 'Developer', 'Reporting_Manager': 2}]
    supabase_client.from_().select().eq().execute.return_value = mock_response

    department = 'IT'
    result = teams_service.get_staff_by_department(department)

    assert result == mock_response.data
    supabase_client.from_.assert_called_with('Employee')

def test_get_staff_by_department_CEO(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', 'Dept': 'IT', 'Position': 'Developer', 'Reporting_Manager': 2}]
    supabase_client.from_().select().eq().execute.return_value = mock_response

    department = 'CEO'
    result = teams_service.get_staff_by_department(department)

    assert result == mock_response.data
    supabase_client.from_.assert_called_with('Employee')

def test_get_staff_by_department_all(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', 'Dept': 'IT', 'Position': 'Developer', 'Reporting_Manager': 2}]
    supabase_client.from_().select().execute.return_value = mock_response

    department = 'All'
    result = teams_service.get_staff_by_department(department)

    assert result == mock_response.data
    supabase_client.from_.assert_called_with('Employee')

def test_get_manager_name(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_FName': 'John', 'Staff_LName': 'Doe'}]
    supabase_client.from_().select().eq().execute.return_value = mock_response

    manager_name = teams_service.get_manager_name(1)

    assert manager_name == "John Doe"

def test_get_manager_name_failure(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = []
    supabase_client.from_().select().eq().execute.return_value = mock_response

    manager_name = teams_service.get_manager_name(1)

    assert manager_name == "Unknown" 

def test_get_team_by_manager_dept(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1}]
    supabase_client.from_().select().eq().eq().eq().execute.return_value = mock_response

    result = teams_service.get_team_by_manager_dept('John', 'Doe', 'IT')

    assert result == mock_response


def test_get_team_ids_for_staff(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'team_id': 1}]
    supabase_client.from_().select().eq().execute.return_value = mock_response

    result = teams_service.get_team_ids_for_staff(1)

    assert result == [1]


def test_get_staff_in_teams(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'staff_id': 2}]
    supabase_client.from_().select().in_().neq().execute.return_value = mock_response

    result = teams_service.get_staff_in_teams([1], 1)

    assert result == [2]


def test_get_requests_for_staff(teams_service, supabase_client):
    mock_response = MagicMock()
    mock_response.data = [{'staff_id': 1, 'reason': 'Vacation'}]
    supabase_client.from_().select().in_().eq().execute.return_value = mock_response

    result = teams_service.get_requests_for_staff([1])

    assert result == mock_response.data


# Test the TeamsController class
def test_get_team_details_success(teams_controller, client):
    mock_response = MagicMock()
    mock_response.data = [{'Staff_ID': 1}]
    with patch.object(teams_controller.teams_service, 'get_team_by_manager_dept', return_value=mock_response):
        with client.application.test_request_context('/?m_name=John Doe&dept=IT'):
            response = teams_controller.get_team_details()

        assert response.status_code == 200
        assert response.get_json() == {"Staff_ID": 1}


def test_get_team_details_failure(teams_controller, client):
    
    response = client.get('/team_details?m_name=John Doe')
    print(response)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Manager name and department are required"}


def test_get_teams_by_reporting_manager(teams_controller, client):
    mock_staff_data = [
        {'Staff_ID': 1, 'Staff_FName': 'John', 'Staff_LName': 'Doe', 'Dept': 'IT', 'Position': 'Developer', 'Reporting_Manager': 2}
    ]
    with patch.object(teams_controller.teams_service, 'get_staff_by_department', return_value=mock_staff_data), \
         patch.object(teams_controller.teams_service, 'get_manager_name', return_value='Jane Doe'):
        
        response = client.get('/teams_by_reporting_manager?department=IT')

    assert response.status_code == 200
    assert "positions" in response.get_json()
    assert "teams" in response.get_json()

def test_get_teams_by_reporting_manager_failure(teams_controller, client):
    
    with patch.object(teams_controller.teams_service, 'get_staff_by_department', return_value=None), \
        patch.object(teams_controller.teams_service, 'get_manager_name', return_value=None):
        
        response = client.get('/teams_by_reporting_manager')
    assert response.status_code == 404
    assert response.get_json() == {"error": "No staff found"}

def test_get_team_requests_success(client, teams_controller):
    # Mock data setup

    with patch.object(teams_controller.teams_service, 'get_team_ids_for_staff', return_value=[1, 2]), \
        patch.object(teams_controller.teams_service, 'get_staff_in_teams', return_value=[10, 11]), \
        patch.object(teams_controller.teams_service, 'get_requests_for_staff', return_value=[{"request_id": 1, "staff_id": 10, "status": 0}, {"request_id": 2, "staff_id": 11, "status": 0}]):
    
    
        with client.application.test_request_context(headers={'X-Staff-ID': '1'}):
            response = teams_controller.get_team_requests()
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["request_id"] == 1
    assert data[1]["request_id"] == 2

def test_get_team_requests_missing_staff_id(client, teams_controller):
    with client.application.test_request_context(headers={}):
        response = teams_controller.get_team_requests()
    
    # Assertions
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Staff ID is required"

def test_get_team_requests_no_teams_found(client, teams_controller):
    # Mock data for no teams found
    with patch.object(teams_controller.teams_service, 'get_team_ids_for_staff', return_value=[]):    
        with client.application.test_request_context(headers={'X-Staff-ID': '1'}):
            response = teams_controller.get_team_requests()
    
    # Assertions
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "No teams found for the staff"

def test_get_team_requests_no_staff_in_teams(client, teams_controller):
    # Mock data for staff in teams

    with patch.object(teams_controller.teams_service, 'get_team_ids_for_staff', return_value=[1, 2]), \
        patch.object(teams_controller.teams_service, 'get_staff_in_teams', return_value=[]):    
        with client.application.test_request_context(headers={'X-Staff-ID': '1'}):
            response = teams_controller.get_team_requests()
    
    # Assertions
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "No staff found in the teams"

def test_get_team_requests_no_requests_for_team_staff(client, teams_controller):
    # Mock data for no requests found

    with patch.object(teams_controller.teams_service, 'get_team_ids_for_staff', return_value=[1, 2]), \
        patch.object(teams_controller.teams_service, 'get_staff_in_teams', return_value=[10, 11]), \
        patch.object(teams_controller.teams_service, 'get_requests_for_staff', return_value=[]):    
        with client.application.test_request_context(headers={'X-Staff-ID': '1'}):
            response = teams_controller.get_team_requests()
    
    # Assertions
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "No requests found for the team"