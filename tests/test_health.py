"""
Baseline Health Check and System Verification Tests
---------------------------------------------------
Verifies that the entry-point routes and health status reports function correctly.
"""

def test_health_check_endpoint(client):
    """Verify /health returns HTTP 200 and baseline online status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data["status"] == "online"
    assert "AttendSync System Online" in data["message"]
    assert data["service"].startswith("AttendSync")
    assert "version" in data
    assert "timestamp" in data


def test_landing_page(client):
    """Verify the root / endpoint renders the Bootstrap landing page with status."""
    response = client.get("/")
    assert response.status_code == 200
    html_content = response.get_data(as_text=True)
    assert "AttendSync System Online" in html_content
    assert "AttendSync" in html_content


def test_404_error_page_html(client):
    """Verify non-existent routes return 404 HTML response."""
    response = client.get("/non-existent-page")
    assert response.status_code == 404
    assert "Page Not Found" in response.get_data(as_text=True)


def test_404_error_page_json(client):
    """Verify API 404 responses return JSON payload."""
    response = client.get("/api/unknown-endpoint", headers={"Accept": "application/json"})
    assert response.status_code == 404
    data = response.get_json()
    assert data["status"] == "error"
    assert data["code"] == 404
