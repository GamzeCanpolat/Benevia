from flask import Blueprint, jsonify

diseases_bp = Blueprint("diseases", __name__)

@diseases_bp.route("/diseases", methods=["GET"])
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
        {"id": 12, "name": "Yüksek Kolesterol"},
    ]
    
    return jsonify(diseases), 200