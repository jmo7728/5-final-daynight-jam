from app.ml_client import get_recommendation

payload = {
    "include": ["tomatoes", "onions"],
    "cuisine": "",
    "allergies": [],
    "taste": [""],
}

result = get_recommendation(payload)
print(result)
