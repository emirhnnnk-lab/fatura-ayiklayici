# Fatura / Evrak Ayıklayıcı

> **EN summary:** Turns PDF invoices into validated JSON using a local LLM (Ollama) plus rule-based field extraction and business-rule checks (tax ID, line totals, VAT math, seller ≠ buyer). LLM-only v1 got all fields right on 1/12 invoices; the hybrid v2 gets 10/12, and both remaining errors are caught by validation, so bad data never passes silently. Data never leaves the machine. Full English version: [README.en.md](README.en.md).

**Canlı demo:** [huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo](https://huggingface.co/spaces/emrhnnnnnn/ai-uygulamalar-demo), sekme: 🧾 Fatura Ayıklayıcı. Demo OpenAI gpt-5.4-mini ile çalışıyor; iş mantığı bu repodakiyle aynı.

Muhasebede biri gün boyu PDF faturaları açıp satıcıyı, alıcıyı, kalemleri ve tutarları elle bir yere geçiriyor. Bu servis PDF faturayı alıp **kontrol edilmiş, düzenli bir veriye** (JSON) çeviriyor. Yerel bir model, kurallarla okuma ve hesap kontrollerini birlikte kullanıyor. Veri bilgisayardan çıkmıyor.

## Nasıl çalışıyor
```
PDF → metin (pdfplumber) → ┬─ Model: kalemleri, tutarları, tarihi belirli bir kalıba (JSON şeması) uygun çıkarır
                           └─ Kural: etiketi belli alanları okur (Düzenleyen, Sayın, VKN, toplamlar)
                        → birleştir (etiketli alanda kural kazanır) → kontrol et → onaylandı / kontrol gerekli
```
**Kontroller:** VKN 10 hane mi · tarih doğru biçimde mi · miktar × birim fiyat = tutar mı · kalemlerin toplamı ara toplamı tutuyor mu · ara toplam × KDV oranı = KDV mi · ara toplam + KDV = genel toplam mı · satıcı ile alıcı aynı kişi mi.

## Sonuçlar (12 örnek fatura, 2 farklı düzen)
| Sürüm | Tüm alanlar doğru | Hatalı okumayı yakalama |
|---|---|---|
| v1: her şey modelde | 1/12 | 1/11 |
| **v2: model + kural + kontrol** | **10/12** | **2/2** |

## Neler patladı, nasıl düzelttim

**1. İlk sürümde her şeyi modele bıraktım.** 12 faturanın sadece 1'inde bütün alanlar doğru çıktı. Asıl korkutucu olan şuydu: **yanlış okunan 11 faturanın 10'u kontrollerden "onaylandı" diye geçti.** Yani hatalı veri sessizce muhasebeye gidecekti.

**2. Alan alan bakınca sebep ortaya çıktı.** Her alanın ayrı ayrı doğruluğunu çıkardım ([v1 raporu](eval/RAPOR_v1_sadece_llm.md)). Fatura no, tarih ve KDV oranı 12/12 doğruydu. Ama satıcı ünvanı 5/12'de, alıcı ünvanı 2/12'de kalmıştı. Hatalar rastgele değildi: küçük model (3B) **satıcıyla alıcıyı yer değiştiriyordu.** Tutarlar kendi içinde tutarlı kaldığı için toplam kontrolleri bunu göremiyordu.

**3. İşi böldüm.**
- Etiketi belli olan alanları ("Düzenleyen", "Sayın", "VKN", toplamlar) **kuralla** okuttum. Bu alanlarda kural modeli ezer.
- Modeli sadece gerçekten zor olan kısma, kalem tablosuna verdim.
- Hesap kontrolleri son kapı olarak kaldı. Okuma düzelince hatayı yakalama oranı 1/11'den 2/2'ye çıktı.

| | v1: her şey modelde | v2: model + kural + kontrol |
|---|---|---|
| Tüm alanlar doğru | 1/12 | **10/12** |
| Satıcı / alıcı ünvanı | 5/12 · 2/12 | **12/12 · 12/12** |
| Hatalı olup "onaylandı" diye geçen | **10** | **0** |

Kalan 2 hata kalem tablosundaydı; ikisi de kontrole takıldı ve "kontrol gerekli" diye insana gitti. Bir de yanlış alarm var: fatura_01 doğru okunduğu halde kontrole düştü. Bu bilinçli bir tercih; sistem hata yapacaksa temkinli tarafta yapıyor.

**Ders:** Modelin iyi olduğu işi (düzeni değişen tabloyu okumak) modele, kuralla kesin yapılabilecek işi kurala verdim. Benim için en önemli ölçü doğruluk oranı değil, **hatalı verinin sessizce geçmemesi** oldu.

Ayrıntılı rapor: [eval/RAPOR.md](eval/RAPOR.md)

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
Python · FastAPI · Ollama (qwen2.5:3b, JSON şemasıyla çıktı) · Pydantic · pdfplumber · reportlab · pytest

> Örnek faturalar değerlendirme için üretilmiş uydurma belgeler.

---
Geliştiren: **Emirhan Karaca**
