# Playbook: Yerel işletme / hizmet (konuma bağlı)

Genel kural: `evrensel-seo-ilkeleri.md` §9 (yerel).

## Kullanıcıya doğrulat
"Müşterileriniz belirli bir şehir/ilçeden mi geliyor (dükkân/klinik/ofis/servis bölgesi)?" ve "Kaç şubeniz var?"

## Hedef ve KPI
Telefon aramaları, yol tarifi istekleri, randevu/form, **Google Haritalar (Local Pack)** görünürlüğü, "[hizmet] + [ilçe]" sıralaması, yorum sayısı/puanı.

## Sayfa tipleri
| Sayfa | Title formülü | Zorunlu içerik |
|---|---|---|
| Ana sayfa | `[Hizmet] [Şehir/İlçe] | Marka` | NAP (ad-adres-telefon), çalışma saatleri, harita, ana hizmetler, yorumlar, randevu CTA |
| Hizmet sayfası (her hizmet 1 sayfa) | `[Hizmet] [Şehir] – Fiyat, Süreç | Marka` | süreç, fiyat aralığı/"fiyat neye göre değişir", SSS, öncesi/sonrası (gerçek), uzman bilgisi |
| Şube / konum sayfası (her şube 1 sayfa) | `[Marka] [İlçe] Şubesi – Adres, Saatler` | o şubeye özgü adres, telefon, harita, saatler, ekip, park/ulaşım |
| Hizmet bölgesi sayfası (yalnız gerçekten hizmet verilen yerler) | `[Hizmet] [İlçe]` | **o bölgeye özgü** içerik (yerel örnekler, süre, tipik sorunlar); şablon kopya yok |
| Hakkımızda / ekip | | kurucu/uzman, lisans-sertifika, deneyim yılı |
| Blog/SSS | yerel sorular | "… ne kadar sürer?", "… fiyatları [şehir]" |

## Schema
`LocalBusiness` (veya uygun alt tür: Dentist, Restaurant, LegalService, AutoRepair, HairSalon…): name, image, address (PostalAddress), telephone, geo, openingHoursSpecification, priceRange, url, sameAs (Google profili, sosyal), areaServed. Her şube ayrı varlık + `@id`. `AggregateRating` yalnızca sayfada gerçekten gösterilen, toplanmış yorumlar için. Eksik veriyi **icat etme**.

## NAP tutarlılığı
Ad-adres-telefon sitede (footer, iletişim, schema), Google İşletme Profili ve dizinlerde **harf harf aynı**. Kodda farklı biçimler varsa raporla ve birleştir.

## Teknik
Mobil hız çok kritik (yerel kullanıcı mobil). Tıklanabilir `tel:` ve harita linkleri. Gömülü harita yavaşsa tembel yükle. Randevu formu çalışıyor mu test et. `lang`, HTTPS.

## Anahtar kelime kalıpları (Türkçe)
`[hizmet] [ilçe]`, `[ilçe] [hizmet] fiyatları`, `yakınımdaki [hizmet]`, `[hizmet] ne kadar`, `en iyi [hizmet] [şehir]`, `[hizmet] randevu`, `acil [hizmet] [ilçe]`.

## Rakip analizi odağı
- Sorgular: hizmet × ilçe/şehir (5–10 kombinasyon) + "yakınımda".
- SERP'te **harita paketi (3'lü)** varsa önce o: rakiplerin profil kategorileri, yorum sayıları, fotoğraf sayısı, yanıt verme (bunu tarayıcıdan gözle; sayısal veri uydurma).
- Organik sonuçlar: dizin siteleri mi (Sahibinden, doktor dizinleri, Yelp benzeri) yoksa işletme siteleri mi? Rakip site sayfalarında hizmet sayfası derinliği, yerel içerik, SSS, schema, yorum bloğu, hız.
- Boşluk: rakipte olmayan yerel bilgi (semt, ulaşım, süre, fiyat şeffaflığı, gerçek vaka/fotoğraf).

## Elle işler (kullanıcı)
Google İşletme Profili kurulum/doğrulama (kategori, saat, fotoğraf, hizmetler, ürünler, sorular), yorum toplama süreci (müşteriye QR/link; yorum satın alma/karşılığında yorum yok), dizin kayıtları (oda, dernek, yerel rehberler), Apple/Bing Places.

## Yapma
Şehir adı değiştirilmiş kopya "doorway" sayfalar, sahte adres/sanal ofis, anahtar kelime yığılmış işletme adı, sahte yorum, görünmeyen metin.
