#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
from pathlib import Path
from drag_drop_helper import DragDropListbox

class PlaylistMergerModule:
    def __init__(self, parent_frame, status_callback=None, progress_callback=None, db_manager=None):
        self.parent_frame = parent_frame
        self.status_callback = status_callback or (lambda x: None)
        self.progress_callback = progress_callback or (lambda x: None)
        self.db_manager = db_manager
        
        # Playlist Merger için değişkenler
        self.selected_files = []
        self.merged_data = []
        self.drag_drop_handler = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Ana frame
        merger_main = ttk.Frame(self.parent_frame, padding="10")
        merger_main.pack(fill='both', expand=True)
        
        # Başlık
        title_label = ttk.Label(merger_main, text="Playlist Merger", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sol panel (Kontrol paneli)
        left_panel = ttk.LabelFrame(merger_main, text="Kontrol Paneli", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Dosya seçimi
        ttk.Label(left_panel, text="Playlist Dosyaları:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(left_panel)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_frame, text="Dosya Ekle", command=self.add_files).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(file_frame, text="Temizle", command=self.clear_files).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(file_frame, text="Birleştir", command=self.merge_playlists).grid(row=0, column=2, padx=(0, 5))
        
        # Debug butonu
        debug_frame = ttk.Frame(left_panel)
        debug_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(debug_frame, text="Dosya İçeriğini Göster", 
                  command=self.show_file_content).grid(row=0, column=0, padx=(0, 5))
        
        # Seçili dosyalar listesi
        files_frame = ttk.LabelFrame(left_panel, text="Seçili Dosyalar", padding="5")
        files_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Listbox ile scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.files_listbox = tk.Listbox(list_frame, height=8, font=('Arial', 9))
        self.files_listbox.pack(side='left', fill='both', expand=True)
        
        files_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.pack(side='right', fill='y')
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        # Seçili dosyayı kaldırma
        ttk.Button(files_frame, text="Seçili Dosyayı Kaldır", 
                  command=self.remove_selected_file).pack(pady=(5, 0))
        
        # Sürükle-bırak özelliği ekle (başlangıçta boş liste ile)
        self.drag_drop_handler = None
        
        # Sürükle-bırak ipucu etiketi ekle
        drag_info_label = ttk.Label(files_frame, 
                                   text="💡 Dosyaları sürükleyerek sıralayabilirsiniz (mavi alan hedef konumu gösterir)", 
                                   font=('Arial', 8), 
                                   foreground='blue')
        drag_info_label.pack(pady=(2, 0))
        
        # Kaydetme seçenekleri
        save_frame = ttk.LabelFrame(left_panel, text="Kaydetme", padding="5")
        save_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(save_frame, text="Playlist Kaydet", 
                  command=self.save_merged_playlist).pack(fill='x')
        
        # Sağ panel (Önizleme)
        right_panel = ttk.LabelFrame(merger_main, text="Birleştirilmiş Playlist Önizlemesi", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Treeview için frame
        tree_frame = ttk.Frame(right_panel)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('source', 'name', 'url', 'group')
        self.merger_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15, style="Custom.Treeview")
        
        # Alternatif satır renkleri için tag'ler
        self.merger_tree.tag_configure('oddrow', background='#f8f8f8', foreground='black')
        self.merger_tree.tag_configure('evenrow', background='white', foreground='black')
        
        # Sütun başlıkları ve sıralama
        self.merger_tree.heading('source', text='Kaynak Dosya', command=lambda: self.sort_treeview(self.merger_tree, 'source', False))
        self.merger_tree.heading('name', text='İstasyon Adı', command=lambda: self.sort_treeview(self.merger_tree, 'name', False))
        self.merger_tree.heading('url', text='Stream URL', command=lambda: self.sort_treeview(self.merger_tree, 'url', False))
        self.merger_tree.heading('group', text='Grup', command=lambda: self.sort_treeview(self.merger_tree, 'group', False))
        
        # Sütun genişlikleri
        self.merger_tree.column('source', width=120, minwidth=80)
        self.merger_tree.column('name', width=200, minwidth=150)
        self.merger_tree.column('url', width=250, minwidth=200)
        self.merger_tree.column('group', width=100, minwidth=70)
        
        self.merger_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.merger_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.merger_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.merger_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.merger_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Grid weights
        merger_main.columnconfigure(0, weight=0)  # Sol panel sabit genişlik
        merger_main.columnconfigure(1, weight=1)  # Sağ panel genişleyebilir
        merger_main.rowconfigure(1, weight=1)     # Ana içerik genişleyebilir
        left_panel.columnconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        left_panel.rowconfigure(3, weight=1)      # Dosya listesi genişleyebilir
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def add_files(self):
        """Playlist dosyalarını ekle"""
        # Son kullanılan klasörü al
        initial_dir = "."
        if self.db_manager:
            initial_dir = self.db_manager.get_last_directory("playlist_merger", "open")
        
        filetypes = [
            ("Playlist files", "*.m3u *.m3u8"),
            ("M3U files", "*.m3u"),
            ("m3u8 files", "*.m3u8"),
            ("All files", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="Playlist Dosyalarını Seçin",
            initialdir=initial_dir,
            filetypes=filetypes
        )
        
        if not filenames:
            return
        
        # Son kullanılan klasörü kaydet (ilk dosyadan)
        if filenames and self.db_manager:
            self.db_manager.set_last_directory("playlist_merger", "open", filenames[0])
        
        added_count = 0
        for filename in filenames:
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                # Sadece dosya adını göster
                display_name = Path(filename).name
                self.files_listbox.insert(tk.END, display_name)
                added_count += 1
        
        # Sürükle-bırak handler'ı oluştur/güncelle
        if self.selected_files and not self.drag_drop_handler:
            from drag_drop_helper import DragDropListbox
            self.drag_drop_handler = DragDropListbox(
                self.files_listbox, 
                self.selected_files, 
                self.on_files_reordered
            )
        
        if added_count > 0:
            self.status_callback(f"{added_count} dosya eklendi")
        else:
            self.status_callback("Seçilen dosyalar zaten listede")
    
    def clear_files(self):
        """Dosya listesini temizle"""
        self.selected_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.merged_data.clear()
        self.update_preview()
        self.status_callback("Dosya listesi temizlendi")
    
    def remove_selected_file(self):
        """Seçili dosyayı listeden kaldır"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Kaldırılacak dosyayı seçin!")
            return
        
        index = selection[0]
        self.files_listbox.delete(index)
        self.selected_files.pop(index)
        
        # Önizlemeyi güncelle
        self.merge_playlists()
        self.status_callback("Dosya kaldırıldı")
    
    def merge_playlists(self):
        """Playlist'leri birleştir"""
        if not self.selected_files:
            messagebox.showwarning("Uyarı", "Birleştirilecek dosya seçin!")
            return
        
        self.merged_data.clear()
        total_stations = 0
        successful_files = 0
        
        try:
            for file_path in self.selected_files:
                file_name = Path(file_path).name
                self.status_callback(f"İşleniyor: {file_name}")
                
                stations = self.parse_playlist_file(file_path)
                
                if stations:
                    successful_files += 1
                    for station in stations:
                        # Kaynak dosya bilgisini ekle
                        station['source'] = file_name
                        self.merged_data.append(station)
                        total_stations += 1
                else:
                    self.status_callback(f"Uyarı: {file_name} dosyasında istasyon bulunamadı")
            
            # Önizlemeyi güncelle
            self.update_preview()
            
            if total_stations > 0:
                self.status_callback(f"Birleştirme tamamlandı: {total_stations} istasyon, {successful_files}/{len(self.selected_files)} dosya başarılı")
                messagebox.showinfo("Başarılı", 
                    f"Birleştirme tamamlandı!\n\n"
                    f"Toplam İstasyon: {total_stations}\n"
                    f"Başarılı Dosya: {successful_files}/{len(self.selected_files)}")
            else:
                messagebox.showwarning("Uyarı", "Hiçbir dosyada geçerli istasyon bulunamadı!")
            
        except Exception as e:
            error_msg = f"Birleştirme hatası: {str(e)}"
            self.status_callback(error_msg)
            messagebox.showerror("Hata", error_msg)
    
    def parse_playlist_file(self, file_path):
        """Playlist dosyasını parse et - geliştirilmiş algoritma"""
        stations = []
        
        try:
            # Farklı encoding'leri dene
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise Exception(f"Dosya okunamadı: {file_path}")
            
            # Satırlara böl - farklı line ending'leri destekle
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            self.status_callback(f"Parse ediliyor: {len(lines)} satır bulundu")
            
            i = 0
            parsed_count = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # EXTINF satırını bul
                if line.startswith('#EXTINF:'):
                    station = {}
                    
                    try:
                        # Logo URL'sini çıkar
                        logo_match = re.search(r'tvg-logo="([^"]*)"', line, re.IGNORECASE)
                        if logo_match:
                            station['logo'] = logo_match.group(1)
                        
                        # TVG name'i çıkar
                        tvg_name_match = re.search(r'tvg-name="([^"]*)"', line, re.IGNORECASE)
                        if tvg_name_match:
                            station['tvg_name'] = tvg_name_match.group(1)
                        
                        # Grup başlığını çıkar
                        group_match = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
                        if group_match:
                            station['group'] = group_match.group(1)
                        else:
                            station['group'] = 'Genel'
                        
                        # İstasyon adını çıkar (virgülden sonraki kısım)
                        name_match = re.search(r',(.+)$', line)
                        if name_match:
                            station['name'] = name_match.group(1).strip()
                        else:
                            station['name'] = 'Bilinmeyen İstasyon'
                        
                        # Sonraki satırlarda URL'yi ara
                        url_found = False
                        j = i + 1
                        while j < len(lines) and j < i + 5:  # En fazla 5 satır ileriye bak
                            next_line = lines[j].strip()
                            if next_line and not next_line.startswith('#'):
                                # URL gibi görünüyor mu kontrol et
                                if (next_line.startswith('http') or 
                                    next_line.startswith('rtmp') or 
                                    next_line.startswith('mms') or
                                    '://' in next_line):
                                    station['url'] = next_line
                                    stations.append(station)
                                    parsed_count += 1
                                    url_found = True
                                    i = j  # URL satırına kadar atla
                                    break
                            j += 1
                        
                        if not url_found:
                            # URL bulunamadı ama yine de ekle (boş URL ile)
                            station['url'] = ''
                            stations.append(station)
                            parsed_count += 1
                    
                    except Exception as parse_error:
                        # Bu satırda hata oldu, devam et
                        self.status_callback(f"Satır parse hatası: {str(parse_error)}")
                
                i += 1
            
            self.status_callback(f"Parse tamamlandı: {parsed_count} istasyon bulundu")
            return stations
            
        except Exception as e:
            error_msg = f"Dosya parse hatası ({Path(file_path).name}): {str(e)}"
            self.status_callback(error_msg)
            return []
    
    def update_preview(self):
        """Önizleme tablosunu güncelle"""
        # Mevcut verileri temizle
        for item in self.merger_tree.get_children():
            self.merger_tree.delete(item)
        
        # Yeni verileri ekle
        for i, station in enumerate(self.merged_data):
            values = (
                station.get('source', ''),
                station.get('name', ''),
                station.get('url', ''),
                station.get('group', '')
            )
            
            # Alternatif satır rengi için tag
            tags = ['evenrow'] if i % 2 == 0 else ['oddrow']
            self.merger_tree.insert('', 'end', values=values, tags=tags)
    
    def save_merged_playlist(self):
        """Birleştirilmiş playlist'i kaydet - çoklu format desteği"""
        if not self.merged_data:
            messagebox.showwarning("Uyarı", "Kaydedilecek veri yok! Önce playlist'leri birleştirin.")
            return
        
        # Son kullanılan klasörü al
        initial_dir = "."
        if self.db_manager:
            initial_dir = self.db_manager.get_last_directory("playlist_merger", "save")
        
        filename = filedialog.asksaveasfilename(
            title="Playlist Kaydet",
            initialdir=initial_dir,
            defaultextension=".m3u8",
            filetypes=[
                ("m3u8 files", "*.m3u8"), 
                ("M3U files", "*.m3u"), 
                ("PLS files", "*.pls"),
                ("DPL files", "*.dpl"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        # Son kullanılan klasörü kaydet
        if self.db_manager:
            self.db_manager.set_last_directory("playlist_merger", "save", filename)
        
        try:
            # Dosya uzantısına göre format belirle
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in ['.m3u', '.m3u8']:
                self.save_as_m3u(filename)
            elif file_ext == '.pls':
                self.save_as_pls(filename)
            elif file_ext == '.dpl':
                self.save_as_dpl(filename)
            else:
                # Varsayılan olarak m3u8 formatında kaydet
                self.save_as_m3u(filename)
            
            self.status_callback(f"Playlist kaydedildi: {filename}")
            messagebox.showinfo("Başarılı", f"Playlist başarıyla kaydedildi!\n\nFormat: {file_ext.upper()}\nToplam İstasyon: {len(self.merged_data)}")
            
        except Exception as e:
            error_msg = f"Kaydetme hatası: {str(e)}"
            self.status_callback(error_msg)
            messagebox.showerror("Hata", error_msg)
    
    def save_as_m3u(self, filename):
        """M3U/M3U8 formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            
            for station in self.merged_data:
                # EXTINF satırını oluştur
                extinf_line = "#EXTINF:-1"
                
                if station.get('logo'):
                    extinf_line += f' tvg-logo="{station["logo"]}"'
                
                if station.get('tvg_name'):
                    extinf_line += f' tvg-name="{station["tvg_name"]}"'
                
                if station.get('group'):
                    extinf_line += f' group-title="{station["group"]}"'
                
                extinf_line += f',{station.get("name", "")}'
                
                f.write(extinf_line + '\n')
                f.write(station.get('url', '') + '\n')
    
    def save_as_pls(self, filename):
        """PLS formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("[playlist]\n")
            f.write(f"NumberOfEntries={len(self.merged_data)}\n")
            
            for i, station in enumerate(self.merged_data, 1):
                f.write(f"File{i}={station.get('url', '')}\n")
                f.write(f"Title{i}={station.get('name', '')}\n")
    
    def save_as_dpl(self, filename):
        """DPL (Daum PotPlayer) formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("DAUMPLAYLIST\n")
            
            # İlk URL'yi playname olarak ayarla
            if self.merged_data:
                f.write(f"playname={self.merged_data[0].get('url', '')}\n")
            
            f.write("topindex=0\n")
            f.write("saveplaypos=0\n")
            
            for i, station in enumerate(self.merged_data, 1):
                f.write(f"{i}*file*{station.get('url', '')}\n")
                f.write(f"{i}*title*{station.get('name', '')}\n")
                
                # Grup bilgisini author olarak ekle
                if station.get('group'):
                    f.write(f"{i}*author*{station.get('group', '')}\n")
    
    def sort_treeview(self, tree, col, reverse):
        """Treeview sütununu sırala"""
        try:
            # Mevcut verileri al
            data = [(tree.set(child, col), child) for child in tree.get_children('')]
            
            # Sırala
            data.sort(reverse=reverse)
            
            # Sıralanmış verileri yeniden yerleştir
            for index, (val, child) in enumerate(data):
                tree.move(child, '', index)
                
                # Zebra stripes için tag'leri yeniden ayarla
                tags = ['evenrow'] if index % 2 == 0 else ['oddrow']
                tree.item(child, tags=tags)
            
            # Başlığı güncelle (sıralama yönünü göster)
            tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))
            
        except Exception as e:
            self.status_callback(f"Sıralama hatası: {str(e)}")
    
    def show_file_content(self):
        """Debug: Seçili dosyanın içeriğini göster"""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "İncelenecek dosyayı seçin!")
            return
        
        index = selection[0]
        file_path = self.selected_files[index]
        file_name = Path(file_path).name
        
        try:
            # Dosya içeriğini oku
            content = None
            encoding_used = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    encoding_used = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                messagebox.showerror("Hata", "Dosya okunamadı!")
                return
            
            # Satır sayısını hesapla
            lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            line_count = len([line for line in lines if line.strip()])
            extinf_count = len([line for line in lines if line.strip().startswith('#EXTINF:')])
            
            # Debug penceresi oluştur
            debug_window = tk.Toplevel()
            debug_window.title(f"Dosya İçeriği: {file_name}")
            debug_window.geometry("800x600")
            
            # Bilgi paneli
            info_frame = tk.Frame(debug_window)
            info_frame.pack(fill='x', padx=10, pady=5)
            
            info_text = f"Dosya: {file_name}\nEncoding: {encoding_used}\nToplam Satır: {len(lines)}\nDolu Satır: {line_count}\nEXTINF Satırları: {extinf_count}"
            tk.Label(info_frame, text=info_text, justify='left', font=('Arial', 9)).pack(anchor='w')
            
            # İçerik alanı
            text_frame = tk.Frame(debug_window)
            text_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            text_widget = tk.Text(text_frame, wrap='none', font=('Consolas', 9))
            text_widget.pack(side='left', fill='both', expand=True)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            scrollbar.pack(side='right', fill='y')
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # İçeriği göster
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')
            
            # Parse test butonu
            button_frame = tk.Frame(debug_window)
            button_frame.pack(fill='x', padx=10, pady=5)
            
            def test_parse():
                stations = self.parse_playlist_file(file_path)
                result = f"Parse Sonucu: {len(stations)} istasyon bulundu\n\n"
                for i, station in enumerate(stations[:10]):  # İlk 10'unu göster
                    result += f"{i+1}. {station.get('name', 'N/A')} - {station.get('url', 'N/A')}\n"
                if len(stations) > 10:
                    result += f"... ve {len(stations)-10} tane daha"
                
                messagebox.showinfo("Parse Test Sonucu", result)
            
            tk.Button(button_frame, text="Parse Testi Yap", command=test_parse).pack(side='left')
            
        except Exception as e:
            messagebox.showerror("Hata", f"Debug hatası: {str(e)}")
    
    def on_files_reordered(self):
        """Dosya sırası değiştiğinde çağrılır"""
        # Eğer birleştirilmiş veri varsa, yeniden birleştir
        if self.merged_data:
            self.merge_playlists()
        
        self.status_callback("Dosya sırası değiştirildi")