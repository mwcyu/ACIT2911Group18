def test_request_example(client):
    res = client.get("/home")
    
    assert b"Products" in res.data