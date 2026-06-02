# recipe_services.py

from db import db


def add_recipe_service(data):
    """
    Firestore -> recipes koleksiyonuna tarif ekler.
    """
    try:
        doc_ref = db.collection("recipes").add(data)
        return {
            "message": "Tarif başarıyla eklendi.",
            "id": doc_ref[1].id
        }
    except Exception as e:
        return {"error": str(e)}


def get_all_recipes_service():
    """
    recipes koleksiyonundaki tüm tarifleri döner.
    """
    try:
        recipes = []
        docs = db.collection("recipes").stream()

        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id
            recipes.append(item)

        return {
            "count": len(recipes),
            "recipes": recipes
        }
    except Exception as e:
        return {"error": str(e)}
