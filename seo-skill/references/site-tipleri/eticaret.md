# Playbook: E-ticaret / online mağaza

Genel kural ve ayrıntılar: `evrensel-seo-ilkeleri.md` §8 (e-ticaret). Bu dosya özetler ve uygulama şablonlarını verir.

## Kullanıcıya doğrulat (tek soru, gerekiyorsa)
"Fiziksel ürün satan mağaza mı (fiyat/stok/kargo), yoksa hizmet/dijital ürün mü?"

## Hedef ve KPI
Organik gelirli sipariş, kategori sayfası sıralamaları, ürün sayfası dizin kapsamı, Merchant Center ürün onayı, ürün zengin sonucu uygunluğu.

## Sayfa tipleri ve şablonlar
| Sayfa | Title formülü | H1 | Zorunlu içerik |
|---|---|---|---|
| Ana sayfa | `Marka | Ana kategori/değer önerisi` | marka + değer önerisi | öne çıkan kategoriler (crawlable link), güven unsurları |
| Kategori | `[Kategori] Modelleri ve Fiyatları | Marka` | `[Kategori]` | kısa tanıtım (üstte kısa, altta uzun SEO metni), filtre, alt kategori linkleri, SSS, breadcrumb |
| Ürün | `[Marka] [Model] [Ayırt edici özellik] | Marka` | ürün adı | benzersiz açıklama, fiyat/para birimi/stok, SKU/GTIN, varyantlar, kargo/iade, gerçek yorumlar, ilgili ürünler |
| Marka / koleksiyon | `[Marka] Ürünleri` | | kısa metin + ürün listesi |
| Rehber/blog | niyete göre ("... nasıl seçilir?") | | ürün ve kategoriye iç link |

## Schema (yalnız sayfada görünen veriyle)
- Ürün: `Product` + `Offer` (price, priceCurrency, availability, url), `brand`, `sku`/`gtin`, `image`; **gerçek** yorum varsa `AggregateRating`/`Review`.
- Kategori/liste: `BreadcrumbList`, ana sayfada `Organization` + `WebSite` (+ site içi arama `SearchAction` isteğe bağlı).
- İade/kargo bilgisi için `MerchantReturnPolicy` / `OfferShippingDetails` (varsa).
- Fiyat/stok değişince schema da otomatik güncellenmeli (veriden üret, elle yazma).

## Teknik tuzaklar (en sık)
1. **Facet/filtre/sıralama URL patlaması:** `?renk=&beden=&sirala=` kombinasyonları. Talebi olan filtre kombinasyonları için temiz URL'li indekslenebilir sayfa, diğerleri canonical → ana kategori veya noindex. robots ile toptan engelleme yapma (canonical/noindex görülemez).
2. **Varyantlar:** tek URL + varyant seçimi veya varyant başına URL; her biri tutarlı canonical. Birbirinin kopyası ince sayfalar üretme.
3. **Sayfalama:** `?sayfa=2` her sayfa kendi ürünlerini gerçek `<a href>` ile göstersin; kendi canonical'ı olsun; hepsini sayfa 1'e canonical yapma. Sonsuz kaydırmada doğrudan URL'li sayfalama linkleri bulunsun.
4. **Stokta yok:** geçiciyse sayfa kalsın (doğru stok durumu + alternatifler); kalıcı kaldırmada gerçek yedek ürüne 301, yoksa 404/410. Hepsini ana sayfaya yönlendirme.
5. Sepet, ödeme, hesap, dahili arama sonuçları: `noindex` (ve gerekirse robots).
6. Çift URL: `/urun/x` ve `/kategori/urun/x` → tek canonical.
7. Görseller: WebP/AVIF, `srcset`, ürün başına çok açılı görsel, anlamlı dosya adı + alt (marka+model+özellik). LCP görseli lazy olmasın.
8. Hız: üçüncü parti script (chat, remarketing, yorum widget) CWV'yi bozar; ertele.
9. Platform (Shopify/ikas/Ticimax/IdeaSoft/WooCommerce): tema/şablon ve platform ayarlarının yerini kullan (ör. Shopify `canonical_url`, `structured_data`). Çekirdeği hacklemeyin.

## Anahtar kelime kalıpları (Türkçe)
`[ürün] fiyatları`, `[ürün] modelleri`, `en iyi [ürün]`, `[ürün] nasıl seçilir`, `[marka] [model] yorumları`, `[ürün] ucuz/indirim`, `[ürün] satın al`, `[A] mı [B] mi`. İşlem niyetli (satın al, fiyat) → kategori/ürün; bilgi niyetli → rehber/blog.

## Rakip analizi odağı
- Sorgu seti: ana kategoriler × (fiyat/model/en iyi/nasıl seçilir) + 5–10 uzun kuyruk ürün sorgusu.
- SERP türü: ilk 10'da kategori mi, pazaryeri mi (Trendyol/Hepsiburada), rehber mi? Pazaryeri doluysa **niş/uzun kuyruk + rehber içeriği** hedefle.
- Ölç: kategori sayfasında üst metin/alt metin uzunluğu, filtre yapısı, SSS, Product/Offer/Breadcrumb/ItemList schema, yorum/puan, görsel sayısı, iç link blokları (alt kategoriler, popüler aramalar).

## İçerik ve iç link mimarisi
Ana sayfa → kategori → alt kategori → ürün (≤3 tık). Kategori sayfalarına rehber yazılarından bağlantı; ürün sayfalarından kategori ve ilgili ürüne. "Birlikte alınanlar", "benzer ürünler" gerçek linklerle.

## Yapma
Sahte yorum/puan/indirim/stok kıtlığı, üretici metnini tek içerik olarak bırakma, her filtre kombinasyonunu indeksleme, doorway kategori sayfaları.

## Kullanıcıdan gerekenler / elle işler
Merchant Center feed ve onay, Search Console, ürün verisi (GTIN, açıklama), gerçek yorum toplama süreci, kargo/iade politikası metinleri, marka/PR bağlantıları.
