import requests
from requests.exceptions import Timeout

def test_recipe_recommend_success(client, mock_ml_client):
    response = client.get("/recipes/recommend?ingredients=ing1,ing2")
    data = response.get_json()
    assert response.status_code == 200
    assert data["recommendation"]["name"] == "Mock Recipe"
    assert "ingredient1" in data["recommendation"]["ingredients"]

def test_recipe_recommend_failure(client, monkeypatch):
    def mock_post(*args, **kwargs):
        raise Timeout("Service timeout")
    monkeypatch.setattr(requests, "post", mock_post)
    response = client.get("/recipes/recommend")
    data = response.get_json()
    assert response.status_code == 503
    assert "error" in data
