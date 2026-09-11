# Üretim Verisinden Enerji Tüketimi Tahmini

Bir üretim tesisinin günlük üretim verilerini (işlenen parça adedi, malzeme
türüne göre ağırlıklar, toplam işlem/rota süresi) kullanarak günlük elektrik
enerjisi tüketimini tahmin eden uçtan uca bir makine öğrenmesi projesi.

Bu depo, gerçek bir üretim ortamında yürütülen bir projenin **metodolojisini**
gösterir: veri kalitesi sorunlarının tespiti, özellik seçimi kararlarının
hipotez testiyle doğrulanması, model eğitimi/değerlendirmesi ve sonucun
kullanılabilir bir araca dönüştürülmesi.

> **Veri hakkında:** `data/sentetik_uretim_enerji.csv`, gerçek bir şirketin
> verisi değildir. Gerçek projede karşılaşılan yapı ve veri kalitesi
> sorunlarını (boşta çalışma günleri, sensör/sayaç kaybı) yansıtacak şekilde
> `generate_synthetic_data.py` ile **sentetik olarak üretilmiştir**. Analiz
> akışı ve karar süreci, gerçek veri üzerinde yürütülen çalışmanın birebir
> aynısıdır.

## Sonuçlar (sentetik veri üzerinde)

| Metrik | Değer |
|---|---|
| Kullanılabilir veri | 172 üretim günü |
| MAE (Ortalama Mutlak Hata) | ≈ 249 kWh |
| Bağıl hata (MAE / ortalama) | ≈ %6,4 |
| R² | ≈ 0,92 |

En etkili özellik **toplam işlem/rota süresi** — enerji tüketiminin büyük
kısmını tek başına açıklıyor. Malzeme türüne göre ağırlık kırılımı (toplam
ağırlık yerine) ve üretilen adet, ikincil düzeyde katkı sağlıyor.

## İçindekiler

```
├── enerji_tahmini.ipynb          # Ana analiz — veri temizliği, modelleme, değerlendirme
├── generate_synthetic_data.py    # Sentetik örnek veri üreticisi
├── data/
│   └── sentetik_uretim_enerji.csv
├── web-tool/
│   └── index.html                # Eğitilmiş modeli tarayıcıda çalıştıran statik demo
├── requirements.txt
└── README.md
```

## Yöntem

1. **Veri temizliği** — sabit/bilgi taşımayan sütunları, sensör/sayaç kaybı
   yaşanan (ve bir sonraki güne yanlış yansıyan) günleri, ve boşta çalışma
   günlerini (farklı bir tüketim rejimi olduğu için) veri setinden çıkarma.
2. **Özellik seçimi** — türetilmiş/oran sütunlarını eleme, bir hipotezi
   ("talaş miktarı enerjiyle ilişkili mi?") veriyle test edip reddetme.
3. **Modelleme** — `RandomForestRegressor` (scikit-learn), %80/%20 eğitim/test
   ayrımı, `MAE` ve `R²` ile değerlendirme.
4. **Yorumlama** — özellik önemi (`feature_importances_`) ile hangi
   unsurların enerjiyi ne kadar etkilediğini analiz etme.
5. **Kullanılabilir hale getirme** — eğitilmiş modeli hem bir Python
   fonksiyonuna hem de tarayıcıda çalışan bağımsız bir web sayfasına
   (`web-tool/index.html`, sunucu gerektirmez) dönüştürme.

## Çalıştırma

```bash
pip install -r requirements.txt
jupyter notebook enerji_tahmini.ipynb
```

Sentetik veriyi yeniden üretmek isterseniz:

```bash
python generate_synthetic_data.py
```

`web-tool/index.html` dosyasını doğrudan tarayıcıda açarak (kurulum
gerektirmeden) canlı tahmin aracını deneyebilirsiniz — eğitilmiş model,
sayfanın içine gömülüdür ve tüm hesaplama tarayıcıda, JavaScript ile yapılır.

## Kullanılan araçlar

Python · pandas · scikit-learn (RandomForestRegressor) · matplotlib · Jupyter

## Lisans

MIT — bkz. [LICENSE](LICENSE).
