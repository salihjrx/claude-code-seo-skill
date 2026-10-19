# Playbook: Portföy / kişisel site ve Kurumsal / B2B tanıtım sitesi

Detect betiği ikisini ayrı skorlar; aynı dosyayı kullanır. İkisinde de hedef **marka aramasını sahiplenmek + güven + iletişim dönüşümü**tür. Küçük sitelerde yarışılabilir alan: marka adı, kişi adı, niş hizmet + şehir, referans/vaka.

## Kullanıcıya doğrulat
Portföy: "Hangi işi/hizmeti satıyorsunuz, hangi şehir/pazar?" Kurumsal: "Hedef müşteri kim (B2B/B2C), hangi hizmetler öncelikli, hangi şehir/sektör?"

## KPI
Marka/ad sorgusunda 1. sıra ve sitelinks, iletişim formu/teklif talepleri, hizmet sayfası sorgularında görünürlük, vaka çalışması trafiği.

## Sayfa tipleri
| Sayfa | Title formülü | Zorunlu içerik |
|---|---|---|
| Ana sayfa | `Ad/Marka – [Uzmanlık] [Şehir]` | kim, ne yapıyor, kime, kanıt (logo/proje/sayı), CTA |
| Hakkımda / Hakkımızda | `Hakkımızda | Marka` | gerçek kişiler/ekip, deneyim, lisans/sertifika, misyon, iletişim (E-E-A-T) |
| Hizmet sayfaları (her hizmet 1 sayfa) | `[Hizmet] [Şehir/Sektör] | Marka` | kimlere, süreç, fiyat mantığı, SSS, vaka, CTA |
| Proje / vaka çalışması | `[Müşteri/Proje]: [Sonuç]` | problem → yaklaşım → sonuç (rakamlarla), görseller, teknoloji, müşteri alıntısı (izinli) |
| Referanslar / müşteriler | | gerçek logolar/yorumlar |
| Blog (opsiyonel ama güçlü) | niyet odaklı | uzmanlığı gösteren yazılar → hizmet sayfasına link |
| İletişim | `İletişim | Marka` | adres/telefon/form/harita, çalışma saatleri |
| Kariyer (kurumsal) | | `JobPosting` açık pozisyonlarda |

## Schema
Kurumsal: `Organization` (logo, sameAs, contactPoint), `WebSite`, `BreadcrumbList`, (şehirli hizmet işletmesiyse `LocalBusiness`/`ProfessionalService`). Portföy: `Person` (name, jobTitle, url, sameAs, knowsAbout), `ProfilePage`; projeler için `CreativeWork`/`SoftwareSourceCode` isteğe bağlı. Sahte ödül/sertifika/rating yok.

## Teknik
- Tek sayfalık (one-page) sitelerde her hizmet için ayrı URL düşün; tek sayfaya her şeyi koymak sorguları böler.
- Görsel ağırlıklı portföylerde: görsel boyutu/CLS, alt metin (proje adı + ne gösterdiği), metin içeriği ekle (yalnız görselli sayfa ince içeriktir).
- SPA ise prerender/SSR; animasyon kütüphaneleri CWV'yi bozmasın.
- Marka adı ile aranınca çıkması için: tutarlı isim, sosyal profiller `sameAs`, Google Business Profile (varsa), LinkedIn/GitHub bağlantıları.

## Anahtar kelime kalıpları
`[hizmet] [şehir]`, `[hizmet] fiyatları`, `[hizmet] firması/ajansı/uzmanı`, `freelance [uzmanlık] [şehir]`, `[sektör] için [hizmet]`, marka/kişi adı + hizmet.

## Rakip analizi odağı
- Hizmet sorguları için ilk 3: ajans/dizin/pazaryeri (Sahibinden, Bionluk, Upwork benzeri) mi, firma siteleri mi?
- Firma sitelerinde: hizmet sayfası derinliği, vaka sayısı, güven unsurları, SSS, fiyat şeffaflığı, schema.
- Boşluk: gerçek vaka çalışmaları (rakamlı), net süreç, fiyat çerçevesi, yerel/sektörel uzmanlık.

## Elle işler
Gerçek proje/vaka içeriği ve görselleri (izinli), müşteri yorumları, LinkedIn/GitHub/Behance profilleri, Google Business Profile (hizmet bölgesi), PR/konuk yazı, alt dizin/ortak bağlantıları.

## Yapma
Sahte referans/ödül, stok fotoğrafla "ekip" uydurmak, tüm hizmetleri tek sayfaya yığmak, yalnız görsel içerikli (metinsiz) sayfalar, gizli metin.
