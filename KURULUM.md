# Kurulum: Claude Code'a SEO'yu bir kez öğret

Bu paket, sitenizi Claude Code'a verdiğinizde SEO'yu tekrar öğrenmeden okuyup uygulaması için hazırlandı.

## Paket içeriği
```
claude-code-paketi/
├─ CLAUDE.md                                  ← Claude Code'un her oturumda okuduğu talimat
├─ KURULUM.md                                 ← bu dosya
├─ DEGISIKLIKLER.md                           ← Apex birleştirme notları
├─ kur.bat                                    ← Windows'ta tek tıkla kurulum (aşağıya bak)
└─ seo-skill/                                 ← kurulumda `.claude\skills\seo` adıyla kopyalanır
   ├─ SKILL.md                                ← iş akışı (algıla → denetle → rakip analizi → uygula → doğrula → raporla)
   ├─ scripts/
   │  ├─ detect_site.py                       ← SİTE TÜRÜNÜ algılar (e-ticaret, yerel, SaaS, blog, ...)
   │  ├─ seo_audit.py                         ← otomatik SEO denetimi (statik HTML)
   │  ├─ competitor_probe.py                  ← rakip/1. sıra sayfa ölçümü + konu boşluğu
   │  ├─ seo_url_audit.py                     ← URL listesi → durum/yönlendirme/canonical/noindex CSV
   │  ├─ seo_sitemap_audit.py                 ← sitemap denetimi
   │  └─ netguard.py                          ← ortak güvenli HTTP katmanı (SSRF koruması)
   ├─ tests/                                  ← 86 birim testi
   └─ references/
      ├─ INDEKS.md                            ← hangi dosya ne zaman (Türkçe)
      ├─ 23 operasyon el kitabı (İngilizce)   ← taşıma, trafik düşüşü, uluslararası, schema, yayın kapısı...
      ├─ site-tipleri/                        ← türe özel playbook'lar (eticaret, yerel-isletme, saas, blog-icerik,
      │                                          portfolyo-kurumsal, ilan-pazaryeri-rehber, egitim-kurs, haber, katmanlar)
      ├─ rakip-analizi.md                     ← gerçek Google sonuçlarıyla rakip analizi prosedürü
      ├─ bilgi-bankasi.md                     ← kurallar, eşikler, kod örnekleri
      ├─ 1-siradakilerin-ozellikleri.md       ← 20 aramada 1. sıradaki sayfaların ölçümü
      ├─ evrensel-seo-ilkeleri.md             ← sizin "universal-seo" skill metniniz (modlar, P0-P3, e-ticaret, taşıma...)
      └─ kontrol-listesi.md
```

> Not: `.claude` adlı klasöre uzaktan dosya yazılamadığı için skill, `seo-skill` adıyla hazırlandı. `kur.bat` onu doğru yere (`.claude\skills\seo`) kopyalar.

## Seçenek 1: Tek sitede kullan (en kolay)
1. `kur.bat` dosyasına **çift tıklayın**; sitenizin ana klasör yolunu sorar (package.json/index.html'in olduğu yer), yapıştırıp Enter'a basın. Script `CLAUDE.md` + `.claude\skills\seo` dosyalarını oraya kopyalar.
   - Elle yapmak isterseniz: `seo-skill` klasörünü sitenizin içine `.claude\skills\seo` olarak kopyalayın ve `CLAUDE.md`'yi ana klasöre koyun.
   - Sitenizde zaten bir `CLAUDE.md` varsa, `kur.bat` onu bozmaz: yedek alır ve SEO bölümünü **sonuna ekler**.
2. Terminalde site klasöründe `claude` yazıp başlatın.
3. Şunu yazın: **`Siteyi incele ve SEO'yu uygula`**
   Claude Code `CLAUDE.md` → `SKILL.md` → `references/` zincirini kendisi okur.

## Seçenek 2: Tüm sitelerinizde kullan (kişisel skill)
`seo-skill` klasörünü kullanıcı klasörünüze `skills\seo` adıyla kopyalayın:
- Windows: `%USERPROFILE%\.claude\skills\seo` (`kur.bat` ikinci soruda bunu da önerir)
- Böylece hangi projede olursanız olun `/seo` veya "SEO yap" dediğinizde skill devreye girer.
- Her projede ayrıca `CLAUDE.md` eklemek isterseniz Seçenek 1'deki dosyayı kullanın (opsiyonel; skill zaten açıklamasıyla tetiklenir).

## Nasıl davranır? (site türüne uyum)
1. `detect_site.py` projeyi okur: framework, dil, marka, alan adı ve **site türü** (e-ticaret / yerel işletme / SaaS / blog / portföy-kurumsal / ilan-pazaryeri / eğitim / haber) puanlanır; güven düşükse Claude size **tek soru** sorar.
2. Türe göre **ilgili playbook** okunur: sayfa şablonları, schema, tuzaklar ve rakip analizi odağı değişir (ör. e-ticarette filtre URL'leri, yerel işletmede NAP ve hizmet×ilçe sayfaları).
3. **Rakip analizi:** sitenin gerçek sayfalarından 10-25 sorgu çıkarılır, Google'da aratılır (Chrome tarayıcı bağlıysa gerçek Google, değilse web araması), ilk 3 sonuç ölçülür, konu boşlukları ve fırsatlar `SEO-RAKIP-ANALIZI.md`'ye yazılır.
4. Düzeltmeler uygulanır, kanıtla doğrulanır, `SEO-RAPOR.md` yazılır.

## Kullanım örnekleri
- `Siteyi incele ve SEO'yu uygula`
- `Önce sadece SEO denetimi yap, dosyaları değiştirme` (rapor üretir)
- `Blog yazısı için SEO planı çıkar, anahtar kelime haritası yap`
- `Sadece rakip analizi yap` (Google'da hedef sorguları aratıp ilk sıradakileri karşılaştırır)
- `/seo` (skill'i doğrudan çağırma)

## Claude Code'un yapacağı / yapmayacağı
Yapar: kodu okur, denetler, title/description/canonical/schema/robots/sitemap/alt/hız iyileştirmelerini uygular, testleri çalıştırır, kanıt etiketli `SEO-RAPOR.md` yazar.
Yapmaz: sıralama/trafik vaadi vermez, veri uydurmaz, onaysız yayın/DNS/push yapmaz.
Sizin yapmanız gerekenler (hesap/erişim gerektirir): Search Console doğrulama ve sitemap gönderimi, GA4, Google İşletme Profili, backlink/PR, içerik üretimi. Bunları rapor listeler.

## Denetim betiğini elle çalıştırma
```
python .claude/skills/seo/scripts/seo_audit.py <build_veya_site_klasörü>
python .claude/skills/seo/scripts/seo_audit.py --url https://alanadiniz.com
```
(Windows'ta `python` yerine `py` gerekebilir.) Next.js/Astro/Vite gibi framework'lerde önce `npm run build` yapıp üretilen HTML klasörünü verin ya da çalışan dev sunucu adresini `--url` ile verin.

## Diğer betikler ve testler
```
python .claude/skills/seo/scripts/seo_url_audit.py urls.txt -o audit.csv --delay 1
python .claude/skills/seo/scripts/seo_sitemap_audit.py https://alanadiniz.com/sitemap.xml --recursive --check-robots --urls-out urls.txt
cd .claude/skills/seo && python -m unittest discover -s tests -v
```
Yerel geliştirme sunucusunu denetlemek için `--allow-private` ekleyin (varsayılan: özel ağ hedefleri reddedilir). Betikler JavaScript çalıştırmaz ve Search Console/tarayıcı render yerine geçmez; çıktı kanıttır, nihai karar değil.
