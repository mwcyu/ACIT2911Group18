def test_login_page_loads(client):
    res = client.get("/auth/login")
    assert res.status_code == 200
    assert b"Login" in res.data


# def test_register_page_loads(client):
#     res = client.get("/auth/register")
#     assert res.status_code == 200
#     assert b"Register" in res.data


# def test_register_new_user(client, app):
#     # Simulate registering a new user
#     res = client.post("/auth/register", data={
#         "name": "Test User",
#         "phone": "1234567890",
#         "password": "testpass"
#     }, follow_redirects=True)

#     assert res.status_code == 200
#     assert b"Login" in res.data


# def test_login_valid_user(client, app):
#     # First register the user
#     client.post("/auth/register", data={
#         "name": "Valid User",
#         "phone": "2223334444",
#         "password": "mypassword"
#     }, follow_redirects=True)

#     # Then try logging in
#     res = client.post("/auth/login", data={
#         "phone": "2223334444",
#         "password": "mypassword"
#     }, follow_redirects=True)

#     assert b"Logged in as" in res.data


# def test_login_invalid_user(client):
#     res = client.post("/auth/login", data={
#         "phone": "wrong",
#         "password": "wrong"
#     })
#     assert b"Invalid phone number or password" in res.data


# def test_logout(client, app):
#     # Register and login
#     client.post("/auth/register", data={
#         "name": "Log Me Out",
#         "phone": "1112223333",
#         "password": "secret"
#     })

#     client.post("/auth/login", data={
#         "phone": "1112223333",
#         "password": "secret"
#     })

#     # Logout
#     res = client.get("/auth/logout", follow_redirects=True)
#     assert b"Login" in res.data
