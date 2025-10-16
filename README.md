# Radyo İstasyonu M3U8 Playlist Oluşturucu & URL Checker

Kapsamlı radyo istasyonu playlist yönetim aracı. JSON dosyalarından M3U8 playlist oluşturma, URL kontrolü ve gelişmiş playlist düzenleme özellikleri sunar.

## 🆕 Yeni Sürüm Özellikleri (v2.1)

### ✨ Modüler Yapı
- **Ayrı Modüller**: Her özellik kendi modülünde (playlist_generator.py, url_checker.py, playlist_editor.py, vlc_player.py)
- **Temiz Kod**: Ana program sadece 300 satır (önceden 2000+ satır)
- **Kolay Bakım**: Her modül bağımsız olarak geliştirilebilir

### 🗄️ SQLite Veritabanı
- **Ayar Yönetimi**: .ini yerine SQLite veritabanı (veriler.db)
- **Otomatik Geçiş**: Mevcut .ini ayarları otomatik olarak SQLite'a aktarılır
- **Gelişmiş Saklama**: Timestamp'li ayar geçmişi
- **Performans**: Daha hızlı ayar okuma/yazma

### 🎵 Gelişmiş VLC Oynatıcı
- **Ses Kontrolü**: 0-100 arası ses seviyesi slider'ı (varsayılan: 80)
- **Tam Ekran**: Oynatma alanına çift tıklayarak tam ekran modu
- **Otomatik VLC Kurulumu**: Program başlangıcında otomatik VLC yolu bulma
- **Tek Seferlik Ayar**: VLC yolu bir kez ayarlanır, bir daha sorulmaz

### 🎨 Gelişmiş Arayüz
- **Belirgin Tablo Çizgileri**: Tüm tablolarda zebra stripes ve belirgin kenarlıklar
- **Kompakt Paneller**: Playlist Editor'da küçük kontrol panelleri, büyük tablo
- **Progress Bar**: Alt kısımda görsel ilerleme çubuğu
- **Otomatik Kurulum**: VLC yolu otomatik bulunur ve ayarlanır

## 🎯 Özellikler

### 📻 Playlist Generator
- **Çoklu Format Desteği**: JSON, Excel (xlsx/xls), CSV, SQLite, XML
- 75+ ülke desteği
- Otomatik ülke tanıma
- Otomatik dosya yolu oluşturma
- **Akıllı Sütun Tanıma**: Farklı dosya formatlarında otomatik sütun eşleştirme

### 🔍 URL Checker
- **Hibrit Test Sistemi**: HTTP (hızlı) + VLC (detaylı) kombinasyonu (HTTP başarılıysa VLC test atlanır, başarısızsa VLC ile ikinci test)
- **İptal Edilebilir**: Kontrol sırasında "İptal Et" butonu ile durdurulabilir
- **Gömülü VLC Oynatıcı**: Hızlı test için program içinde oynatıcı (tam boyut)
- **Kompakt Kontrol Paneli**: İstatistikler ve kontroller tek panelde
- **Çift Oynatma Modu**: Gömülü ve pencere modu arası geçiş
- **Gelişmiş Tablo**: TVG Name, Logo URL, Grup bilgileri ile
- **Sıralanabilir Sütunlar**: Başlıklara tıklayarak alfabetik sıralama
- **Sağ Tık Menüsü**: Gömülü/Pencere modu seçimi
- **Otomatik Seçim**: Çalışmayan linkler kontrol sonrası otomatik seçilir
- **Metadata Korunması**: TVG bilgileri kaybolmaz

### ✏️ Playlist Editor
- **Kompakt Kontrol Paneli**: 2 sütunlu buton düzeni ile daha az yer kaplar
- **Gelişmiş M3U8 Düzenleme**: tvg-name, tvg-logo, group-title desteği
- **Sıralanabilir Sütunlar**: Başlıklara tıklayarak alfabetik sıralama
- **Hızlı Düzenleme**: Kısa buton isimleri ile daha pratik kullanım
- **Kanal Yönetimi**: Ekleme/silme/düzenleme/sıralama

## 🚀 Kurulum

### Gereksinimler
- Python 3.7+
- VLC Media Player (opsiyonel, radyo test için)

### Kütüphane Kurulumu
```bash
# Otomatik kurulum (Windows)
install_requirements.bat

# Manuel kurulum
pip install python-vlc pandas openpyxl xlrd lxml
```

## 🎮 Kullanım

### 1. Playlist Generator
1. **Veri Dosyası Seç**: JSON, Excel, CSV, SQLite veya XML dosyasını seç
2. **Ülke Seçimi**: Otomatik algılanır veya manuel seç
3. **M3U8 Oluştur**: Aynı klasöre otomatik kaydedilir
4. **Format Desteği**: 
   - **Excel**: Sheet isimleri ülke koduna göre aranır
   - **CSV**: Farklı encoding'ler otomatik denenir
   - **SQLite**: Tablo isimleri ülke koduna göre aranır
   - **XML**: Farklı XML yapıları desteklenir

### 2. URL Checker
1. **M3U8 Yükle**: Sol panelde dosya seç, otomatik yüklenir (TVG bilgileri ile)
2. **Gömülü Oynatıcı**: Sağ panelde hızlı test oynatıcısı
3. **Çift Tıklama**: Gömülü oynatıcıda çal (varsayılan)
4. **Sağ Tık Menüsü**: Gömülü/Pencere modu seçimi
5. **Pencere Geçişi**: 🔊 butonu ile pencere moduna geç
6. **VLC Sessiz Test**: Gerçek ses çıkışı ile URL kontrolü (önerilen)
7. **HTTP Yedek Test**: VLC yoksa HTTP status kontrolü
8. **Sıralama**: Sütun başlıklarına tıklayarak alfabetik sıralama
9. **Otomatik Seçim**: Çalışmayan linkler otomatik seçilir
10. **Akıllı Silme**: Silme sonrası kaydetme dialog'u otomatik açılır

### 3. Playlist Editor
1. **Playlist Yükle**: M3U8/M3U dosyasını yükle
2. **Sıralama**: Sütun başlıklarına tıklayarak alfabetik sıralama
3. **Düzenleme**: Çift tıklayarak kanal bilgilerini düzenle
4. **Yönetim**: Kanal ekle/sil/taşı
5. **Kaydet**: Gelişmiş M3U8 formatında kaydet

## 🔧 VLC Entegrasyonu

### Otomatik VLC Bulma
Program VLC'yi otomatik olarak şu konumlarda arar:
- `C:\Program Files\VideoLAN\VLC\vlc.exe`
- `C:\Program Files (x86)\VideoLAN\VLC\vlc.exe`
- `%LOCALAPPDATA%\Programs\VLC\vlc.exe`

### Manuel VLC Ayarlama
1. **VLC Yolu Ayarla** butonuna tıklayın
2. `vlc.exe` dosyasını seçin
3. Ayar otomatik olarak kaydedilir

### Çalma Özellikleri

#### Gömülü Oynatıcı
- **Program İçi**: URL Checker sağ panelinde
- **Hızlı Test**: Anında çalma, durdurma
- **Şarkı Bilgisi**: Üst panelde çalan şarkı adı
- **Kontrol Butonları**: ▶ ⏸ ⏹ 🔊
- **Video Desteği**: IPTV kanalları için görüntü

#### Pencere Modu
- **Ayrı Pencere**: 400x350 boyutunda
- **Çift Mod**: Gömülü oynatıcıdan pencereye geçiş
- **Otomatik Geri Dönüş**: Pencere kapanınca gömülü modda devam
- **Şarkı Bilgisi**: Pencere başlığında ve ayrı panelde
- **Otomatik Güncelleme**: Şarkı bilgisi 3 saniyede bir güncellenir
- **Otomatik Ortalama**: Pencere ekran ortasında açılır

## 🎯 URL Test Sistemi (Hibrit Metod)

### Akıllı İki Aşamalı Test
1. **HTTP Test (1. Aşama)**: Hızlı HTTP status kontrolü (5 saniye timeout)
2. **VLC Test (2. Aşama)**: HTTP başarısızsa VLC ile detaylı test (3 saniye)

### HTTP Test (Hızlı)
- **İlk Kontrol**: Tüm URL'ler önce HTTP ile test edilir
- **Hızlı Sonuç**: 5 saniye timeout ile hızlı yanıt
- **Başarılı ise**: VLC test atlanır, bir sonraki URL'ye geçilir
- **Başarısız ise**: VLC test devreye girer

### VLC Test (Detaylı)
- **İkinci Şans**: HTTP başarısız olan URL'ler için
- **Gerçek Test**: Stream'i gerçekten çalarak test eder
- **Sessiz Çalışma**: Test sırasında ses çıkışı olmaz (volume=0)
- **Kısa Süre**: 3 saniye test süresi

### Test Süreci
1. **HTTP Kontrolü**: URL HTTP 200 OK dönüyor mu? (5sn)
2. **Başarılı ise**: ✓ Çalışıyor, sonraki URL'ye geç
3. **Başarısız ise**: VLC ile ikinci test (3sn)
4. **VLC Sonucu**: ✓ Çalışıyor veya ✗ Çalışmıyor
5. **İptal Edilebilir**: İstediğiniz zaman "İptal Et" ile durdurun

### Avantajları
- **Hız**: Çalışan URL'ler için sadece 5 saniye
- **Doğruluk**: Çalışmayan URL'ler için VLC ile ikinci kontrol
- **Esneklik**: İstediğiniz zaman iptal edilebilir
- **Verimlilik**: Gereksiz VLC testleri atlanır

## 🎵 Şarkı Bilgisi Takibi

### VLC Meta Veri Sistemi
- **Now Playing**: Stream'den gelen anlık şarkı bilgisi
- **Title/Artist**: VLC'nin algıladığı başlık ve sanatçı
- **Description**: Stream açıklaması
- **Otomatik Filtreleme**: URL'ler ve kısa metinler filtrelenir

### Görüntüleme Özellikleri
- **Pencere Başlığı**: "Oynatıcı - TRT FM | Şarkı Adı"
- **Ayrı Panel**: Oynatma penceresinde üst kısımda şarkı bilgisi
- **Otomatik Kısaltma**: 60 karakterden uzun metinler kısaltılır
- **3 Saniye Güncelleme**: Şarkı bilgisi sürekli güncellenir

### Desteklenen Formatlar
- **ICY Metadata**: Internet radyo stream'lerinin standart formatı
- **VLC Meta**: VLC'nin desteklediği tüm meta veri türleri
- **Fallback**: Bilgi yoksa sadece istasyon adı gösterilir

## 🎬 Gömülü VLC Oynatıcı Sistemi

### Yeni Arayüz Düzeni
- **Sol Panel**: Dosya seçimi ve kontrol butonları
- **Sağ Panel**: Gömülü VLC oynatıcı (200px yükseklik)
- **Alt Kısım**: URL listesi tablosu (daha kompakt)

### Oynatma Modları
1. **Gömülü Mod** (Varsayılan)
   - Çift tıklama ile gömülü oynatıcıda çalar
   - Program içinde hızlı test
   - Video içerik için görüntü desteği
   
2. **Pencere Modu**
   - Sağ tık → "Pencere Modunda Çal"
   - 🔊 butonu ile geçiş
   - Daha büyük görüntü alanı

### Akıllı Geçiş Sistemi
- **Gömülü → Pencere**: 🔊 butonu veya çift tıklama
- **Pencere → Gömülü**: Pencere kapatma ile otomatik geri dönüş
- **Stream Sürekliliği**: Mod değişiminde stream devam eder
- **Şarkı Takibi**: Her iki modda da çalan şarkı gösterilir

### Kontrol Özellikleri
- **▶ Oynat**: Stream'i başlat/devam ettir
- **⏸ Duraklat**: Geçici durdurma
- **⏹ Durdur**: Tamamen durdur
- **🔊 Pencere**: Pencere moduna geç
- **Sağ Tık**: Gelişmiş seçenekler menüsü

### IPTV Desteği
- **Video Stream'ler**: Gömülü oynatıcıda görüntü
- **Radyo Stream'ler**: Sadece ses, siyah ekran
- **Otomatik Algılama**: VLC stream türünü otomatik belirler
- **Esnek Boyutlandırma**: Video boyutuna göre ayarlanır

## 📁 Dosya Formatları

### Desteklenen Giriş Formatları
- **JSON**: Radyo istasyonu verileri
- **Excel (xlsx/xls)**: Çalışma sayfaları ile organize veriler
- **CSV**: Virgülle ayrılmış değerler (farklı encoding desteği)
- **SQLite**: Veritabanı dosyaları (.db, .sqlite, .sqlite3)
- **XML**: Yapılandırılmış XML verileri
- **M3U8/M3U**: Mevcut playlist'ler

### Çıktı Formatları
- **Basit M3U8**: Temel playlist
- **Gelişmiş M3U8**: tvg parametreleri ile

### Örnek Gelişmiş M3U8
```m3u8
#EXTM3U
#EXTINF:-1 tvg-name="TRT1" tvg-logo="logo.png" group-title="Ulusal",TRT 1
http://stream-url.com/trt1
```

## ⚙️ Ayarlar

### SQLite Veritabanı (Yeni!)
Ayarlar artık `veriler.db` SQLite veritabanında saklanır:
- **VLC Yolu**: Otomatik bulma ve manuel ayarlama
- **Kullanıcı Tercihleri**: Gelişmiş ayar yönetimi
- **Geçmiş Saklama**: Timestamp'li ayar geçmişi
- **Otomatik Geçiş**: Mevcut .ini dosyası otomatik olarak SQLite'a aktarılır

### Eski INI Desteği
- Mevcut `radio_settings.ini` dosyası otomatik olarak `veriler.db`'ye aktarılır
- Orijinal dosya `.backup` uzantısı ile yedeklenir
- Geriye dönük uyumluluk korunur

## 🎨 Arayüz Özellikleri

- **Birleşik Progress/Status Bar**: Alt kısımda hem ilerleme hem durum bilgisi
- **Ortalanmış Pencereler**: Ana program ve dialog'lar ekran ortasında açılır
- **Responsive Tasarım**: Yeniden boyutlandırılabilir
- **Sıralanabilir Tablolar**: Sütun başlıklarına tıklayarak alfabetik sıralama
- **Şarkı Bilgisi Takibi**: VLC oynatma penceresinde çalan şarkı adı
- **Tablo Görünümü**: Kolay veri yönetimi
- **Akıllı Butonlar**: Duruma göre enable/disable
- **Otomatik İşlemler**: Kullanıcı deneyimini kolaylaştıran otomasyonlar

## 🔍 Sorun Giderme

### VLC Bulunamıyor
1. VLC Media Player'ı yükleyin
2. "VLC Yolu Ayarla" ile manuel olarak ayarlayın

### Python-VLC Hatası
1. `install_requirements.bat` çalıştırın
2. Manuel: `pip install python-vlc`
3. VLC yoksa HTTP test modu otomatik devreye girer

### URL Kontrol Yavaş
- VLC test modu daha yavaş ama daha doğru
- HTTP test modu daha hızlı ama daha az güvenilir
- Timeout süresi 15 saniye (VLC) / 10 saniye (HTTP)

### Yanlış Sonuçlar
- **HTTP Test**: Çalışmayan radyolar "çalışıyor" gösterebilir
- **VLC Test**: Gerçek ses çıkışı kontrolü yapar
- **Çözüm**: python-vlc kütüphanesini yükleyin

### Pandas/Excel Hatası
1. `install_requirements.bat` çalıştırın
2. Manuel: `pip install pandas openpyxl xlrd`

## 📝 Lisans

Bu proje açık kaynak kodludur ve eğitim amaçlı kullanım için tasarlanmıştır.

## 🤝 Katkıda Bulunma

Hata raporları ve öneriler için issue açabilirsiniz.
