# Rakip Analizi Prosedürü (gerçek Google sonuçlarına dayalı)

Amaç: "Rakip" = iş rakibi değil, **hedef sorgularda Google'ın ilk sayfada gösterdiği sayfalar**. Bu rakiplerin neyi doğru yaptığını ölç, boşlukları bul, sayfaları ona göre kur. Uydurma veri yok; ölçemediğini "ölçülemedi" yaz.

## 0. Önkoşul
`scripts/detect_site.py` çıktısı (site türü, dil, marka, alan adı) ve ilgili `site-tipleri/*.md` playbook'u okunmuş olmalı. Playbook'taki "Rakip analizi odağı" bölümü hangi sorguların seçileceğini ve nelere bakılacağını belirler.

## 1. Tohum sorguları çıkar (10–25 adet)
Kaynaklar (sırayla): sitenin gerçek sayfa başlıkları/H1'leri/ürün-hizmet adları → playbook'taki sorgu kalıpları → Google otomatik tamamlama/"Diğer sorular"/"Kullanıcıların yaptığı diğer aramalar" → Search Console sorguları (kullanıcı verdiyse).
- Dili ve ülkeyi siteden al (`tr` → `hl=tr&gl=tr`).
- Marka adını içermeyen, **niyetli** sorgular seç (bilgi / ticari / işlem / yerel).
- Her sorguya niyet etiketi ve hedef sayfa ata (anahtar kelime haritası).

## 2. SERP'i oku (öncelik sırası)
1. **Tarayıcı aracı** varsa (Claude in Chrome veya yerleşik tarayıcı): gerçek Google sayfasını aç `https://www.google.com/search?q=SORGU&hl=tr&gl=tr`, `get_page_text` ile sonuçları oku. İlk **organik** sonucu al; reklam ("Ücretli sponsorlu reklam"), video, "Diğer sorular", harita ve görsel bloklarını atla. Her sonucun URL yolunu almak için sayfa içinde şu JS çalıştırılır (sorgu parametresi içeren tam URL yazdırma, yalnızca host+path yazdır):
   ```js
   [...document.querySelectorAll('a h3')].slice(0,8).map(h=>{const u=new URL(h.closest('a').href);return u.hostname+u.pathname}).join(' | ')
   ```
2. Tarayıcı yoksa `WebSearch` (sıra yaklaşık bir göstergedir, **gerçek SERP değildir**; raporda belirt).
3. Google "Gerçek kullanıcı değil" doğrulaması (CAPTCHA) çıkarsa **aşmaya çalışma**; kullanıcıya bildir, WebSearch'e geç.
4. Aramalar arasında küçük bekleme koy; en çok 25 sorgu.

## 3. Rakip kümesini belirle
- Her sorgu için ilk 3 organik sonuç → toplam ≤ 60 URL.
- **Tekrar eden alan adları** gerçek SEO rakipleridir (ör. aynı 3 site 8 sorguda çıkıyorsa temel rakip odur).
- Sonuçları türe göre etiketle: resmi kaynak / marka sitesi / yayıncı-blog / pazaryeri-dizin / forum / video / Wikipedia. **SERP'te hangi tür kazanıyorsa sayfanı o türde kur** (ör. ilk 10 hep ürün kategorisiyse blog yazısıyla yarışma).

## 4. Rakip sayfalarını ölç
```
python .claude/skills/seo/scripts/competitor_probe.py URL1 URL2 URL3 --self <senin_sayfan_html_veya_url>
python .claude/skills/seo/scripts/competitor_probe.py --file rakipler.txt --json
```
Ölçülenler: title/description uzunluğu, H1, H2 listesi, H3 sayısı, kelime sayısı, schema türleri, görsel/alt, liste/tablo, SSS/İçindekiler, canonical, tarih, iç/dış link.
- Bot doğrulaması çıkan sayfa **atlanır** ("ölçülemedi"); tarayıcı aracıyla açıp aynı metrikleri JS ile çıkar ya da raporda ölçülemedi diye bırak.
- JS ile render edilen sayfada betik kelime sayısını düşük görür; tarayıcıyla doğrula.

Tarayıcıda hızlı metrik JS (tek sayfa, URL yazdırmaz):
```js
(()=>{const q=s=>document.querySelector(s),m=n=>q(`meta[name="${n}"]`)?.content||'',t=(q('article')||q('main')||document.body).innerText;return JSON.stringify({title:document.title.length,desc:m('description').length,h1:[...document.querySelectorAll('h1')].map(h=>h.innerText.slice(0,80)),h2:[...document.querySelectorAll('h2')].map(h=>h.innerText.slice(0,70)),h3:document.querySelectorAll('h3').length,words:t.trim().split(/\s+/).length,imgs:document.images.length,ld:[...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>{try{const j=JSON.parse(s.textContent);return JSON.stringify(j['@graph']?j['@graph'].map(x=>x['@type']):j['@type'])}catch(e){return 'err'}}),canon:!!q('link[rel=canonical]'),lang:document.documentElement.lang})})()
```

## 5. Boşluk analizi (kendi sayfan ↔ ilk 3)
Her hedef sorgu için tablo çıkar:

| Ölçüt | Rakip ortancası | Senin sayfan | Aksiyon |
|---|---|---|---|
| Title (karakter, ana sorgu başta mı, yıl/rakam/fayda) | | | |
| Description | | | |
| H1 ↔ niyet uyumu | | | |
| Kelime/derinlik (kapsanan alt konular) | | | |
| H2 konuları (≥2 rakipte geçen = **zorunlu konu**) | | | |
| Biçim: liste, tablo, SSS, TOC, görsel | | | |
| Schema türleri | | | |
| Güncellik (tarih, yıl ibaresi) | | | |
| E-E-A-T: yazar, kaynak, iletişim, yorum/kanıt | | | |
| İç linkleme / konu kümesi | | | |
| Teknik: canonical, mobil, hız (PSI varsa) | | | |

Kural: Kelime sayısı **hedef değil sonuçtur**; "zorunlu konuları kapsa + rakipte olmayan en az bir katma değer ekle" (güncel veri, özgün örnek/görsel, şablon/araç, vaka, fiyat tablosu, yerel bilgi).

## 6. Fırsat sınıflandırması
- **Hızlı kazanç:** sayfan var, ilk 20'de, title/description/yapı eksik → düzelt.
- **Boşluk:** rakipler kapsıyor, sende sayfa yok → yeni sayfa/yazı (brief ile).
- **Savunma:** zaten iyi → dokunma, güncel tut.
- **Vazgeç/ertele:** ilk 3'ü devasa otorite (Google, Wikipedia, Semrush, büyük marka) ve niyet bilgi ise geniş sorguyu bırak, **uzun kuyruk/niş/yerel** varyantı hedefle.
- Otorite (backlink) verisi ücretli araç gerektirir; yoksa "ölçülmedi" yaz, tahmin etme.

## 7. Çıktılar
Proje köküne `SEO-RAKIP-ANALIZI.md`:
1. Yöntem ve sınırlar (tarih, ülke/dil, kaç sorgu, hangi araç, ölçülemeyenler)
2. Sorgu tablosu: sorgu · niyet · hedef sayfa · 1. sıra (alan adı + tür) · rakip ortancası
3. Tekrar eden rakipler listesi
4. Sayfa bazlı boşluk tabloları (bölüm 5)
5. Öncelikli aksiyon listesi (hızlı kazanç → boşluk → savunma)
6. İçerik brief'leri (her yeni sayfa için: başlık/H1 önerisi, zorunlu H2 konuları, SSS soruları, schema, iç link hedefleri, katma değer fikri)
7. Kullanıcıdan gerekenler

## 8. Etik ve güvenlik
- Rakip metnini kopyalama/spin yapma; yalnızca **yapı ve kapsam** öğren.
- Robots/bot korumasını aşma, hesap açma, giriş yapma, ücretli duvarı geçme yok.
- Tarama hızını düşük tut (sorgu başına birkaç istek).
