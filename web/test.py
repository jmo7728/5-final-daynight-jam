from ml_subsystem import get_recommendation

payload = {
    "include": ["tomatoes", "onions"],
    "cuisine": "",
    "allergies": [],
    "taste": [""],
}

result = get_recommendation(payload)
print(result)
