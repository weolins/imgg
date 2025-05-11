import os
import json
import base64
from firebase_admin import credentials, firestore, initialize_app

# Load base64-encoded Firebase key from environment variable
key_b64 = os.getenv("FIREBASE_KEY")

if not key_b64:
    raise RuntimeError("FIREBASE_KEY environment variable not found.")

# Decode and load credentials
try:
    key_json = base64.b64decode(key_b64).decode("utf-8")
    key_dict = json.loads(key_json)
except Exception as e:
    raise RuntimeError("Failed to decode FIREBASE_KEY. Check base64 format.") from e

cred = credentials.Certificate(key_dict)
initialize_app(cred)
db = firestore.client()
