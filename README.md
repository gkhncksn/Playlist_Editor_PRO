# 🎵 Playlist Editor PRO

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com)

**Kapsamlı radyo istasyonu playlist yönetim aracı** - JSON/Excel/CSV/XML dosyalarından playlist oluşturma (m3u, m3u8, pls, dpl), gelişmiş Stream URL kontrolü, playlist düzenleme ve VLC entegrasyonu ile canlı oynatma/istasyon test özellikleri sunar.

## 🌟 Öne Çıkan Özellikler

- 🎯 **4 Modül Bir Arada**: URL Checker, Playlist Editor, Playlist Generator, Playlist Merger
- 🎵 **Canlı Oynatma**: Gömülü VLC player ile anında test ve dinleme
- 📊 **Çoklu Format Desteği**: JSON, Excel, CSV, SQLite, XML, M3U8, PLS, DPL
- 🔍 **Akıllı URL Kontrolü**: HTTP + VLC hibrit test sistemi
- 🎨 **Modern Arayüz**: Tab-based tasarım, dinamik pencere başlığı, şarkı metaverisi
- 🗄️ **SQLite Veritabanı**: Hızlı ayar yönetimi ve otomatik INI geçişi
- 🌍 **75+ Ülke Desteği**: Otomatik ülke tanıma ve playlist oluşturma

## 📸 Ekran Görüntüleri

### URL Checker - Canlı Test ve Oynatma
<img width="1252" height="936" alt="url checker" src="https://github.com/user-attachments/assets/923f0115-292d-488f-b512-704955b46dc0" />


### Playlist Editor - Gelişmiş Düzenleme
<img width="1252" height="931" alt="playlist editor" src="https://github.com/user-attachments/assets/9e34db3c-7394-4b7e-a862-5fb25ac705ca" />


### Playlist Generator - Çoklu Format Desteği
<img width="1247" height="933" alt="playlist generator" src="https://github.com/user-attachments/assets/dafe7459-29f1-4c6b-9674-4cd4ff5989ed" />

### Playlist Merger - Çok Sayıda Playlist Dosyasını Tek Dosyada Birleştirin
<img width="1248" height="932" alt="playlist merger" src="https://github.com/user-attachments/assets/6e01f553-654d-4f24-95f2-05878af4de40" />


## 🚀 Hızlı Başlangıç

### Gereksinimler
- **Python 3.7+**
- **VLC Media Player** (opsiyonel, oynatma için)

### Kurulum

#### Otomatik Kurulum (Windows)
```bash
# 1. Projeyi indirin
git clone https://github.com/username/playlist-editor-pro.git
cd playlist-editor-pro

# 2. Bağımlılıkları yükleyin
install_requirements.bat

# 3. Programı başlatın
python main.py
```

#### Manuel Kurulum
```bash
# Bağımlılıkları yükleyin
pip install python-vlc pandas openpyxl xlrd lxml

# Programı başlatın
python main.py
```

### İlk Çalıştırma
1. Program VLC'yi otomatik bulur ve ayarlar
2. Bulunamazsa manuel yol seçimi yapabilirsiniz
3. VLC olmadan da HTTP kontrolü ile çalışır

## 🎯 Modüller ve Özellikler

### 🔍 URL Checker
**Radyo istasyonu URL'lerini test edin ve canlı dinleyin**

#### Temel Özellikler
- **Hibrit Test Sistemi**: HTTP (hızlı) + VLC (detaylı) kombinasyonu
- **Gömülü VLC Player**: Program içinde anında oynatma
- **Çift Oynatma Modu**: Gömülü ve ayrı pencere seçenekleri
- **Akıllı Filtreleme**: Çalışmayan URL'leri otomatik seçme
- **Sıralanabilir Tablo**: Sütun başlıklarına tıklayarak sıralama

#### Kullanım
```
1. M3U8 dosyası yükleyin
2. "URL Kontrolü Başlat" ile test edin
3. Çift tıklayarak canlı dinleyin
4. Sağ tık menüsü ile gelişmiş seçenekler
5. Çalışmayan URL'leri silin ve kaydedin
```

#### Test Sistemi
- **1. Aşama**: HTTP kontrolü (5 saniye timeout)
- **2. Aşama**: HTTP başarısızsa VLC testi (3 saniye)
- **Sonuç**: ✅ Çalışıyor / ❌ Çalışmıyor
- **İptal**: İstediğiniz zaman durdurabilirsiniz

### ✏️ Playlist Editor
**M3U8 playlist'lerini profesyonel düzeyde düzenleyin**

#### Temel Özellikler
- **Çoklu Format Desteği**: M3U8, M3U, PLS, DPL okuma/yazma
- **Gelişmiş Metadata**: tvg-name, tvg-logo, group-title desteği
- **Sürükle-Bırak Sıralama**: Satırları sürükleyerek yeniden sıralama
- **Canlı Oynatma**: Çift tıklayarak anında dinleme
- **Grup Yönetimi**: Otomatik grup listesi ve yeni grup ekleme

#### Kullanım
```
1. Playlist dosyası yükleyin (M3U8/PLS/DPL)
2. Tabloda istasyonu seçin
3. Sağ panelde bilgileri düzenleyin
4. "Değişiklikleri Uygula" ile kaydedin
5. Çift tıklayarak test edin
```

#### Desteklenen Formatlar
- **Okuma**: M3U8, M3U, PLS, DPL
- **Yazma**: M3U8, M3U, PLS, DPL
- **Metadata**: Tam EXTINF desteği

### 📻 Playlist Generator
**Çeşitli veri kaynaklarından M3U8 playlist oluşturun**

#### Desteklenen Formatlar
- **JSON**: Radyo istasyonu verileri
- **Excel**: .xlsx, .xls (çoklu sheet desteği)
- **CSV**: Farklı encoding'ler (UTF-8, Latin-1, CP1254)
- **SQLite**: .db, .sqlite, .sqlite3 dosyaları
- **XML**: Yapılandırılmış XML verileri

#### Akıllı Özellikler
- **Otomatik Ülke Tanıma**: Dosya adından ülke kodu algılama
- **Sütun Eşleştirme**: Farklı sütun adlarını otomatik tanıma
- **Encoding Algılama**: CSV dosyaları için otomatik encoding
- **Sheet Seçimi**: Excel dosyalarında ülke koduna göre sheet bulma

#### Kullanım
```
1. Veri dosyasını seçin (JSON/Excel/CSV/SQLite/XML)
2. Ülke otomatik algılanır (veya manuel seçin)
3. "M3U8 Oluştur" butonuna tıklayın
4. Aynı klasöre otomatik kaydedilir
```

### 🔗 Playlist Merger
**Birden fazla playlist'i birleştirin**

#### Temel Özellikler
- **Çoklu Dosya Seçimi**: Birden fazla M3U8 dosyası seçme
- **Sürükle-Bırak Sıralama**: Dosya sırasını değiştirme
- **Duplicate Kontrolü**: Tekrarlanan URL'leri filtreleme
- **Metadata Koruma**: Tüm EXTINF bilgilerini koruma

#### Kullanım
```
1. "Dosya Ekle" ile playlist'leri seçin
2. Listede sürükleyerek sıralayın
3. "Birleştir" butonuna tıklayın
4. Birleştirilmiş dosyayı kaydedin
```

## 🎵 VLC Entegrasyonu

### Otomatik VLC Bulma
Program VLC'yi şu konumlarda otomatik arar:
```
C:\Program Files\VideoLAN\VLC\vlc.exe
C:\Program Files (x86)\VideoLAN\VLC\vlc.exe
%LOCALAPPDATA%\Programs\VLC\vlc.exe
D:\Program Files\VideoLAN\VLC\vlc.exe
D:\Program Files (x86)\VideoLAN\VLC\vlc.exe
```

### Oynatma Modları

#### 🖥️ Gömülü Oynatıcı
- **Program İçi**: URL Checker'da sağ panelde
- **Anında Test**: Çift tıklayarak hızlı oynatma
- **Video Desteği**: IPTV kanalları için görüntü
- **Kontrol Butonları**: ▶️ ⏸️ ⏹️ 🔊

#### 🪟 Ayrı Pencere Modu
- **Büyük Ekran**: 640x480 boyutunda ayrı pencere
- **Tam Ekran**: F11 veya çift tık ile tam ekran
- **Klavye Kısayolları**: Space (oynat/duraklat), Esc (tam ekrandan çık)
- **Otomatik Ortalama**: Pencere ekran ortasında açılır

### Şarkı Metaverisi Takibi
- **Pencere Başlığı**: "Tab Adı - Çalıyor: İstasyon (Şarkı - Sanatçı)"
- **Otomatik Güncelleme**: 3 saniyede bir metadata kontrolü
- **Akıllı Filtreleme**: URL'ler ve gereksiz bilgiler filtrelenir
- **Fallback**: Metadata yoksa sadece istasyon adı gösterilir

## 🎨 Arayüz Özellikleri

### Dinamik Pencere Başlığı
```
Oynatma Yok:     "URL Checker"
Sadece İstasyon: "URL Checker - Çalıyor: Radyo Mega FM"
Şarkı ile:       "URL Checker - Çalıyor: Radyo Mega FM (Sezen Aksu - Gülümse)"
```

### Modern Tasarım
- **Tab-based Arayüz**: 4 ana modül ayrı tab'larda
- **Zebra Stripes**: Tablolarda alternatif satır renkleri
- **Sıralanabilir Sütunlar**: Başlıklara tıklayarak alfabetik sıralama
- **Progress Bar**: Alt kısımda birleşik ilerleme/durum çubuğu
- **Responsive**: Pencere boyutlandırılabilir

### Kullanıcı Deneyimi
- **Otomatik Ortalama**: Tüm pencereler ekran ortasında açılır
- **Akıllı Butonlar**: Duruma göre enable/disable
- **Sağ Tık Menüleri**: Gelişmiş seçenekler
- **Drag & Drop**: Sürükle-bırak desteği

## 🗄️ Veri Yönetimi

### SQLite Veritabanı
Ayarlar `veriler.db` SQLite veritabanında saklanır:
- **VLC Yolu**: Otomatik bulma ve manuel ayarlama
- **Son Klasörler**: Dosya dialog'ları için son kullanılan konumlar
- **Playlist Grupları**: Kullanıcı tanımlı grup listesi
- **Timestamp**: Ayar değişiklik geçmişi

### Otomatik INI Geçişi
- Mevcut `radio_settings.ini` otomatik olarak SQLite'a aktarılır
- Orijinal dosya `.backup` uzantısı ile korunur
- Geriye dönük uyumluluk sağlanır

## 📁 Dosya Formatları

### Giriş Formatları
| Format | Uzantı | Açıklama |
|--------|--------|----------|
| JSON | .json | Radyo istasyonu verileri |
| Excel | .xlsx, .xls | Çoklu sheet desteği |
| CSV | .csv | Farklı encoding desteği |
| SQLite | .db, .sqlite | Veritabanı dosyaları |
| XML | .xml | Yapılandırılmış veriler |
| M3U8 | .m3u8, .m3u | Mevcut playlist'ler |
| PLS | .pls | Winamp playlist formatı |
| DPL | .dpl | Daum playlist formatı |

### Çıktı Formatları
```m3u8
#EXTM3U
#EXTINF:-1 tvg-name="TRT1" tvg-logo="logo.png" group-title="Ulusal",TRT 1
http://stream-url.com/trt1
#EXTINF:-1 tvg-name="TRT2" tvg-logo="logo2.png" group-title="Ulusal",TRT 2
http://stream-url.com/trt2
```

## ⚙️ Yapılandırma

### Sistem Gereksinimleri
- **İşletim Sistemi**: Windows 7/8/10/11
- **Python**: 3.7 veya üzeri
- **RAM**: Minimum 512 MB
- **Disk**: 100 MB boş alan
- **VLC**: Opsiyonel (oynatma için)

### Bağımlılıklar
```txt
python-vlc>=3.0.0    # VLC entegrasyonu
pandas>=1.3.0        # Excel/CSV işleme
openpyxl>=3.0.0      # Excel okuma/yazma
xlrd>=2.0.0          # Eski Excel desteği
lxml>=4.6.0          # XML işleme
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar

#### VLC Bulunamıyor
```
Çözüm 1: VLC Media Player'ı yükleyin
Çözüm 2: Program başlangıcında manuel yol seçin
Çözüm 3: HTTP test modu ile devam edin
```

#### Python-VLC Hatası
```bash
# Windows
pip install python-vlc

# Hata devam ederse
pip uninstall python-vlc
pip install python-vlc --no-cache-dir
```

#### Pandas/Excel Hatası
```bash
# Tüm bağımlılıkları yeniden yükle
pip install -r requirements.txt --upgrade
```

#### Encoding Sorunları
- CSV dosyaları için UTF-8 encoding kullanın
- Excel dosyaları otomatik algılanır
- Türkçe karakterler için CP1254 denenebilir

### Performans İpuçları
- **URL Kontrolü**: VLC test daha doğru ama yavaş
- **Büyük Dosyalar**: Excel yerine CSV kullanın
- **Bellek**: Çok büyük playlist'ler için parça parça işleyin

## 📊 Sürüm Geçmişi

### v2.1.0 (Güncel)
- ✨ Dinamik pencere başlığı ve şarkı metaverisi
- 🎵 Gömülü oynatıcıdan şarkı bilgisi paneli kaldırıldı
- 🔧 Tab sıralaması güncellendi (URL Checker ilk sırada)
- 🎨 Playlist Editor layout iyileştirmeleri

### v2.0.0
- 🆕 Modüler yapıya geçiş (6 ayrı modül)
- 🗄️ SQLite veritabanı entegrasyonu
- 🎵 Gelişmiş VLC player ve şarkı takibi
- 🎨 Modern arayüz ve zebra stripes

### v1.x
- 📻 Temel playlist oluşturma
- 🔍 HTTP URL kontrolü
- ✏️ Basit M3U8 düzenleme

## 🤝 Katkıda Bulunma

### Geliştirme Ortamı
```bash
# Projeyi fork edin ve klonlayın
git clone https://github.com/yourusername/playlist-editor-pro.git
cd playlist-editor-pro

# Geliştirme branch'i oluşturun
git checkout -b feature/yeni-ozellik

# Değişikliklerinizi yapın ve test edin
python main.py

# Commit ve push
git commit -m "Yeni özellik: açıklama"
git push origin feature/yeni-ozellik

# Pull request oluşturun
```

### Kod Standartları
- **PEP 8**: Python kod standartları
- **Modüler Tasarım**: Her özellik ayrı modülde
- **Hata Yönetimi**: Try-except blokları kullanın
- **Dokümantasyon**: Fonksiyonları dokümante edin

### Hata Bildirimi
[Issues](https://github.com/username/playlist-editor-pro/issues) sayfasından hata bildirebilirsiniz:
- 🐛 **Bug Report**: Hata açıklaması ve adımlar
- 💡 **Feature Request**: Yeni özellik önerileri
- 📖 **Documentation**: Dokümantasyon iyileştirmeleri

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında yayınlanmıştır.

```
MIT License

Copyright (c) 2024 Playlist Editor PRO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Teşekkürler

- **VLC Media Player**: Güçlü multimedia framework
- **Python Community**: Harika kütüphaneler
- **Kullanıcılar**: Değerli geri bildirimler
- **Katkıda Bulunanlar**: Açık kaynak ruhu

## 📞 İletişim

- **GitHub**: [Issues](https://github.com/username/playlist-editor-pro/issues)
- **Email**: developer@example.com
- **Website**: https://playlist-editor-pro.com

---

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

Made with ❤️ by [gkhncksn](https://github.com/gkhncksn)

</div>
