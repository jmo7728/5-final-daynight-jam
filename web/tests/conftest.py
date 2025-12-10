import pytest
from app import create_app
import mongodb_subsystem.db as db_mod
from unittest.mock import patch

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",  
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def reset_in_memory_db():
    db_mod._memory["users"].clear()
    db_mod._memory["recipes"].clear()
    db_mod.USE_MONGO = False
    yield

@pytest.fixture()
def mock_ml_client():
    with patch("app.ml_client._get_default_client") as mock_client:
        # Mock get_recommendation
        mock_client.return_value.get_recommendation.return_value = {
            "recipe_id": "1",
            "name": "Mock Recipe",
            "ingredients": ["ingredient1", "ingredient2"],
            "tools": ["pan", "oven"],
            "steps": ["step1", "step2"],
            "substitutions": ["sub1"]
        }

        # Mock replace_ingredient
        mock_client.return_value.replace_ingredient.return_value = {
            "recipe_id": "1",
            "name": "Mock Recipe Updated",
            "ingredients": ["ingredient1", "ingredient2", "ingredient3"],
            "tools": ["pan", "oven"],
            "steps": ["step1", "step2", "step3"],
            "substitutions": ["sub1", "sub2"]
        }

        yield mock_client
