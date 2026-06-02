# -----------------------------------------------------
# recommendation_services.py — KURAL BAZLI ÖNERİ
# -----------------------------------------------------

from db import db


# USER GET
def get_user(uid: str):
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        return None

    data = doc.to_dict()

    diseases = data.get("diseases", [])

    if isinstance(diseases, (int, float, str)):
        diseases = [diseases]

    if isinstance(diseases, dict):
        diseases = list(diseases.keys())

    disease_ids = []
    for d in diseases:
        try:
            disease_ids.append(int(d))
        except:
            pass

    data["diseases"] = disease_ids
    return data



def get_rules_for_diseases(disease_ids):
    rules = []
    for doc in db.collection("rules").stream():
        r = doc.to_dict()

        try:
            h = int(r.get("hastalik_id"))
        except:
            continue

        if h in disease_ids:
            try:
                r["yiyecek_id"] = int(r.get("yiyecek_id"))
            except:
                continue

            rules.append(r)

    return rules



def get_foods_by_yiyecek_id():
    foods = {}
    for doc in db.collection("foods").stream():
        f = doc.to_dict()

        try:
            yid = int(f.get("yiyecek_id"))
        except:
            continue

        foods[yid] = f

    return foods



def build_recommendations_for_user(uid):
    user = get_user(uid)
    if not user:
        return None, None, None

    diseases = user.get("diseases", [])

    if not diseases:
        return user, [], []

    rules = get_rules_for_diseases(diseases)
    foods = get_foods_by_yiyecek_id()

    recommended = []
    forbidden = []

    for rule in rules:
        yid = rule["yiyecek_id"]
        food = foods.get(yid)

        if food:
            item = {
                "food_id": yid,
                "food_name": food.get("ad"),
                "calories": food.get("kalori"),
                "protein": food.get("protein"),
                "carbs": food.get("karbonhidrat"),
                "fat": food.get("yag"),
                "disease_id": rule.get("hastalik_id"),
                "status": "forbidden" if rule.get("durum") == 0 else "recommended",
                "rule_description": rule.get("aciklama")
            }

            if rule.get("durum") == 0:
                forbidden.append(item)
            else:
                recommended.append(item)

    return user, recommended, forbidden
