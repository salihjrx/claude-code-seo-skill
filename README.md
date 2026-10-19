# Claude Code SEO Skill (Türkçe)

Claude Code'a SEO'yu bir kez öğreten paket: siteyi okur, **site türünü algılar** (e-ticaret, yerel işletme, SaaS, blog, portföy/kurumsal, ilan/pazaryeri, eğitim, haber), **rakip analizi** yapar, türe uygun SEO'yu uygular ve **kanıtla** raporlar.

> Sıralama, indekslenme veya trafik vaadi vermez. Betikler JavaScript çalıştırmaz ve Search Console'un yerine geçmez; çıktıları kanıttır, nihai karar değildir.

## Hızlı kurulum
- **Windows:** `kur.bat` dosyasını çalıştırın, sitenizin klasör yolunu yapıştırın. Skill `.claude\skills\seo` altına, `CLAUDE.md` site köküne kopyalanır.
- **Elle:** `seo-skill/` klasörünü sitenizde `.claude/skills/seo/` olarak, `CLAUDE.md` dosyasını site köküne kopyalayın.
- Sonra site klasöründe `claude` çalıştırıp şunu yazın: `Siteyi incele ve SEO'yu uygula`

Ayrıntı: [KURULUM.md](KURULUM.md) · Neler birleştirildi: [DEGISIKLIKLER.md](DEGISIKLIKLER.md)

## İçerik
- `seo-skill/SKILL.md`: iş akışı (algıla → araştır → denetle → rakip analizi → uygula → doğrula → raporla)
- `seo-skill/scripts/`: `detect_site.py`, `seo_audit.py`, `competitor_probe.py`, `seo_url_audit.py`, `seo_sitemap_audit.py` (yalnızca Python standart kütüphanesi; ağ betikleri SSRF korumalı)
- `seo-skill/references/`: Türkçe tür playbook'ları, bilgi bankası, kontrol listesi ve İngilizce operasyon el kitapları (`INDEKS.md` hangisini ne zaman açacağınızı söyler)
- `seo-skill/tests/`: birim testleri

## Test
```
cd seo-skill
python -m unittest discover -s tests -v
```

## Sorumluluk
Yalnızca denetlemeye yetkili olduğunuz sitelerde kullanın. Betikler hız sınırlıdır ve bot korumasını aşmaz.

## Lisans
MIT; bkz. [LICENSE](LICENSE).
