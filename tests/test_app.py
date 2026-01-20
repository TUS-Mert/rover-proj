def test_index_redirect(client):
    """Test that accessing index redirects to login if not authenticated."""
    response = client.get('/')
    # Should redirect (302) to login page
    assert response.status_code == 302
    assert '/login' in response.location


def test_login_page_loads(client):
    """Test that the login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200