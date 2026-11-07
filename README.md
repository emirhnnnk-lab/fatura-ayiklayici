# Fatura / Evrak Ayıklayıcı

**🔴 Canlı demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo) — sekme: 🧾 Fatura Ayıklayıcı (demo OpenAI gpt-5.4-mini ile çalışır; iş mantığı bu repodakiyle aynı)

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

## Hata → düzeltme süreci

**1. Ne bozuktu?** İlk sürümde her şeyi LLM'e bıraktım. 12 faturanın sadece 1'inde tüm alanlar doğru çıktı. Asıl tehlike şuydu: **yanlış okunan 11 faturanın 10'u doğrulamadan "onaylandı" diye geçti.** Hatalı veri sessizce muhasebeye gidecekti.

**2. Nasıl fark ettim?** Alan alan doğruluk tablosu çıkardım ([v1 raporu](eval/RAPOR_v1_sadece_llm.md)). Fatura no, tarih ve KDV oranı 12/12 doğruydu. Ama satıcı ünvanı 5/12, alıcı ünvanı 2/12'de kaldı. Hatalar rastgele değildi: model **satıcı ile alıcıyı yer değiştiriyordu.** Tutarlar tutarlı kaldığı için toplam kontrolleri bu hatayı göremiyordu.

**3. Ne değiştirdim?**
- Etiketi belli alanları ("Düzenleyen", "Sayın", "VKN", toplamlar) **kuralla** okuttum. Bu alanlarda kural LLM'i ezer.
- LLM'i yalnızca gerçekten zor olan kısma, yani kalem tablosuna odakladım.
- Doğrulama kuralları (miktar × fiyat, kalem toplamı, KDV hesabı, satıcı ≠ alıcı) son kapı olarak kaldı. Okuma düzelince yakalama oranı 1/11'den 2/2'ye çıktı.

**4. Sonuç**

| | v1: sadece LLM | v2: LLM + kural + doğrulama |
|---|---|---|
| Tüm alanlar doğru | 1/12 | **10/12** |
| Satıcı / alıcı ünvanı | 5/12 · 2/12 | **12/12 · 12/12** |
| Hatalı olup "onaylandı" diye geçen | **10** | **0** |

Kalan 2 hata (kalem tablosu) doğrulamaya takıldı ve "kontrol gerekli" olarak insana gitti. Bir de yanlış alarm var: fatura_01 doğru okunduğu hâlde kontrole düştü. Bu kasıtlı bir tercih; sistem temkinli tarafta hata yapıyor.

**Ders:** LLM'in iyi olduğu işi (serbest düzenli tablo) LLM'e, kuralla kesin yapılabilecek işi kurala verdim. En önemli ölçüt doğruluk oranı değil, **hatalı verinin sessizce geçmemesi** oldu.

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
