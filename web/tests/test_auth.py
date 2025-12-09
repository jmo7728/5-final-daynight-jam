from app.auth import create_user, find_user_by_username

def test_create_user():
    result = create_user("bob", "abc123")
    assert result is True
    result2 = create_user("bob", "abc456")
    assert result2 is False

def test_find_user_by_username():
    create_user("jen", "abc123")
    user_doc = find_user_by_username("jen")
    assert user_doc is not None
    assert user_doc["username"] == "jen"

def test_find_user_by_username_not_exist():
    user_doc = find_user_by_username("nonexistent")
    assert user_doc is None

def test_register_success(client):
    response = client.post(
        "/auth/register",
        data={"username": "bob", "password": "abc123"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"registration successful" in response.data.lower()

def test_register_duplicate_username(client):
    client.post("/auth/register", data={"username": "jen", "password": "abc123"}, follow_redirects=True)
    response = client.post("/auth/register", data={"username": "jen", "password": "abc456"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"already taken" in response.data.lower()

def test_login_success(client):
    client.post("/auth/register", data={"username": "bob", "password": "abc123"}, follow_redirects=True)
    response = client.post("/auth/login", data={"username": "bob", "password": "abc123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"home" in response.data.lower() or b"welcome" in response.data.lower()

def test_login_wrong_password(client):
    client.post("/auth/register", data={"username": "jen", "password": "abc123"}, follow_redirects=True)
    response = client.post("/auth/login", data={"username": "jen", "password": "abc456wrong"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"invalid" in response.data.lower()

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={"username": "ghost", "password": "abc123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"invalid" in response.data.lower()

def test_logout(client):
    client.post("/auth/register", data={"username": "bob", "password": "abc123"}, follow_redirects=True)
    client.post("/auth/login", data={"username": "bob", "password": "abc123"}, follow_redirects=True)
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out" in response.data.lower()

def test_me_authenticated(client):
    client.post("/auth/register", data={"username": "jen", "password": "abc123"}, follow_redirects=True)
    client.post("/auth/login", data={"username": "jen", "password": "abc123"}, follow_redirects=True)
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "jen"

def test_me_unauthenticated(client):
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] is None
