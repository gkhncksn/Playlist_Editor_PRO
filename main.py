#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path

# Modülleri import et
from database_manager import DatabaseManager
from playlist_generator import PlaylistGeneratorModule
from url_checker import URLCheckerModule
from playlist_editor import PlaylistEditorModule
from playlist_merger import PlaylistMergerModule
from vlc_player import VLCPlayerModule

class RadioPlaylistGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Playlist Editor PRO")
        self.root.geometry("1250x900")
        
    # Pencereyi ekranın ortasına yerleştir
        self.center_window(self.root, 1250, 900)
        
        # Veritabanı yöneticisini başlat
        self.db_manager = DatabaseManager("veriler.db")
        
        # INI dosyasından SQLite'a geçiş yap
        self.migrate_from_ini()
        
        # VLC yolu kontrolü ve ayarı
        self.check_and_setup_vlc_path()
        
        # VLC player modülünü başlat
        self.vlc_player = VLCPlayerModule(self.db_manager, self.update_status, self.on_vlc_stop, self.on_song_info_update)
        
        # Şarkı takibi durumu
        self.song_tracking_active = False
        
        # Çalan istasyon bilgisi
        self.current_playing_station = None
        self.current_song_info = None
        
        # Tab isimleri
        self.tab_names = {
            0: "URL Checker",
            1: "Playlist Editor", 
            2: "Playlist Generator",
            3: "Playlist Merger"
        }
        
        self.setup_ui()
        
    def center_window(self, window, width, height):
        """Pencereyi ekranın ortasına yerleştir"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_treeview_styles(self):
        """Treeview stilleri ayarla - belirgin hücre çizgileri ve zebra stripes"""
        style = ttk.Style()
        
        # Treeview için özel stil oluştur
        style.configure("Custom.Treeview",
                       background="white",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="white",
                       borderwidth=1,
                       relief="solid")
        
        # Seçili satır rengi
        style.map("Custom.Treeview",
                 background=[('selected', '#0078d4')],
                 foreground=[('selected', 'white')])
        
        # Başlık stili
        style.configure("Custom.Treeview.Heading",
                       background="#f0f0f0",
                       foreground="black",
                       borderwidth=1,
                       relief="solid",
                       font=('Arial', 9, 'bold'))
        
        # Sütun sürükleme özelliği için
        style.configure("Custom.Treeview.Heading",
                       cursor="hand2")
    
    def migrate_from_ini(self):
        """INI dosyasından SQLite'a geçiş"""
        ini_file = "radio_settings.ini"
        if os.path.exists(ini_file):
            try:
                success = self.db_manager.migrate_from_ini(ini_file)
                if success:
                    # Başarılı geçişten sonra INI dosyasını yedekle
                    backup_file = "radio_settings.ini.backup"
                    if not os.path.exists(backup_file):
                        os.rename(ini_file, backup_file)
                        print("Ayarlar SQLite veritabanına aktarıldı")
            except Exception as e:
                print(f"INI geçiş hatası: {e}")
    
    def check_and_setup_vlc_path(self):
        """VLC yolunu kontrol et ve gerekirse ayarla"""
        vlc_path = self.db_manager.get_setting('vlc.path')
        
        if not vlc_path or not os.path.exists(vlc_path):
            # VLC yolu yok veya geçersiz, otomatik ara
            auto_vlc_path = self.find_vlc_automatically()
            
            if auto_vlc_path:
                # Otomatik bulundu
                self.db_manager.set_setting('vlc.path', auto_vlc_path)
                print(f"VLC otomatik bulundu: {auto_vlc_path}")
            else:
                # Otomatik bulunamadı, kullanıcıdan iste
                from tkinter import filedialog, messagebox
                
                # Ana pencere henüz oluşmadığı için geçici bir root oluştur
                temp_root = tk.Tk()
                temp_root.withdraw()  # Gizle
                
                result = messagebox.askyesno(
                    "VLC Bulunamadı", 
                    "VLC Media Player bulunamadı.\n\n"
                    "VLC oynatıcı özelliklerini kullanmak için VLC yolunu seçmek ister misiniz?\n\n"
                    "Hayır'ı seçerseniz sadece HTTP URL kontrolü yapılacaktır.",
                    parent=temp_root
                )
                
                if result:
                    vlc_exe_path = filedialog.askopenfilename(
                        title="VLC Executable Seç (vlc.exe)",
                        filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
                        parent=temp_root
                    )
                    
                    if vlc_exe_path and os.path.exists(vlc_exe_path):
                        self.db_manager.set_setting('vlc.path', vlc_exe_path)
                        print(f"VLC yolu ayarlandı: {vlc_exe_path}")
                    else:
                        print("VLC yolu ayarlanmadı - sadece HTTP kontrolü kullanılacak")
                else:
                    print("VLC ayarı atlandı - sadece HTTP kontrolü kullanılacak")
                
                temp_root.destroy()
    
    def find_vlc_automatically(self):
        """VLC'yi otomatik olarak bul"""
        possible_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\VLC\vlc.exe"),
            r"D:\Program Files\VideoLAN\VLC\vlc.exe",
            r"D:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def setup_ui(self):
        # Treeview stilleri ayarla
        self.setup_treeview_styles()
        
        # Ana notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        
        # Tab 1: URL Checker (ilk sıraya taşındı)
        self.checker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.checker_frame, text="URL Checker")
        
        # Tab 2: Playlist Editor
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="Playlist Editor")
        
        # Tab 3: Playlist Generator
        self.generator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.generator_frame, text="Playlist Generator")
        
        # Tab 4: Playlist Merger
        self.merger_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.merger_frame, text="Playlist Merger")
        
        # Tab değişiklik olayını bağla
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Alt panel (Progressbar + Statusbar birleşik)
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        # Progressbar (metin ile birleşik)
        self.progress_var = tk.StringVar(value="Hazır")
        self.combined_progress = ttk.Progressbar(bottom_frame, mode='determinate')
        self.combined_progress.pack(fill=tk.X, pady=(0, 2))
        
        # Progressbar üzerine metin yazmak için Label (şeffaf background)
        self.progress_label = ttk.Label(bottom_frame, textvariable=self.progress_var, 
                                       anchor=tk.CENTER)
        self.progress_label.place(in_=self.combined_progress, relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Modülleri başlat
        self.setup_modules()
        
        # Başlangıçta pencere başlığını ayarla
        self.update_window_title()
    
    def setup_modules(self):
        """Modülleri başlat"""
        # Playlist Generator modülü
        self.playlist_generator = PlaylistGeneratorModule(
            self.generator_frame, 
            self.update_status, 
            self.update_progress,
            self.db_manager
        )
        
        # URL Checker modülü
        self.url_checker = URLCheckerModule(
            self.checker_frame, 
            self.update_status, 
            self.update_progress,
            self.db_manager
        )
        
        # Playlist Editor modülü
        self.playlist_editor = PlaylistEditorModule(
            self.editor_frame, 
            self.update_status, 
            self.update_progress,
            self.db_manager
        )
        
        # Playlist Editor'a çalma callback'ini ayarla
        self.playlist_editor.set_play_callback(self.play_station_from_editor)
        
        # Playlist Merger modülü
        self.playlist_merger = PlaylistMergerModule(
            self.merger_frame, 
            self.update_status, 
            self.update_progress,
            self.db_manager
        )
        
        # URL Checker'a VLC player entegrasyonu ekle
        self.setup_vlc_integration()
    
    def setup_vlc_integration(self):
        """URL Checker'a VLC player entegrasyonu"""
        # URL Checker'ın sağ panelini VLC player ile değiştir
        if hasattr(self.url_checker, 'parent_frame'):
            # Mevcut sağ paneli bul ve değiştir
            checker_main = None
            for child in self.url_checker.parent_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    checker_main = child
                    break
            
            if checker_main:
                # Sağ paneli bul
                right_panel = None
                for child in checker_main.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and ("Test" in str(child.cget('text')) or "Oynatıcı" in str(child.cget('text'))):
                        right_panel = child
                        break
                
                if right_panel:
                    # VLC player'ı sağ panele ekle (tam boyut)
                    self.vlc_player.setup_embedded_player(right_panel)
        
        # Çift tıklama olayını bağla
        if hasattr(self.url_checker, 'url_tree'):
            self.url_checker.url_tree.bind('<Double-1>', self.on_station_double_click)
            
        # Sağ tık menüsünü güncelle
        if hasattr(self.url_checker, 'url_tree'):
            self.url_checker.url_tree.bind('<Button-3>', self.show_context_menu)
        
        # VLC ayar butonu artık gerekli değil - otomatik ayarlanıyor
    
    # VLC ayar butonu artık gerekli değil - program başlangıcında otomatik ayarlanıyor
    
    def on_station_double_click(self, event):
        """İstasyon çift tıklama olayı - geliştirilmiş kontrol"""
        selection = self.url_checker.url_tree.selection()
        if not selection:
            return
        
        # Seçili item bilgilerini al
        item = selection[0]
        values = self.url_checker.url_tree.item(item)['values']
        if len(values) >= 6:
            station_name = values[1]
            url = values[5]
            status = values[0]
            
            # URL geçerli mi kontrol et
            if not url or url.strip() == '':
                self.update_status("Geçersiz URL")
                return
            
            # Önceki oynatmayı temizle
            self.stop_current_playback()
            
            # Kısa bekleme (temizlik için)
            self.root.after(100, lambda: self.start_new_playback(url, station_name, status))
    
    def start_new_playback(self, url, station_name, status):
        """Yeni oynatmayı başlat"""
        # Eğer URL çalışmıyorsa uyarı ver ama yine de dene
        if "Çalışmıyor" in status:
            self.update_status(f"Uyarı: {station_name} - URL çalışmıyor olarak işaretli")
        
        # Oynatmayı başlat
        success = self.vlc_player.play_stream(url, station_name, embedded=True)
        if success:
            # Ana pencere başlığını güncelle
            self.current_playing_station = station_name
            self.update_window_title()
            self.song_tracking_active = True
            self.update_status(f"Oynatılıyor: {station_name}")
        else:
            self.update_status(f"Oynatma başarısız: {station_name}")
    
    def stop_current_playback(self):
        """Mevcut oynatmayı durdur ve temizle"""
        # VLC oynatmayı durdur (callback otomatik olarak çağrılacak)
        self.vlc_player.stop_embedded()
        
        # Status bar'ı güncelle
        self.update_status("Oynatma durduruldu")
    
    def show_context_menu(self, event):
        """Sağ tık menüsü göster"""
        selection = self.url_checker.url_tree.selection()
        if not selection:
            return
        
        # Context menu oluştur
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Gömülü Oynatıcıda Çal", 
                                command=lambda: self.on_station_double_click(event))
        context_menu.add_command(label="Pencere Modunda Çal", 
                                command=lambda: self.play_in_window_mode(event))
        context_menu.add_separator()
        context_menu.add_command(label="URL'yi Kopyala", 
                                command=self.copy_selected_url)
        context_menu.add_separator()
        context_menu.add_command(label="Oynatmayı Durdur", 
                                command=self.stop_current_playback)
        
        # Menüyü göster
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def play_in_window_mode(self, event):
        """Pencere modunda oynat"""
        selection = self.url_checker.url_tree.selection()
        if not selection:
            return
        
        # Önceki oynatmayı durdur
        self.stop_current_playback()
        
        # Seçili item bilgilerini al
        item = selection[0]
        values = self.url_checker.url_tree.item(item)['values']
        if len(values) >= 6:
            station_name = values[1]
            url = values[5]
            
            # URL geçerli mi kontrol et
            if not url or url.strip() == '':
                self.update_status("Geçersiz URL")
                return
            
            # Pencere modunda oynat
            success = self.vlc_player.play_stream(url, station_name, embedded=False)
            if success:
                # Pencere modunu aç
                self.vlc_player.open_vlc_window()
                self.song_tracking_active = True
    
    def copy_selected_url(self):
        """Seçili URL'yi panoya kopyala"""
        selection = self.url_checker.url_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.url_checker.url_tree.item(item)['values']
        if len(values) >= 6:
            url = values[5]
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.update_status("URL panoya kopyalandı")
    
    # VLC yolu artık program başlangıcında otomatik ayarlanıyor
    
    def update_status(self, message):
        """Durum mesajını güncelle"""
        self.progress_var.set(message)
    
    def play_station_from_editor(self, url, station_name):
        """Playlist Editor'dan radyo istasyonu çal"""
        try:
            # Mevcut oynatmayı durdur
            self.stop_current_playback()
            
            # Yeni istasyonu çal
            success = self.vlc_player.play_stream(url, station_name, embedded=True)
            
            if success:
                # Ana pencere başlığını güncelle
                self.current_playing_station = station_name
                self.update_window_title()
                self.song_tracking_active = True
                self.update_status(f"Oynatılıyor: {station_name}")
            else:
                self.update_status(f"Oynatma başarısız: {station_name}")
                
        except Exception as e:
            self.update_status(f"Çalma hatası: {str(e)}")
        self.root.update_idletasks()
    
    def update_progress(self, message, progress_value=None):
        """Progress mesajını ve değerini güncelle"""
        self.progress_var.set(message)
        
        # Progress değeri verilmişse progressbar'ı güncelle
        if progress_value is not None:
            self.combined_progress.config(value=progress_value)
        
        self.root.update_idletasks()
    
    def on_vlc_stop(self):
        """VLC player durdurulduğunda çağrılır"""
        # Çalan istasyon bilgisini temizle
        self.current_playing_station = None
        self.current_song_info = None
        self.song_tracking_active = False
        
        # Pencere başlığını güncelle
        self.update_window_title()
    
    def on_song_info_update(self, song_info):
        """Şarkı bilgisi güncellendiğinde çağrılır"""
        self.current_song_info = song_info
        self.update_window_title()
    
    def on_tab_changed(self, event):
        """Tab değiştirildiğinde pencere başlığını güncelle"""
        self.update_window_title()
    
    def update_window_title(self):
        """Pencere başlığını aktif tab ve çalan istasyona göre güncelle"""
        try:
            # Aktif tab'ı al
            current_tab = self.notebook.index(self.notebook.select())
            tab_name = self.tab_names.get(current_tab, "Playlist Editor PRO")
            
            # Başlık oluştur
            if self.current_playing_station:
                title = f"{tab_name} - Çalıyor: {self.current_playing_station}"
                
                # Şarkı bilgisi varsa ekle
                if self.current_song_info and self.current_song_info.strip():
                    # Şarkı bilgisinin istasyon adı olmadığından emin ol
                    if (not self.current_song_info.startswith("Çalıyor:") and 
                        self.current_song_info != self.current_playing_station):
                        title += f" ({self.current_song_info})"
            else:
                title = tab_name
            
            self.root.title(title)
        except:
            # Hata durumunda varsayılan başlık
            self.root.title("Playlist Editor PRO")
    
    def on_closing(self):
        """Program kapanırken temizlik yap"""
        # VLC oynatmayı durdur
        self.stop_current_playback()
        
        # VLC penceresini kapat
        if hasattr(self.vlc_player, 'vlc_window') and self.vlc_player.vlc_window:
            self.vlc_player.close_vlc_window()
        
        # Ana pencereyi kapat
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RadioPlaylistGenerator(root)
    
    # Kapanma olayını bağla
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()