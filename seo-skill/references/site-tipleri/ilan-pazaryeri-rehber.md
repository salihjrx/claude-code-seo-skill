# Playbook: İlan / pazaryeri / rehber / dizin / karşılaştırma siteleri

Çok sayıda dinamik sayfa içeren siteler. SEO'nun ana riskleri: **tarama bütçesi, kopya/ince sayfa, süresi dolan ilanlar, filtre patlaması, kullanıcı içeriği kalitesi.**

## Kullanıcıya doğrulat
"İlanları kim giriyor (siz mi, kullanıcılar mı)? İlanların süresi doluyor mu? Hangi kategori/şehirlerde hizmet veriyorsunuz?"

## KPI
Dizindeki geçerli ilan/liste sayısı, kategori×şehir sayfalarının sıralaması, ilan başına organik giriş, ilan→başvuru/iletişim dönüşümü, tarama istatistikleri.

## Sayfa hiyerarşisi
Ana sayfa → kategori → alt kategori → **kategori × konum** (talebi olanlar) → ilan/liste detay. Kategori×konum sayfaları gerçek arama talebi ve yeterli ilan olduğunda indekslensin; boş/az ilanlı kombinasyonlar `noindex` veya üretme.

| Sayfa | Title formülü | Zorunlu içerik |
|---|---|---|
| Kategori / konum listesi | `[Şehir] [Kategori] İlanları (N ilan) | Marka` | benzersiz tanıtım metni, ilan listesi, filtre, SSS, breadcrumb, komşu kategori/konum linkleri |
| İlan detay | `[Başlık] – [Konum] | Marka` | özgün açıklama, fiyat/koşullar, görseller, satıcı bilgisi, güncel durum, benzer ilanlar |
| Satıcı / mağaza profili | | gerçek bilgiler, ilanları |
| Rehber / karşılaştırma | `[Konu] Rehberi / En İyi [N]` | **yöntem** (nasıl seçildi), kriter tablosu, güncel veri, bağlantılar |

## Schema
İlan türüne göre: `JobPosting` (validThrough!), `Product`/`Offer`, `RealEstateListing`, `Vehicle`, `Event`; listelerde `ItemList`; `BreadcrumbList`; rehberlerde `Article` + (gerçekse) `Review`/`ItemList`. Süresi dolan iş ilanında `validThrough` doğru olsun.

## Teknik tuzaklar
1. **Süresi dolan/satılan ilanlar:** kısa süreli ise sayfa 200 + "artık yayında değil" + benzer ilanlar; kalıcı kaldırmada 410/404; yerine uygun kategoriye 301 (alakalıysa). Soft-404 üretme.
2. **Filtre/sıralama parametreleri:** canonical → temiz liste URL'si; yalnız talep gören kombinasyonlar indekslenebilir.
3. **Sayfalama:** her sayfa crawlable `<a href>` ile; kendi canonical'ı.
4. **Kullanıcı içeriği:** kopya ilan, spam, çalıntı görsel → moderasyon; `rel="ugc nofollow"` kullanıcı linklerinde; ince ilanlar `noindex` (eşik tanımla: metin < N kelime, görsel yok).
5. **Sitemap:** ilan sitemap'leri parçalı (≤50.000 URL), `lastmod` gerçek; sık güncellenen dosyaları ayır; süresi dolanları çıkar.
6. **Hız ve ölçek:** büyük liste sayfalarında görsel lazy-load, sayfa başına makul ilan sayısı, sunucu önbelleği.
7. **Dahili arama sonuçları** (`/ara?q=`) `noindex`.
8. Harita görünümü/JS ile yüklenen listeler HTML'de de bulunmalı.

## Anahtar kelime kalıpları
`[şehir/ilçe] [kategori] ilanları`, `satılık/kiralık [şey] [ilçe]`, `[meslek] iş ilanları [şehir]`, `en iyi [kategori]`, `[A] vs [B]`, `[kategori] fiyatları`. Kategori×konum matrisinden talep olanları seç.

## Rakip analizi odağı
- Büyük oyuncular (ilan portalları) baskın; hedef: **niş kategori + yerel + uzun kuyruk** ve **rehber/karşılaştırma içeriği**.
- Ölç: rakip liste sayfalarında tanıtım metni uzunluğu, filtre yapısı, SSS, schema (ItemList/Offer/JobPosting), ilan sayısı ibaresi, iç link blokları (popüler aramalar, komşu bölgeler).
- Boşluk: özgün yerel veri (ortalama fiyat/kira, trend), rehberler, doğrulanmış ilan etiketi, güncel durum.

## Elle işler
İlan moderasyon politikası, spam raporlama, Search Console'da URL kalıp analizi, kategori×konum talep verisi (Keyword Planner/Trends), satıcı doğrulama, PR/yerel ortaklıklar.

## Yapma
Boş/ince kategori×şehir sayfaları toplu üretmek (doorway), süresi dolan ilanı normal 200 bırakmak, her filtre kombinasyonunu indekslemek, kullanıcı linklerini follow bırakmak, çalıntı içerik.
