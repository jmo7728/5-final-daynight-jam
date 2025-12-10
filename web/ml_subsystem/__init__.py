# ml_subsystem/__init__.py
from pathlib import Path
import os
from typing import Any, Dict

from .client import MLClient

_default_client: MLClient | None = None

def _get_default_client() -> MLClient:
    global _default_client
    if _default_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

        csv_path = os.getenv("RECIPES_CSV_PATH")
        if csv_path is None:
            repo_root = Path(__file__).resolve().parents[1]
            csv_path = repo_root / "web" / "app" / "dataset" / "1_Recipe_csv.csv"

        _default_client = MLClient(api_key=api_key, csv_path=Path(csv_path))

    return _default_client

def get_recommendation(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _get_default_client().get_recommendation(payload)

def replace_ingredient(recipe: Dict[str, Any], from_name: str, to_name: str) -> Dict[str, Any]:
    return _get_default_client().replace_ingredient(recipe, from_name, to_name)
