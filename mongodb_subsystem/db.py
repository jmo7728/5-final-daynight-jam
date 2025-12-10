import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# In-memory fallback stores
_memory = {
    "users": {},
    "recipes": {}
}

mongo_client = None
db = None
USE_MONGO = False

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["food_recommendation"]
users_collection = db["users"]

def init_db_client(app=None):
    global mongo_client, db, USE_MONGO
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        try:
            mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            # trigger server selection
            mongo_client.server_info()
            db = mongo_client.get_database()  # default from URI
            USE_MONGO = True
            print("Connected to MongoDB via MONGO_URI")
            return
        except PyMongoError as e:
            print("Warning: cannot connect to MongoDB, falling back to in-memory. Error:", e)

    # fallback
    mongo_client = None
    db = None
    USE_MONGO = False
    print("Using in-memory DB fallback")

# user helpers
def create_user(username, password_hash):
    if USE_MONGO:
        users = db.get_collection("users")
        if users.find_one({"username": username}):
            return False
        users.insert_one({"username": username, "password": password_hash})
        return True
    else:
        if username in _memory["users"]:
            return False
        _memory["users"][username] = {"username": username, "password": password_hash}
        return True

def find_user(username):
    if USE_MONGO:
        users = db.get_collection("users")
        return users.find_one({"username": username})
    else:
        return _memory["users"].get(username)

# recipe store (for placeholder recipes you can insert)
def insert_recipe(doc):
    if USE_MONGO:
        recipes = db.get_collection("recipes")
        return recipes.insert_one(doc).inserted_id
    else:
        _id = str(len(_memory["recipes"]) + 1)
        doc["_id"] = _id
        _memory["recipes"][_id] = doc
        return _id

def find_recipe_by_id(rid):
    if USE_MONGO:
        recipes = db.get_collection("recipes")
        return recipes.find_one({"_id": rid})
    else:
        return _memory["recipes"].get(rid)