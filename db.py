# -----------------------------------------------------
# db.py — FIREBASE BAĞLANTISI
# -----------------------------------------------------

import firebase_admin
from firebase_admin import credentials, firestore
from config import CERT_PATH

# Tek sefer initialize
if not firebase_admin._apps:
    cred = credentials.Certificate(CERT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()
print("Firestore bağlantısı başarılı.")
