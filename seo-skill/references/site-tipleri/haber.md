# Playbook: Haber / dergi / medya

## Kullanıcıya doğrulat
"Güncel haber mi (son dakika), yoksa dergi/analiz tarzı içerik mi? Editör kadrosu var mı?"

## KPI
Google Haberler/Discover görünürlüğü, güncel sorgularda ilk sayfa, makale başına organik giriş, dizine alınma hızı, Core Web Vitals.

## Öne çıkan gereksinimler
- **Hız:** haber hızla dizine girmeli. Sitemap'i sık güncelle (gerekirse Google News sitemap), iç linkleme ile yeni haberi ana sayfa/kategoriden bağla.
- **Şeffaflık/E-E-A-T:** yazar adı + yazar sayfası, editör ilkeleri, hakkımızda, iletişim, düzeltme politikası, kaynak belirtme, yayın/güncelleme tarihi.
- **Tarih dürüstlüğü:** `datePublished` ve gerçek `dateModified`; güncellenen haberde güncelleme notu.
- **YMYL:** sağlık/finans/siyaset haberlerinde güçlü kaynak ve uzman doğrulaması.

## Sayfa tipleri
| Sayfa | Title formülü | Zorunlu içerik |
|---|---|---|
| Haber | net, olgusal başlık (abartısız); marka sonda | özet cümle, 5N1K, yazar/tarih, kaynak, görsel+alt, ilgili haberler |
| Kategori / etiket | `[Kategori] Haberleri | Marka` | son haberler, sayfalama, kısa açıklama |
| Dosya/konu sayfası (evergreen) | `[Konu]: Son Gelişmeler ve Arka Plan` | sürekli güncellenen kronoloji, bağlantılı haberler |
| Yazar sayfası | | biyografi, uzmanlık, yazıları |
| Analiz / köşe | | özgün görüş ve veri |

## Schema
`NewsArticle`/`Article` (headline, image, datePublished, dateModified, author, publisher), `NewsMediaOrganization`/`Organization`, `BreadcrumbList`, yazar `Person`. Başlık, görsel ve tarihler görünür içerikle eşleşsin.

## Teknik
- Agresif reklam/interstitial yok (CLS, kullanıcı deneyimi). Reklam alanları için boyut ayır.
- Görseller büyük (`max-image-preview:large`, geniş görsel, en az 1200px genişlik) — Discover için önemli.
- AMP zorunlu değil. Hız için sade şablon, geç yüklenen reklam.
- Sayfalama, "devamını oku" ile içerik gizleme yok; tam metin HTML'de.
- Eski haberleri silmek yerine arşiv olarak tut; güncelliğini yitirenleri kategori/dosya sayfasına bağla.
- Sitemap: `lastmod` doğru; haber sitemap ayrı (son 2 gün).

## Anahtar kelime kalıpları
Güncel olay adı + gelişme ("… son durum", "… ne zaman", "… neden oldu"), evergreen açıklayıcılar ("… nedir"), canlı takip ("canlı blog").

## Rakip analizi odağı
- Haber sorgularında büyük yayıncılar baskın: kendi **özgün haber/analiz/yerel/niş** alanını bul. Rakiplerin başlık formülü, görsel kullanımı, güncelleme sıklığı, yazar/kaynak şeffaflığı, Top Stories kutusunda görünenler.
- Evergreen açıklayıcılarda rakip derinliği ve güncelliği (mevcut ölçüm yöntemi uygulanır).

## Elle işler
Google News/Discover performans takibi (Search Console), Publisher Center (uygunsa), editör politikası sayfaları, yazar kadrosu, görsel/telif lisansları, sosyal dağıtım.

## Yapma
Çalıntı/rewrite haber, yapay zekâ ile toplu haber fabrikası, tıklama tuzağı başlık, sahte yazar, tarihleri sürekli "yeni" göstermek, kaynaksız iddia.
