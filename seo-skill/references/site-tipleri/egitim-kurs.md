# Playbook: Eğitim / kurs / akademi

## Kullanıcıya doğrulat
"Kurslar canlı/kayıtlı mı, ücretli/ücretsiz mi, sertifika veriyor mu? Hedef kitle (öğrenci, çalışan, kurumsal)?"

## KPI
Kurs sayfası sıralamaları, kayıt/ön kayıt, bilgi talebi, bülten, blog→kurs dönüşümü, marka+kurs adı aramaları.

## Sayfa tipleri
| Sayfa | Title formülü | Zorunlu içerik |
|---|---|---|
| Kurs sayfası | `[Konu] Kursu – [Süre/Seviye/Sertifika] | Marka` | kime uygun, kazanımlar, müfredat (başlıklar), süre/takvim, fiyat/taksit, eğitmen, sertifika, SSS, yorumlar (gerçek), CTA |
| Kategori (ör. Yazılım, Dil) | `[Kategori] Kursları | Marka` | kurs listesi, seçim rehberi |
| Eğitmen profili | `[Ad Soyad] – [Uzmanlık]` | biyografi, deneyim, kanıt (E-E-A-T) |
| Rehber/blog | "… nasıl öğrenilir?", "… yol haritası" | kursa/müfredata iç link |
| Ücretsiz ders/kaynak | | arama ihtiyacını karşılar, kayıtlara dönüşüm |
| Sertifika/akreditasyon | | doğrulanabilir bilgi |

## Schema
`Course` + `CourseInstance` (courseMode, startDate, instructor, location/online), `Offer` (fiyat), `Organization`/`EducationalOrganization`, `Person` (eğitmen), `BreadcrumbList`, `VideoObject` (ders önizlemesi), `FAQPage` (görünürse). Sahte puan/yorum/öğrenci sayısı yok.

## Teknik
Ders içeriği giriş duvarı arkasındaysa pazarlama sayfası (müfredat özeti, önizleme) açık ve indekslenebilir olsun; üye alanı `noindex`. Video sayfalarına transkript/özet ekle. Tarih geçen kurs oturumlarını güncelle (eski tarih = güven kaybı). Mobil ve hız önemli.

## Anahtar kelime kalıpları
`[konu] kursu`, `[konu] eğitimi online`, `[konu] sertifika programı`, `[konu] nasıl öğrenilir`, `[konu] yol haritası`, `sıfırdan [konu]`, `[konu] eğitimi fiyat`, `[şehir] [konu] kursu`.

## Rakip analizi odağı
- Kazananlar kimler: büyük platformlar (Udemy benzeri), üniversite/resmi kurumlar, ajanslar, bloglar? Platformlar baskınsa **niş konu + seviye + yerel + sertifika + canlı destek** farkına odaklan.
- Ölç: kurs sayfasında müfredat detayı, SSS, eğitmen kanıtı, Course schema, fiyat şeffaflığı, yorumlar, güncelleme tarihi.
- Boşluk: net kazanım/yol haritası, proje portföyü, mezun sonuçları (gerçek), ücretsiz mini ders.

## Elle işler
Gerçek öğrenci yorumları/başarı hikâyeleri (izinli), eğitmen biyografileri, akreditasyon belgeleri, YouTube/ücretsiz içerik, kurumsal/üniversite bağlantıları, bülten.

## Yapma
Kazanım/iş garantisi vaadi, sahte "N bin öğrenci" sayıları, uydurma sertifika/akreditasyon, geçmiş tarihli kayıt sayfaları, müfredatı gizleyip yalnız satış metni yazmak.
