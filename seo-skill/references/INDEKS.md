# Referans İndeksi: hangi dosyayı ne zaman aç

Dil notu: B bölümündeki dosyalar İngilizcedir (SEO Apex'ten alındı). İçerikleri kısa ve işlemseldir; Türkçe çıktı üretirken içeriği Türkçe kullan, terimleri koru.

## A. Türkçe çekirdek (her çalıştırmada önce)
| Dosya | Ne zaman |
|---|---|
| `site-tipleri/<tür>.md` | `detect_site.py` türü söyledikten hemen sonra |
| `site-tipleri/katmanlar.md` | çok dilli, SPA, taşıma, WordPress, çok şube |
| `rakip-analizi.md` | rakip analizi prosedürü + rapor formatı |
| `bilgi-bankasi.md` | title/description/canonical/schema/robots/hız kuralları ve kod örnekleri |
| `kontrol-listesi.md` | bitirmeden önce |
| `1-siradakilerin-ozellikleri.md` | yalnız bağlam: küçük bir SERP gözlemi, kural değil |
| `evrensel-seo-ilkeleri.md` | kullanıcının "universal-seo" metni (modlar, P0–P3, e-ticaret, uluslararası, taşıma) |
| `_apex-skill-orijinal.md` | Apex'in tam İngilizce işletim sistemi metni; ayrıntı gerektiğinde bölüm bölüm |

## B. Operasyon el kitapları (İngilizce, Apex)
| Dosya | Konu | Ne zaman |
|---|---|---|
| `seo-architecture-and-url-governance.md` | URL envanteri, politika matrisi (robots/noindex/canonical/sitemap), facet-sayfalama-normalizasyon | yeni şablon/rota, filtreli listeler, URL kuralı |
| `javascript-rendering-debugging.md` | ham HTML ↔ render DOM karşılaştırması, hata modeli | SPA/Next/Nuxt, "içerik görünmüyor" şüphesi |
| `ecommerce-catalog-and-facets.md` | varyant, stok politikası, facet uygunluk ölçütü, feed-sayfa tutarlılığı | e-ticaret |
| `schema-validation-matrix.md` | sayfa türü × schema × görünür veri uyumu | schema eklerken/denetlerken |
| `technical-seo-release-gate.md` | Kritik/Önemli yayın kapısı | her yayın öncesi |
| `acceptance-test-catalog.md` | kabul testleri | düzeltme sonrası doğrulama |
| `migration-playbook.md` | taşıma öncesi/gün/sonrası | alan adı, CMS, URL değişikliği |
| `drop-investigation-runbook.md` | trafik düşüşü inceleme sırası | "trafik düştü" |
| `incident-response-seo.md` | SEV-1..4, ilk 30 dk | noindex/robots kazası, toplu deindex |
| `international-localization-operations.md`, `international-seo-qa.md` | pazar hazırlığı, locale eşleme, hreflang QA | çok dilli/çok ülkeli |
| `global-market-research.md`, `market-research-workbook.md` | pazar matrisi, sorgu→URL haritası | yeni pazar/dil |
| `content-brief-template.md`, `content-quality-and-editorial-governance.md` | içerik brief'i ve kalite yönetişimi | içerik üretimi |
| `ai-search-and-entity-readiness.md` | AI arama/varlık hazırlığı (garanti yok) | AI görünürlüğü sorusu |
| `measurement-plan.md`, `analytics-experiment-design.md` | ölçüm ve deney kaydı | ölçüm kurulumu, A/B |
| `seo-prioritization-model.md` | puanlama (referans: kanıt/etki/çaba) | çok bulgu varken sıralama |
| `seo-report-template.md` | denetim/teslim raporu iskeleti | rapor yazarken |
| `security-privacy-seo.md` | gizli veri, SSRF, onay gereken işlemler | her zaman geçerli |
| `global-launch-checklist.md` | yayın öncesi küresel liste | yeni site/pazar lansmanı |
| `guncel-resmi-kaynaklar.md` | resmi dokümantasyon bağlantıları | değişime duyarlı iddia öncesi |

## C. Betikler (yalnızca standart kütüphane; JS çalıştırmaz, tam tarayıcı değildir)
| Betik | Kullanım |
|---|---|
| `detect_site.py <klasör> [--json]` | site türü/teknoloji/dil (hipotez) |
| `seo_audit.py <klasör>` / `--url <adres>` | sayfa denetimi; yerel sunucu için `--allow-private` |
| `competitor_probe.py <url...> [--self <klasör>]` | rakip ölçümü + konu boşluğu |
| `seo_url_audit.py urls.txt -o audit.csv --delay 1` | URL listesi → durum, yönlendirme zinciri, canonical, noindex… (CSV) |
| `seo_sitemap_audit.py <url\|dosya> -o s.csv [--recursive --check-robots --urls-out urls.txt]` | sitemap denetimi |
| testler | `python -m unittest discover -s tests -v` (seo-skill klasöründen) |

Ağ betikleri SSRF korumalıdır (özel ağ hedefleri varsayılan reddedilir). Yalnız denetlemeye yetkili olduğun siteleri tara.
