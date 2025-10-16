#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time

# VLC kütüphanesini import et (opsiyonel)
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

class VLCPlayerModule:
    def __init__(self, database_manager, status_callback=None, stop_callback=None, song_info_callback=None):
        self.db_manager = database_manager
        self.status_callback = status_callback or (lambda x: None)
        self.stop_callback = stop_callback or (lambda: None)
        self.song_info_callback = song_info_callback or (lambda x: None)
        
        # VLC player değişkenleri
        self.vlc_instance = None
        self.vlc_player = None
        self.vlc_window = None
        self.embedded_vlc_frame = None
        
        # Oynatma durumu
        self.current_url = None
        self.current_station = None
        self.is_playing = False
        self.song_tracking_active = False
        
        # VLC yolu
        self.vlc_path = self.db_manager.get_setting('vlc.path', '')
    
    def setup_embedded_player(self, parent_frame):
        """Gömülü VLC oynatıcı kurulumu"""
        if not VLC_AVAILABLE:
            # VLC yoksa basit bir bilgi paneli göster
            info_label = tk.Label(parent_frame, text="VLC kütüphanesi bulunamadı!\nOynatıcı kullanılamaz.", 
                                 bg='lightgray', fg='red', font=('Arial', 10, 'bold'))
            info_label.pack(fill='both', expand=True)
            return
        
        # VLC oynatma alanı (şarkı bilgisi paneli kaldırıldı)
        self.embedded_vlc_frame = tk.Frame(parent_frame, bg='black', height=200)
        self.embedded_vlc_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        # Kontrol butonları
        control_frame = tk.Frame(parent_frame)
        control_frame.pack(fill='x')
        
        # Oynatma kontrolleri (sol)
        play_frame = tk.Frame(control_frame)
        play_frame.pack(side='left')
        
        tk.Button(play_frame, text="▶", command=self.play_embedded, width=3).pack(side='left', padx=2)
        tk.Button(play_frame, text="⏸", command=self.pause_embedded, width=3).pack(side='left', padx=2)
        tk.Button(play_frame, text="⏹", command=self.stop_embedded, width=3).pack(side='left', padx=2)
        tk.Button(play_frame, text="🗔", command=self.open_separate_window, width=3, 
                 font=('Arial', 8)).pack(side='left', padx=2)
        
        # Ses kontrolü (sağ)
        volume_frame = tk.Frame(control_frame)
        volume_frame.pack(side='right', padx=5)
        
        tk.Label(volume_frame, text="Ses:", font=('Arial', 8)).pack(side='left')
        self.volume_var = tk.IntVar(value=80)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal', 
                                   variable=self.volume_var, command=self.on_volume_change,
                                   length=100, width=15)
        self.volume_scale.pack(side='left', padx=2)
        
        # Çift tık ile ayrı pencere aç
        self.embedded_vlc_frame.bind('<Double-Button-1>', self.open_separate_window)
    
    def play_stream(self, url, station_name, embedded=True):
        """Stream çal"""
        if not VLC_AVAILABLE:
            messagebox.showerror("Hata", "VLC kütüphanesi bulunamadı!")
            return False
        
        try:
            # Önceki oynatmayı durdur
            self.stop_embedded()
            
            # VLC instance oluştur (tam ekran desteği ile)
            if not self.vlc_instance:
                vlc_args = [
                    '--quiet',           # Hata mesajlarını azalt
                    '--intf=dummy',      # Interface sorunlarını önle
                    '--no-video-title-show',  # Video başlığını gösterme
                    '--disable-screensaver',  # Ekran koruyucuyu devre dışı bırak
                    '--verbose=0',       # Verbose çıktıyı kapat
                    '--no-stats',        # İstatistikleri kapat
                    '--no-osd',          # On-screen display'i kapat
                ]
                
                # Windows'a özel ayarlar
                if os.name == 'nt':
                    vlc_args.extend([
                        '--no-directx-hw-yuv',  # DirectX donanım hızlandırmasını kapat
                        '--avcodec-hw=none',    # Donanım kod çözücüyü kapat
                        '--no-video-deco',      # Video dekorasyonlarını kapat
                    ])
                else:
                    vlc_args.append('--no-xlib')  # Linux için X11 sorunlarını önle
                
                self.vlc_instance = vlc.Instance(vlc_args)
            
            # Media player oluştur
            self.vlc_player = self.vlc_instance.media_player_new()
            
            if embedded and self.embedded_vlc_frame:
                # VLC'yi frame'e bağla
                if os.name == 'nt':  # Windows
                    self.vlc_player.set_hwnd(self.embedded_vlc_frame.winfo_id())
                else:  # Linux/Mac
                    self.vlc_player.set_xwindow(self.embedded_vlc_frame.winfo_id())
            
            # Media oluştur ve çal
            media = self.vlc_instance.media_new(url)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
            
            # Ses seviyesini ayarla
            if hasattr(self, 'volume_var'):
                volume = self.volume_var.get()
                self.vlc_player.audio_set_volume(volume)
            
            # Bilgileri sakla
            self.current_url = url
            self.current_station = station_name
            self.is_playing = True
            
            # Şarkı bilgisi takibini başlat
            if embedded:
                self.start_song_tracking(station_name)
            
            self.status_callback(f"Oynatılıyor: {station_name}")
            return True
            
        except Exception as e:
            messagebox.showerror("Hata", f"Oynatma hatası: {str(e)}")
            return False
    
    def start_song_tracking(self, station_name):
        """Şarkı bilgisi takibi başlat - pencere başlığı için"""
        # Önceki takibi temizle
        self.stop_song_tracking()
        
        # Yeni takibi başlat
        self.song_tracking_active = True
        self.current_station = station_name
        
        def update_song_info():
            # Takip aktif mi ve player çalışıyor mu kontrol et
            if (not self.song_tracking_active or 
                not self.vlc_player or 
                not self.is_playing):
                return
            
            try:
                # Player durumunu kontrol et
                state = self.vlc_player.get_state()
                if state not in [vlc.State.Playing, vlc.State.Buffering]:
                    # Player durmuş veya hata durumunda
                    self.song_info_callback("")
                    return
                
                # VLC'den meta bilgileri al
                media = self.vlc_player.get_media()
                if media:
                    title = media.get_meta(vlc.Meta.Title)
                    artist = media.get_meta(vlc.Meta.Artist)
                    now_playing = media.get_meta(vlc.Meta.NowPlaying)
                    description = media.get_meta(vlc.Meta.Description)
                    
                    # En uygun bilgiyi seç
                    song_info = None
                    if now_playing and now_playing.strip():
                        song_info = now_playing.strip()
                    elif description and description.strip() and len(description.strip()) > 5:
                        song_info = description.strip()
                    elif title and title.strip() and len(title.strip()) > 5:
                        if artist and artist.strip():
                            song_info = f"{artist} - {title}"
                        else:
                            song_info = title.strip()
                    
                    # Şarkı bilgisini ana pencereye gönder
                    if song_info and len(song_info) > 3:
                        # URL'leri ve gereksiz bilgileri filtrele
                        if not (song_info.startswith('http') or 
                               song_info.startswith('www') or
                               song_info.lower().startswith('stream')):
                            # Uzun metinleri kısalt (pencere başlığı için)
                            if len(song_info) > 60:
                                song_info = song_info[:57] + "..."
                            
                            self.song_info_callback(song_info)
                        else:
                            self.song_info_callback("")
                    else:
                        self.song_info_callback("")
                else:
                    self.song_info_callback("")
                
                # 3 saniye sonra tekrar kontrol et
                if self.song_tracking_active and self.is_playing:
                    threading.Timer(3.0, update_song_info).start()
                
            except Exception as e:
                # Hata durumunda boş şarkı bilgisi gönder
                self.song_info_callback("")
                # 5 saniye sonra tekrar dene
                if self.song_tracking_active and self.is_playing:
                    threading.Timer(5.0, update_song_info).start()
        
        # İlk güncellemeyi 2 saniye sonra başlat
        threading.Timer(2.0, update_song_info).start()
    
    def stop_song_tracking(self):
        """Şarkı bilgisi takibini durdur - geliştirilmiş temizlik"""
        self.song_tracking_active = False
        # Ana pencereye boş şarkı bilgisi gönder
        self.song_info_callback("")
    
    def play_embedded(self):
        """Gömülü oynatıcıyı başlat"""
        if self.vlc_player:
            self.vlc_player.play()
            self.is_playing = True
            if self.current_station:
                self.start_song_tracking(self.current_station)
    
    def pause_embedded(self):
        """Gömülü oynatıcıyı duraklat"""
        if self.vlc_player:
            self.vlc_player.pause()
            self.is_playing = False
            self.stop_song_tracking()
    
    def stop_embedded(self):
        """Gömülü oynatıcıyı durdur - geliştirilmiş temizlik"""
        # Önce şarkı takibini durdur
        self.stop_song_tracking()
        
        # Player'ı durdur
        if self.vlc_player:
            self.vlc_player.stop()
            self.is_playing = False
        
        # Değişkenleri temizle
        self.current_url = None
        self.current_station = None
        
        # Status callback ile durumu bildir
        self.status_callback("Oynatma durduruldu")
        
        # Stop callback'ini çağır (ana pencereye bildir)
        self.stop_callback()
    
    def on_volume_change(self, value):
        """Ses seviyesi değiştirildiğinde"""
        if self.vlc_player:
            volume = int(value)
            self.vlc_player.audio_set_volume(volume)
    
    def toggle_fullscreen(self, event=None):
        """Tam ekran moduna geç/çık"""
        if self.vlc_player:
            try:
                # Önce player'ın hazır olduğunu kontrol et
                state = self.vlc_player.get_state()
                if state in [vlc.State.Playing, vlc.State.Paused, vlc.State.Buffering]:
                    # Tam ekran durumunu kontrol et ve değiştir
                    is_fullscreen = self.vlc_player.get_fullscreen()
                    self.vlc_player.set_fullscreen(not is_fullscreen)
                    
                    if not is_fullscreen:
                        self.status_callback("Tam ekran modu açıldı (Esc ile çıkış)")
                    else:
                        self.status_callback("Tam ekran modundan çıkıldı")
                else:
                    self.status_callback("Tam ekran için önce oynatmayı başlatın")
            except Exception as e:
                self.status_callback(f"Tam ekran hatası: {str(e)}")
    
    def open_separate_window(self, event=None):
        """Ayrı oynatma penceresi aç"""
        if not self.current_url or not self.current_station:
            self.status_callback("Önce bir radyo istasyonu çalın")
            return
        
        # Eğer zaten ayrı pencere varsa, onu öne getir
        if hasattr(self, 'separate_window') and self.separate_window and self.separate_window.winfo_exists():
            self.separate_window.lift()
            self.separate_window.focus_force()
            return
        
        # Ana oynatıcıyı durdur (ayrı pencereye devredilecek)
        if self.vlc_player:
            self.vlc_player.stop()
        self.stop_song_tracking()
        self.is_playing = False
        
        try:
            # Yeni pencere oluştur
            self.separate_window = tk.Toplevel()
            self.separate_window.title(f"VLC Player - {self.current_station}")
            self.separate_window.geometry("640x480")
            self.separate_window.configure(bg='black')
            
            # Pencereyi ekranın ortasına yerleştir
            self.separate_window.update_idletasks()
            width = 640
            height = 480
            x = (self.separate_window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.separate_window.winfo_screenheight() // 2) - (height // 2)
            self.separate_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Şarkı bilgisi paneli
            info_frame = tk.Frame(self.separate_window, bg='lightgray', height=30)
            info_frame.pack(fill='x', pady=(0, 2))
            info_frame.pack_propagate(False)
            
            self.separate_song_var = tk.StringVar(value=f"Çalıyor: {self.current_station}")
            song_label = tk.Label(info_frame, textvariable=self.separate_song_var, 
                                 bg='lightgray', fg='black', font=('Arial', 10, 'bold'))
            song_label.pack(expand=True, fill='both', padx=5, pady=2)
            
            # VLC oynatma alanı
            self.separate_vlc_frame = tk.Frame(self.separate_window, bg='black')
            self.separate_vlc_frame.pack(fill='both', expand=True, pady=(0, 2))
            
            # Kontrol butonları
            control_frame = tk.Frame(self.separate_window, bg='lightgray', height=40)
            control_frame.pack(fill='x')
            control_frame.pack_propagate(False)
            
            # Sol taraf - oynatma kontrolleri
            play_frame = tk.Frame(control_frame, bg='lightgray')
            play_frame.pack(side='left', padx=10, pady=5)
            
            tk.Button(play_frame, text="▶", command=self.play_separate, width=3).pack(side='left', padx=2)
            tk.Button(play_frame, text="⏸", command=self.pause_separate, width=3).pack(side='left', padx=2)
            tk.Button(play_frame, text="⏹", command=self.stop_separate, width=3).pack(side='left', padx=2)
            tk.Button(play_frame, text="⛶", command=self.simple_fullscreen_toggle, width=3, 
                     font=('Arial', 10)).pack(side='left', padx=2)
            
            # Sağ taraf - ses kontrolü
            volume_frame = tk.Frame(control_frame, bg='lightgray')
            volume_frame.pack(side='right', padx=10, pady=5)
            
            tk.Label(volume_frame, text="Ses:", font=('Arial', 8), bg='lightgray').pack(side='left')
            self.separate_volume_var = tk.IntVar(value=80)
            separate_volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal', 
                                           variable=self.separate_volume_var, command=self.on_separate_volume_change,
                                           length=100, width=15, bg='lightgray')
            separate_volume_scale.pack(side='left', padx=2)
            
            # Klavye kısayolları ve çift tık
            self.separate_window.bind('<Alt-Return>', self.simple_fullscreen_toggle)
            self.separate_window.bind('<Alt-Key-Return>', self.simple_fullscreen_toggle)
            self.separate_window.bind('<Escape>', self.exit_separate_fullscreen)
            self.separate_window.bind('<space>', self.toggle_separate_play_pause)
            self.separate_window.bind('<F11>', self.simple_fullscreen_toggle)  # F11 kısayolu ekle
            self.separate_vlc_frame.bind('<Double-Button-1>', self.simple_fullscreen_toggle)
            self.separate_window.focus_set()
            
            # Tam ekran durumu takibi
            self.separate_fullscreen_state = False
            
            # Pencere kapatıldığında temizlik yap
            self.separate_window.protocol("WM_DELETE_WINDOW", self.close_separate_window)
            
            # Ayrı VLC player oluştur
            self.create_separate_player()
            
            self.status_callback(f"Ayrı pencerede açıldı: {self.current_station}")
            
        except Exception as e:
            self.status_callback(f"Ayrı pencere açma hatası: {str(e)}")
    
    def create_separate_player(self):
        """Ayrı pencere için VLC player oluştur"""
        try:
            # Yeni VLC instance ve player oluştur (tam ekran desteği ile)
            vlc_args = [
                '--quiet',           # Hata mesajlarını azalt
                '--intf=dummy',      # Interface sorunlarını önle
                '--no-video-title-show',  # Video başlığını gösterme
                '--disable-screensaver',  # Ekran koruyucuyu devre dışı bırak
                '--verbose=0',       # Verbose çıktıyı kapat
                '--no-stats',        # İstatistikleri kapat
                '--no-osd',          # On-screen display'i kapat
            ]
            
            # Windows'a özel ayarlar
            if os.name == 'nt':
                vlc_args.extend([
                    '--no-directx-hw-yuv',  # DirectX donanım hızlandırmasını kapat
                    '--avcodec-hw=none',    # Donanım kod çözücüyü kapat
                    '--no-video-deco',      # Video dekorasyonlarını kapat
                ])
            else:
                vlc_args.append('--no-xlib')  # Linux için X11 sorunlarını önle
            
            self.separate_vlc_instance = vlc.Instance(vlc_args)
            self.separate_vlc_player = self.separate_vlc_instance.media_player_new()
            
            # VLC'yi frame'e bağla
            if os.name == 'nt':  # Windows
                self.separate_vlc_player.set_hwnd(self.separate_vlc_frame.winfo_id())
            else:  # Linux/Mac
                self.separate_vlc_player.set_xwindow(self.separate_vlc_frame.winfo_id())
            
            # Media oluştur ve çal
            media = self.separate_vlc_instance.media_new(self.current_url)
            self.separate_vlc_player.set_media(media)
            self.separate_vlc_player.play()
            
            # Ses seviyesini ayarla
            self.separate_vlc_player.audio_set_volume(self.separate_volume_var.get())
            
            # Şarkı bilgisi takibini başlat
            self.start_separate_song_tracking()
            
        except Exception as e:
            self.status_callback(f"Ayrı player oluşturma hatası: {str(e)}")
    
    def start_separate_song_tracking(self):
        """Ayrı pencere için şarkı bilgisi takibi"""
        if not hasattr(self, 'separate_song_var') or not self.separate_song_var:
            return
        
        def update_separate_song_info():
            if (not hasattr(self, 'separate_vlc_player') or 
                not self.separate_vlc_player or
                not hasattr(self, 'separate_window') or
                not self.separate_window or
                not self.separate_window.winfo_exists()):
                return
            
            try:
                # Player durumunu kontrol et
                state = self.separate_vlc_player.get_state()
                if state in [vlc.State.Playing, vlc.State.Buffering]:
                    # VLC'den meta bilgileri al
                    media = self.separate_vlc_player.get_media()
                    if media:
                        title = media.get_meta(vlc.Meta.Title)
                        artist = media.get_meta(vlc.Meta.Artist)
                        now_playing = media.get_meta(vlc.Meta.NowPlaying)
                        
                        # En uygun bilgiyi seç
                        song_info = None
                        if now_playing and now_playing.strip():
                            song_info = now_playing.strip()
                        elif title and title.strip() and len(title.strip()) > 5:
                            if artist and artist.strip():
                                song_info = f"{artist} - {title}"
                            else:
                                song_info = title.strip()
                        
                        # Şarkı bilgisini güncelle
                        if song_info and len(song_info) > 3:
                            if not (song_info.startswith('http') or 
                                   song_info.startswith('www')):
                                if len(song_info) > 50:
                                    song_info = song_info[:47] + "..."
                                self.separate_song_var.set(song_info)
                            else:
                                self.separate_song_var.set(f"Çalıyor: {self.current_station}")
                        else:
                            self.separate_song_var.set(f"Çalıyor: {self.current_station}")
                    else:
                        self.separate_song_var.set(f"Çalıyor: {self.current_station}")
                
                # 3 saniye sonra tekrar kontrol et
                if (hasattr(self, 'separate_window') and self.separate_window and 
                    self.separate_window.winfo_exists()):
                    self.separate_window.after(3000, update_separate_song_info)
                
            except Exception:
                if (hasattr(self, 'separate_song_var') and self.separate_song_var and
                    hasattr(self, 'separate_window') and self.separate_window and 
                    self.separate_window.winfo_exists()):
                    self.separate_song_var.set(f"Çalıyor: {self.current_station}")
                    self.separate_window.after(5000, update_separate_song_info)
        
        # İlk güncellemeyi 2 saniye sonra başlat
        if hasattr(self, 'separate_window') and self.separate_window:
            self.separate_window.after(2000, update_separate_song_info)
    
    def play_separate(self):
        """Ayrı pencerede oynat"""
        if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
            self.separate_vlc_player.play()
    
    def pause_separate(self):
        """Ayrı pencerede duraklat"""
        if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
            self.separate_vlc_player.pause()
    
    def stop_separate(self):
        """Ayrı pencerede durdur"""
        if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
            self.separate_vlc_player.stop()
    
    def toggle_separate_fullscreen(self, event=None):
        """Ayrı pencerede tam ekran aç/kapat"""
        if not hasattr(self, 'separate_vlc_player') or not self.separate_vlc_player:
            self.status_callback("VLC player hazır değil")
            return
        
        try:
            # Önce player'ın hazır olduğunu kontrol et
            state = self.separate_vlc_player.get_state()
            if state not in [vlc.State.Playing, vlc.State.Paused, vlc.State.Buffering]:
                self.status_callback("Tam ekran için önce oynatmayı başlatın")
                return
            
            # Windows'ta daha güvenli tam ekran yöntemi
            if os.name == 'nt':  # Windows
                try:
                    # VLC'nin kendi tam ekran fonksiyonunu kullan
                    current_fullscreen = self.separate_vlc_player.get_fullscreen()
                    self.separate_vlc_player.set_fullscreen(not current_fullscreen)
                    
                    if not current_fullscreen:
                        self.status_callback("Tam ekran modu açıldı (Esc/F11 ile çıkış)")
                        self.separate_fullscreen_state = True
                    else:
                        self.status_callback("Tam ekran modundan çıkıldı")
                        self.separate_fullscreen_state = False
                        
                except Exception as vlc_error:
                    # VLC tam ekran başarısız olursa, pencere tam ekranı dene
                    self.toggle_window_fullscreen()
            else:
                # Linux/Mac için standart yöntem
                is_fullscreen = self.separate_vlc_player.get_fullscreen()
                self.separate_vlc_player.set_fullscreen(not is_fullscreen)
                
                if not is_fullscreen:
                    self.status_callback("Tam ekran modu açıldı (Esc ile çıkış)")
                else:
                    self.status_callback("Tam ekran modundan çıkıldı")
                    
        except Exception as e:
            self.status_callback(f"Tam ekran hatası: {str(e)}")
            # Hata durumunda pencere tam ekranını dene
            self.toggle_window_fullscreen()
    
    def toggle_window_fullscreen(self):
        """Pencere seviyesinde tam ekran (VLC tam ekran başarısız olursa)"""
        try:
            if not hasattr(self, 'separate_fullscreen_state'):
                self.separate_fullscreen_state = False
            
            if not self.separate_fullscreen_state:
                # Tam ekrana geç
                self.separate_window.attributes('-fullscreen', True)
                self.separate_fullscreen_state = True
                self.status_callback("Pencere tam ekran modu (Esc ile çıkış)")
            else:
                # Tam ekrandan çık
                self.separate_window.attributes('-fullscreen', False)
                self.separate_fullscreen_state = False
                self.status_callback("Tam ekran modundan çıkıldı")
                
        except Exception as e:
            self.status_callback(f"Pencere tam ekran hatası: {str(e)}")
    
    def simple_fullscreen_toggle(self, event=None):
        """Basit tam ekran toggle (sadece pencere seviyesinde)"""
        try:
            if not hasattr(self, 'separate_window') or not self.separate_window:
                return
            
            if not hasattr(self, 'separate_fullscreen_state'):
                self.separate_fullscreen_state = False
            
            if not self.separate_fullscreen_state:
                # Tam ekrana geç
                self.separate_window.attributes('-fullscreen', True)
                self.separate_window.attributes('-topmost', True)  # En üstte tut
                self.separate_fullscreen_state = True
                self.status_callback("Tam ekran modu açıldı (Esc/F11 ile çıkış)")
            else:
                # Tam ekrandan çık
                self.separate_window.attributes('-fullscreen', False)
                self.separate_window.attributes('-topmost', False)
                self.separate_fullscreen_state = False
                self.status_callback("Tam ekran modundan çıkıldı")
                
        except Exception as e:
            self.status_callback(f"Tam ekran hatası: {str(e)}")
    
    def exit_separate_fullscreen(self, event=None):
        """Tam ekrandan çık"""
        try:
            # Önce VLC tam ekranından çıkmayı dene
            if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
                self.separate_vlc_player.set_fullscreen(False)
            
            # Pencere tam ekranından da çık
            if hasattr(self, 'separate_window') and self.separate_window:
                self.separate_window.attributes('-fullscreen', False)
            
            # Durumu güncelle
            if hasattr(self, 'separate_fullscreen_state'):
                self.separate_fullscreen_state = False
            
            self.status_callback("Tam ekran modundan çıkıldı")
            
        except Exception as e:
            self.status_callback(f"Tam ekran çıkış hatası: {str(e)}")
    
    def toggle_separate_play_pause(self, event=None):
        """Space ile oynat/duraklat"""
        if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
            state = self.separate_vlc_player.get_state()
            if state == vlc.State.Playing:
                self.separate_vlc_player.pause()
            else:
                self.separate_vlc_player.play()
    
    def on_separate_volume_change(self, value):
        """Ayrı pencerede ses seviyesi değiştirildiğinde"""
        if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
            volume = int(value)
            self.separate_vlc_player.audio_set_volume(volume)
    
    def close_separate_window(self):
        """Ayrı pencereyi kapat ve ana oynatıcıda devam et"""
        try:
            # Ayrı pencere player'ını durdur
            if hasattr(self, 'separate_vlc_player') and self.separate_vlc_player:
                self.separate_vlc_player.stop()
                self.separate_vlc_player = None
            
            if hasattr(self, 'separate_vlc_instance'):
                self.separate_vlc_instance = None
            
            if hasattr(self, 'separate_window') and self.separate_window:
                self.separate_window.destroy()
                self.separate_window = None
            
            # Ana oynatıcıda devam et
            if self.current_url and self.current_station:
                self.play_stream(self.current_url, self.current_station, embedded=True)
                self.status_callback(f"Ana oynatıcıda devam ediyor: {self.current_station}")
            else:
                self.status_callback("Ayrı pencere kapatıldı")
            
        except Exception as e:
            self.status_callback("Ayrı pencere kapatıldı")
    
    def toggle_window_mode(self, event=None):
        """Pencere moduna geç/geri dön"""
        if not self.current_url or not self.current_station:
            return
        
        if self.vlc_window and self.vlc_window.winfo_exists():
            # Pencere modundan gömülü moda geç
            self.close_vlc_window()
            # Gömülü oynatıcıda devam et
            self.play_stream(self.current_url, self.current_station, embedded=True)
        else:
            # Gömülü moddan pencere moduna geç
            self.stop_embedded()
            # Pencere modunda aç
            self.open_vlc_window()
    
    def open_vlc_window(self):
        """VLC pencere modunu aç"""
        if not self.current_url or not self.current_station:
            return
        
        try:
            # Yeni pencere oluştur
            self.vlc_window = tk.Toplevel()
            self.vlc_window.title(f"VLC Player - {self.current_station}")
            self.vlc_window.geometry("640x480")
            
            # Şarkı bilgisi paneli
            info_frame = tk.Frame(self.vlc_window, bg='lightgray', height=30)
            info_frame.pack(fill='x', pady=(0, 5))
            info_frame.pack_propagate(False)
            
            self.window_song_var = tk.StringVar(value=f"Çalıyor: {self.current_station}")
            song_label = tk.Label(info_frame, textvariable=self.window_song_var, 
                                 bg='lightgray', fg='black', font=('Arial', 10, 'bold'))
            song_label.pack(expand=True, fill='both', padx=5, pady=2)
            
            # VLC oynatma alanı
            vlc_frame = tk.Frame(self.vlc_window, bg='black')
            vlc_frame.pack(fill='both', expand=True, pady=(0, 5))
            
            # Kontrol butonları
            control_frame = tk.Frame(self.vlc_window)
            control_frame.pack(fill='x', pady=5)
            
            tk.Button(control_frame, text="▶", command=self.play_embedded, width=3).pack(side='left', padx=2)
            tk.Button(control_frame, text="⏸", command=self.pause_embedded, width=3).pack(side='left', padx=2)
            tk.Button(control_frame, text="⏹", command=self.stop_embedded, width=3).pack(side='left', padx=2)
            tk.Button(control_frame, text="Gömülü Moda Dön", command=self.toggle_window_mode).pack(side='right', padx=2)
            
            # VLC player'ı pencereye bağla
            if not self.vlc_instance:
                self.vlc_instance = vlc.Instance()
            
            self.vlc_player = self.vlc_instance.media_player_new()
            
            if os.name == 'nt':  # Windows
                self.vlc_player.set_hwnd(vlc_frame.winfo_id())
            else:  # Linux/Mac
                self.vlc_player.set_xwindow(vlc_frame.winfo_id())
            
            # Media oluştur ve çal
            media = self.vlc_instance.media_new(self.current_url)
            self.vlc_player.set_media(media)
            self.vlc_player.play()
            
            # Pencere kapanma olayı
            self.vlc_window.protocol("WM_DELETE_WINDOW", self.close_vlc_window)
            
            # Şarkı takibini başlat (pencere için)
            self.start_window_song_tracking()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Pencere modu hatası: {str(e)}")
    
    def start_window_song_tracking(self):
        """Pencere modu için şarkı takibi"""
        if not hasattr(self, 'window_song_var') or not self.window_song_var:
            return
        
        def update_window_song_info():
            if (not self.vlc_window or not self.vlc_window.winfo_exists() or 
                not self.vlc_player or not hasattr(self, 'window_song_var')):
                return
            
            try:
                # VLC'den meta bilgileri al
                media = self.vlc_player.get_media()
                if media:
                    title = media.get_meta(vlc.Meta.Title)
                    artist = media.get_meta(vlc.Meta.Artist)
                    now_playing = media.get_meta(vlc.Meta.NowPlaying)
                    description = media.get_meta(vlc.Meta.Description)
                    
                    # En uygun bilgiyi seç
                    song_info = None
                    if now_playing and now_playing.strip():
                        song_info = now_playing.strip()
                    elif description and description.strip() and len(description.strip()) > 5:
                        song_info = description.strip()
                    elif title and title.strip() and len(title.strip()) > 5:
                        if artist and artist.strip():
                            song_info = f"{artist} - {title}"
                        else:
                            song_info = title.strip()
                    
                    # Şarkı bilgisini güncelle
                    if song_info and len(song_info) > 3:
                        # URL'leri filtrele
                        if not (song_info.startswith('http') or song_info.startswith('www')):
                            self.window_song_var.set(song_info)
                            self.vlc_window.title(f"VLC Player - {self.current_station} | {song_info}")
                        else:
                            self.window_song_var.set(f"Çalıyor: {self.current_station}")
                            self.vlc_window.title(f"VLC Player - {self.current_station}")
                    else:
                        self.window_song_var.set(f"Çalıyor: {self.current_station}")
                        self.vlc_window.title(f"VLC Player - {self.current_station}")
                
                # 3 saniye sonra tekrar kontrol et
                if self.vlc_window and self.vlc_window.winfo_exists():
                    self.vlc_window.after(3000, update_window_song_info)
                
            except Exception as e:
                # Hata durumunda sadece istasyon adını göster
                if hasattr(self, 'window_song_var') and self.window_song_var:
                    self.window_song_var.set(f"Çalıyor: {self.current_station}")
                # 5 saniye sonra tekrar dene
                if self.vlc_window and self.vlc_window.winfo_exists():
                    self.vlc_window.after(5000, update_window_song_info)
        
        # İlk güncellemeyi 2 saniye sonra başlat
        if self.vlc_window and self.vlc_window.winfo_exists():
            self.vlc_window.after(2000, update_window_song_info)
    
    def close_vlc_window(self):
        """VLC penceresini kapat"""
        if self.vlc_window and self.vlc_window.winfo_exists():
            self.vlc_window.destroy()
        self.vlc_window = None
        
        # Window song var'ı temizle
        if hasattr(self, 'window_song_var'):
            delattr(self, 'window_song_var')
    
    def set_vlc_path(self, parent_window):
        """VLC yolu ayarla"""
        from tkinter import filedialog
        
        vlc_path = filedialog.askopenfilename(
            title="VLC Executable Seç",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        
        if vlc_path:
            self.vlc_path = vlc_path
            self.db_manager.set_setting('vlc.path', vlc_path)
            messagebox.showinfo("Başarılı", f"VLC yolu ayarlandı: {vlc_path}")
            return True
        
        return False
    
    def get_vlc_path(self):
        """VLC yolunu getir"""
        return self.vlc_path
    
    def is_vlc_available(self):
        """VLC kütüphanesinin mevcut olup olmadığını kontrol et"""
        return VLC_AVAILABLE