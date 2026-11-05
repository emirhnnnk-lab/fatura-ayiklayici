from app.ayikla import dogrula

IYI = {"fatura_no": "X1", "tarih": "2026-05-04", "satici_unvan": "A", "satici_vkn": "1234567890", "alici_unvan": "B",
       "alici_vkn": "9876543210", "kalemler": [{"aciklama": "k", "miktar": 2, "birim_fiyat": 100.0, "tutar": 200.0}],
       "ara_toplam": 200.0, "kdv_orani": 20, "kdv_tutari": 40.0, "genel_toplam": 240.0}


def test_tutarli_fatura_gecer():
    assert dogrula(IYI) == []


def test_hatalar_yakalanir():
    kotu = {**IYI, "satici_vkn": "123", "genel_toplam": 250.0, "tarih": "04.05.2026"}
    u = dogrula(kotu)
    assert any("satici_vkn" in x for x in u)
    assert any("genel toplam" in x for x in u)
    assert any("tarih" in x for x in u)


def test_kalem_toplami_tutarsizligi():
    kotu = {**IYI, "kalemler": [{"aciklama": "k", "miktar": 2, "birim_fiyat": 100.0, "tutar": 150.0}]}
    assert any("kalem" in x for x in dogrula(kotu))


def test_kural_ayikla_iki_duzen():
    import glob, json, os
    from app.ayikla import kural_ayikla, metin_cikar
    d = os.path.join(os.path.dirname(__file__), "..", "ornekler")
    for p in sorted(glob.glob(os.path.join(d, "*.pdf"))):
        gt = json.load(open(p.replace(".pdf", ".json"), encoding="utf-8"))
        k = kural_ayikla(metin_cikar(p))
        for a in ["satici_unvan", "satici_vkn", "alici_unvan", "alici_vkn"]:
            assert k[a] == gt[a], (p, a, k.get(a))
        assert abs(k["genel_toplam"] - gt["genel_toplam"]) < 0.01
