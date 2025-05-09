import pytest

def test_invalid_route_returns_404(client):
    res = client.get("/fake/page")
    assert res.status_code == 404

def test_register_blank_fields(client):
    res = client.post("/auth/register", data={
        "name": "",
        "phone": "",
        "password": ""
    })
    assert b"Invalid phone number or password."