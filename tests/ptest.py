import pytest

def test_register_page_loads(client):
    res = client.get("/auth/register")
    assert res.status_code == 200
    assert b"Register" in res.data