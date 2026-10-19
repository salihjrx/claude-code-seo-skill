# SEO Bilgi Bankası (uygulama odaklı)

Kaynak: Google Search Central resmi dokümanları (SEO Başlangıç Kılavuzu, Helpful Content, AI features, Core Web Vitals, snippet) + 20 anahtar kelimede Google'da 1. sıradaki 19 sayfanın ölçümü (Ekim 2026). Eşikler ve kurallar bu tarihte geçerlidir.

## 0. Altın ilkeler
1. **İnsan öncelikli, özgün, yararlı içerik** her teknik adımdan daha etkilidir (Google'ın kendi ifadesi).
2. Arama niyetini title + H1 + ilk bölümde açıkça karşıla (anahtar kelimeyi mekanik/birebir tekrar etme; sayfa kullanıcının sorusunu net yanıtlasın).
3. Teknik olarak taranabilir, dizine eklenebilir ve hızlı ol.
4. Otorite (kaliteli bağlantı, marka, uzmanlık) zamanla birikir; kısa yolu yok.
5. Etki saatler–aylar sürer; değişiklikten sonra birkaç hafta bekle.

## 1. Sıralama için YAPILACAKLAR (etkili)
- Benzersiz, açıklayıcı `<title>` ve `<meta description>`
- Tek `<h1>`, mantıklı H2/H3
- Temiz, açıklayıcı URL
- Canonical, tek tercih edilen URL
- robots.txt + sitemap.xml
- Mobil uyum, HTTPS, hız (Core Web Vitals)
- Görsellerde alt metin; metne yakın konumlandırma
- Açıklayıcı anchor metinli iç/dış linkler
- Yapılandırılmış veri (JSON-LD), sayfadaki görünür içerikle eşleşen
- Yazar, hakkında, iletişim; kaynak gösterme; güncel içerik

## 2. Google'ın "üzerinde durma" dedikleri (yapma / abartma)
- `meta keywords` (kullanılmıyor), anahtar kelime doldurma
- Alan adı/URL'ye anahtar kelime sıkıştırma, TLD seçimi (özel ülke hedefi hariç)
- İçerik uzunluğunu hedefleme (tek başına faktör değil)
- Başlık sırası saplantısı (H2'den önce H3 gelmesi vb. sıralamayı bozmaz; yine de mantıklı kur)
- "Yinelenen içerik cezası" korkusu (ama kopya içerik ve başkasından çalmak ayrı sorun)
- PageRank saplantısı, subdomain/subdirectory tartışması
- E-E-A-T tek başına sıralama faktörü değildir (ama kaliteyi gösteren sinyallerin karışımı faydalıdır)

## 3. Title ve Description

**Title**
- Benzersiz, açık ve sayfayı doğru anlatan başlık. Uzunluk **editoryal rehberdir, kural değildir**: Google sabit karakter sınırı garanti etmez, cihaz/sorguya göre keser veya yeniden yazar. Pratik başlangıç: ~50–60 karakter (piksel genişliği belirleyici).
- Ana sorgu başta, marka sonda: `Ana Sorgu: Fayda/Ek | Marka`.
- Yıl, rakam, "rehber", "adım adım", "fiyat" gibi niyete uygun ekler CTR'yi artırır. Yıl yalnızca içerik gerçekten o yıl güncellendiyse.
- Abartılı/clickbait olma. Google gerekirse başlığı yeniden yazar.

**Meta description**
- Benzersiz ve sayfayı özetleyen metin (uzunluk rehberi ~120–160 karakter; sabit sınır yok). Sorgunun cevabını + faydayı + hafif eylem çağrısını içersin.
- Doğrudan sıralama faktörü değil; tıklamayı etkiler. Google yeniden yazabilir.
- Boş bırakma: sayfa özeti yaz.

```html
<title>Teknik SEO Nedir? 12 Adımda Kontrol Listesi (2026) | Marka</title>
<meta name="description" content="Teknik SEO nedir, nasıl yapılır? Tarama, dizine ekleme, hız ve schema için adım adım kontrol listesi ve örnek kodlar.">
```

## 4. Başlık yapısı
- Sayfada genelde tek, net bir H1 iyi uygulamadır (ana konu ve niyet; title ile uyumlu, birebir aynı olması şart değil). **Tek H1 bir Google sıralama şartı değildir**; yalnız H1 sayısına takılıp içerik/tasarımı bozma. Mantıklı, erişilebilir başlık hiyerarşisi önemlidir.
- H2: ana alt konular/sorular. H3: alt detaylar. Gözlenen küçük örneklemde (19 sayfa) ortanca 9 H2 ve 15 H3; bu hedef değil, gözlemdir.
- Sorulu başlıklar ("... nasıl yapılır?") ve sayılı başlıklar ("5 adım") sık kullanılıyor.
- Uzun sayfaya İçindekiler (TOC) ekle (kimi 1. sıra sayfalarda var).

## 5. URL
- Küçük harf, tire, kısa, anlamlı, mümkünse parametresiz: `/blog/teknik-seo-nedir`
- Türkçe karakter → ASCII (ş→s, ı→i, ğ→g, ü→u, ö→o, ç→c).
- Tarih/ID yığını yok. Değiştirirsen 301 + iç linkleri güncelle.
- Sonda `/` tutarlılığı: tek biçim seç, diğerini 301 ile yönlendir.

## 6. Canonical, yönlendirme, durum kodları
```html
<link rel="canonical" href="https://alanadi.com/sayfa-yolu">
```
- Her indekslenebilir sayfa **kendi mutlak URL'sini** canonical gösterir.
- Filtre/parametre/yazdır sürümleri ana sayfaya canonical.
- http→https, www↔non-www: tek sürüm, kalan 301.
- 404 gerçek 404 dönsün (soft 404 olmasın). Silinen içerik için 410 veya ilgili sayfaya 301.
- Yönlendirme zinciri en fazla 1 sıçrama.

## 7. robots.txt ve noindex
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /sepet/
Disallow: /*?siralama=

Sitemap: https://alanadi.com/sitemap.xml
```
- robots.txt **taramayı** yönetir, **dizine eklemeyi** engellemez. Dizin dışı bırakmak için sayfada `<meta name="robots" content="noindex">` kullan; o sayfayı robots.txt ile engelleme (Google noindex'i göremez).
- CSS/JS/görsel dosyalarını engelleme.
- Canlıya geçerken `Disallow: /` ve `noindex` kalmadığını doğrula (en sık felaket).
- Yapay zekâ eğitimi kontrolü: `Google-Extended` user-agent (isteğe bağlı karar kullanıcıya ait).

## 8. sitemap.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://alanadi.com/</loc><lastmod>2026-10-18</lastmod></url>
</urlset>
```
- Sadece 200 dönen, canonical, indekslenmesini istediğin URL'ler. `noindex`/yönlendirilen/404 URL koyma.
- Dosya başına ≤ 50.000 URL ve ≤ 50 MB; fazlası için sitemap index.
- `lastmod` gerçek değişiklik tarihi olsun (priority/changefreq Google'a gerekmez).
- robots.txt'e `Sitemap:` satırı ekle + Search Console → Sitemaps'ten gönder (kullanıcı yapar).

Framework karşılıkları:
- Next.js (App Router): `app/sitemap.ts`, `app/robots.ts` (`MetadataRoute.Sitemap`/`Robots`)
- Astro: `@astrojs/sitemap` + `site:` ayarı `astro.config`
- Nuxt: `@nuxtjs/sitemap` veya `@nuxtjs/seo`
- WordPress: Yoast / Rank Math / WP çekirdek sitemap (`/wp-sitemap.xml`)
- SvelteKit/diğer: `src/routes/sitemap.xml/+server.ts` ile dinamik

## 9. Mobil, HTTPS, hız (Core Web Vitals)
Eşikler ("iyi", sayfa ziyaretlerinin %75'i için): **LCP ≤ 2,5 sn · INP ≤ 200 ms · CLS ≤ 0,1**.

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```
Hız kontrol listesi:
- Görseller: WebP/AVIF, gerçek gösterim boyutuna göre `srcset`/`sizes`, `width`+`height` (CLS), ekran dışı `loading="lazy"`, LCP görseline `fetchpriority="high"` (lazy verme), hero için preload.
- Fontlar: `font-display: swap`, subset, en çok 2 aile, kritik font preload.
- JS: gereksiz paketleri çıkar, kod bölme, `defer`/`async`, 3. parti script'leri (chat, tag manager, widget) geciktir.
- CSS: kritik CSS satır içi, kullanılmayanı at, minify.
- Sunucu: CDN, önbellek başlıkları, gzip/brotli, HTTP/2-3, düşük TTFB (hedef < 800 ms).
- Reklam/banner/iframe için yer ayır (CLS).
- Ölç: PageSpeed Insights (gerçek kullanıcı CrUX verisi + lab), Search Console CWV raporu, Lighthouse.

## 10. JavaScript ve SPA
- Kritik metin, başlıklar, linkler ve meta etiketler **ilk HTML'de** (SSR/SSG/prerender) bulunmalı.
- Linkler gerçek `<a href="...">`; `onclick`/`router.push`-only linkler izlenmez.
- Hash (`#/sayfa`) URL'leri yerine History API yolları.
- İçerik "kullanıcı eylemi" gerektirmeden yüklenmeli; lazy-load içeriği görünür alanda tetiklenmeli.
- Google'ın sayfayı nasıl gördüğünü Search Console **URL Denetleme** ile test edin (kullanıcı yapar).

## 11. Görseller ve video
- Dosya adı anlamlı: `teknik-seo-kontrol-listesi.webp`.
- `alt`: görselin içeriğini ve sayfayla ilişkisini kısa, doğal anlat (doldurma yok). Dekoratif görselde `alt=""`.
- Görseli ilgili metnin yanına koy. Ayrı görsel sitemap gerekmez (çoğu durumda).
- Video: kendi sayfasında veya metin yanında, açıklayıcı başlık/açıklama, `VideoObject` schema (isteğe bağlı).

## 12. İç ve dış linkler
- Her sayfa ana menüden en çok 3 tıkta erişilebilir; **orphan** (hiç link almayan) sayfa olmasın.
- Konu kümesi: pillar sayfa ↔ destek yazıları karşılıklı linkli.
- Anchor metni hedefi anlatsın: "teknik SEO kontrol listesi" (✓), "tıklayın" (✗).
- Dış kaynaklara güvenilir siteleri bağla; kullanıcı yorumu/forum linkleri `rel="ugc nofollow"`, reklam/sponsor `rel="sponsored"`, güvenmediğin `nofollow`.
- Kırık link taramasını düzenli yap.

## 13. Yapılandırılmış veri (JSON-LD)
Kurallar: JSON-LD kullan, sayfada **görünen** içeriği yansıt, uydurma veri ekleme, geçerli JSON olsun.

Ana sayfa: Organization + WebSite
```html
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"Organization","@id":"https://alanadi.com/#org","name":"MARKA","url":"https://alanadi.com/","logo":"https://alanadi.com/logo.png","sameAs":["https://www.instagram.com/marka"]},
 {"@type":"WebSite","@id":"https://alanadi.com/#website","url":"https://alanadi.com/","name":"MARKA","inLanguage":"tr","publisher":{"@id":"https://alanadi.com/#org"}}
]}
</script>
```
Blog yazısı: Article/BlogPosting + BreadcrumbList
```html
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"BlogPosting","headline":"BAŞLIK","description":"ÖZET","image":["https://alanadi.com/img/kapak.webp"],"datePublished":"2026-10-18","dateModified":"2026-10-18","author":{"@type":"Person","name":"YAZAR ADI","url":"https://alanadi.com/yazar/ad"},"publisher":{"@id":"https://alanadi.com/#org"},"mainEntityOfPage":"https://alanadi.com/blog/yazi"},
 {"@type":"BreadcrumbList","itemListElement":[
   {"@type":"ListItem","position":1,"name":"Ana Sayfa","item":"https://alanadi.com/"},
   {"@type":"ListItem","position":2,"name":"Blog","item":"https://alanadi.com/blog"},
   {"@type":"ListItem","position":3,"name":"BAŞLIK"}]}
]}
</script>
```
Diğer türler: `Product` + `Offer` (fiyat, stok, para birimi; sayfada görünen), `LocalBusiness` (ad, adres, telefon, saatler, geo), `FAQPage` (sayfada görünen S&C), `Review`/`AggregateRating` (**yalnız gerçek, sayfada görünen** yorumlar).

Notlar: FAQ ve HowTo zengin sonuçları Google'da büyük ölçüde kısıtlandı/kaldırıldı (FAQ yalnızca belirli kamu/sağlık sitelerinde); yine de anlamsal işaretleme zararsızdır ama zengin sonuç vaadi verme. Doğrulama: Google Rich Results Test, schema.org validator (kullanıcı yapar).

## 14. Open Graph / sosyal
```html
<meta property="og:type" content="article">
<meta property="og:title" content="BAŞLIK">
<meta property="og:description" content="ÖZET">
<meta property="og:image" content="https://alanadi.com/img/og.jpg"> <!-- 1200x630 -->
<meta property="og:url" content="https://alanadi.com/sayfa">
<meta property="og:locale" content="tr_TR">
<meta name="twitter:card" content="summary_large_image">
```
Önizleme zenginliği için (Google): `<meta name="robots" content="max-snippet:-1, max-image-preview:large">` (ikas gibi 1. sıra sitelerde var).

## 15. Çok dilli
```html
<link rel="alternate" hreflang="tr" href="https://alanadi.com/tr/sayfa">
<link rel="alternate" hreflang="en" href="https://alanadi.com/en/page">
<link rel="alternate" hreflang="x-default" href="https://alanadi.com/">
```
Her dil sürümü diğerlerine karşılıklı işaret etmeli ve kendi canonical'ına sahip olmalı.

## 16. İçerik kuralları (E-E-A-T uyumlu)
- Her sayfa tek ana niyeti karşılasın; rakip 1. sıradaki sayfalardan **daha faydalı** olacak: güncel veri, özgün örnek/görsel, net adımlar, SSS.
- İlk 100 kelimede cevap/özet; sonra derinleş.
- Yazar adı + kısa biyografi + uzmanlık; "Hakkımızda", iletişim, gizlilik/şartlar sayfaları; kaynak göster.
- Birinci elden deneyim (fotoğraf, test, vaka, müşteri sonucu) ekle.
- Güncelleme: yalnız içerik gerçekten güncellendiğinde `dateModified`/görünür tarih değişsin.
- Yapay zekâ ile taslak üretiliyorsa insan editörlüğü, doğrulama ve katma değer şart; ölçekli otomasyonla sayfa yığma yok. Sahte yazar yok.
- Kopya içerik yok; ince/alakasız sayfalar birleştirilsin veya noindex edilsin.

## 17. Anahtar kelime araştırma yöntemi (ücretli araç olmadan)
1. Siteden tohum çıkar: ürün/hizmet adları, kategori başlıkları, mevcut H1'ler.
2. Genişlet: Google otomatik tamamlama, "Diğer sorular", "Kullanıcıların yaptığı diğer aramalar", rakip başlıkları/H2'leri, Search Console sorguları (kullanıcıda varsa).
3. Niyeti sınıfla: bilgi / ticari araştırma / işlem / navigasyon.
4. Önceliği belirle: iş değeri × alaka × rekabet (yeni sitelerde uzun kuyruk, 3+ kelime).
5. Haritala: **sayfa ↔ 1 ana sorgu + 3–8 yardımcı sorgu**. Aynı sorguyu iki sayfa hedeflemesin (kanibalizasyon).
6. SERP'e bak: ilk 10 hangi tür? Aynı türde, daha iyi sayfa üret.
Kural: Web araması varsa (WebSearch) sorguları güncel doğrula; yoksa koddan ve içerikten türet ve varsayımı raporda belirt.

## 18. Yerel SEO
- Google İşletme Profili (kullanıcı yönetir): doğru kategori, NAP, saatler, fotoğraf, hizmetler, yorum yanıtları.
- Sitede NAP her yerde aynı biçimde; iletişim sayfası + footer + `LocalBusiness` schema.
- Şehir/ilçe + hizmet sayfaları (her biri özgün içerik, kopya şablon değil).
- Gömülü harita, yorumlar, yerel dizin/oda/dernek kayıtları.

## 19. AI aramaları (AI Overviews / AI Mode)
Google'a göre: **ek teknik gereksinim yok**, temel SEO yeterli. Taramaya izin ver, içeriği metin olarak sun, iç linklerle erişilebilir kıl, sayfa deneyimini iyileştir, kaliteli görsel/video kullan, schema'yı görünür içerikle eşleştir, İşletme Profili/Merchant Center'ı güncel tut. Özel "AI dosyası" veya özel schema gerekmez. Net cevap veren kısa özetler, açık başlıklar ve güvenilir kaynaklar hem klasik hem AI aramasında yardımcı olur.

## 20. Ölçüm (kullanıcı yapacak)
- Search Console: mülk ekle (alan adı mülkü önerilir) → sahiplik doğrula → sitemap gönder → Performans/Sayfa dizine ekleme/CWV raporlarını izle → önemli URL'lerde URL Denetleme.
- GA4 kur (olay/dönüşüm tanımla).
- Takvim: haftalık hata kontrolü, aylık sorgu/CTR incelemesi, 3 aylık içerik güncellemesi.

## 21. Spam ve yasaklar
Cloaking, gizli metin/link, anahtar kelime doldurma, link şemaları (satın alınan/toplu backlink, PBN), otomatik ölçekli düşük kaliteli içerik, kopya/scraped içerik, sahte yorum/yazar, yanıltıcı yönlendirme, hacklenmiş içerik. Hiçbirini yapma.

## 22. Dil ve Türkçe notları
- `<html lang="tr">`, `og:locale` `tr_TR`, `inLanguage: "tr"`.
- Türkçe karakterler başlık/içerikte doğru kullanılsın (ı, İ, ş, ğ); URL'de ASCII.
- Büyük/küçük harf: "İ/ı" dönüşümü için CSS `text-transform` yerine içerikte doğru yaz (SEO için title/description düz metin olmalı).
- Türkçe sorgularda İngilizce kaynaklar (ör. Semrush) çevrilmiş halde üst sırada çıkıyor: derin ve güncel Türkçe içerik fırsatı var.

## 23. Güncel tutma
Bu bilgi Ekim 2026 itibarıyla Google dokümanlarına dayanır. Emin olmadığın eşik/politika için (ör. CWV eşikleri, zengin sonuç desteği) şu resmi sayfalara bak (web erişimin varsa):
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/appearance/core-web-vitals
- https://developers.google.com/search/docs/appearance/structured-data/search-gallery
- https://developers.google.com/search/docs/appearance/ai-features
- https://developers.google.com/search/updates
