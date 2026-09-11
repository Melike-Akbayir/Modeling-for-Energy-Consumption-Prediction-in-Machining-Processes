"""
Sentetik (yapay) veri üreticisi.

Bu script, gerçek bir üretim tesisinden alınan veriye YAPISAL olarak benzeyen
(aynı sütunlar, aynı ölçek ve ilişkiler) ama tamamen uydurma/rastgele üretilmiş
bir veri seti oluşturur. Amaç: gerçek şirket verisini paylaşmadan, aynı analiz
ve modelleme sürecini herkesin çalıştırabileceği bir örnek sağlamak.

Gerçek projede karşılaşılan iki veri kalitesi durumu da (boşta çalışma günleri,
sayaç/sensör kayıp günleri) burada bilinçli olarak simüle edilmiştir, böylece
notebook'taki veri temizliği adımları anlamlı kalır.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N_DAYS = 260
start_date = pd.Timestamp("2024-01-01")
dates = pd.date_range(start_date, periods=N_DAYS, freq="D")

rows = []
for d in dates:
    is_weekend = d.dayofweek >= 5
    # ~%12 ihtimalle hafta içi de olsa üretim olmayan bir gün (bakım, tatil vb.)
    idle = is_weekend or (rng.random() < 0.05)

    if idle:
        adet = 0
        pik_adet = sfr_adet = adi_adet = bos_adet = 0
        sure = 0.0
        pik_kg = sfr_kg = adi_kg = bos_kg = 0.0
    else:
        adet = int(max(5, rng.normal(780, 340)))
        pik_pay = rng.uniform(0.40, 0.62)
        sfr_pay = rng.uniform(0.20, 0.35)
        adi_pay = max(0.0, 1 - pik_pay - sfr_pay)
        pik_adet = int(adet * pik_pay)
        sfr_adet = int(adet * sfr_pay)
        adi_adet = int(adet * adi_pay * rng.uniform(0.6, 1.0))
        bos_adet = max(0, adet - pik_adet - sfr_adet - adi_adet)

        sure = max(300, rng.normal(13000, 4800) + adet * 2.5)

        pik_kg = pik_adet * rng.uniform(9, 14)
        sfr_kg = sfr_adet * rng.uniform(14, 20)
        adi_kg = adi_adet * rng.uniform(6, 12)
        bos_kg = bos_adet * rng.uniform(0, 3)

    uretim_net = pik_kg + sfr_kg + adi_kg + bos_kg
    uretim_brut = uretim_net + max(0, rng.normal(0, 3))  # neredeyse net'e eşit (gerçek veride de böyleydi)

    kontrol = 0
    kontrol_kg = 0
    pik_yuzde = pik_adet / adet if adet else 0.0
    sfr_yuzde = sfr_adet / adet if adet else 0.0
    pik_kg_yuzde = pik_kg / uretim_net if uretim_net else 0.0
    sfr_kg_yuzde = sfr_kg / uretim_net if uretim_net else 0.0

    # --- enerji tüketimi ---
    if adet == 0:
        # boşta çalışma / taban tüketim
        enerji = max(0, rng.normal(1550, 180))
    else:
        taban = rng.normal(500, 60)
        enerji = (
            taban
            + sure * 0.19          # süre en baskın etken
            + adet * 0.55          # parça adedi (setup/geçiş etkisi)
            + sfr_kg * 0.09
            + adi_kg * 0.05
            + pik_kg * 0.02
            + rng.normal(0, 140)   # gürültü
        )
        enerji = max(200, enerji)

    rows.append(dict(
        Tarih=d, Uretilen_Adet=adet, Toplam_Rota_Suresi=round(sure, 2),
        Uretim_Net_Kg=round(uretim_net, 2), Uretim_Brut_Kg=round(uretim_brut, 2),
        Pik_Adet=pik_adet, Sfr_Adet=sfr_adet, Adi_Adet=adi_adet, Tipi_Bos_Adet=bos_adet,
        Kontrol=kontrol, Pik_Yuzde=round(pik_yuzde, 6), Sfr_Yuzde=round(sfr_yuzde, 6),
        Pik_Net_Kg=round(pik_kg, 2), Sfr_Net_Kg=round(sfr_kg, 2), Adi_Net_Kg=round(adi_kg, 2),
        Tipi_Bos_Net_Kg=round(bos_kg, 2), Kontrol_Kg=kontrol_kg,
        Pik_Kg_Yuzde=round(pik_kg_yuzde, 6), Sfr_Kg_Yuzde=round(sfr_kg_yuzde, 6),
        Enerji_kWh=round(enerji, 2),
    ))

df = pd.DataFrame(rows)

# --- sensör/sayaç kaybı simülasyonu: 2 örnek gün, enerji 0 kaydedilmiş,
#     kaybolan değer bir sonraki güne yansıtılmış (gerçek projedeki bulguyla aynı desen) ---
loss_idx = [37, 151]  # rastgele iki üretim günü
for idx in loss_idx:
    if df.loc[idx, "Uretilen_Adet"] > 0:
        lost_energy = df.loc[idx, "Enerji_kWh"]
        df.loc[idx, "Enerji_kWh"] = 0.0
        df.loc[idx + 1, "Enerji_kWh"] = round(df.loc[idx + 1, "Enerji_kWh"] + lost_energy, 2)

df.to_csv("data/sentetik_uretim_enerji.csv", index=False)
print("Kaydedildi:", df.shape)
print(df.head())
