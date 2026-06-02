# -----------------------------------------------------
# app.py — ANA FLASK BACKEND (GERÇEK MOD)
# -----------------------------------------------------

from flask import Flask, request, jsonify
from functools import wraps

from config import TEST_MODE
from recommendation_services import build_recommendations_for_user
from profile_service import get_user_profile, update_user_profile
from meal_plan_service import build_weekly_meal_plan
from db import db
from firebase_admin import auth

# -----------------------------------------------------
# Flask App
# -----------------------------------------------------
app = Flask(__name__)


# -----------------------------------------------------
# TOKEN DOĞRULAMA MIDDLEWARE
# -----------------------------------------------------
def verify_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        # 🎯 TEST MODE (Token doğrulama kapalı)
        if TEST_MODE:
            print("TEST MODU AKTİF → uid=TEST_USER (Token doğrulama yok)")
            kwargs["uid"] = "TEST_USER"
            return f(*args, **kwargs)

        # 🎯 GERÇEK MODE — Token zorunlu
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Authorization header eksik veya hatalı. "
                         "Format: 'Authorization: Bearer <token>' olmalı."
            }), 401

        id_token = auth_header.split(" ")[1].strip()

        try:
            decoded = auth.verify_id_token(id_token)
            uid = decoded.get("uid")

            if not uid:
                return jsonify({"error": "Token doğrulandı ama uid yok."}), 401

            kwargs["uid"] = uid

        except Exception as e:
            return jsonify({
                "error": "Token doğrulanamadı.",
                "detail": str(e)
            }), 401

        return f(*args, **kwargs)

    return wrapper


# -----------------------------------------------------
# 📌 1) HASTALIK LİSTESİ ENDPOINT (Flutter için)
# -----------------------------------------------------
@app.route("/diseases", methods=["GET"])
def get_diseases():
    diseases = [
        {"id": 1, "name": "Gastrit"},
        {"id": 2, "name": "Reflü"},
        {"id": 3, "name": "Mide Ülseri"},
        {"id": 4, "name": "Çölyak"},
        {"id": 5, "name": "Diyabet (Tip 2 Diyabet)"},
        {"id": 6, "name": "Hipertansiyon"},
        {"id": 7, "name": "Böbrek Yetmezliği"},
        {"id": 8, "name": "Laktoz İntoleransı"},
        {"id": 9, "name": "İrritabl Bağırsak Sendromu (IBS)"},
        {"id": 10, "name": "Gut Hastalığı"},
        {"id": 11, "name": "Demir Eksikliği Anemisi"},
        {"id": 12, "name": "Yüksek Kolesterol"}
    ]

    return jsonify(diseases), 200


# -----------------------------------------------------
# 📌 2) PROFİL GETİRME
# -----------------------------------------------------
@app.route("/profile", methods=["GET"])
@verify_token
def get_profile(uid):
    user = get_user_profile(uid)
    if not user:
        return jsonify({"error": "Kullanıcı profili bulunamadı."}), 404
    return jsonify(user)


# -----------------------------------------------------
# 📌 3) PROFİL GÜNCELLEME
# -----------------------------------------------------
@app.route("/profile", methods=["POST"])
@verify_token
def update_profile_route(uid):
    incoming = request.json or {}
    updated = update_user_profile(uid, incoming)

    if updated is None:
        return jsonify({"error": "Geçerli alan yok."}), 400

    return jsonify({
        "message": "Profil güncellendi.",
        "data": updated
    })


# -----------------------------------------------------
# 📌 4) AKILLI ÖNERİ SİSTEMİ
# -----------------------------------------------------
@app.route("/smart-recommendations", methods=["GET"])
@verify_token
def smart_recommendations(uid):
    user, recommended, forbidden = build_recommendations_for_user(uid)

    if user is None:
        return jsonify({"error": "Kullanıcı bulunamadı."}), 404

    return jsonify({
        "user": user,
        "recommended": recommended,
        "forbidden": forbidden,
        "counts": {
            "recommended": len(recommended),
            "forbidden": len(forbidden)
        }
    })

# -----------------------------------------------------
#  6) TÜM YİYECEKLER + KATEGORİ & HASTALIK FİLTRESİ
# -----------------------------------------------------
@app.route("/foods", methods=["GET"])
@verify_token
def get_foods(uid):

    # 1) Tüm yiyecekleri çek
    foods = []
    for doc in db.collection("foods").stream():
        f = doc.to_dict()

        try:
            f["yiyecek_id"] = int(f.get("yiyecek_id"))
        except:
            continue

        if "kategori" in f and isinstance(f["kategori"], str):
            f["kategori"] = f["kategori"].lower()

        foods.append(f)

    # 2) Kullanıcının hastalık bilgisi (normalize!)
    user_doc = db.collection("users").document(uid).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}

    diseases = user_data.get("diseases", [])







    # aynı recommendation_services.py’deki gibi normalize edelim
    if isinstance(diseases, (int, float, str)):
        diseases = [diseases]

    if isinstance(diseases, dict):
        diseases = list(diseases.keys())

    user_diseases = []
    for d in diseases:
        try:
            user_diseases.append(int(d))
        except:
            pass

    # 3) Rules tablosuna göre yiyeceklerin yasak/serbest durumu
    rule_map = {}  # yiyecek_id → durum (0 yasak, 1 serbest)

    for doc in db.collection("rules").stream():
        rule = doc.to_dict()

        try:
            h = int(rule.get("hastalik_id"))
            y = int(rule.get("yiyecek_id"))
            durum = int(rule.get("durum"))
        except:
            continue

        if h in user_diseases:
            rule_map[y] = durum

    # 4) Kategori filtresi
    # 4) Kategori filtresi (kategori_id'ye göre)
# 4) kategori filtresi (kategori_id'ye göre)
    category = request.args.get("category")
    if category: 
       try:
        cid = int(category)
        foods = [f for f in foods if int(f.get("kategori_id", -1)) == cid]
       except:
        foods = []
    # 5) Hastalığa göre yiyeceğe status ekle
    for f in foods:
        yid = f["yiyecek_id"]

        if yid in rule_map:
            f["status"] = "recommended" if rule_map[yid] == 1 else "forbidden"
        else:
            f["status"] = "neutral"

    return jsonify({
        "uid": uid,
        "count": len(foods),
        "foods": foods
    }), 200
# -----------------------------------------------------
# 📌 5) 7 GÜNLÜK OTOMATİK DİYET PLANI
# -----------------------------------------------------
@app.route("/weekly-meal-plan", methods=["GET"])
@verify_token
def weekly_meal_plan(uid):
    plan = build_weekly_meal_plan(uid)

    if plan is None:
        return jsonify({"error": "Diyet planı bulunamadı."}), 404

    return jsonify({
        "uid": uid,
        "weekly_meal_plan": plan
    })


# -----------------------------------------------------
# ÇALIŞTIR
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)