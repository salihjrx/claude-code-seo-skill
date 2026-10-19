# SEO Kontrol Listesi (bitirmeden önce)

## A. Engelleyiciler
- [ ] Canlıda `Disallow: /` yok, sayfalarda istenmeyen `noindex` yok
- [ ] Tek sürüm: https + (www veya non-www), diğerleri 301
- [ ] Önemli sayfalar 200 dönüyor; 404'ler gerçek 404; yönlendirme zinciri yok
- [ ] Kritik içerik/linkler erişilebilir: ilk HTML'de veya render sonrası DOM'da doğrulandı (SPA ise kanıta göre SSR/SSG/prerender değerlendir)

## B. Dosyalar
- [ ] `robots.txt` (Sitemap satırı ile)
- [ ] `sitemap.xml` (yalnız canonical, 200, indekslenebilir URL'ler)
- [ ] Favicon, 404 sayfası
- [ ] Open Graph varsayılan görseli (1200×630)

## C. Her sayfa için
- [ ] Benzersiz, açık `<title>` (uzunluk rehberi ~50–60 krk; katı kural değil)
- [ ] Benzersiz `<meta description>` (rehber ~120–160 krk; Google yeniden yazabilir)
- [ ] Net bir `<h1>`; mantıklı H2/H3 hiyerarşisi (tek H1 sıralama şartı değil)
- [ ] `<html lang="tr">`, viewport, canonical (kendi mutlak URL'si)
- [ ] OG/Twitter etiketleri
- [ ] Açıklayıcı URL (ASCII, tire)
- [ ] Görsellerde `alt`, `width/height`, modern format, lazy-load (LCP hariç)
- [ ] İç linkler açıklayıcı anchor ile; orphan sayfa yok
- [ ] JSON-LD geçerli ve görünür içerikle uyumlu
- [ ] Sayfa kullanıcının sorusunu net yanıtlıyor (doğal anlatım; anahtar kelime doldurma yok)

## D. Site geneli schema
- [ ] Ana sayfa: Organization + WebSite
- [ ] İç sayfalar: BreadcrumbList
- [ ] Blog: BlogPosting/Article (yazar, tarih)
- [ ] E-ticaret: Product + Offer; yerel işletme: LocalBusiness
- [ ] Uydurma veri / sahte puan yok

## E. Performans
- [ ] LCP ≤ 2,5 sn, INP ≤ 200 ms, CLS ≤ 0,1 (PageSpeed Insights / Lighthouse)
- [ ] Görseller sıkıştırılmış ve boyutlandırılmış
- [ ] Gereksiz 3. parti script/font azaltılmış
- [ ] Önbellek + sıkıştırma (CDN/hosting)

## F. İçerik ve güven
- [ ] Hakkımızda, İletişim, Gizlilik, Şartlar sayfaları
- [ ] Yazar bilgisi ve kaynaklar
- [ ] Her sayfa tek ana niyet; kanibalizasyon yok
- [ ] Anahtar kelime haritası var (sayfa ↔ sorgu ↔ niyet)
- [ ] Kopya/ince içerik yok

## G. Kullanıcının elle yapacakları
- [ ] Search Console'a mülk ekle + sahiplik doğrula + sitemap gönder
- [ ] GA4 kur, dönüşümleri tanımla
- [ ] Google İşletme Profili (yerel işletmeyse)
- [ ] Rich Results Test ve PageSpeed Insights ile doğrula
- [ ] Doğal backlink/PR planı, içerik takvimi
- [ ] 2–4 hafta sonra Search Console'da dizin ve performans kontrolü

## H. Çıktılar
- [ ] `seo_audit.py` KRİTİK = 0
- [ ] Build/lint/test geçti
- [ ] `SEO-RAPOR.md` yazıldı (yapılanlar, kalanlar, kullanıcı işleri, 30/60/90 gün planı)
