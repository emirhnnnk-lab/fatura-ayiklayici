"""PDF fatura → doğrulanmış JSON. Akış: metin çıkar → LLM ile şemaya uygun yapılandırılmış çıktı → kural tabanlı doğrulama."""
import json, os, re
import httpx
import pdfplumber
from pydantic import BaseModel, Field

OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("CHAT_MODEL", "qwen2.5:3b")


class Kalem(BaseModel):
    aciklama: str
    miktar: float
    birim_fiyat: float
    tutar: float


class Fatura(BaseModel):
    fatura_no: str
    tarih: str = Field(description="YYYY-MM-DD")
    satici_unvan: str
    satici_vkn: str
    alici_unvan: str
    alici_vkn: str
    kalemler: list[Kalem]
    ara_toplam: float
    kdv_orani: float
    kdv_tutari: float
    genel_toplam: float


SISTEM = """Türkçe bir faturadan bilgi çıkaran bir asistansın. Sadece metinde yazanı kullan, tahmin etme.
- Tutarlar Türk biçimindedir (1.234,56 = 1234.56). Sayıları nokta ondalıklı sayı olarak yaz.
- Tarihi YYYY-MM-DD biçimine çevir.
- 'Düzenleyen' satıcıdır, 'Sayın' / 'Alıcı' alıcıdır. VKN 10 hanelidir."""


def metin_cikar(pdf_yolu: str) -> str:
    with pdfplumber.open(pdf_yolu) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def llm_ayikla(metin: str) -> dict:
    r = httpx.post(f"{OLLAMA}/api/chat", timeout=300, json={
        "model": MODEL, "stream": False, "options": {"temperature": 0},
        "format": Fatura.model_json_schema(),  # yapılandırılmış çıktı: model şemaya uymak zorunda
        "messages": [{"role": "system", "content": SISTEM}, {"role": "user", "content": metin}]})
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])


def dogrula(f: dict) -> list[str]:
    """Çıkarılan veriyi iş kurallarıyla denetler. Boş liste = tutarlı."""
    u = []
    for alan in ("satici_vkn", "alici_vkn"):
        if not re.fullmatch(r"\d{10}", str(f.get(alan, ""))):
            u.append(f"{alan} 10 haneli olmalı")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f.get("tarih", ""))):
        u.append("tarih biçimi hatalı")
    kal = f.get("kalemler", [])
    for k in kal:
        if abs(k["miktar"] * k["birim_fiyat"] - k["tutar"]) > 0.05:
            u.append(f"kalem tutarı tutmuyor: {k['aciklama']}")
    if kal and abs(sum(k["tutar"] for k in kal) - f.get("ara_toplam", 0)) > 0.05:
        u.append("kalemlerin toplamı ara toplamı tutmuyor")
    if abs(f.get("ara_toplam", 0) * f.get("kdv_orani", 0) / 100 - f.get("kdv_tutari", 0)) > 0.05:
        u.append("KDV tutarı oranla tutmuyor")
    if abs(f.get("ara_toplam", 0) + f.get("kdv_tutari", 0) - f.get("genel_toplam", 0)) > 0.05:
        u.append("ara toplam + KDV genel toplamı tutmuyor")
    return u


def _tl(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def kural_ayikla(metin: str) -> dict:
    """Etiketli alanları kuralla okur. Küçük modeller taraf (satıcı/alıcı) karıştırdığı için
    taraf ve toplam bilgisi önce burada, deterministik olarak çıkarılır."""
    f, satir = {}, [s.strip() for s in metin.splitlines() if s.strip()]
    g = lambda p: (re.search(p, metin) or [None, None])[1]
    if "Düzenleyen" in metin:  # e-arşiv düzeni
        f["satici_unvan"], f["satici_vkn"] = g(r"Düzenleyen:\s*(.+)"), g(r"Düzenleyen VKN:\s*(\d{10})")
        f["alici_unvan"], f["alici_vkn"] = g(r"Alıcı:\s*(.+)"), g(r"Alıcı Vergi No:\s*(\d{10})")
    elif "SAYIN" in metin:  # klasik düzen: ilk satır satıcı, SAYIN altı alıcı
        f["satici_unvan"] = re.sub(r"\s*FATURA\s*$", "", satir[0])
        f["satici_vkn"] = g(r"VKN:\s*(\d{10})")
        i = satir.index("SAYIN")
        f["alici_unvan"] = satir[i + 1]
        f["alici_vkn"] = (re.search(r"VKN:\s*(\d{10})", satir[i + 2]) or [None, None])[1]
    for alan, desen in [("ara_toplam", r"Ara Toplam:\s*([\d.,]+)"), ("kdv_tutari", r"KDV \(%\d+\):\s*([\d.,]+)"),
                        ("genel_toplam", r"GENEL TOPLAM:\s*([\d.,]+)")]:
        v = g(desen)
        if v:
            f[alan] = _tl(v)
    oran = g(r"KDV \(%(\d+)\)")
    if oran:
        f["kdv_orani"] = float(oran)
    return {k: v for k, v in f.items() if v not in (None, "")}


def isle(pdf_yolu: str) -> dict:
    metin = metin_cikar(pdf_yolu)
    f = llm_ayikla(metin)
    kural = kural_ayikla(metin)
    farklar = [k for k, v in kural.items() if str(f.get(k)) != str(v)]
    f.update(kural)  # etiketli alanlarda kural kazanır; LLM kalemleri ve geri kalanı doldurur
    uyarilar = dogrula(f)
    if f.get("satici_vkn") and f.get("satici_vkn") == f.get("alici_vkn"):
        uyarilar.append("satıcı ve alıcı VKN aynı")
    return {"veri": f, "uyarilar": uyarilar, "durum": "onaylandi" if not uyarilar else "kontrol_gerekli",
            "llm_kural_farki": farklar}
