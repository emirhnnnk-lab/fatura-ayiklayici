"""Alan bazında doğruluk: örnek faturalardan çıkarılan veri doğru cevapla karşılaştırılır."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.ayikla import isle

ORN = os.path.join(os.path.dirname(__file__), "..", "ornekler")
ALANLAR = ["fatura_no", "tarih", "satici_unvan", "satici_vkn", "alici_unvan", "alici_vkn", "ara_toplam", "kdv_orani", "kdv_tutari", "genel_toplam"]


def esit(a, b):
    if isinstance(b, (int, float)):
        try:
            return abs(float(a) - float(b)) < 0.05
        except (TypeError, ValueError):
            return False
    return str(a).strip().lower() == str(b).strip().lower()


dogru = {a: 0 for a in ALANLAR}
kalem_ok = tam = yakalanan = 0
rows, t0 = [], time.time()
pdfs = sorted(glob.glob(os.path.join(ORN, "*.pdf")))
for p in pdfs:
    gt = json.load(open(p.replace(".pdf", ".json"), encoding="utf-8"))
    r = isle(p)
    v = r["veri"]
    hata = [a for a in ALANLAR if not esit(v.get(a), gt[a])]
    for a in ALANLAR:
        dogru[a] += a not in hata
    k_ok = len(v.get("kalemler", [])) == len(gt["kalemler"]) and all(
        esit(x["tutar"], y["tutar"]) for x, y in zip(v["kalemler"], gt["kalemler"]))
    kalem_ok += k_ok
    tam += (not hata and k_ok)
    if (hata or not k_ok) and r["uyarilar"]:
        yakalanan += 1
    rows.append(f"| {os.path.basename(p)} | {'✅' if not hata and k_ok else '❌ ' + ', '.join(hata + ([] if k_ok else ['kalemler']))} | {r['durum']} |")
n = len(pdfs)
hatali = n - tam
rep = ["# Değerlendirme raporu", "", f"- Fatura sayısı: **{n}** (2 farklı düzen: klasik ve e-arşiv)",
       f"- Tüm alanları doğru: **{tam}/{n}**", f"- Kalem tablosu doğru: **{kalem_ok}/{n}**",
       f"- Hatalı çıkarımlardan doğrulama kurallarının yakaladığı: **{yakalanan}/{hatali}**" if hatali else "- Hatalı çıkarım yok",
       f"- Model: `{os.getenv('CHAT_MODEL', 'qwen2.5:3b')}` (lokal) · Süre: {time.time() - t0:.0f} sn", "",
       "| Alan | Doğruluk |", "|---|---|"] + [f"| {a} | {dogru[a]}/{n} |" for a in ALANLAR] + ["",
       "| Dosya | Sonuç | Doğrulama durumu |", "|---|---|---|"] + rows
open(os.path.join(os.path.dirname(__file__), "RAPOR.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
print(f"tam {tam}/{n} kalem {kalem_ok}/{n}")
