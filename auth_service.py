# -----------------------------------------------------
# auth_service.py — REGISTER & LOGIN
# -----------------------------------------------------

import uuid
from db import db
from profile_service import create_empty_user_profile

# -----------------------------------------------------
# REGISTER
# -----------------------------------------------------
def register_user(email, password, name, surname):

    # Email zaten var mı?
    query = db.collection("users").where("email", "==", email).stream()
    for q in query:
        return None, "Bu email zaten kayıtlı."

    # UID üret
    uid = str(uuid.uuid4())

    # Kullanıcı verisi
    user_data = {
        "uid": uid,
        "email": email,
        "password": password,
        "name": name,
        "surname": surname,
        "gender": "",
        "age": 0,
        "height": 0,
        "weight": 0,
        "diseases": []
    }

    db.collection("users").document(uid).set(user_data)

    return uid, None


# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
def login_user(email, password):

    # Mail ile kullanıcıyı ara
    users = db.collection("users").where("email", "==", email).stream()

    for user in users:
        data = user.to_dict()
        if data.get("password") == password:
            return data.get("uid"), None

        return None, "Şifre hatalı."

    return None, "Kullanıcı bulunamadı."
