# Katmanlar: her site türünün üstüne eklenen durumlar

`detect_site.py` çıktısında "Ek katmanlar" olarak önerilir. Ayrıntı için `evrensel-seo-ilkeleri.md` §10 (uluslararası) ve §14 (taşıma).

## <a id="cok-dilli"></a>Çok dilli / çok bölgeli site
- Her dil sürümü için kararlı, ayrı URL (`/tr/`, `/en/` veya alt alan adı). Yalnızca çerez/IP ile dil değiştirme yok.
- `hreflang`: karşılıklı (A→B ve B→A), kendine referans, `x-default`; her sürüm **kendi canonical'ına** sahip (diğer dile canonical verme).
- Metin gerçekten yerelleştirilmiş olsun (makine çevirisi bırakma); title/description/schema/menü/URL slug da çevrilsin.
- Otomatik dil yönlendirmesi kullanıcıyı diğer dillerden alıkoymasın; dil seçici gerçek `<a href>`.
- Sitemap'te dil alternatifleri (`xhtml:link`) isteğe bağlı; sitemap'ler dil bazlı bölünebilir.
- Anahtar kelime araştırması **her dil/ülke için ayrı** yapılır; çeviri ≠ yerelleştirme.
- Rakip analizi her ülke için ayrı (`hl`/`gl` değiştir).

## <a id="spa"></a>SPA / istemci tarafı render
- SPA **tek başına sorun değildir** (Google JavaScript'i işleyebilir; yine de render gecikmesi ve diğer arama motorları/botlar nedeniyle SSR/SSG/prerender çoğu projede yararlıdır). Karar kanıta dayanır: ham HTML ile render edilmiş DOM'u karşılaştır (`javascript-rendering-debugging.md`).
- Test: derlenmiş çıktıda (veya `curl` ile) başlık, metin ve linkler var mı? Önemli içerik/link/meta **yalnız JS sonrası** geliyorsa ve bu somut olarak gösterilebiliyorsa bulguyu P1/UYARI olarak yaz; sırf SPA diye mimariyi yeniden yazmayı önerme.
- Çözüm sırası: framework'ün SSR/SSG'si (Next/Nuxt/SvelteKit/Astro) → prerender (statik üretim) → son çare dinamik render servisi.
- Her görünüm için gerçek URL (History API), sayfaya özgü title/description/canonical; client-side 404 yerine gerçek HTTP 404.
- Primer navigasyon gerçek `<a href>`. Lazy içerik kullanıcı etkileşimi beklemesin.

## Taşıma / yeniden tasarım / alan adı değişikliği
- Eski URL envanteri → yeni URL eşlemesi (en yakın karşılık); URL'yi mümkünse koru.
- Tek sıçramalı 301; zincir/döngü yok; her şeyi ana sayfaya yönlendirme.
- İç linkler, canonical, hreflang, sitemap, schema yeni URL'lere güncellenir. Eski yönlendirmeler aylarca kalır.
- Staging `noindex`/auth ile korunur; **canlıya geçişte kaldırıldığı doğrulanır**.
- Search Console: yeni mülk, sitemap, adres değişikliği (alan adı taşımada); taşıma sonrası 2–4 hafta izle.
- Taşıma öncesi trafik alan en iyi sayfaların ve backlink alan URL'lerin listesini çıkar ve sınama yap.

## WordPress / CMS eklentisi katmanı
Yoast / Rank Math / SEOPress tek biçimde kullanılsın (iki SEO eklentisi çakışmasın). Başlık şablonları, sitemap, breadcrumb, schema eklentiden; tema dosyasına çift schema/meta ekleme. Gereksiz arşivler (tarih, yazar, etiket) `noindex`.

## Çok şubeli işletme
Her şube kendi sayfası + `LocalBusiness` `@id`; tek ortak "şubeler" dizin sayfası. NAP şube bazında.

## Mevcut trafiği olan site
Dokunmadan önce Search Console verisini iste (veya kullanıcıdan sorgu/sayfa dışa aktarımı). En çok trafik alan URL'leri, title'ları ve içerik yapısını **koru**; değişiklikleri küçük adımlarla ve ölçerek yap.
