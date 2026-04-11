"""
QualityPulse — Seed Script
Populates quality.db with realistic aluminum die casting data.
Only seeds if tables are empty.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
import math
from datetime import datetime, timedelta
from db.database import init_db, get_connection

random.seed(42)

DEFECT_TYPES = [
    "Boyutsal Sapma",
    "Yüzey Hatası",
    "Gözeneklilik",
    "Çekme Boşluğu",
    "Çapak",
]

SHIFTS = ["A", "B", "C"]
LINES = ["Hat-1", "Hat-2"]

MEASUREMENT_POINTS = [
    ("Çap-A", 50.00, 50.10, 49.90),   # (name, nominal, USL, LSL)
    ("Çap-B", 25.00, 25.05, 24.95),
    ("Derinlik-C", 12.50, 12.60, 12.40),
    ("Kalınlık-D", 8.00, 8.08, 7.92),
    ("Uzunluk-E", 100.00, 100.20, 99.80),
]

OWNERS = ["Ahmet Yılmaz", "Fatma Demir", "Mehmet Kaya", "Ayşe Çelik", "Hasan Öztürk"]

PROCESS_STEPS = [
    "Eritme", "Döküm", "Kalıp Kapatma", "Basınç Uygulama",
    "Soğutma", "Kalıp Açma", "Parça Çıkarma", "Çapak Alma",
    "Yüzey İşleme", "Kalite Kontrol",
]

FAILURE_MODES = [
    ("Eritme",          "Sıcaklık sapması",     "Yetersiz akışkanlık"),
    ("Eritme",          "Gaz tutuklanması",     "Gözeneklilik"),
    ("Döküm",           "Erken katılaşma",      "Eksik dolum"),
    ("Döküm",           "Metal sıçraması",      "Yüzey hatası"),
    ("Kalıp Kapatma",   "Yetersiz kenetleme",   "Flash / çapak"),
    ("Basınç Uygulama", "Düşük basınç",         "Çekme boşluğu"),
    ("Basınç Uygulama", "Yüksek basınç",        "Kalıp çatlağı"),
    ("Soğutma",         "Yavaş soğutma",        "Büzülme"),
    ("Soğutma",         "Hızlı soğutma",        "İç gerilme"),
    ("Kalıp Açma",      "Yapışma",              "Parça hasarı"),
    ("Parça Çıkarma",   "İtici arızası",        "Boyutsal sapma"),
    ("Çapak Alma",      "Yetersiz kesim",       "Artan çapak"),
    ("Yüzey İşleme",    "Kimyasal sapması",     "Renk farklılığı"),
    ("Kalite Kontrol",  "Yanlış ölçüm",         "Hatalı kabul/ret"),
    ("Kalıp Kapatma",   "Aşınmış kalıp",        "Boyutsal tutarsızlık"),
    ("Döküm",           "Kirli metal",          "İçyapı kusuru"),
    ("Eritme",          "Yanlış alaşım",        "Mekanik özellik kaybı"),
    ("Soğutma",         "Soğutma kanalı tıkanması", "Bölgesel sertlik"),
    ("Basınç Uygulama", "Atış hız sapması",     "Türbülans / gaz"),
    ("Yüzey İşleme",    "Aşırı işleme",         "Tolerans kaybı"),
]

CAPA_DATA = [
    {
        "title": "Gözeneklilik artışı Hat-1",
        "description": "Hat-1'de son 2 haftada %3.5'e çıkan gözeneklilik oranı.",
        "root_cause": "Eritme fırınında sıcaklık kontrolü yetersiz.",
        "corrective_action": "PID kontrol kalibrasyonu yapıldı.",
        "owner": "Ahmet Yılmaz", "criticality": "Critical", "status": "Closed",
        "days_offset_created": -60, "days_offset_due": -30, "days_offset_closed": -20,
    },
    {
        "title": "Çapak oranı hedef üstünde",
        "description": "Shift-B'de üretilen parçaların %8'inde kabul edilemez çapak.",
        "root_cause": "Kalıp kenetleme kuvveti yetersiz.",
        "corrective_action": "Kenetleme basıncı 200 bar'dan 230 bar'a yükseltildi.",
        "owner": "Fatma Demir", "criticality": "Major", "status": "Closed",
        "days_offset_created": -50, "days_offset_due": -20, "days_offset_closed": -15,
    },
    {
        "title": "Boyutsal sapma Çap-A",
        "description": "Çap-A ölçüm noktasında Cpk 1.0'ın altına düştü.",
        "root_cause": "Kalıp aşınması.",
        "corrective_action": "Kalıp revizyon planlandı.",
        "owner": "Mehmet Kaya", "criticality": "Critical", "status": "In Progress",
        "days_offset_created": -30, "days_offset_due": 10, "days_offset_closed": None,
    },
    {
        "title": "Yüzey hatası müşteri şikayeti",
        "description": "Müşteri XYZ'den 3 adet yüzey hatası şikayeti alındı.",
        "root_cause": None,
        "corrective_action": None,
        "owner": "Ayşe Çelik", "criticality": "Critical", "status": "Open",
        "days_offset_created": -10, "days_offset_due": 20, "days_offset_closed": None,
    },
    {
        "title": "Hat-2 OEE düşüşü",
        "description": "Hat-2 OEE %75'in altına indi.",
        "root_cause": "Plansız duruşlar artışı.",
        "corrective_action": "Önleyici bakım sıklığı artırıldı.",
        "owner": "Hasan Öztürk", "criticality": "Major", "status": "In Progress",
        "days_offset_created": -25, "days_offset_due": 5, "days_offset_closed": None,
    },
    {
        "title": "Çekme boşluğu oranı artışı",
        "description": "Çekme boşluğu hat-1'de %2'yi aştı.",
        "root_cause": "Soğutma süresi kısaltılmış.",
        "corrective_action": "Soğutma parametreleri restore edildi.",
        "owner": "Ahmet Yılmaz", "criticality": "Major", "status": "Closed",
        "days_offset_created": -45, "days_offset_due": -10, "days_offset_closed": -5,
    },
    {
        "title": "Kalıp ömrü takip sistemi eksikliği",
        "description": "Kalıp shot sayısı manuel takip ediliyor, hata riski yüksek.",
        "root_cause": "Otomatik sayaç yok.",
        "corrective_action": "SCADA entegrasyonu planlandı.",
        "owner": "Mehmet Kaya", "criticality": "Minor", "status": "Open",
        "days_offset_created": -20, "days_offset_due": 30, "days_offset_closed": None,
    },
    {
        "title": "Ölçüm cihazı kalibrasyonu gecikti",
        "description": "3 adet kumpas kalibrasyonu 2 ay gecikmiş.",
        "root_cause": "Kalibrasyon planlaması yapılmamış.",
        "corrective_action": "Harici laboratuvara gönderildi.",
        "owner": "Fatma Demir", "criticality": "Major", "status": "Closed",
        "days_offset_created": -70, "days_offset_due": -40, "days_offset_closed": -35,
    },
    {
        "title": "İş başı eğitim eksikliği",
        "description": "Yeni operatörler SOP'lara göre eğitim almadı.",
        "root_cause": "Eğitim programı güncel değil.",
        "corrective_action": "Eğitim materyalleri güncelleniyor.",
        "owner": "Ayşe Çelik", "criticality": "Minor", "status": "In Progress",
        "days_offset_created": -15, "days_offset_due": 15, "days_offset_closed": None,
    },
    {
        "title": "Döküm gözenek üstü limit ihlali",
        "description": "X-ray kontrol raporunda %4 gözenek tespit edildi.",
        "root_cause": "Gaz giderme süreci yetersiz.",
        "corrective_action": "Degassing süresini 3 dakika artır.",
        "owner": "Hasan Öztürk", "criticality": "Critical", "status": "Open",
        "days_offset_created": -5, "days_offset_due": 25, "days_offset_closed": None,
    },
    {
        "title": "Hat-1 shift-C kalite düşüşü",
        "description": "Gece vardiyasında hata oranı %6'ya çıktı.",
        "root_cause": "Deneyimsiz operatör görevlendirilmesi.",
        "corrective_action": "Deneyimli operatör desteği atandı.",
        "owner": "Ahmet Yılmaz", "criticality": "Major", "status": "Closed",
        "days_offset_created": -35, "days_offset_due": -5, "days_offset_closed": -3,
    },
    {
        "title": "PPM hedefi aşıldı (Q3)",
        "description": "Q3 PPM değeri 1200 ile hedefin (%800) üzerinde.",
        "root_cause": "Çoklu hata türü aynı anda artış gösterdi.",
        "corrective_action": "Köklü neden analizi yapıldı, aksiyon planı oluşturuldu.",
        "owner": "Fatma Demir", "criticality": "Critical", "status": "In Progress",
        "days_offset_created": -40, "days_offset_due": 0, "days_offset_closed": None,
    },
    {
        "title": "SOP güncellemesi gecikti",
        "description": "2 adet SOP 6 aydan uzun süredir güncellenmedi.",
        "root_cause": "Süreç değişimleri dokümante edilmedi.",
        "corrective_action": "Tüm SOP'ların 30 gün içinde revizyonu planlandı.",
        "owner": "Mehmet Kaya", "criticality": "Minor", "status": "Open",
        "days_offset_created": -12, "days_offset_due": 18, "days_offset_closed": None,
    },
    {
        "title": "Soğutma suyu kalitesi",
        "description": "Soğutma suyunda kireç birikimi tespit edildi.",
        "root_cause": "Su arıtma filtreleri değiştirilmedi.",
        "corrective_action": "Filtreler değiştirildi, periyodik kontrol eklendi.",
        "owner": "Hasan Öztürk", "criticality": "Major", "status": "Closed",
        "days_offset_created": -55, "days_offset_due": -25, "days_offset_closed": -20,
    },
    {
        "title": "İç tedarikçi kalite denetimi",
        "description": "İç tedarikçi XY'nin ürünlerinde %2 hata oranı.",
        "root_cause": "Tedarikçi kalite planı eksik.",
        "corrective_action": "Tedarikçi geliştirme programı başlatıldı.",
        "owner": "Ayşe Çelik", "criticality": "Major", "status": "Open",
        "days_offset_created": -8, "days_offset_due": 40, "days_offset_closed": None,
    },
]


def seed_defects(conn):
    count = conn.execute("SELECT COUNT(*) FROM defects").fetchone()[0]
    if count > 0:
        print(f"  Defects already seeded ({count} records), skipping.")
        return

    today = datetime.today()
    records = []
    for day_offset in range(89, -1, -1):
        date = (today - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        for shift in SHIFTS:
            for line in LINES:
                # Each shift has 1-3 defect types recorded
                n_types = random.randint(1, 3)
                defect_sample = random.sample(DEFECT_TYPES, n_types)
                total_produced = random.randint(200, 400)
                for defect_type in defect_sample:
                    # Seasonal trend: slight improvement over time
                    base_qty = random.randint(1, 20)
                    # Add occasional spike
                    if random.random() < 0.05:
                        base_qty += random.randint(10, 30)
                    records.append((
                        date, shift, defect_type, base_qty, total_produced, line, ""
                    ))

    conn.executemany(
        "INSERT INTO defects (date, shift, defect_type, quantity, total_produced, line, notes) VALUES (?,?,?,?,?,?,?)",
        records
    )
    conn.commit()
    print(f"  Seeded {len(records)} defect records.")


def seed_measurements(conn):
    count = conn.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
    if count > 0:
        print(f"  Measurements already seeded ({count} records), skipping.")
        return

    today = datetime.today()
    records = []
    # 500 total measurements spread across 5 points, 2 lines
    for _ in range(500):
        mp, nominal, usl, lsl = random.choice(MEASUREMENT_POINTS)
        line = random.choice(LINES)
        sigma = (usl - nominal) / 4  # process sigma: moderate capability
        value = round(random.gauss(nominal + random.uniform(-0.01, 0.01), sigma), 4)
        # Timestamps spread over last 90 days
        ts = today - timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        records.append((
            ts.strftime("%Y-%m-%d %H:%M:%S"),
            line, mp, value, nominal, usl, lsl
        ))

    conn.executemany(
        "INSERT INTO measurements (timestamp, line, measurement_point, value, nominal, tolerance_upper, tolerance_lower) VALUES (?,?,?,?,?,?,?)",
        records
    )
    conn.commit()
    print(f"  Seeded {len(records)} measurement records.")


def seed_capa(conn):
    count = conn.execute("SELECT COUNT(*) FROM capa").fetchone()[0]
    if count > 0:
        print(f"  CAPA already seeded ({count} records), skipping.")
        return

    today = datetime.today()
    records = []
    for c in CAPA_DATA:
        created = (today + timedelta(days=c["days_offset_created"])).strftime("%Y-%m-%d")
        due = (today + timedelta(days=c["days_offset_due"])).strftime("%Y-%m-%d")
        closed = None
        if c["days_offset_closed"] is not None:
            closed = (today + timedelta(days=c["days_offset_closed"])).strftime("%Y-%m-%d")
        records.append((
            created, c["title"], c["description"],
            c.get("root_cause"), c.get("corrective_action"),
            c["owner"], due, c["criticality"], c["status"], closed
        ))

    conn.executemany(
        """INSERT INTO capa
           (created_date, title, description, root_cause, corrective_action,
            owner, due_date, criticality, status, closed_date)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        records
    )
    conn.commit()
    print(f"  Seeded {len(records)} CAPA records.")


def seed_fmea(conn):
    count = conn.execute("SELECT COUNT(*) FROM fmea").fetchone()[0]
    if count > 0:
        print(f"  FMEA already seeded ({count} records), skipping.")
        return

    fmea_rows = [
        # (step, mode, effect, S, O, D, controls, action, owner, status)
        ("Eritme", "Sıcaklık sapması", "Yetersiz akışkanlık, eksik dolum", 7, 4, 3,
         "Termokupl izleme, alarm", "PID kalibrasyonu", "Ahmet Yılmaz", "Closed"),
        ("Eritme", "Gaz tutuklanması", "Gözeneklilik", 8, 5, 4,
         "Degassing ünitesi", "Süre optimize et", "Ahmet Yılmaz", "In Progress"),
        ("Eritme", "Yanlış alaşım", "Mekanik özellik kaybı", 9, 2, 3,
         "Spektrometre analiz", "Giriş kalite kontrolü", "Fatma Demir", "Open"),
        ("Döküm", "Erken katılaşma", "Eksik dolum", 8, 4, 4,
         "Sıcaklık takibi", "Kalıp ön ısıtma prosedürü", "Mehmet Kaya", "Open"),
        ("Döküm", "Metal sıçraması", "Yüzey hatası, operatör güvenliği", 6, 3, 2,
         "Muhafaza paneli", "Muhafaza kontrolü", "Mehmet Kaya", "Closed"),
        ("Döküm", "Kirli metal", "İçyapı kusuru", 8, 3, 4,
         "Cüruf alma prosedürü", "Fırın temizlik süreci", "Ahmet Yılmaz", "Open"),
        ("Kalıp Kapatma", "Yetersiz kenetleme", "Flash / çapak", 6, 5, 3,
         "Basınç sensörü", "Kenetleme kalibrasyonu", "Hasan Öztürk", "Closed"),
        ("Kalıp Kapatma", "Aşınmış kalıp", "Boyutsal tutarsızlık", 7, 6, 4,
         "Shot sayaç", "PM programı", "Hasan Öztürk", "In Progress"),
        ("Basınç Uygulama", "Düşük basınç", "Çekme boşluğu", 8, 4, 3,
         "Basınç sensörü alarmı", "Baskı profili doğrulama", "Fatma Demir", "Open"),
        ("Basınç Uygulama", "Yüksek basınç", "Kalıp çatlağı", 9, 3, 3,
         "Limit switch", "Güvenli limit revizyonu", "Fatma Demir", "Open"),
        ("Basınç Uygulama", "Atış hız sapması", "Türbülans / gaz", 7, 5, 4,
         "Hız sensörü", "Simülasyon doğrulama", "Mehmet Kaya", "Open"),
        ("Soğutma", "Yavaş soğutma", "Büzülme", 7, 4, 4,
         "Zaman rölesi", "Soğutma profili optimizasyonu", "Ahmet Yılmaz", "Closed"),
        ("Soğutma", "Hızlı soğutma", "İç gerilme / çatlak", 8, 3, 5,
         "Termal görüntüleme", "Kademeli soğutma prosedürü", "Ahmet Yılmaz", "In Progress"),
        ("Soğutma", "Soğutma kanalı tıkanması", "Bölgesel sertlik", 7, 3, 4,
         "Akış ölçer", "Kanal temizlik planı", "Hasan Öztürk", "Open"),
        ("Kalıp Açma", "Yapışma", "Parça hasarı", 6, 4, 3,
         "Ayırıcı spreyi otomasyonu", "Spreyi optimize et", "Mehmet Kaya", "Closed"),
        ("Parça Çıkarma", "İtici arızası", "Boyutsal sapma, parça hasarı", 7, 3, 3,
         "Sensörlü itici kontrolü", "Preventif bakım", "Hasan Öztürk", "Open"),
        ("Çapak Alma", "Yetersiz kesim", "Artan çapak", 5, 5, 3,
         "Görsel kontrol", "Pres parametre revizyonu", "Fatma Demir", "Closed"),
        ("Yüzey İşleme", "Kimyasal sapması", "Renk farklılığı", 5, 3, 3,
         "Kimyasal analiz", "Dozaj kontrolü", "Ayşe Çelik", "Open"),
        ("Yüzey İşleme", "Aşırı işleme", "Tolerans kaybı", 8, 2, 4,
         "Zaman kontrolü", "Otomatik duruş sistemi", "Ayşe Çelik", "Open"),
        ("Kalite Kontrol", "Yanlış ölçüm", "Hatalı kabul/ret kararı", 9, 3, 2,
         "Kalibrasyon programı", "MSA çalışması", "Ayşe Çelik", "In Progress"),
    ]

    conn.executemany(
        """INSERT INTO fmea
           (process_step, failure_mode, failure_effect, severity, occurrence, detection,
            current_controls, recommended_action, responsible, status)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        fmea_rows
    )
    conn.commit()
    print(f"  Seeded {len(fmea_rows)} FMEA records.")


def run():
    print("QualityPulse — Database Seed")
    print("=" * 40)
    init_db()
    conn = get_connection()
    seed_defects(conn)
    seed_measurements(conn)
    seed_capa(conn)
    seed_fmea(conn)
    conn.close()
    print("=" * 40)
    print("Seed complete.")


if __name__ == "__main__":
    run()
