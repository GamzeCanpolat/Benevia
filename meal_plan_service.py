# -----------------------------------------------------
# meal_plan_service.py — ÖĞÜN AYRIMLI SÜRÜM
# -----------------------------------------------------

from db import db

def get_user_diseases(uid):
    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        return []

    diseases = doc.to_dict().get("diseases", [])

    if isinstance(diseases, dict):
        diseases = list(diseases.keys())

    result = []
    for d in diseases:
        try: 
            result.append(int(d))
        except:
            pass

    return result


def get_diet_list_ids(disease_ids):
    list_ids = []

    for doc in db.collection("diet_lists").stream():
        data = doc.to_dict()

        try:
            if int(data.get("hastalik_id")) in disease_ids:
                list_ids.append(int(data.get("liste_id")))
        except:
            continue

    return sorted(list_ids)


def get_meal_contents(list_id):
    result = []

    for doc in db.collection("meal_contents").stream():
        data = doc.to_dict()

        try:
            if int(data.get("liste_id")) == list_id:
                result.append({
                    "yiyecek_id": int(data.get("yiyecek_id")),
                    "miktar": data.get("miktar"),
                    "ogun_vakti": data.get("ogun_vakti")  # ← YENİ ÖĞÜN ALANI
                })
        except:
            continue

    return result


def get_foods_map():
    foods = {}
    for doc in db.collection("foods").stream():
        f = doc.to_dict()
        try:
            yid = int(f.get("yiyecek_id"))
            foods[yid] = f
        except:
            pass
    return foods


def get_rules_map(disease_ids):
    rules = {}
    for doc in db.collection("rules").stream():
        r = doc.to_dict()
        try:
            if int(r.get("hastalik_id")) in disease_ids:
                rules[int(r.get("yiyecek_id"))] = int(r.get("durum"))
        except:
            pass

    return rules


# -----------------------------------------------------
# ÖĞÜN AYRIMLI 7 GÜNLÜK DİYET PLANI
# -----------------------------------------------------
def build_weekly_meal_plan(uid):

    disease_ids = get_user_diseases(uid)
    if not disease_ids:
        return None

    list_ids = get_diet_list_ids(disease_ids)
    if not list_ids:
        return None

    foods = get_foods_map()
    rules = get_rules_map(disease_ids)

    days = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday"
    ]

    plan = {}

    for day, list_id in zip(days, list_ids):

        # ---- 4 öğün ayrımı burada yapılıyor ----
        day_plan = {
            "sabah": [],
            
            "ogle": [],
            "aksam": [],
            "ara": []
        }

        contents = get_meal_contents(list_id)

        for c in contents:
            yid = c["yiyecek_id"]

            # yasaksa geç
            if yid in rules and rules[yid] == 0:
                continue

            food = foods.get(yid)
            if not food:
                continue

            meal_item = {
                "yiyecek_id": yid,
                "name": food.get("ad"),
                "kalori": food.get("kalori"),
                "protein": food.get("protein"),
                "karbonhidrat": food.get("karbonhidrat"),
                "yag": food.get("yag"),
                "miktar": c.get("miktar"),
            }

            # ---- Öğün dağıtımı ----
            ogun = c.get("ogun_vakti", "").lower()

            if "sabah" in ogun:
                day_plan["sabah"].append(meal_item)
            elif "öğle" in ogun or "ogle" in ogun:
                day_plan["ogle"].append(meal_item)
            elif "akşam" in ogun or "aksam" in ogun:
                day_plan["aksam"].append(meal_item)
            else:
                day_plan["ara"].append(meal_item)

        plan[day] = day_plan

    return plan
