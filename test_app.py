import pytest
import json
from app import app, nonprofits, sent_emails

@pytest.fixture
def client():
    with app.test_client() as client:
        # Clear nonprofits dict before each test to isolate tests
        nonprofits.clear()
        sent_emails.clear()
        yield client

def test_add_nonprofits(client):
    # Prepare test data: two nonprofits
    data = [
        {
            "name": "Helping Hands",
            "address": "123 Charity St",
            "email": "helping@nonprofit.org"
        },
        {
            "name": "Food For All",
            "address": "456 Kindness Ave",
            "email": "food@nonprofit.org"
        }
    ]

    # Send POST request to /nonprofits
    response = client.post(
        "/nonprofits",
        data=json.dumps(data),
        content_type='application/json'
    )

    # Check response status code
    assert response.status_code == 201

    # Check response content
    json_data = response.get_json()
    assert json_data["message"] == "2 nonprofit(s) created"
    # assert json_data["message"] == "Nonprofit(s) created"

    # Verify nonprofits are stored correctly
    assert "helping@nonprofit.org" in nonprofits
    assert nonprofits["helping@nonprofit.org"]["name"] == "Helping Hands"
    assert "food@nonprofit.org" in nonprofits


def test_get_nonprofits(client):
    # Inject fake data directly into the in-memory store
    nonprofits["alpha@example.org"] = {
        "name": "Alpha Org",
        "address": "100 Main St",
        "email": "alpha@example.org"
    }
    nonprofits["beta@example.org"] = {
        "name": "Beta Org",
        "address": "200 Side Ave",
        "email": "beta@example.org"
    }

    # Make GET request
    response = client.get("/nonprofits")

    # Assert response status
    assert response.status_code == 200

    # Parse JSON response
    data = response.get_json()

    # Check response contains expected nonprofits
    assert isinstance(data, list)
    assert len(data) == 2
    assert any(n['email'] == "alpha@example.org" for n in data)
    assert any(n['email'] == "beta@example.org" for n in data)


# Quick and easy integration test
def test_post_then_get_nonprofits(client):
    # POST a nonprofit
    client.post("/nonprofits", json=[{
        "name": "Test Org",
        "address": "42 Street",
        "email": "test@org.org"
    }])
    
    # GET nonprofits
    response = client.get("/nonprofits")
    data = response.get_json()
    
    assert len(data) == 1
    assert data[0]["email"] == "test@org.org"


def test_send_emails(client):
    # Setup: manually insert nonprofits
    nonprofits["a@example.org"] = {
        "name": "Org A",
        "address": "123 A Street",
        "email": "a@example.org"
    }
    nonprofits["b@example.org"] = {
        "name": "Org B",
        "address": "456 B Street",
        "email": "b@example.org"
    }

    # Send POST to /send_emails
    response = client.post("/send_emails", json={
        "template": "Sending money to {name} at {address}",
        "recipients": ["a@example.org", "b@example.org", "missing@example.org"]
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "sent" in data and "skipped" in data

    assert sorted(data["sent"]) == ["a@example.org", "b@example.org"]
    assert data["skipped"] == ["missing@example.org"]





def test_get_sent_emails(client):
    # Setup: manually populate sent_emails
    sent_emails.clear()
    sent_emails.append({
        "to": "a@example.org",
        "body": "Sending money to Org A at 123 A Street"
    })
    sent_emails.append({
        "to": "b@example.org",
        "body": "Sending money to Org B at 456 B Street"
    })

    # Send GET request
    response = client.get("/emails")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert any(email["to"] == "a@example.org" for email in data)


def test_email_workflow_integration(client):
    # Step 1: Add nonprofits
    response = client.post("/nonprofits", json=[
        {
            "name": "Org A",
            "address": "123 A Street",
            "email": "a@example.org"
        },
        {
            "name": "Org B",
            "address": "456 B Street",
            "email": "b@example.org"
        }
    ])
    assert response.status_code == 201

    # Step 2: Send emails
    response = client.post("/send_emails", json={
        "template": "Hi {name}, we’re sending help to {address}.",
        "recipients": ["a@example.org", "b@example.org"]
    })
    assert response.status_code == 200
    result = response.get_json()
    assert sorted(result["sent"]) == ["a@example.org", "b@example.org"]
    assert result["skipped"] == []

    # Step 3: Retrieve sent emails
    response = client.get("/emails")
    emails = response.get_json()
    assert len(emails) == 2
    assert any("Hi Org A" in email["body"] for email in emails)


