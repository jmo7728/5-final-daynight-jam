from app.ml_client import get_recommendation, replace_ingredient

def test_get_recommendation(mock_ml_client):
    payload = {"include": ["ing1"]}
    result = get_recommendation(payload)
    assert result["name"] == "Mock Recipe"

def test_replace_ingredient(mock_ml_client):
    recipe = {"recipe_id": "1", "name": "Mock Recipe"}
    result = replace_ingredient(recipe, "ingredient1", "ingredient3")
    assert result["name"] == "Mock Recipe Updated"
    assert "ingredient3" in result["ingredients"]
