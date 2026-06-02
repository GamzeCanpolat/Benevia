import os
import sys

# 1. Kütüphane Kontrolü
print("1. Adım: Kütüphaneler kontrol ediliyor...")
try:
    import sqlite3
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    print("   ✅ Kütüphaneler yüklü.")
except ImportError as e:
    print(f"   ❌ HATA: Gerekli kütüphane eksik! Lütfen terminale 'pip install firebase-admin' yaz.\nHata detayı: {e}")
    sys.exit()

# 2. Dosya Kontrolü
print("\n2. Adım: Dosyalar kontrol ediliyor...")

# VERİTABANI DOSYA ADINI BURADAN GÜNCELLEDİK
db_name = "benevia.db" 
json_name = "firebase_key.json"

# Dosya var mı kontrolü (Uzantı hatası ihtimaline karşı)
if not os.path.exists(db_name):
    # Belki kullanıcı uzantısız "benevia" olarak kaydetmiştir, onu deneyelim
    if os.path.exists("benevia"):
        db_name = "benevia"
        print(f"   ⚠️ Uyarı: Dosya uzantısız 'benevia' olarak bulundu, bu kullanılıyor.")
    else:
        print(f"   ❌ HATA: '{db_name}' dosyası klasörde bulunamadı!")
        print(f"      Lütfen veritabanı dosyanın adının tam olarak '{db_name}' olduğundan emin ol.")
        sys.exit()
else:
    print(f"   ✅ Veritabanı bulundu: {db_name}")

if not os.path.exists(json_name):
    print(f"   ❌ HATA: '{json_name}' dosyası bulunamadı! Firebase anahtar dosyanın adını kontrol et.")
    sys.exit()
else:
    print(f"   ✅ Key dosyası bulundu: {json_name}")

# 3. Bağlantı Kurma
print("\n3. Adım: Firebase ve SQLite bağlantısı kuruluyor...")
try:
    cred = credentials.Certificate(json_name)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("   ✅ Firebase bağlantısı BAŞARILI.")
    
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print("   ✅ SQLite bağlantısı BAŞARILI.")
except Exception as e:
    print(f"   ❌ BAĞLANTI HATASI: {e}")
    sys.exit()

# 4. Taşıma Fonksiyonu
def tabloyu_tasima(sql_tablo_adi, firebase_koleksiyon_adi, id_sutunu):
    print(f"\n   >>> '{sql_tablo_adi}' tablosu okunuyor...")
    try:
        cursor.execute(f"SELECT * FROM {sql_tablo_adi}")
        veriler = cursor.fetchall()
        
        if len(veriler) == 0:
            print(f"       ⚠️ UYARI: '{sql_tablo_adi}' tablosu BOŞ! Atlanıyor.")
            return

        print(f"       Toplam {len(veriler)} veri bulundu. Yükleniyor...")
        
        batch = db.batch()
        count = 0
        total_count = 0
        
        for satir in veriler:
            doc_data = dict(satir)
            
            # ID sütununu alıp string'e çevir
            if id_sutunu in doc_data:
                doc_id = str(doc_data[id_sutunu])
            else:
                # Eğer ID sütunu bulunamazsa (isim hatası varsa)
                print(f"       ❌ HATA: '{id_sutunu}' sütunu bu tabloda yok!")
                continue

            # Veri temizliği (Boş değerleri temizle)
            doc_data = {k: v for k, v in doc_data.items() if v is not None}

            doc_ref = db.collection(firebase_koleksiyon_adi).document(doc_id)
            batch.set(doc_ref, doc_data)
            
            count += 1
            total_count += 1
            
            if count == 400:
                batch.commit()
                batch = db.batch()
                print(f"       ... {total_count} veri gönderildi.")
                count = 0
        
        if count > 0:
            batch.commit()
            
        print(f"       ✅ '{sql_tablo_adi}' -> '{firebase_koleksiyon_adi}' olarak yüklendi.")
        
    except Exception as e:
        print(f"       ❌ HATA ({sql_tablo_adi}): {e}")

# 5. İşlemleri Başlat
print("\n4. Adım: Veri Transferi Başlıyor...")

tablolar = [
    ("Kategoriler", "categories", "kategori_id"),
    ("Yiyecekler", "foods", "yiyecek_id"),
    ("Hastaliklar", "diseases", "hastalik_id"),
    ("Kurallar", "rules", "kural_id"),
    ("DiyetListeleri", "diet_lists", "liste_id"),
    ("OgunIcerigi", "meal_contents", "detay_id")
]

for t in tablolar:
    tabloyu_tasima(t[0], t[1], t[2])

print("\n🎉 İŞLEM TAMAMLANDI! Firebase konsolunu kontrol edebilirsin.")
conn.close()