# Proje talimatı: SEO

Bu proje bir web sitesidir. Kullanıcı Türkçe konuşur; Türkçe yanıt ver.

## Otomatik SEO kuralı
Kullanıcı projeyi açıp **"SEO yap"**, **"siteyi incele ve SEO'ya uygula"**, **"SEO denetimi"**, **"rakip analizi"**, **"trafik düştü"**, **"Google'da yükselt"** gibi bir şey istediğinde veya siteyi verip SEO'dan bahsettiğinde:

1. SEO'yu yeniden araştırma/öğrenme. Önce `.claude/skills/seo/SKILL.md` dosyasını oku ve iş akışını uygula (gerekirse `Skill` aracıyla `seo` skill'ini çağır). Hangi referansın ne zaman açılacağı: `.claude/skills/seo/references/INDEKS.md`.
2. **İlk adım her zaman site türünü algılamaktır:** `python .claude/skills/seo/scripts/detect_site.py .` (Windows'ta `py`). Çıktı bir hipotezdir. Türe göre `references/site-tipleri/` altındaki ilgili playbook'u oku ve davranışını uyarla.
3. Sonra: araştırma kaydı → denetim (`seo_audit.py`) → **rakip analizi** (`rakip-analizi.md`, `competitor_probe.py`) → önceliklendir (P0–P3 + güven etiketi) → uygula → doğrula (yayın kapısı) → `SEO-RAPOR.md` (+ `SEO-RAKIP-ANALIZI.md`).
4. "SEO yap" = güvenli, geri alınabilir düzeltmeleri uygula + testleri çalıştır + rapor yaz. "Sadece denetle / dokunma" denirse dosya değiştirme.

## Değişmez ilkeler
- **Sıralama vaadi yok:** 1. sıra, indekslenme, zengin sonuç, AI yanıtlarında yer alma, trafik, gelir garanti edilmez.
- **Kanıt sözleşmesi:** erişmediğin kaynağa eriştim deme; arama hacmi/zorluk/trafik/backlink/CWV/indeks verisi uydurma. İddiaları Doğrulandı / Gözlendi / Hipotez / Bilinmiyor / Test edilmedi diye etiketle; tarih, ülke/dil, cihaz, sorgu ve URL kaydet.
- Betik çıktısı kanıttır, nihai karar değil (JS çalıştırmaz, Search Console/log yerine geçmez). SERP gözlemi nedensellik kanıtı değildir.
- Tek göstergeden hüküm verme: SPA otomatik "kritik" değildir; title/description karakter sayısı ve tek H1 sıralama kuralı değildir; her sayfaya schema eklenmez.
- Hiçbir bilgiyi uydurma (adres, telefon, puan, yorum, yazar). Kodda yoksa kullanıcıya "gerekli" olarak listele.
- Sahte yorum/yazar/AggregateRating, gizli metin, cloaking, anahtar kelime doldurma, doorway sayfa yok.
- Kanıtsız "bitti" deme: çalıştırılan testleri ve gerçek sonuçları yaz; çalışmayanı açıkça "çalıştırılamadı" de. Üretim erişimi yoksa üretim doğrulaması "beklemede".
- Mevcut tasarımı ve işlevi bozma; küçük, geri alınabilir değişiklikler. Kritik değişiklik öncesi mevcut URL/metadata/canonical/indeks durumunu kaydet ve geri alma planı yaz.
- URL değişirse 301 ekle; trafik alan sayfaların URL'sini gerekçesiz değiştirme.
- `Disallow: /` ve `noindex` canlıda kalmamalı (staging'de kalabilir; canlıya geçişte kaldırıldığını doğrula).
- Bot korumasını/CAPTCHA'yı aşma; rakip metnini kopyalama; yalnız yetkili olduğun siteleri tara, hız sınırı koy.
- Gizli anahtar/çerez/.env/kişisel veri çıktıya yazılmaz.
- Üretime yayın, DNS, harici hesap işlemi, ücretli işlem ve push için **açık onay** al.
