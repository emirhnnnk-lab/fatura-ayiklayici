# Değerlendirme raporu

- Fatura sayısı: **12** (2 farklı düzen: klasik ve e-arşiv)
- Tüm alanları doğru: **10/12**
- Kalem tablosu doğru: **10/12**
- Hatalı çıkarımlardan doğrulama kurallarının yakaladığı: **2/2**
- Model: `qwen2.5:3b` (lokal) · Süre: 85 sn

| Alan | Doğruluk |
|---|---|
| fatura_no | 12/12 |
| tarih | 12/12 |
| satici_unvan | 12/12 |
| satici_vkn | 12/12 |
| alici_unvan | 12/12 |
| alici_vkn | 12/12 |
| ara_toplam | 12/12 |
| kdv_orani | 12/12 |
| kdv_tutari | 12/12 |
| genel_toplam | 12/12 |

| Dosya | Sonuç | Doğrulama durumu |
|---|---|---|
| fatura_00.pdf | ✅ | onaylandi |
| fatura_01.pdf | ✅ | kontrol_gerekli |
| fatura_02.pdf | ✅ | onaylandi |
| fatura_03.pdf | ✅ | onaylandi |
| fatura_04.pdf | ❌ kalemler | kontrol_gerekli |
| fatura_05.pdf | ✅ | onaylandi |
| fatura_06.pdf | ✅ | onaylandi |
| fatura_07.pdf | ✅ | onaylandi |
| fatura_08.pdf | ❌ kalemler | kontrol_gerekli |
| fatura_09.pdf | ✅ | onaylandi |
| fatura_10.pdf | ✅ | onaylandi |
| fatura_11.pdf | ✅ | onaylandi |
