import pytest
from db import create_user, find_user, insert_recipe, find_recipe_by_id

def test_create_user_success():
    result = create_user("bob", "abc123")
    assert result is True

def test_create_user_dupe():
    create_user("jen", "abc123")  
    result = create_user("jen", "abc456")  
    assert result is False

def test_find_user_exists():
    create_user("joe", "abc123")
    user = find_user("joe")
    assert user["username"] == "joe"
    assert user["password"] == "abc123"

def test_find_user_nonexistent():
    user = find_user("doesnotexist")
    assert user is None

def test_insert_recipe_success():
    recipe = {"name": "Test Recipe", "ingredients": ["ing1"]}
    recipe_id = insert_recipe(recipe)
    assert recipe_id is not None
    assert isinstance(recipe_id, str)  

def test_find_recipe_exists():
    recipe = {"name": "Another Recipe", "ingredients": ["ing2"]}
    recipe_id = insert_recipe(recipe)
    stored = find_recipe_by_id(recipe_id)
    assert stored["name"] == "Another Recipe"
    assert "ing2" in stored["ingredients"]

def test_find_recipe_nonexistent():
    stored = find_recipe_by_id("999")
    assert stored is None