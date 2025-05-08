def login(client, phone, password):
    return client.post("/auth/login", data={"phone": phone, "password": password}, follow_redirects=True)
