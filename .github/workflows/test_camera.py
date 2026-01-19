def test_stream_endpoint_loads(client):
    """
    Tests if the /stream endpoint is available.

    This relies on the `ENV=test` in the CI pipeline, which ensures
    the MockCamera is used, preventing errors from missing hardware.
    """
    response = client.get('/stream')
    # A successful response indicates the endpoint is correctly set up.
    assert response.status_code == 200