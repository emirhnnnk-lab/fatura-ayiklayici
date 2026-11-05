# Fatura / Evrak Ayıklayıcı

PDF faturayı **doğrulanmış JSON**'a çeviren servis. Lokal LLM (Ollama) ile yapılandırılmış çıktı, kural tabanlı okuma ve iş kuralı doğrulamasını birleştirir. Veri makineden çıkmaz.

## Akış
```
PDF → metin (pdfplumber) → ┬─ LLM: JSON şemasına zorlanmış çıktı (kalemler, tutarlar, tarih)
                           └─ Kural: etiketli alanlar (Düzenleyen, Sayın, VKN, toplamlar)
                        → birleştir (etiketli alanda kural kazanır) → doğrula → onaylandı / kontrol gerekli
```
**Doğrulama kuralları:** VKN 10 hane · tarih biçimi · miktar × birim fiyat = tutar · kalemler toplamı = ara toplam · ara toplam × KDV oranı = KDV · ara toplam + KDV = genel toplam · satıcı ≠ alıcı.

## Sonuçlar (12 örnek fatura, 2 farklı düzen)
| Sürüm | Tüm alanlar doğru | Hatalı çıkarımı yakalama |
|---|---|---|
| v1: sadece LLM | 1/12 | 1/11 |
| **v2: LLM + kural + doğrulama** | **10/12** | **2/2** |

v1'de küçük model (3B) satıcı ile alıcıyı sık karıştırıyordu ([rapor](eval/RAPOR_v1_sadece_llm.md)). v2'de etiketli alanlar kuralla okunuyor, LLM kalem tablosuna odaklanıyor. Kalan 2 hatanın ikisi de doğrulama kurallarına takıldı: **hatalı veri sessizce geçmiyor.** Ayrıntı: [eval/RAPOR.md](eval/RAPOR.md)

## Çalıştırma
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
python ornekler/uret.py          # örnek faturaları üretir (uydurma veri)
uvicorn app.main:app --reload    # http://localhost:8000 → PDF'i sürükle-bırak
python eval/degerlendir.py       # doğruluk raporu
pytest
```

## Teknoloji
Python · FastAPI · Ollama (qwen2.5:3b, JSON şeması ile structured output) · Pydantic · pdfplumber · reportlab · pytest

> Örnek faturalar değerlendirme amacıyla üretilmiş uydurma belgelerdir.

---
Geliştiren: **Emirhan Karaca**
