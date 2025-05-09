from bs4 import BeautifulSoup

def test_password_hashing(test_user):
    assert test_user.check_password("testpass") is True
    assert test_user.check_password("wrongpass") is False


def test_access_login_route(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_flow(client, test_user):
    response = client.post("/auth/login", data={
        "phone": test_user.phone,
        "password": "testpass"
    }, follow_redirects=True)
    
    html = response.data.decode()
    soup = BeautifulSoup(html, "html.parser")
    print(soup.prettify())

    assert response.status_code == 200
    assert b"Order Summary" in response.data or b"Logout" in response.data
