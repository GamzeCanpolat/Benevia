# -----------------------------------------------------
# profile_service.py — USER PROFILE GET/UPDATE
# -----------------------------------------------------

from db import db


# Kullanıcıyı getir
def get_user_profile(uid):
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None


# Varsayılan boş profil oluştur (register sırasında kullanılır)
def create_empty_user_profile(uid):
    db.collection("users").document(uid).set({
        "uid": uid,
        "email": "",
        "password": "",
        "name": "",
        "surname": "",
        "gender": "",
        "age": 0,
        "height": 0,
        "weight": 0,
        "diseases": []
    }, merge=True)


# Profil güncelle
def update_user_profile(uid, data):

    allowed_fields = ["name", "surname", "gender", "age", "height", "weight", "diseases"]

    filtered = {k: v for k, v in data.items() if k in allowed_fields}

    if not filtered:
        return None

    ref = db.collection("users").document(uid)
    ref.set(filtered, merge=True)

    return filtered
