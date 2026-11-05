"""Değerlendirme için farklı düzenlerde örnek (uydurma) fatura PDF'leri ve doğru cevap JSON'ları üretir."""
import json, os, random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "C:/Windows/Fonts/arial.ttf"
pdfmetrics.registerFont(TTFont("Ar", FONT))
pdfmetrics.registerFont(TTFont("ArB", FONT.replace("arial", "arialbd")))
random.seed(7)

SATICI = [("Örnek Kırtasiye Ltd. Şti.", "1234567890"), ("Mavi Lojistik A.Ş.", "2345678901"), ("Yıldız Yazılım A.Ş.", "3456789012"),
          ("Deniz Gıda San. Tic. Ltd.", "4567890123"), ("Kuzey Enerji A.Ş.", "5678901234"), ("Atlas Mobilya Ltd. Şti.", "6789012345")]
ALICI = [("Örnek Teknoloji A.Ş.", "9876543210"), ("Güneş İnşaat Ltd. Şti.", "8765432109")]
KALEM = [("A4 Fotokopi Kağıdı (koli)", 420.0), ("Toner Kartuşu", 1850.0), ("Nakliye Hizmeti", 3200.0), ("Yazılım Lisansı (yıllık)", 12500.0),
         ("Danışmanlık (saat)", 1500.0), ("Ofis Sandalyesi", 4750.0), ("Elektrik Tüketimi (kWh)", 3.85), ("Kahve (kg)", 640.0)]


def tl(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fatura(i, duzen):
    s, a = random.choice(SATICI), random.choice(ALICI)
    kalemler = []
    for ad, fiyat in random.sample(KALEM, random.randint(1, 4)):
        adet = random.randint(1, 12) if fiyat > 10 else random.randint(500, 2500)
        kalemler.append({"aciklama": ad, "miktar": adet, "birim_fiyat": fiyat, "tutar": round(adet * fiyat, 2)})
    ara = round(sum(k["tutar"] for k in kalemler), 2)
    oran = random.choice([10, 20])
    kdv = round(ara * oran / 100, 2)
    gt = {"fatura_no": f"ORN2026{100000 + i * 37}", "tarih": f"2026-{random.randint(1, 10):02d}-{random.randint(1, 28):02d}",
          "satici_unvan": s[0], "satici_vkn": s[1], "alici_unvan": a[0], "alici_vkn": a[1],
          "kalemler": kalemler, "ara_toplam": ara, "kdv_orani": oran, "kdv_tutari": kdv, "genel_toplam": round(ara + kdv, 2)}
    p = os.path.join(OUT, f"fatura_{i:02d}.pdf")
    c = canvas.Canvas(p, pagesize=A4)
    W, H = A4
    g, y, m = gt, H - 60, gt["tarih"].split("-")
    tarih_txt = f"{m[2]}.{m[1]}.{m[0]}"
    if duzen == 0:  # klasik: üstte satıcı, sağda fatura bilgisi
        c.setFont("ArB", 15); c.drawString(50, y, g["satici_unvan"])
        c.setFont("Ar", 9); c.drawString(50, y - 14, f"VKN: {g['satici_vkn']}  ·  Örnek Mah. Deneme Cad. No:1 İstanbul")
        c.setFont("ArB", 18); c.drawRightString(W - 50, y, "FATURA")
        c.setFont("Ar", 10); c.drawRightString(W - 50, y - 18, f"Fatura No: {g['fatura_no']}"); c.drawRightString(W - 50, y - 32, f"Tarih: {tarih_txt}")
        y -= 70; c.setFont("ArB", 10); c.drawString(50, y, "SAYIN"); c.setFont("Ar", 10)
        c.drawString(50, y - 14, g["alici_unvan"]); c.drawString(50, y - 28, f"VKN: {g['alici_vkn']}")
    else:  # e-arşiv tarzı: tablo halinde başlık, alıcı önce
        c.setFont("ArB", 13); c.drawCentredString(W / 2, y, "e-Arşiv Fatura")
        c.setFont("Ar", 9); y -= 26
        for lab, val in [("Alıcı", g["alici_unvan"]), ("Alıcı Vergi No", g["alici_vkn"]), ("Düzenleyen", g["satici_unvan"]),
                         ("Düzenleyen VKN", g["satici_vkn"]), ("Belge No", g["fatura_no"]), ("Düzenlenme Tarihi", tarih_txt)]:
            c.drawString(60, y, f"{lab}:"); c.drawString(190, y, val); y -= 14
        y -= 0
    y -= 50; c.setFont("ArB", 9)
    for x, t in [(50, "Açıklama"), (300, "Miktar"), (370, "Birim Fiyat"), (470, "Tutar")]:
        c.drawString(x, y, t)
    c.line(50, y - 4, W - 50, y - 4); c.setFont("Ar", 9); y -= 18
    for k in kalemler:
        c.drawString(50, y, k["aciklama"]); c.drawString(300, y, str(k["miktar"]))
        c.drawString(370, y, tl(k["birim_fiyat"]) + " TL"); c.drawString(470, y, tl(k["tutar"]) + " TL"); y -= 15
    y -= 20; c.setFont("Ar", 10)
    c.drawRightString(W - 50, y, f"Ara Toplam: {tl(ara)} TL")
    c.drawRightString(W - 50, y - 15, f"KDV (%{oran}): {tl(kdv)} TL")
    c.setFont("ArB", 11); c.drawRightString(W - 50, y - 33, f"GENEL TOPLAM: {tl(g['genel_toplam'])} TL")
    c.setFont("Ar", 7); c.drawString(50, 40, "Bu belge değerlendirme amaçlı üretilmiş örnek bir faturadır; gerçek bir ticari işlemi temsil etmez.")
    c.save()
    json.dump(gt, open(p.replace(".pdf", ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


for i in range(12):
    fatura(i, i % 2)
print("12 örnek fatura üretildi")
