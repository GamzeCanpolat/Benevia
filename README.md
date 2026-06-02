# Benevia

Benevia, kullanicinin saglik bilgilerine gore beslenme onerileri ve haftalik ogun plani sunan bir mobil saglikli beslenme uygulamasidir. Proje Flutter tabanli mobil arayuz, Flask tabanli backend API ve Firebase/Firestore entegrasyonundan olusur.

## Ozellikler

- Kullanici profili olusturma ve guncelleme
- Firebase Authentication token dogrulamasi
- Hastalik listesi ve kullanici hastalik bilgisi takibi
- Hastaliklara gore onerilen, yasakli ve notr yiyecek siniflandirmasi
- Kategori bazli yiyecek filtreleme
- Akilli beslenme onerileri
- Haftalik otomatik ogun plani

## Teknolojiler

- Flutter / Dart
- Flask / Python
- Firebase Authentication
- Cloud Firestore
- Firebase Storage
- Android Gradle

## Proje Yapisi

```text
.
+-- app.py                         # Flask API giris noktasi
+-- auth_service.py                # Kullanici kayit/giris servisleri
+-- config.py                      # Backend ayarlari
+-- db.py                          # Firebase Admin ve Firestore baglantisi
+-- meal_plan_service.py           # Haftalik ogun plani mantigi
+-- profile_service.py             # Kullanici profil islemleri
+-- recommendation_services.py     # Beslenme onerisi mantigi
+-- diseases.py                    # Hastalik verileri
+-- tasi.py                        # Veri tasima yardimci scripti
+-- benevia/                       # Flutter mobil uygulamasi
    +-- android/
    +-- assets/
    +-- firebase.json
    +-- pubspec.yaml
    +-- pubspec.lock
```

## Backend Kurulumu

1. Python sanal ortamini olusturun ve aktif edin.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Gerekli paketleri yukleyin.

```bash
pip install flask firebase-admin
```

3. Firebase Admin SDK servis anahtarinizi indirin ve `config.py` icindeki `CERT_PATH` degerini kendi dosya yolunuza gore guncelleyin.

```python
CERT_PATH = r"C:\path\to\firebase_key.json"
```

4. Backend API'yi calistirin.

```bash
python app.py
```

API varsayilan olarak `http://localhost:5000` adresinde calisir.

## Mobil Uygulama Kurulumu

1. Flutter projesi klasorune girin.

```bash
cd benevia
```

2. Paketleri yukleyin.

```bash
flutter pub get
```

3. Uygulamayi calistirin.

```bash
flutter run
```

## API Endpointleri

| Metot | Endpoint | Aciklama |
| --- | --- | --- |
| GET | `/diseases` | Hastalik listesini getirir |
| GET | `/profile` | Kullanici profilini getirir |
| POST | `/profile` | Kullanici profilini gunceller |
| GET | `/smart-recommendations` | Kullaniciya ozel beslenme onerilerini getirir |
| GET | `/foods` | Yiyecekleri kategori ve hastalik durumuna gore listeler |
| GET | `/weekly-meal-plan` | Haftalik ogun planini getirir |

## Notlar

- `config.py` icindeki Firebase Admin SDK yolu her bilgisayarda farkli olacagi icin yerel olarak guncellenmelidir.
- Firebase servis hesabi anahtar dosyalari Git'e eklenmemelidir. Bu proje icin `.gitignore` dosyasinda bu tur dosyalar dislanmistir.
- Flutter build ve cache klasorleri Git'e eklenmez; gerekli dosyalar `flutter pub get` ile tekrar uretilir.
