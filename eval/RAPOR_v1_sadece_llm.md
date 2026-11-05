# Değerlendirme raporu

- Fatura sayısı: **12** (2 farklı düzen: klasik ve e-arşiv)
- Tüm alanları doğru: **1/12**
- Kalem tablosu doğru: **10/12**
- Hatalı çıkarımlardan doğrulama kurallarının yakaladığı: **1/11**
- Model: `qwen2.5:3b` (lokal) · Süre: 99 sn

| Alan | Doğruluk |
|---|---|
| fatura_no | 12/12 |
| tarih | 12/12 |
| satici_unvan | 5/12 |
| satici_vkn | 5/12 |
| alici_unvan | 2/12 |
| alici_vkn | 5/12 |
| ara_toplam | 10/12 |
| kdv_orani | 12/12 |
| kdv_tutari | 10/12 |
| genel_toplam | 10/12 |

| Dosya | Sonuç | Doğrulama durumu |
|---|---|---|
| fatura_00.pdf | ❌ alici_unvan | onaylandi |
| fatura_01.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | kontrol_gerekli |
| fatura_02.pdf | ❌ alici_unvan | onaylandi |
| fatura_03.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | onaylandi |
| fatura_04.pdf | ❌ alici_unvan, ara_toplam, kdv_tutari, genel_toplam, kalemler | onaylandi |
| fatura_05.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | onaylandi |
| fatura_06.pdf | ✅ | onaylandi |
| fatura_07.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | onaylandi |
| fatura_08.pdf | ❌ ara_toplam, kdv_tutari, genel_toplam, kalemler | onaylandi |
| fatura_09.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | onaylandi |
| fatura_10.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | onaylandi |
| fatura_11.pdf | ❌ satici_unvan, satici_vkn, alici_unvan, alici_vkn | onaylandi |
