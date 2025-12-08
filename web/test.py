from app.ml_client import get_recommendation

payload = {
    "include": ["egg", "milk", "butter"],
    "cuisine": "italian",
    "allergies": [],
    "taste": ["savory"],
}

result = get_recommendation(payload)
print(result)
