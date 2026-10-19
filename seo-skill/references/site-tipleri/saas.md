# Playbook: SaaS / yazılım ürünü / uygulama

## Kullanıcıya doğrulat
"Ana hedef: deneme/demo kaydı mı, ücretli abonelik mi? Hedef kitle bireysel mi (B2C) kurumsal mı (B2B)?"

## Hedef ve KPI
Kayıt/deneme/demo sayısı, markasız (non-brand) organik trafik, "alternatif/karşılaştırma/kullanım senaryosu" sayfa sıralamaları, dokümantasyondan kayıt dönüşümü.

## Kritik teknik konu: pazarlama sayfaları vs uygulama
- **Pazarlama sayfaları (ana, özellikler, fiyat, blog, dokümantasyon, kullanım senaryoları):** SSR/SSG, taranabilir, indekslenebilir.
- **Uygulama alanı** (`/app`, `/dashboard`, `/settings`, giriş sonrası): `noindex` + robots uyumu; indekslenmesin.
- Aynı alan adında SPA ise pazarlama sayfalarını SPA'dan ayır (ayrı SSG/SSR rotaları ya da prerender). Aksi halde meta ve içerik HTML'de yoktur → KRİTİK.
- Alt alan adı (`app.`/`docs.`/`blog.`) kararı: Google için ikisi de çalışır; yönetim kolaylığına göre seç, ama canonical ve iç linkleri tutarlı tut.

## Sayfa tipleri ve şablonlar
| Sayfa | Title formülü | Zorunlu içerik |
|---|---|---|
| Ana sayfa | `Marka: [Net değer önerisi] | [Kategori]` | ne yapar / kimin için / kanıt (logolar, sayılar), CTA, SSS |
| Özellik sayfaları (her özellik 1 sayfa) | `[Özellik] – [Fayda] | Marka` | sorun → çözüm, ekran görüntüsü, kullanım örneği |
| Kullanım senaryosu / sektör / rol sayfaları | `[Marka] [Rol/Sektör] için` | gerçek senaryo, vaka kanıtı |
| Fiyatlandırma | `Fiyatlandırma ve Planlar | Marka` | net plan tablosu, SSS, itirazlar (`FAQPage` içeriği görünürse) |
| Entegrasyonlar | `[Marka] + [Araç] Entegrasyonu` | gerçek kurulum adımları |
| Karşılaştırma / alternatif | `[Marka] vs [Rakip]`, `[Rakip] alternatifleri` | **dürüst**, doğrulanabilir tablo (yanıltıcı değil) |
| Dokümantasyon / rehber | görev odaklı | kod örnekleri, güncel sürüm |
| Blog | niyet odaklı | ürünle ilgili sorunlara çözüm, ürün CTA |
| Changelog, güvenlik, durum | | güven sinyali |

## Schema
`Organization` + `WebSite`; ürün sayfasında `SoftwareApplication`/`WebApplication` (applicationCategory, offers varsa gerçek fiyat); `BreadcrumbList`; blog `BlogPosting`; SSS `FAQPage` (zengin sonuç garantisi yok); video `VideoObject`.

## Anahtar kelime kalıpları
`[kategori] yazılımı`, `en iyi [kategori] programı`, `[rakip] alternatifleri`, `[A] vs [B]`, `[iş] nasıl yapılır` (problem odaklı), `[kategori] fiyatları`, `ücretsiz [kategori] aracı`, `[araç] entegrasyonu`.

## Rakip analizi odağı
- Önce hangi tür kazanıyor bak: listicle'lar ("en iyi 10 …"), incelemeler (G2/Capterra benzeri), rakip markalar, resmi doküman.
- Karşılaştırma ve alternatif sorgularında ilk 3'ün yapısı (tablo, kriter seti, adil dil). Fiyat sayfası: sayfa yapısı + SSS + schema.
- Doküman/rehber sorgularında rakip dokümanı: kod örneği, iç link ağı, güncellik.
- Boşluk: kendi ürün kanıtın (müşteri sonucu, benchmark, şablon, ücretsiz araç) — katma değer olarak ekle.

## Elle işler
Search Console + GA4 olayları (kayıt, deneme), G2/Capterra/ürün dizin profilleri, müşteri vakaları (izinli), entegrasyon ortaklarından bağlantı, ücretsiz araç/şablonla doğal backlink, PR.

## Yapma
Uygulama içi (giriş gerektiren) sayfaları indekslemek, abartılı veya doğrulanamayan karşılaştırma iddiaları, rakip adıyla yanıltıcı sayfa, yapay zekâ ile toplu "alternatif" sayfa fabrikası, sahte müşteri logosu.
