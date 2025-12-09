from app.db import insert_recipe

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_home_page(client):
    response = client.get("/home")
    assert response.status_code == 200

def test_ingredients_page(client):
    response = client.get("/ingredients")
    assert response.status_code == 200

def test_recipe_page(client):
    response = client.get("/recipe")
    assert response.status_code == 200

def test_result_page_with_recipe(client):
    rid = insert_recipe({"name": "Test Recipe", "ingredients": ["ing1"]})
    response = client.get(f"/result?recipe_id={rid}")
    assert response.status_code == 200
