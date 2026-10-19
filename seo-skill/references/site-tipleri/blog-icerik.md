# Playbook: Blog / içerik / yayıncı sitesi

Bu site türünde SEO = **konu otoritesi + içerik kalitesi + bilgi mimarisi**. 1. sıradaki sayfaların ortak özellikleri için `1-siradakilerin-ozellikleri.md`'ye bak (ölçülmüş veri).

## Kullanıcıya doğrulat
"Blog neyle para kazanıyor/ne amaçlıyor (reklam, e-posta listesi, ürün satışı, marka)?" ve "Uzman olduğunuz ana konu(lar) hangileri?"

## Hedef ve KPI
Markasız organik tıklama, konu başına sıralanan sorgu sayısı, ilk 10'daki sayfa sayısı, CTR, kaydırma/okuma etkileşimi, bülten kaydı, güncelleme sonrası artış.

## Mimari: konu kümeleri (topic cluster)
- 3–6 ana konu (pillar). Her pillar için kapsamlı bir **ana rehber** + 8–20 destek yazısı.
- Destek yazıları → pillar'a ve birbirine bağlanır; pillar → tüm desteklere bağlanır.
- Tek konuya odaklan; alakasız konularda dağınık yazma (Google'ın "farklı konularda toplu içerik" uyarısı).
- Kategori/etiket arşivlerini kontrol et: ince etiket sayfalarını `noindex` yap veya birleştir; sayfalama düzgün.

## Yazı şablonu (rakip ölçümlerinden)
1. Title: `Ana Sorgu: Fayda/Rakam (Yıl) | Marka`; H1 sorguyu karşılar.
2. İlk 100 kelimede net cevap/özet (snippet adayı) + "Bu yazıda" özeti / içindekiler.
3. 6–12 H2: nedir → neden önemli → nasıl (adımlar) → örnekler → araçlar → yaygın hatalar → SSS.
4. Liste/tablo/görsel/ekran görüntüsü; alt metin.
5. Yazar adı + biyografi + uzmanlık + kaynaklar; `datePublished` + gerçek `dateModified`.
6. 3–6 ilgili iç link (açıklayıcı anchor), pillar'a link.
7. Bölüm sonu: sonraki adım/CTA/bülten.
8. Rakipte olmayan en az bir katma değer (özgün veri, deneyim, şablon, karşılaştırma).

## Schema
`BlogPosting`/`Article` (headline, image, datePublished, dateModified, author→Person, publisher→Organization), `BreadcrumbList`, yazar sayfasında `Person`/`ProfilePage`, ana sayfada `Organization` + `WebSite`. SSS görünürse `FAQPage` (zengin sonuç beklenmez).

## Teknik
- Okuma süresi/tarih görünür; `dateModified` yalnız anlamlı güncellemede.
- Görsel optimizasyonu ve CLS (reklam alanı için yer ayır); reklamlar içeriği kapatmasın.
- RSS/Atom, sitemap (`lastmod` doğru), canonical (UTM/parametre kopyaları), sayfalama.
- Yorum spam'i: `rel="ugc nofollow"`.
- Eski yazılar: birleştir/güncelle/301; "içerik budama" yalnız trafik ve backlink kontrolünden sonra.

## Anahtar kelime kalıpları
`X nedir`, `X nasıl yapılır`, `X ne işe yarar`, `en iyi X`, `X vs Y`, `X örnekleri`, `X hataları`, `X 2026`, `X rehberi`. Niyet: bilgi + ticari araştırma.

## Rakip analizi odağı
- Her pillar için 3–5 ana sorgu + 10 uzun kuyruk. İlk 3'ü: resmi kaynak mı, büyük yayıncı mı, küçük niş blog mu? Niş bloglar çıkıyorsa hedef gerçekçi.
- `competitor_probe.py` ile H2 haritası → **ortak konular zorunlu**, eksiklerini brief'e ekle.
- Başlık kalıpları (sayılı, sorulu, yıllı), TOC/SSS oranı, güncellik, yazar görünürlüğü.
- Zayıf rakip işareti: eski tarih, ince içerik, çevrilmiş İngilizce sayfa ile yarışıyorsan derin ve güncel Türkçe içerik fırsatı.

## Elle işler
Search Console, yazar profilleri ve görselleri (gerçek), bülten, konuk yazarlık/PR, sosyal dağıtım, içerik takvimi, 3 ayda bir içerik güncellemesi.

## Yapma
Toplu yapay zekâ içerik, sahte yazar, tarihi sadece "taze görünsün" diye değiştirme, kopya/spun içerik, anahtar kelime doldurma, alakasız konularda trend avcılığı, aynı sorguyu hedefleyen birden çok yazı (kanibalizasyon).
