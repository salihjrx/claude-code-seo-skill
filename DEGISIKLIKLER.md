# Birleştirme notları (SEO Apex → bu paket)

Bu paket, ilk sürüm (tür algılama + rakip analizi + Türkçe playbook'lar) ile `seo-ultimate-apex` klasöründeki genişletilmiş sürümün birleşimidir.

## Apex'ten alınanlar
- Kanıt sözleşmesi ve etiketler, yayın kapısı, bitti tanımı, anti-pattern'ler, araştırma zorunluluğu (SKILL.md, CLAUDE.md).
- 23 operasyon referansı (mimari/URL yönetişimi, JS render hata ayıklama, e-ticaret facet, schema matrisi, taşıma, trafik düşüşü, olay yönetimi, uluslararası, pazar araştırması, ölçüm, içerik yönetişimi, AI hazırlığı, güvenlik/gizlilik, rapor şablonu…). İngilizce kaldı; Türkçe `references/INDEKS.md` ne zaman açılacağını söyler.
- `seo_url_audit.py`, `seo_sitemap_audit.py`, `test_seo_url_audit.py`, `PAKET-DENETİMİ` düzeltmelerinin tamamı.

## Bizim katmanda kalanlar (Apex'te yoktu)
Site türü algılama (`detect_site.py`), rakip analizi (`competitor_probe.py`, `rakip-analizi.md`), 9 Türkçe tür/katman playbook'u, kullanıcının universal-seo metni, Türkçe çıktı.

## Paket denetimi düzeltmeleri (10/10 uygulandı)
SPA otomatik kritik değil · karakter sayıları rehber · "1. sıradakiler" yalnız sınırlı SERP gözlemi · tek H1 sıralama şartı değil · schema her sayfaya değil · betik tek başına yeterli değil · sıralama vaadi yok · anahtar kelime mekanik tekrar yok · AI arama abartısı yok · performansta saha/laboratuvar ayrımı.

## Apex betiklerinde sertleştirmeler (birleştirirken)
- Tüm ağ betikleri ortak `netguard.py` kullanır: her yönlendirme adımında SSRF kontrolü, boyut sınırı, sınırlı gunzip, yönlendirme zinciri kaydı. Yerel sunucu için bilerek `--allow-private`.
- `seo_sitemap_audit.py`: DOCTYPE/ENTITY reddi (XXE), namespace'siz sitemap'i okur, gerçek kontroller (yinelenen, localhost sızıntısı, 50.000 URL/50 MB sınırı, lastmod, robots engeli), `--recursive`, `--urls-out`.
- `seo_url_audit.py`: yeni CSV sütunları sona eklendi (eskiler korunur), h1 sayısı ayrıştırıcıdan, iç link gerçekten iç link.
- `seo_audit.py`/`detect_site.py`: SPA ve karakter sayısı bulguları düşük şiddette; robots ve noindex ayrıştırması testlerle güvence altında.
- Test: `python -m unittest discover -s tests -v` (seo-skill klasöründen) → 86 test.

## Çatışma kuralı
Çelişkide: resmi Google dokümanı > Apex denetim notu > kullanıcının pratik kuralları > bizim ölçüm gözlemlerimiz. Kullanıcının kendi birikimi geldiğinde "pratik kural" olarak ayrı etiketlenip, çatışanlar listelenip kararına sunulacak.
