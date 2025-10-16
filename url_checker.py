#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import urllib.request
import urllib.error
import time
import re
import os
from pathlib import Path

class URLCheckerModule:
    def __init__(self, parent_frame, status_callback=None, progress_callback=None, db_manager=None):
        self.parent_frame = parent_frame
        self.status_callback = status_callback or (lambda x: None)
        self.progress_callback = progress_callback or (lambda x: None)
        self.db_manager = db_manager
        
        # URL Checker için değişkenler
        self.playlist_data = []
        self.checking_urls = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Ana frame
        checker_main = ttk.Frame(self.parent_frame, padding="10")
        checker_main.pack(fill='both', expand=True)
        
        # Başlık
        title_label = ttk.Label(checker_main, text="Playlist URL Checker", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sol panel (Kontrol paneli - genişletilmiş)
        left_panel = ttk.LabelFrame(checker_main, text="Kontrol Paneli", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # m3u8 dosyası seçimi
        ttk.Label(left_panel, text="Playlist Dosyası Seç:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        m3u8_frame = ttk.Frame(left_panel)
        m3u8_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.m3u8_path = tk.StringVar()
        self.m3u8_entry = ttk.Entry(m3u8_frame, textvariable=self.m3u8_path, width=40)
        self.m3u8_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(m3u8_frame, text="Gözat", command=self.browse_m3u8_file).grid(row=0, column=1, padx=(5, 0))
        
        # Kontrol butonları (2 sütunlu düzen)
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # İptal durumu için değişken
        self.checking_cancelled = False
        
        self.check_button = ttk.Button(button_frame, text="URL'leri Kontrol Et", command=self.toggle_url_check)
        self.check_button.grid(row=0, column=0, pady=2, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.delete_button = ttk.Button(button_frame, text="Seçili URL'leri Sil", command=self.delete_selected_urls)
        self.delete_button.grid(row=0, column=1, pady=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        self.save_button = ttk.Button(button_frame, text="Temizlenmiş Playlist Kaydet", command=self.save_cleaned_m3u8)
        self.save_button.grid(row=1, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        # İstatistikler paneli (kontrol paneli içinde)
        stats_frame = ttk.LabelFrame(left_panel, text="İstatistikler", padding="5")
        stats_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=35, state='disabled', font=('Arial', 9))
        self.stats_text.pack(fill='both', expand=True)
        
        # Sağ panel (VLC Oynatıcı - tam boyut)
        right_panel = ttk.LabelFrame(checker_main, text="Hızlı Test Oynatıcısı", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Alt kısım - Treeview
        tree_frame = ttk.Frame(checker_main)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Treeview
        columns = ('status', 'title', 'tvg_name', 'tvg_logo', 'group_title', 'url')
        self.url_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12, style="Custom.Treeview")
        
        # Alternatif satır renkleri için tag'ler
        self.url_tree.tag_configure('oddrow', background='#f9f9f9')
        self.url_tree.tag_configure('evenrow', background='white')
        
        # Sütun başlıkları ve sıralama
        self.url_tree.heading('status', text='Durum', command=lambda: self.sort_treeview(self.url_tree, 'status', False))
        self.url_tree.heading('title', text='İstasyon Adı', command=lambda: self.sort_treeview(self.url_tree, 'title', False))
        self.url_tree.heading('tvg_name', text='TVG Name', command=lambda: self.sort_treeview(self.url_tree, 'tvg_name', False))
        self.url_tree.heading('tvg_logo', text='Logo URL', command=lambda: self.sort_treeview(self.url_tree, 'tvg_logo', False))
        self.url_tree.heading('group_title', text='Grup', command=lambda: self.sort_treeview(self.url_tree, 'group_title', False))
        self.url_tree.heading('url', text='Stream URL', command=lambda: self.sort_treeview(self.url_tree, 'url', False))
        
        # Sütun genişlikleri
        self.url_tree.column('status', width=80, minwidth=60)
        self.url_tree.column('title', width=200, minwidth=150)
        self.url_tree.column('tvg_name', width=120, minwidth=80)
        self.url_tree.column('tvg_logo', width=150, minwidth=100)
        self.url_tree.column('group_title', width=100, minwidth=70)
        self.url_tree.column('url', width=300, minwidth=200)
        
        self.url_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Delete tuşu desteği
        self.url_tree.bind('<Delete>', self.on_delete_key)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.url_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.url_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.url_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.url_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Grid weights - Kontrol Paneli %75 genişletildi, Hızlı Test Oynatıcısı %25 daraltıldı
        checker_main.columnconfigure(0, weight=3)  # Sol panel (Kontrol Paneli) %75 genişletildi
        checker_main.columnconfigure(1, weight=1)  # Sağ panel (Hızlı Test Oynatıcısı) %25 daraltıldı
        checker_main.rowconfigure(1, weight=1)
        checker_main.rowconfigure(2, weight=2)
        
        # Sol panel içindeki widget'ların genişlemesi için
        left_panel.columnconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        
        m3u8_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        left_panel.rowconfigure(3, weight=1)  # İstatistikler frame'i genişleyebilir
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def browse_m3u8_file(self):
        """Playlist dosyası seç"""
        # Son kullanılan klasörü al
        initial_dir = "."
        if self.db_manager:
            initial_dir = self.db_manager.get_last_directory("url_checker", "open")
        
        filename = filedialog.askopenfilename(
            title="Playlist Dosyası Seç",
            initialdir=initial_dir,
            filetypes=[
                ("Playlist files", "*.m3u;*.m3u8;*.pls;*.dpl"),
                (".m3u files", "*.m3u;*.m3u8"),
                (".pls files", "*.pls"),
                (".dpl files", "*.dpl"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Son kullanılan klasörü kaydet
            if self.db_manager:
                self.db_manager.set_last_directory("url_checker", "open", filename)
            
            self.m3u8_path.set(filename)
            self.load_playlist_file(filename)
    
    def load_playlist_file(self, file_path):
        """Playlist dosyasını yükle ve parse et - çoklu format desteği"""
        try:
            self.playlist_data = []
            
            # Dosya varlığını kontrol et
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
            
            # Dosya uzantısına göre format belirle
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.m3u', '.m3u8']:
                self.load_m3u_format(file_path)
            elif file_ext == '.pls':
                self.load_pls_format(file_path)
            elif file_ext == '.dpl':
                self.load_dpl_format(file_path)
            else:
                # Varsayılan olarak M3U formatı dene
                self.load_m3u_format(file_path)
            
            # Widget'ların var olduğunu kontrol et
            if hasattr(self, 'url_tree') and self.url_tree and self.url_tree.winfo_exists():
                # Treeview'i güncelle
                self.update_treeview()
                self.update_stats()
            
            self.status_callback(f"Playlist dosyası yüklendi: {len(self.playlist_data)} istasyon ({file_ext.upper()})")
            
        except Exception as e:
            error_msg = f"Playlist dosyası yüklenirken hata: {str(e)}"
            self.status_callback(error_msg)
            messagebox.showerror("Hata", error_msg)
    
    def load_m3u_format(self, file_path):
        """m3u/m3u8 formatını yükle"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # EXTINF satırını parse et
                current_entry = self.parse_extinf_line(line)
            elif line and not line.startswith('#'):
                # URL satırı
                if current_entry:
                    current_entry['url'] = line
                    self.playlist_data.append(current_entry.copy())
                    current_entry = {}
    
    def load_pls_format(self, file_path):
        """PLS formatını yükle"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        files = {}
        titles = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('File'):
                # File1=http://url formatı
                match = re.match(r'File(\d+)=(.+)', line)
                if match:
                    index = int(match.group(1))
                    url = match.group(2)
                    files[index] = url
            
            elif line.startswith('Title'):
                # Title1=Station Name formatı
                match = re.match(r'Title(\d+)=(.+)', line)
                if match:
                    index = int(match.group(1))
                    title = match.group(2)
                    titles[index] = title
        
        # Playlist data'yı oluştur
        for index in sorted(files.keys()):
            entry = {
                'title': titles.get(index, f'İstasyon {index}'),
                'tvg_name': '',
                'tvg_logo': '',
                'group_title': 'Genel',
                'status': 'Kontrol Edilmedi',
                'url': files[index]
            }
            self.playlist_data.append(entry)
    
    def load_dpl_format(self, file_path):
        """DPL formatını yükle"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        files = {}
        titles = {}
        authors = {}
        
        for line in lines:
            line = line.strip()
            
            # 1*file*http://url formatı
            file_match = re.match(r'(\d+)\*file\*(.+)', line)
            if file_match:
                index = int(file_match.group(1))
                url = file_match.group(2)
                files[index] = url
            
            # 1*title*Station Name formatı
            title_match = re.match(r'(\d+)\*title\*(.+)', line)
            if title_match:
                index = int(title_match.group(1))
                title = title_match.group(2)
                titles[index] = title
            
            # 1*author*Group Name formatı
            author_match = re.match(r'(\d+)\*author\*(.+)', line)
            if author_match:
                index = int(author_match.group(1))
                author = author_match.group(2)
                authors[index] = author
        
        # Playlist data'yı oluştur
        for index in sorted(files.keys()):
            entry = {
                'title': titles.get(index, f'İstasyon {index}'),
                'tvg_name': '',
                'tvg_logo': '',
                'group_title': authors.get(index, 'Genel'),
                'status': 'Kontrol Edilmedi',
                'url': files[index]
            }
            self.playlist_data.append(entry)
    
    def parse_extinf_line(self, line):
        """EXTINF satırını parse et"""
        entry = {
            'title': '',
            'tvg_name': '',
            'tvg_logo': '',
            'group_title': '',
            'status': 'Kontrol Edilmedi'
        }
        
        # tvg-logo çıkar
        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        if logo_match:
            entry['tvg_logo'] = logo_match.group(1)
        
        # tvg-name çıkar
        name_match = re.search(r'tvg-name="([^"]*)"', line)
        if name_match:
            entry['tvg_name'] = name_match.group(1)
        
        # group-title çıkar
        group_match = re.search(r'group-title="([^"]*)"', line)
        if group_match:
            entry['group_title'] = group_match.group(1)
        
        # Title çıkar (virgülden sonraki kısım)
        title_match = re.search(r',(.+)$', line)
        if title_match:
            entry['title'] = title_match.group(1).strip()
        
        return entry
    
    def update_treeview(self):
        """Treeview'i güncelle"""
        # Mevcut verileri temizle
        for item in self.url_tree.get_children():
            self.url_tree.delete(item)
        
        # Yeni verileri ekle
        for i, entry in enumerate(self.playlist_data):
            values = (
                entry.get('status', ''),
                entry.get('title', ''),
                entry.get('tvg_name', ''),
                entry.get('tvg_logo', ''),
                entry.get('group_title', ''),
                entry.get('url', '')
            )
            
            # Alternatif satır rengi için tag
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            item = self.url_tree.insert('', 'end', values=values, tags=(tag,))
            
            # Durum rengini ayarla
            status = entry.get('status', '')
            if status == 'Çalışıyor':
                self.url_tree.set(item, 'status', '✓ Çalışıyor')
            elif status == 'Çalışmıyor':
                self.url_tree.set(item, 'status', '✗ Çalışmıyor')
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        total = len(self.playlist_data)
        working = len([x for x in self.playlist_data if x.get('status') == 'Çalışıyor'])
        not_working = len([x for x in self.playlist_data if x.get('status') == 'Çalışmıyor'])
        not_checked = len([x for x in self.playlist_data if x.get('status') == 'Kontrol Edilmedi'])
        
        # Kontrol edilenler (çalışan + çalışmayan)
        checked = working + not_working
        success_rate = (working/checked*100) if checked > 0 else 0
        
        stats_text = f"""İstatistikler:

Toplam İstasyon: {total}
Çalışan: {working}
Çalışmayan: {not_working}
Kontrol Edilmemiş: {not_checked}

Başarı Oranı: {success_rate:.1f}% (Kontrol edilenler arasında)"""
        
        # stats_text widget'ı varsa güncelle
        if hasattr(self, 'stats_text') and self.stats_text and self.stats_text.winfo_exists():
            try:
                self.stats_text.config(state='normal')
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, stats_text)
                self.stats_text.config(state='disabled')
            except tk.TclError:
                # Widget silinmişse sessizce geç
                pass
        
        # Status callback ile bilgi ver
        self.status_callback(f"İstatistikler: {total} toplam, {working} çalışan, {not_working} çalışmayan")
    
    def toggle_url_check(self):
        """URL kontrolünü başlat/iptal et"""
        if self.checking_urls:
            # İptal et
            self.checking_cancelled = True
            self.checking_urls = False
            self.check_button.config(text="URL'leri Kontrol Et", state='normal')
            self.status_callback("URL kontrolü iptal edildi")
        else:
            # Başlat
            if not self.playlist_data:
                messagebox.showwarning("Uyarı", "Önce bir m3u8 dosyası yükleyin!")
                return
            
            self.checking_urls = True
            self.checking_cancelled = False
            self.check_button.config(text="İptal Et", state='normal')
            
            # Thread'de kontrol et
            thread = threading.Thread(target=self._check_urls_thread)
            thread.daemon = True
            thread.start()
    
    def _check_urls_thread(self):
        """URL kontrol thread'i - Hibrit metod (HTTP + VLC)"""
        try:
            total = len(self.playlist_data)
            
            for i, entry in enumerate(self.playlist_data):
                if self.checking_cancelled or not self.checking_urls:  # İptal edildi mi?
                    break
                
                url = entry.get('url', '')
                station_name = entry.get('title', f'İstasyon {i+1}')
                
                # Progress güncelle
                progress = (i + 1) / total * 100
                self.progress_callback(f"Kontrol ediliyor ({i+1}/{total}): {station_name}", progress)
                
                # 1. Önce HTTP kontrolü yap (hızlı)
                http_status = self.check_single_url_http(url)
                
                if http_status == 'Çalışıyor':
                    # HTTP başarılı, VLC test gerek yok
                    entry['status'] = 'Çalışıyor'
                    self.status_callback(f"HTTP OK: {station_name}")
                else:
                    # HTTP başarısız, VLC ile ikinci test
                    if not self.checking_cancelled:
                        self.status_callback(f"HTTP başarısız, VLC test: {station_name}")
                        vlc_status = self.check_single_url_vlc(url)
                        entry['status'] = vlc_status
                        if vlc_status == 'Çalışıyor':
                            self.status_callback(f"VLC OK: {station_name}")
                        else:
                            self.status_callback(f"VLC başarısız: {station_name}")
                
                # UI'yi güncelle (main thread'de)
                if not self.checking_cancelled:
                    self.parent_frame.after(0, self.update_single_item, i, entry)
                
                # Kısa bekleme (iptal kontrolü için)
                if not self.checking_cancelled:
                    time.sleep(0.1)
            
            # Kontrol tamamlandı
            self.parent_frame.after(0, self._check_completed)
            
        except Exception as e:
            self.parent_frame.after(0, lambda: messagebox.showerror("Hata", f"URL kontrol hatası: {str(e)}"))
            self.parent_frame.after(0, self._check_completed)
    
    def check_single_url_http(self, url):
        """HTTP ile hızlı URL kontrolü"""
        try:
            # HTTP request timeout ile
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(request, timeout=5) as response:
                # HTTP status code kontrol et
                if response.getcode() == 200:
                    return 'Çalışıyor'
                else:
                    return 'Çalışmıyor'
                    
        except urllib.error.HTTPError as e:
            return 'Çalışmıyor'
        except urllib.error.URLError as e:
            return 'Çalışmıyor'
        except Exception as e:
            return 'Çalışmıyor'
    
    def check_single_url_vlc(self, url):
        """VLC ile detaylı URL kontrolü (HTTP başarısız olduğunda)"""
        try:
            # VLC kütüphanesi var mı kontrol et
            try:
                import vlc
            except ImportError:
                # VLC yoksa HTTP sonucunu kabul et
                return 'Çalışmıyor'
            
            # VLC instance oluştur
            vlc_instance = vlc.Instance('--intf', 'dummy', '--extraintf', 'dummy', '--quiet')
            player = vlc_instance.media_player_new()
            
            # Media oluştur
            media = vlc_instance.media_new(url)
            player.set_media(media)
            
            # Sessiz çal
            player.audio_set_volume(0)
            player.play()
            
            # 3 saniye bekle ve durumu kontrol et
            time.sleep(3)
            
            state = player.get_state()
            player.stop()
            
            # VLC durumuna göre karar ver
            if state in [vlc.State.Playing, vlc.State.Buffering]:
                return 'Çalışıyor'
            else:
                return 'Çalışmıyor'
                
        except Exception as e:
            return 'Çalışmıyor'
    
    def update_single_item(self, index, entry):
        """Tek bir item'ı güncelle"""
        try:
            # Tree widget'ının var olduğunu kontrol et
            if not hasattr(self, 'url_tree') or not self.url_tree or not self.url_tree.winfo_exists():
                return
                
            items = self.url_tree.get_children()
            if index < len(items):
                item = items[index]
                
                # Durum sütununu güncelle
                status = entry.get('status', '')
                if status == 'Çalışıyor':
                    self.url_tree.set(item, 'status', '✓ Çalışıyor')
                elif status == 'Çalışmıyor':
                    self.url_tree.set(item, 'status', '✗ Çalışmıyor')
                
                # İstatistikleri güncelle
                self.update_stats()
                
        except (tk.TclError, AttributeError):
            pass  # Widget silinmişse sessizce geç
        except Exception as e:
            pass  # Diğer hatalar için sessizce geç
    
    def _check_completed(self):
        """URL kontrolü tamamlandı"""
        self.checking_urls = False
        self.checking_cancelled = False
        self.check_button.config(text="URL'leri Kontrol Et", state='normal')
        self.update_stats()
        
        if self.checking_cancelled:
            self.status_callback("URL kontrolü iptal edildi")
        else:
            self.status_callback("URL kontrolü tamamlandı")
            # Çalışmayan URL'leri otomatik seç
            self.auto_select_failed_urls()
    
    def auto_select_failed_urls(self):
        """Çalışmayan URL'leri otomatik seç"""
        try:
            # Mevcut seçimleri temizle
            for item in self.url_tree.selection():
                self.url_tree.selection_remove(item)
            
            # Çalışmayan URL'leri seç
            failed_items = []
            for item in self.url_tree.get_children():
                values = self.url_tree.item(item)['values']
                if len(values) > 0 and '✗ Çalışmıyor' in str(values[0]):
                    failed_items.append(item)
                    self.url_tree.selection_add(item)
            
            if failed_items:
                self.status_callback(f"{len(failed_items)} çalışmayan URL otomatik seçildi")
                # İlk seçili öğeye odaklan
                self.url_tree.focus(failed_items[0])
                self.url_tree.see(failed_items[0])
            
        except Exception as e:
            pass  # Hata durumunda sessizce geç
    
    def delete_selected_urls(self):
        """Seçili URL'leri sil"""
        selection = self.url_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Silinecek URL'leri seçin!")
            return
        
        # Onay al
        if not messagebox.askyesno("Onay", f"{len(selection)} URL silinecek. Emin misiniz?"):
            return
        
        # Seçili indeksleri al
        indices_to_remove = []
        for item in selection:
            index = self.url_tree.index(item)
            indices_to_remove.append(index)
        
        # Büyükten küçüğe sırala (silme işlemi için)
        indices_to_remove.sort(reverse=True)
        
        # Playlist data'dan sil
        for index in indices_to_remove:
            if 0 <= index < len(self.playlist_data):
                del self.playlist_data[index]
        
        # Treeview'i güncelle
        self.update_treeview()
        self.update_stats()
        
        self.status_callback(f"{len(selection)} URL silindi")
    
    def save_cleaned_m3u8(self):
        """Temizlenmiş playlist dosyasını kaydet - çoklu format desteği"""
        if not self.playlist_data:
            messagebox.showwarning("Uyarı", "Kaydedilecek veri yok!")
            return
        
        # Son kullanılan klasörü al
        initial_dir = "."
        if self.db_manager:
            initial_dir = self.db_manager.get_last_directory("url_checker", "save")
        
        filename = filedialog.asksaveasfilename(
            title="Temizlenmiş Playlist Kaydet",
            initialdir=initial_dir,
            defaultextension=".m3u8",
            filetypes=[
                (".m3u8 files", "*.m3u8"), 
                (".m3u files", "*.m3u"), 
                (".pls files", "*.pls"),
                (".dpl files", "*.dpl"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        # Son kullanılan klasörü kaydet
        if self.db_manager:
            self.db_manager.set_last_directory("url_checker", "save", filename)
        
        try:
            # Dosya uzantısına göre format belirle
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in ['.m3u', '.m3u8']:
                self.save_as_m3u_format(filename)
            elif file_ext == '.pls':
                self.save_as_pls_format(filename)
            elif file_ext == '.dpl':
                self.save_as_dpl_format(filename)
            else:
                # Varsayılan olarak m3u8 formatında kaydet
                self.save_as_m3u_format(filename)
            
            self.status_callback(f"Temizlenmiş playlist kaydedildi: {filename}")
            messagebox.showinfo("Başarılı", f"Playlist başarıyla kaydedildi!\n\nFormat: {file_ext.upper()}\nToplam İstasyon: {len(self.playlist_data)}")
            
        except Exception as e:
            error_msg = f"Kaydetme hatası: {str(e)}"
            self.status_callback(error_msg)
            messagebox.showerror("Hata", error_msg)
    
    def save_as_m3u_format(self, filename):
        """M3U/M3U8 formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            
            for entry in self.playlist_data:
                # EXTINF satırını oluştur
                extinf_line = "#EXTINF:-1"
                
                if entry.get('tvg_logo'):
                    extinf_line += f' tvg-logo="{entry["tvg_logo"]}"'
                
                if entry.get('tvg_name'):
                    extinf_line += f' tvg-name="{entry["tvg_name"]}"'
                
                if entry.get('group_title'):
                    extinf_line += f' group-title="{entry["group_title"]}"'
                
                extinf_line += f',{entry.get("title", "")}'
                
                f.write(extinf_line + '\n')
                f.write(entry.get('url', '') + '\n')
    
    def save_as_pls_format(self, filename):
        """PLS formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("[playlist]\n")
            f.write(f"NumberOfEntries={len(self.playlist_data)}\n")
            
            for i, entry in enumerate(self.playlist_data, 1):
                f.write(f"File{i}={entry.get('url', '')}\n")
                f.write(f"Title{i}={entry.get('title', '')}\n")
    
    def save_as_dpl_format(self, filename):
        """DPL formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("DAUMPLAYLIST\n")
            
            # İlk URL'yi playname olarak ayarla
            if self.playlist_data:
                f.write(f"playname={self.playlist_data[0].get('url', '')}\n")
            
            f.write("topindex=0\n")
            f.write("saveplaypos=0\n")
            
            for i, entry in enumerate(self.playlist_data, 1):
                f.write(f"{i}*file*{entry.get('url', '')}\n")
                f.write(f"{i}*title*{entry.get('title', '')}\n")
                f.write(f"{i}*author*{entry.get('group_title', 'Genel')}\n")
    
    def on_delete_key(self, event):
        """Delete tuşuna basıldığında seçili URL'leri sil"""
        self.delete_selected_urls()
    
    def sort_treeview(self, tree, col, reverse):
        """Treeview sütunlarını sırala"""
        try:
            data = [(tree.set(child, col), child) for child in tree.get_children('')]
            data.sort(reverse=reverse)
            
            for index, (val, child) in enumerate(data):
                tree.move(child, '', index)
            
            # Başlığı güncelle (sıralama yönünü göster)
            tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))
            
        except Exception as e:
            pass  # Sıralama hatası durumunda sessizce geç