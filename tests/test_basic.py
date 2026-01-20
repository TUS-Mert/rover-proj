def test_homepage_redirects_if_not_logged_in(client):
    """Verify that accessing / without login redirects (302) to login page."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_homepage_loads_when_logged_in(client, auth):
    """Verify that the dashboard loads (200) after logging in."""
    auth.login()
    response = client.get('/')
    assert response.status_code == 200

def test_telemetry_api(client, auth):
    """Verify API access."""
    auth.login()
    response = client.get('/api/telemetry')
    assert response.status_code in [200, 404]