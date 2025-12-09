
def test_api_recommend(client, mock_ml_client):
    response = client.post("/api/recommend", json={})
    data = response.get_json()
    assert response.status_code == 200
    assert "recipe" in data
    assert data["recipe"]["name"] == "Mock Recipe"

def test_api_replace(client, mock_ml_client):
    payload = {
        "recipe_id": "1",
        "from": "ingredient1",
        "to": "ingredient3"
    }
    response = client.post("/api/replace", json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data["recipe"]["name"] == "Mock Recipe Updated"
    assert "ingredient3" in data["recipe"]["ingredients"]

def test_api_replace_missing(client):
    response = client.post("/api/replace", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
