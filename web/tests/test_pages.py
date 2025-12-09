def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"🍳 What can I cook right now?" in response.data
    assert b"Smart Ingredient Match" in response.data


def test_ingredients_page(client):
    response = client.get("/ingredients")
    assert response.status_code == 200
    assert b"🥬 My Ingredients" in response.data
    assert b"Add Ingredient" in response.data
    assert b"No ingredients added yet" in response.data


def test_recipe_page_authenticated(client, mock_ml_client):
    response = client.post("/recipe", data={"ingredients": "chicken, eggs"})
    assert response.status_code == 200
    assert b"Mock Recipe" in response.data
    assert b"ingredient1" in response.data
    assert b"ingredient2" in response.data
    assert b"sub1" in response.data


def test_recipe_page_no_data(client):
    response = client.get("/recipe")
    assert response.status_code == 200
    assert b"No recipe suggestions yet" in response.data
    assert b"No ingredients submitted yet" in response.data
