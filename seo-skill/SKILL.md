---
name: seo
description: Bir web sitesinin türünü (e-ticaret, yerel işletme, SaaS, blog, portföy/kurumsal, ilan/pazaryeri, eğitim, haber) otomatik algılar, gerçek Google sonuçlarında rakip analizi yapar ve siteye uygun SEO'yu kanıt disipliniyle uygular (teknik, sayfa içi, schema, içerik, performans, uluslararası, taşıma, trafik düşüşü). Kullanıcı "SEO yap", "siteyi SEO'ya uygun yap", "SEO denetimi", "rakip analizi", "trafik düştü", "Google'da yükselt" dediğinde veya bir site projesi verip SEO istediğinde kullan.
---

# SEO Skill: algıla → araştır → denetle → rakiple karşılaştır → uygula → kanıtla

Amaç **sıralama vaadi değil**, doğru sorgularda görünürlüğü, nitelikli trafiği ve dönüşümü sistematik ve kanıtlı biçimde artırmaktır. **1. sıra, indekslenme, zengin sonuç, AI yanıtlarında yer alma, trafik veya gelir garanti edilemez; asla vaat etme.**

Bilgi `references/` altındadır: SEO'yu yeniden araştırma, önce oradan oku. Hangi dosyanın ne zaman açılacağı için `references/INDEKS.md`. Kullanıcı Türkçe konuşur: yanıt, rapor ve commit mesajları Türkçe (kod/dosya adları orijinal).

## Kanıt sözleşmesi (her çıktı için geçerli)
- Erişmediğin şeye eriştiğini söyleme (site, SERP, Search Console, analitik, log, üretim). Erişemediğini açıkça yaz.
- Arama hacmi, zorluk, CPC, sıralama, trafik, backlink, indekslenme, Core Web Vitals, rakip verisi **uydurma**. Kaynağı ve tarihi yaz.
- Önemli iddiaları etiketle: **Doğrulandı** (çalıştırıp/okuyup gördün) · **Gözlendi** (SERP/sayfa anlık gözlemi) · **Hipotez** · **Bilinmiyor** · **Test edilmedi**.
- SERP gözlemi yerel ve zamana bağlıdır (ülke, dil, cihaz, tarih, kişiselleştirme); **nedenselliğin kanıtı değil**. Korelasyonu "sıralama faktörü" diye sunma.
- Betik çıktısı **kanıt**tır, nihai karar değil: betikler JavaScript çalıştırmaz, tam tarayıcı/Search Console/log yerine geçmez.
- Her araştırma kaydında: tarih, ülke/dil, cihaz varsayımı, sorgu, URL, örneklem. Erişilemeyen veri → "yapılamadı: sebep".

## Mod seç (isteğe göre)
| Mod | Ne zaman | Ana referanslar |
|---|---|---|
| Kur (build) | yeni site/özellik | site-tipleri, bilgi-bankasi, seo-architecture-and-url-governance |
| Denetle (audit, salt-okunur) | "sadece denetle / dokunma" → **dosya değiştirme** | kontrol-listesi, technical-seo-release-gate |
| Düzelt (fix) | bulguları uygula | bilgi-bankasi, acceptance-test-catalog |
| Rakip / pazar araştırması | rakip, yeni dil/ülke | rakip-analizi, global-market-research, market-research-workbook |
| E-ticaret | mağaza | site-tipleri/eticaret, ecommerce-catalog-and-facets |
| Uluslararası | çok dil/ülke | katmanlar#cok-dilli, international-* |
| Yerel | şube/hizmet bölgesi | site-tipleri/yerel-isletme |
| Taşıma (migration) | alan adı/CMS/URL değişimi | migration-playbook, katmanlar |
| Trafik düşüşü | "trafik düştü" | drop-investigation-runbook, incident-response-seo |
| İçerik sistemi | blog/içerik planı | content-brief-template, content-quality-and-editorial-governance |
| Ölçüm | analitik/deney | measurement-plan, analytics-experiment-design |
| AI keşfedilebilirlik | "AI aramada çıkmak" | ai-search-and-entity-readiness (garanti yok; temel SEO + özgün, doğrulanabilir içerik) |

Tam "SEO yap" = Algıla + Araştır + Denetle + Rakip analizi + **güvenli, geri alınabilir düzeltmeleri uygula** + doğrula + rapor. Üretime yayın, DNS, harici hesap işlemi, ücretli işlem ve push için **açık onay** gerekir.

## İş akışı

### 1. Algıla (soru sormadan önce)
```
python .claude/skills/seo/scripts/detect_site.py .
```
(Windows'ta `py`.) Çıktı: tür tahmini + güven + kanıt dosyalar, teknoloji/render notları, dil, çok dillilik, marka, alan adı, okunacak playbook. **Çıktı bir hipotezdir.**
- **Güven yüksek:** türü bildir, ilgili playbook'u oku, devam et.
- **Orta (karma):** iki playbook'u da oku, kullanıcıya **tek** doğrulama sorusu sor, cevap beklerken denetimle ilerle.
- **Düşük / boş proje:** tek soru: "Bu site ne tür bir site ve kimlere hitap ediyor?"
- Alan adı bulunamadıysa tek kısa soru: canlı alan adı? Gerisini koddan çıkar.
- Mevcut kodu, yapıyı, tasarım dilini tanı; framework'ün yerleşik yolunu kullan.

### 2. Araştır (her projede zorunlu)
- Önce kod deposunu incele; sonra mümkünse canlı siteyi ve arama sonuçlarını.
- Uygulamadan önce mevcut URL, metadata, canonical, indekslenebilirlik ve (varsa) trafik verisini **kaydet** (geri dönüş ve karşılaştırma için). Kritik değişiklikten önce **etki alanı ve geri alma planı** belirle.
- Sorgu araştırmasında ülke, dil, cihaz, niyet, SERP özelliklerini kaydet. Çok pazarlıysa pazar matrisi + sorgu→URL haritası (`global-market-research.md`).
- Rakipten metin kopyalama; onların eksik bıraktığı kullanıcı ihtiyaçlarını bul.

### 3. Denetle
- `python .claude/skills/seo/scripts/seo_audit.py <build_veya_site_klasörü>` (Next/Astro/Vite için önce `npm run build`; HTML çıkmıyorsa dev sunucu + `--url http://localhost:PORT --allow-private`).
- Canlı URL listesi: `seo_url_audit.py urls.txt -o audit.csv --delay 1`. Sitemap: `seo_sitemap_audit.py <url|dosya> --recursive --check-robots --urls-out urls.txt`.
- Betik + kod incelemesi + `kontrol-listesi.md` + türün playbook'undaki teknik tuzaklar. SPA/JS ise ham HTML ile render edilmiş DOM'u karşılaştır (`javascript-rendering-debugging.md`).
- Kontrol mekanizmalarını karıştırma: robots = tarama; noindex = sayfa düzeyi (taranabilmeli ki görülsün); canonical = ipucu; sitemap = keşif sinyali (indeks garantisi değil).
- Bulguları **P0–P3** + güven etiketiyle sınıfla: P0 site engelli/noindex/HTTPS/5xx · P1 keşfedilemeyen/kopya/yanlış durum kodu · P2 sayfa içi/içerik/schema/görsel/hız · P3 cila. Çok bulgu varsa `seo-prioritization-model.md` (ham değerleri göster, sonucu resmi metrik gibi sunma). Güvenlik/gizlilik ve yayın engelleyicileri puanı geçersiz kılar. Aynı kök neden için tek kayıt.

### 4. Rakip analizi (gerçek Google sonuçlarına dayalı)
`references/rakip-analizi.md`: 10–25 niyetli sorgu → Google SERP (tarayıcı aracı varsa gerçek Google, yoksa WebSearch; CAPTCHA aşılmaz) → ilk 3 organik sonuç → `competitor_probe.py` (`--self <klasör>` ile boşluk) → boşluk tablosu → fırsat sınıfı (hızlı kazanç / boşluk / savunma / vazgeç). Ağ yoksa "yapılamadı: ağ/arama erişimi yok" yaz. Sonuçları nedensellik değil **gözlem** olarak sun.

### 5. Uygula (öncelik sırasıyla, türe göre)
1. P0 engelleyiciler (robots/noindex/HTTPS/host/5xx/canonical localhost).
2. Temel dosyalar: `robots.txt` + Sitemap satırı, `sitemap.xml`, favicon, 404.
3. Sayfa içi: benzersiz ve açık title/description, net H1 ve mantıklı hiyerarşi, `lang`, viewport, canonical, OG/Twitter, görsel alt/boyut, iç link. (Karakter sayıları ve H1 sayısı **rehberdir, sıralama kuralı değil**.)
4. Schema: yalnız sayfanın **görünür ve doğru** içeriği için geçerli türler (`schema-validation-matrix.md`). Her sayfaya her türü ekleme; geçerli JSON-LD zengin sonuç garantisi vermez.
5. Performans: LCP/INP/CLS için **saha verisi** (CrUX/Search Console) ile laboratuvar (Lighthouse) ayrımı; eşikleri güncel resmi dokümandan doğrula.
6. SPA/JS: sırf SPA diye mimariyi yeniden yazma; kanıt varsa (önemli içerik/link/meta yalnız JS sonrası geliyor) SSR/SSG/prerender öner.
7. İçerik: rakip analizindeki zorunlu konulara ve brief'lere göre mevcut sayfaları güçlendir; toplu yeni içerik kullanıcı onayı olmadan üretilmez.
8. Türe özel öncelikler:

| Tür | Önce bak/yap |
|---|---|
| E-ticaret | Facet/filtre URL politikası, kategori sayfası metni, Product/Offer schema (görünür fiyat/stok ile tutarlı), varyant-canonical, stoksuz ürün politikası, sepet/ödeme noindex |
| Yerel işletme | NAP tutarlılığı, LocalBusiness schema, hizmet×ilçe sayfaları (ince/kopya değil), mobil hız, tel/harita linkleri |
| SaaS | Pazarlama sayfaları SSR/SSG, uygulama alanı noindex, özellik/fiyat/karşılaştırma sayfaları, SoftwareApplication schema |
| Blog/içerik | Konu kümeleri + iç link, yazı şablonu, yazar/E-E-A-T, arşiv/etiket politikası, kanibalizasyon |
| Portföy/Kurumsal | Marka+hizmet sayfaları, vaka çalışmaları, Organization/Person schema, tek sayfalık siteyi bölme |
| İlan/Pazaryeri | Süresi dolan ilan politikası, kategori×konum matrisi, ince sayfa eşiği, ItemList/JobPosting schema, sitemap parçalama |
| Eğitim | Course schema, müfredat görünürlüğü, eğitmen E-E-A-T, geçmiş tarihli oturumlar |
| Haber | Hız, tarih dürüstlüğü, yazar şeffaflığı, NewsArticle schema, görsel boyutu |

### 6. Doğrula (kanıt olmadan "bitti" deme)
- Build/lint/test; üretilen çıktıda title/description/canonical/H1/schema; `seo_audit.py` tekrar → KRİTİK = 0; `python -m unittest discover -s tests` (paket testleri).
- **Yayın kapısı** (`technical-seo-release-gate.md`): Kritik maddeler geçmeden "SEO-doğrulandı" deme: üretim yanlışlıkla noindex/engelli değil; host+HTTPS+yönlendirme döngüsüz; gelir getiren URL'ler doğru durum kodu; canonical doğru; önemli içerik/link render oluyor; staging/preview URL'si sitemap/canonical'a sızmamış.
- Üretim erişimi yoksa üretim doğrulaması **"beklemede"** yazılır, "geçti" değil. Çalıştırılamayan kontrol → "çalıştırılamadı" + elle doğrulama adımı.
- Kayıt formatı: test URL'si, beklenen, gözlenen, tarih, araç, durum, sınırlama.

### 7. Raporla
Proje köküne `SEO-RAPOR.md` (iskelet: `seo-report-template.md`): yönetici özeti (**kanıta dayalı durum, sahte skor yok**) · yöntem ve sınırlar (hangi URL/veri/araç gerçekten kullanıldı, tarih, örneklem) · bulgular (ID, öncelik, güven, etkilenen şablon/URL örnekleri, kanıt, beklenen/gözlenen, etki, kök neden hipotezi, düzeltme, kabul testi, geri alma/izleme) · yapılan değişiklikler (dosya, davranış, çalıştırılan testler ve gerçek sonuçları, çalıştırılmayanlar) · yayın/ölçüm planı (korumalı metrikler, geri alma tetikleyicisi, gözden geçirme tarihi) · **kullanıcının elle yapacakları** (Search Console doğrulama+sitemap, GA4, Google İşletme Profili/Merchant Center, backlink/PR, içerik) · 30/60/90 gün planı · anahtar kelime haritası (sayfa ↔ sorgu ↔ niyet; hacim uydurma yok). Rakip analizi yapıldıysa `SEO-RAKIP-ANALIZI.md` (`rakip-analizi.md` §7). Sohbette kısa Türkçe özet.

## Anti-pattern'ler (yapma)
- Tek göstergeden (SPA, H1 sayısı, karakter sayısı, betik skoru, tek SERP örneği) kesin hüküm çıkarma.
- Sırf bulgu sayısını artırmak için küçük detayları "kritik" yazma.
- Doğrulanmamış rakamı rapora koyma; "bitti" deyip testi çalıştırmama.
- Aynı sorun için çoğul kayıt; kök neden yerine belirti yamama.
- Trafik alan sayfanın URL/title'ını gerekçesiz değiştirme; yönlendirmesiz URL taşıma.
- Trafik düşüşünde nedensellik atfetme (mevsim, SERP değişimi, izleme hatası, stok, rakip aynı grafiği verebilir): önce `drop-investigation-runbook.md`.

## Kurallar
- **Uydurma yok:** adres, telefon, puan, yorum, yazar, fiyat, kuruluş yılı, sosyal link kodda yoksa icat etme, schema'ya ekleme; raporda "kullanıcıdan gerekli" yaz.
- **Sahte sinyal yok:** sahte yazar/yorum/AggregateRating, gizli metin, cloaking, anahtar kelime doldurma, doorway sayfa, toplu yapay zekâ içerik fabrikası.
- **Mevcut tasarımı/işlevi bozma;** küçük, geri alınabilir değişiklikler. URL değişirse 301 + iç link güncelle.
- **Canlı güvenliği:** `Disallow: /` / `noindex` yalnız staging'de; canlıda kalıntı kontrolü yap. robots.txt erişim kontrolü değildir (herkese açık).
- **Etik tarama:** bot korumasını/CAPTCHA'yı aşma, giriş/hesap açma, ücretli duvarı geçme; hız sınırı koy; yalnız yetkili olduğun siteleri tara.
- **Gizlilik:** gizli anahtar, çerez, yetki başlığı, .env, kişisel veri çıktıya/rapora yazılmaz; sorgu dizelerinde token/oturum olabilir (maskele). Harici SEO servisine veri gönderme ancak yetki ve gizlilik onayıyla.
- Git varsa küçük mantıklı commit; kullanıcı istemedikçe push/yayın yok.
- Güncel eşik/politika şüphesi → `guncel-resmi-kaynaklar.md` ve `bilgi-bankasi.md` "Güncel tutma".
- Kullanıcıya yalnızca kararı etkileyen şeyi sor; gerisi için makul varsayım yap ve raporda belirt.

## Bitti tanımı
(1) Tür ve güven bildirildi, (2) P0 yok veya kullanıcı kararına bağlı, (3) değişiklikler küçük/geri alınabilir ve listelendi, (4) testler çalıştırıldı, gerçek sonuçları yazıldı, (5) yayın kapısı: geçen/beklemede/çalıştırılamayan ayrıldı, (6) etiketli kanıt + sınırlar rapora yazıldı, (7) kullanıcı işleri ve izleme planı verildi.
