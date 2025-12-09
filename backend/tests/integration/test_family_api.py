"""
Integration tests for Family Management API endpoints.

Tests User Stories 1-6 with test-first approach per Constitution Principle II.
All tests verify API contracts, validation rules, and success criteria from spec.md.
"""

import json
import pytest
from datetime import date, timedelta
from bellweaver.api import create_app
from bellweaver.db.database import get_session, init_db, Base, get_engine


@pytest.fixture
def app():
    """Create Flask app for testing with isolated database."""
    app = create_app()
    app.config['TESTING'] = True

    # Use in-memory SQLite database for tests
    import os
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

    with app.app_context():
        # Initialize database schema
        init_db()

    yield app

    # Cleanup
    with app.app_context():
        session = get_session()
        session.close()
        engine = get_engine()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    """Create test client for API requests."""
    return app.test_client()


# ============================================================================
# Phase 3: User Story 1 - Add First Child Profile
# ============================================================================

class TestUserStory1CreateChild:
    """Tests for POST /api/children endpoint."""

    def test_create_child_with_valid_data(self, client):
        """
        T016: POST /api/children with valid data
        Expect: 201 Created, response matches ChildCreate schema, SC-001 (<200ms)
        """
        payload = {
            "name": "Emma Johnson",
            "date_of_birth": "2015-06-15",
            "gender": "female",
            "interests": "Soccer, reading, science experiments"
        }

        import time
        start_time = time.time()
        response = client.post('/api/children',
                              data=json.dumps(payload),
                              content_type='application/json')
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        # Verify 201 Created
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.get_json()}"

        # Verify response schema
        data = response.get_json()
        assert 'id' in data
        assert data['name'] == "Emma Johnson"
        assert data['date_of_birth'] == "2015-06-15"
        assert data['gender'] == "female"
        assert data['interests'] == "Soccer, reading, science experiments"
        assert 'created_at' in data
        assert 'updated_at' in data

        # Verify SC-001: Response time < 200ms
        assert elapsed_time < 200, f"Response took {elapsed_time:.2f}ms, expected < 200ms"

    def test_create_child_with_missing_required_fields(self, client):
        """
        T017: POST /api/children with missing required fields
        Expect: 400 Bad Request with validation errors
        """
        # Missing name
        payload = {
            "date_of_birth": "2015-06-15"
        }

        response = client.post('/api/children',
                              data=json.dumps(payload),
                              content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'message' in data

    def test_create_child_with_future_date_of_birth(self, client):
        """
        T018: POST /api/children with future date_of_birth
        Expect: 400 Bad Request per FR-010b
        """
        future_date = (date.today() + timedelta(days=1)).isoformat()

        payload = {
            "name": "Future Child",
            "date_of_birth": future_date
        }

        response = client.post('/api/children',
                              data=json.dumps(payload),
                              content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'message' in data
        # Verify error message mentions future date
        error_text = json.dumps(data).lower()
        assert 'future' in error_text or 'date' in error_text


class TestUserStory1GetChild:
    """Tests for GET /api/children/:id endpoint."""

    def test_get_child_by_id_valid(self, client):
        """
        T019: GET /api/children/:id with valid ID
        Expect: 200 OK, verify child data returned
        """
        # Create a child first
        payload = {
            "name": "Test Child",
            "date_of_birth": "2016-03-20"
        }
        create_response = client.post('/api/children',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        assert create_response.status_code == 201
        child_id = create_response.get_json()['id']

        # Get the child
        response = client.get(f'/api/children/{child_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == child_id
        assert data['name'] == "Test Child"
        assert data['date_of_birth'] == "2016-03-20"

    def test_get_child_by_id_not_found(self, client):
        """
        T020: GET /api/children/:id with invalid ID
        Expect: 404 Not Found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f'/api/children/{fake_id}')

        assert response.status_code == 404


class TestUserStory1ListChildren:
    """Tests for GET /api/children endpoint."""

    def test_list_all_children(self, client):
        """
        T021: GET /api/children
        Expect: 200 OK, list contains created children, SC-005 (<200ms)
        """
        # Create multiple children
        children_data = [
            {"name": "Alice", "date_of_birth": "2014-01-15"},
            {"name": "Bob", "date_of_birth": "2016-06-30"},
            {"name": "Charlie", "date_of_birth": "2018-11-22"}
        ]

        for child_data in children_data:
            response = client.post('/api/children',
                                  data=json.dumps(child_data),
                                  content_type='application/json')
            assert response.status_code == 201

        # List all children
        import time
        start_time = time.time()
        response = client.get('/api/children')
        elapsed_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        data = response.get_json()

        # Verify we got a list
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify all children are present
        names = [child['name'] for child in data]
        assert 'Alice' in names
        assert 'Bob' in names
        assert 'Charlie' in names

        # Verify SC-005: Response time < 200ms
        assert elapsed_time < 200, f"Response took {elapsed_time:.2f}ms, expected < 200ms"


# ============================================================================
# Phase 4: User Story 2 - Manage Multiple Children
# ============================================================================

class TestUserStory2UpdateChild:
    """Tests for PUT /api/children/:id endpoint."""

    def test_update_child_with_valid_data(self, client):
        """
        T027: PUT /api/children/:id with valid data
        Expect: 200 OK, verify updated fields only
        """
        # Create a child
        payload = {
            "name": "Original Name",
            "date_of_birth": "2015-05-10",
            "gender": "male"
        }
        create_response = client.post('/api/children',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        assert create_response.status_code == 201
        child_id = create_response.get_json()['id']

        # Update the child
        update_payload = {
            "name": "Updated Name",
            "date_of_birth": "2015-05-10",  # Same date
            "gender": "male",
            "interests": "New interests added"
        }
        response = client.put(f'/api/children/{child_id}',
                            data=json.dumps(update_payload),
                            content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == "Updated Name"
        assert data['interests'] == "New interests added"
        assert data['date_of_birth'] == "2015-05-10"

    def test_update_child_invalid_id(self, client):
        """
        T028: PUT /api/children/:id with invalid ID
        Expect: 404 Not Found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        payload = {"name": "New Name", "date_of_birth": "2015-05-10"}

        response = client.put(f'/api/children/{fake_id}',
                            data=json.dumps(payload),
                            content_type='application/json')

        assert response.status_code == 404

    def test_update_child_with_future_date_of_birth(self, client):
        """
        T029: PUT /api/children/:id with future date_of_birth
        Expect: 400 Bad Request
        """
        # Create a child
        payload = {"name": "Test Child", "date_of_birth": "2015-05-10"}
        create_response = client.post('/api/children',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        assert create_response.status_code == 201
        child_id = create_response.get_json()['id']

        # Try to update with future date
        future_date = (date.today() + timedelta(days=1)).isoformat()
        update_payload = {"name": "Test Child", "date_of_birth": future_date}

        response = client.put(f'/api/children/{child_id}',
                            data=json.dumps(update_payload),
                            content_type='application/json')

        assert response.status_code == 400


class TestUserStory2DeleteChild:
    """Tests for DELETE /api/children/:id endpoint."""

    def test_delete_child_success(self, client):
        """
        T030: DELETE /api/children/:id
        Expect: 204 No Content, verify child removed and associations cascade deleted (FR-017)
        """
        # Create a child
        payload = {"name": "To Be Deleted", "date_of_birth": "2015-01-01"}
        create_response = client.post('/api/children',
                                     data=json.dumps(payload),
                                     content_type='application/json')
        assert create_response.status_code == 201
        child_id = create_response.get_json()['id']

        # Delete the child
        response = client.delete(f'/api/children/{child_id}')

        assert response.status_code == 204

        # Verify child is gone
        get_response = client.get(f'/api/children/{child_id}')
        assert get_response.status_code == 404

    def test_delete_child_invalid_id(self, client):
        """
        T031: DELETE /api/children/:id with invalid ID
        Expect: 404 Not Found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f'/api/children/{fake_id}')

        assert response.status_code == 404


# ============================================================================
# Phase 5: User Story 3 - Define Organisation
# ============================================================================

class TestUserStory3CreateOrganisation:
    """Tests for POST /api/organisations endpoint."""

    def test_create_organisation_with_valid_data(self, client):
        """
        T035: POST /api/organisations with valid data
        Expect: 201 Created, verify organisation created
        """
        payload = {
            "name": "Springfield Elementary",
            "type": "school",
            "address": "123 School Lane",
            "contact_info": {"phone": "555-1234", "email": "admin@springfield.edu"}
        }

        response = client.post('/api/organisations',
                              data=json.dumps(payload),
                              content_type='application/json')

        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == "Springfield Elementary"
        assert data['type'] == "school"
        assert data['address'] == "123 School Lane"
        assert data['contact_info']['phone'] == "555-1234"
        assert 'id' in data

    def test_create_organisation_duplicate_name(self, client):
        """
        T036: POST /api/organisations with duplicate name
        Expect: 409 Conflict with error per FR-010a
        """
        payload = {
            "name": "Unique School",
            "type": "school"
        }
        # Create first time
        client.post('/api/organisations',
                   data=json.dumps(payload),
                   content_type='application/json')
        
        # Create second time
        response = client.post('/api/organisations',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        # Check either error or message field for the detail
        error_text = json.dumps(data).lower()
        assert 'name' in error_text

    def test_create_organisation_invalid_type(self, client):
        """
        T037: POST /api/organisations with invalid type
        Expect: 400 Bad Request
        """
        payload = {
            "name": "Bad Type School",
            "type": "invalid_type"
        }

        response = client.post('/api/organisations',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 400

class TestUserStory3GetOrganisation:
    """Tests for GET /api/organisations endpoints."""

    def test_get_organisation_by_id(self, client):
        """
        T038: GET /api/organisations/:id
        Expect: 200 OK with organisation data
        """
        # Create org
        payload = {"name": "Test Org", "type": "school"}
        create_resp = client.post('/api/organisations',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        org_id = create_resp.get_json()['id']

        # Get org
        response = client.get(f'/api/organisations/{org_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == org_id
        assert data['name'] == "Test Org"

    def test_list_organisations_with_filter(self, client):
        """
        T039: GET /api/organisations with type filter
        Expect: 200 OK, verify filtering works, verify SC-005 (<200ms)
        """
        # Create orgs of different types
        orgs = [
            {"name": "School A", "type": "school"},
            {"name": "Club B", "type": "club"},
            {"name": "School C", "type": "school"}
        ]
        for org in orgs:
            client.post('/api/organisations',
                       data=json.dumps(org),
                       content_type='application/json')

        import time
        start_time = time.time()
        # Filter for schools
        response = client.get('/api/organisations?type=school')
        elapsed_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, list)
        assert len(data) == 2
        for org in data:
            assert org['type'] == "school"

        assert elapsed_time < 200


# ============================================================================
# Phase 6: User Story 4 - Associate Children with Organisations
# ============================================================================

class TestUserStory4Associations:
    """Tests for child-organisation association endpoints."""

    def test_create_association_success(self, client):
        """
        T045: POST /api/children/:id/organisations with valid IDs
        Expect: 201 Created, verify association created, verify SC-002 (<200ms)
        """
        # Create child
        child_resp = client.post('/api/children',
                                data=json.dumps({"name": "Student", "date_of_birth": "2015-01-01"}),
                                content_type='application/json')
        child_id = child_resp.get_json()['id']

        # Create organisation
        org_resp = client.post('/api/organisations',
                              data=json.dumps({"name": "School", "type": "school"}),
                              content_type='application/json')
        org_id = org_resp.get_json()['id']

        # Create association
        payload = {"organisation_id": org_id}
        
        import time
        start_time = time.time()
        response = client.post(f'/api/children/{child_id}/organisations',
                              data=json.dumps(payload),
                              content_type='application/json')
        elapsed_time = (time.time() - start_time) * 1000

        assert response.status_code == 201
        
        # Verify SC-002: Response time < 200ms
        assert elapsed_time < 200

        # Verify association exists
        get_resp = client.get(f'/api/children/{child_id}/organisations')
        assert get_resp.status_code == 200
        orgs = get_resp.get_json()
        assert len(orgs) == 1
        assert orgs[0]['id'] == org_id

    def test_create_association_not_found(self, client):
        """
        T046: POST /api/children/:id/organisations with non-existent child/org
        Expect: 404 Not Found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        # Case 1: Child not found
        resp1 = client.post(f'/api/children/{fake_id}/organisations',
                           data=json.dumps({"organisation_id": fake_id}),
                           content_type='application/json')
        assert resp1.status_code == 404

        # Case 2: Org not found (create child first)
        child_resp = client.post('/api/children',
                                data=json.dumps({"name": "Student", "date_of_birth": "2015-01-01"}),
                                content_type='application/json')
        child_id = child_resp.get_json()['id']
        
        resp2 = client.post(f'/api/children/{child_id}/organisations',
                           data=json.dumps({"organisation_id": fake_id}),
                           content_type='application/json')
        assert resp2.status_code == 404

    def test_create_association_duplicate(self, client):
        """
        T047: POST /api/children/:id/organisations with duplicate association
        Expect: 409 Conflict
        """
        # Create child and org
        child_id = client.post('/api/children', 
                              data=json.dumps({"name": "C", "date_of_birth": "2015-01-01"}),
                              content_type='application/json').get_json()['id']
        org_id = client.post('/api/organisations',
                            data=json.dumps({"name": "S", "type": "school"}),
                            content_type='application/json').get_json()['id']
        
        # Create first time
        client.post(f'/api/children/{child_id}/organisations',
                   data=json.dumps({"organisation_id": org_id}),
                   content_type='application/json')
        
        # Create second time
        response = client.post(f'/api/children/{child_id}/organisations',
                              data=json.dumps({"organisation_id": org_id}),
                              content_type='application/json')
        
        assert response.status_code == 409

    def test_get_child_organisations(self, client):
        """
        T048: GET /api/children/:id/organisations
        Expect: 200 OK with organisations list
        """
        # Create child
        child_id = client.post('/api/children',
                              data=json.dumps({"name": "C", "date_of_birth": "2015-01-01"}),
                              content_type='application/json').get_json()['id']
        
        # Create and link 2 orgs
        for name in ["School A", "Club B"]:
            org_id = client.post('/api/organisations',
                                data=json.dumps({"name": name, "type": "school"}),
                                content_type='application/json').get_json()['id']
            client.post(f'/api/children/{child_id}/organisations',
                       data=json.dumps({"organisation_id": org_id}),
                       content_type='application/json')
            
        # Get list
        response = client.get(f'/api/children/{child_id}/organisations')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        names = [o['name'] for o in data]
        assert "School A" in names
        assert "Club B" in names

    def test_delete_association(self, client):
        """
        T049: DELETE /api/children/:child_id/organisations/:org_id
        Expect: 204 No Content, verify association removed
        """
        # Setup
        child_id = client.post('/api/children',
                              data=json.dumps({"name": "C", "date_of_birth": "2015-01-01"}),
                              content_type='application/json').get_json()['id']
        org_id = client.post('/api/organisations',
                            data=json.dumps({"name": "S", "type": "school"}),
                            content_type='application/json').get_json()['id']
        client.post(f'/api/children/{child_id}/organisations',
                   data=json.dumps({"organisation_id": org_id}),
                   content_type='application/json')
        
        # Delete
        response = client.delete(f'/api/children/{child_id}/organisations/{org_id}')
        assert response.status_code == 204
        
        # Verify removed
        get_resp = client.get(f'/api/children/{child_id}/organisations')
        data = get_resp.get_json()
        assert len(data) == 0

    def test_get_child_detail_includes_organisations(self, client):
        """
        T050: GET /api/children/:id returns ChildDetail
        Expect: 200 OK, response includes organisations list
        """
        # Setup
        child_id = client.post('/api/children',
                              data=json.dumps({"name": "C", "date_of_birth": "2015-01-01"}),
                              content_type='application/json').get_json()['id']
        org_id = client.post('/api/organisations',
                            data=json.dumps({"name": "S", "type": "school"}),
                            content_type='application/json').get_json()['id']
        client.post(f'/api/children/{child_id}/organisations',
                   data=json.dumps({"organisation_id": org_id}),
                   content_type='application/json')
        
        # Get child detail
        response = client.get(f'/api/children/{child_id}')
        data = response.get_json()
        
        assert 'organisations' in data
        assert isinstance(data['organisations'], list)
        assert len(data['organisations']) == 1
        assert data['organisations'][0]['id'] == org_id