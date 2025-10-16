#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os
from pathlib import Path
from drag_drop_helper import DragDropTreeview

class PlaylistEditorModule:
    def __init__(self, parent_frame, status_callback=None, progress_callback=None, db_manager=None):
        self.parent_frame = parent_frame
        self.status_callback = status_callback or (lambda x: None)
        self.progress_callback = progress_callback or (lambda x: None)
        self.db_manager = db_manager
        
        # Playlist Editor için değişkenler
        self.editor_data = []
        self.drag_drop_handler = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Ana frame
        editor_main = ttk.Frame(self.parent_frame, padding="10")
        editor_main.pack(fill='both', expand=True)
        
        # Başlık
        title_label = ttk.Label(editor_main, text="Playlist Editor", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sol panel (Kontrol paneli - kompakt)
        left_panel = ttk.LabelFrame(editor_main, text="Kontrol Paneli", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Dosya işlemleri
        ttk.Label(left_panel, text="Playlist Dosyası:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(left_panel)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.editor_file_path = tk.StringVar()
        self.editor_file_entry = ttk.Entry(file_frame, textvariable=self.editor_file_path, width=20)
        self.editor_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Aç", command=self.load_editor_file).grid(row=0, column=1, padx=(2, 0))
        
        # Düzenleme butonları (sadece temel işlemler)
        edit_frame = ttk.LabelFrame(left_panel, text="Düzenleme", padding="5")
        edit_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(edit_frame, text="Yeni Ekle", command=self.add_new_station).grid(row=0, column=0, pady=2, padx=(0, 2), sticky=(tk.W, tk.E))
        ttk.Button(edit_frame, text="Sil", command=self.delete_selected_station).grid(row=0, column=1, pady=2, padx=(2, 0), sticky=(tk.W, tk.E))
        ttk.Button(edit_frame, text="Kaydet", command=self.save_editor_file).grid(row=1, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        # Sağ panel (Detay düzenleme)
        right_panel = ttk.LabelFrame(editor_main, text="İstasyon Detayları", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Detay form alanları
        ttk.Label(right_panel, text="İstasyon Adı:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.detail_name = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.detail_name, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(right_panel, text="Stream URL:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.detail_url = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.detail_url, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(right_panel, text="Logo URL:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.detail_logo = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.detail_logo, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(right_panel, text="Grup:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.detail_group = tk.StringVar()
        self.group_combo = ttk.Combobox(right_panel, textvariable=self.detail_group, width=47)
        self.group_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Combobox'a değer değişiklik olayını bağla
        self.group_combo.bind('<FocusOut>', self.on_group_changed)
        self.group_combo.bind('<Return>', self.on_group_changed)
        
        # Grup listesini yükle
        self.load_group_list()
        
        ttk.Label(right_panel, text="TVG Name:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.detail_tvg_name = tk.StringVar()
        ttk.Entry(right_panel, textvariable=self.detail_tvg_name, width=50).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Güncelleme butonları
        button_frame = ttk.Frame(right_panel)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Değişiklikleri Uygula", command=self.apply_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Temizle", command=self.clear_details).pack(side=tk.LEFT, padx=2)
        
        # Alt kısım - Treeview
        tree_frame = ttk.Frame(editor_main)
        tree_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Treeview
        columns = ('name', 'url', 'logo', 'group', 'tvg_name')
        self.editor_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10, style="Custom.Treeview")
        
        # Alternatif satır renkleri için tag'ler
        self.editor_tree.tag_configure('oddrow', background='#f9f9f9')
        self.editor_tree.tag_configure('evenrow', background='white')
        
        # Sütun başlıkları ve sıralama
        self.editor_tree.heading('name', text='İstasyon Adı', command=lambda: self.sort_treeview(self.editor_tree, 'name', False))
        self.editor_tree.heading('url', text='Stream URL', command=lambda: self.sort_treeview(self.editor_tree, 'url', False))
        self.editor_tree.heading('logo', text='Logo URL', command=lambda: self.sort_treeview(self.editor_tree, 'logo', False))
        self.editor_tree.heading('group', text='Grup', command=lambda: self.sort_treeview(self.editor_tree, 'group', False))
        self.editor_tree.heading('tvg_name', text='TVG Name', command=lambda: self.sort_treeview(self.editor_tree, 'tvg_name', False))
        
        # Sütun genişlikleri
        self.editor_tree.column('name', width=200, minwidth=150)
        self.editor_tree.column('url', width=300, minwidth=200)
        self.editor_tree.column('logo', width=150, minwidth=100)
        self.editor_tree.column('group', width=100, minwidth=70)
        self.editor_tree.column('tvg_name', width=120, minwidth=80)
        
        self.editor_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Seçim olayı
        self.editor_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Çift tık ile çalma özelliği
        self.editor_tree.bind('<Double-1>', self.on_station_double_click)
        
        # Sürükle-bırak özelliği ekle (başlangıçta boş liste ile)
        self.drag_drop_handler = None
        
        # Sürükle-bırak ipucu etiketi ekle
        drag_info_label = ttk.Label(tree_frame, 
                                   text="💡 İpucu: Satırları sürükleyerek sıralayabilirsiniz (mavi alan hedef konumu gösterir)", 
                                   font=('Arial', 8), 
                                   foreground='blue')
        drag_info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.editor_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.editor_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.editor_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.editor_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Grid weights - İstasyon Detayları genişletildi, Kontrol Paneli daraltıldı
        editor_main.columnconfigure(0, weight=1)  # Sol panel (Kontrol Paneli) daraltıldı
        editor_main.columnconfigure(1, weight=3)  # Sağ panel (İstasyon Detayları) genişletildi
        editor_main.rowconfigure(1, weight=0)     # Üst paneller küçük (sabit boyut)
        editor_main.rowconfigure(3, weight=1)     # Tablo büyük (genişleyebilir)
        
        # Sol panel içindeki widget'ların genişlemesi için
        left_panel.columnconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        
        file_frame.columnconfigure(0, weight=1)
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.columnconfigure(1, weight=1)
        right_panel.columnconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def load_editor_file(self):
        """Editor için playlist dosyası yükle"""
        # Son kullanılan klasörü al
        initial_dir = "."
        if self.db_manager:
            initial_dir = self.db_manager.get_last_directory("playlist_editor", "open")
        
        filename = filedialog.askopenfilename(
            title="Playlist Dosyası Seç",
            initialdir=initial_dir,
            filetypes=[
                ("Playlist files", "*.m3u;*.m3u8;*.pls;*.dpl"),
                ("M3U files", "*.m3u;*.m3u8"),
                ("PLS files", "*.pls"),
                ("DPL files", "*.dpl"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Son kullanılan klasörü kaydet
            if self.db_manager:
                self.db_manager.set_last_directory("playlist_editor", "open", filename)
            
            self.editor_file_path.set(filename)
            self.parse_playlist_for_editor(filename)
    
    def parse_playlist_for_editor(self, file_path):
        """Playlist dosyasını editor için parse et - çoklu format desteği"""
        try:
            self.editor_data = []
            
            # Dosya uzantısına göre format belirle
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.m3u', '.m3u8']:
                self.parse_m3u_for_editor(file_path)
            elif file_ext == '.pls':
                self.parse_pls_for_editor(file_path)
            elif file_ext == '.dpl':
                self.parse_dpl_for_editor(file_path)
            else:
                # Varsayılan olarak M3U formatı dene
                self.parse_m3u_for_editor(file_path)
            
            # Treeview'i güncelle
            self.update_editor_treeview()
            
            self.status_callback(f"Editor için playlist yüklendi: {len(self.editor_data)} istasyon ({file_ext.upper()})")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Playlist dosyası yüklenirken hata: {str(e)}")
    
    def parse_m3u_for_editor(self, file_path):
        """M3U/M3U8 formatını editor için parse et"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # EXTINF satırını parse et
                current_entry = self.parse_extinf_for_editor(line)
            elif line and not line.startswith('#'):
                # URL satırı
                if current_entry:
                    current_entry['url'] = line
                    self.editor_data.append(current_entry.copy())
                    current_entry = {}
    
    def parse_pls_for_editor(self, file_path):
        """PLS formatını editor için parse et"""
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
        
        # Editor data'yı oluştur
        for index in sorted(files.keys()):
            entry = {
                'title': titles.get(index, f'İstasyon {index}'),
                'tvg_name': '',
                'tvg_logo': '',
                'group_title': 'Genel',
                'url': files[index]
            }
            self.editor_data.append(entry)
    
    def parse_dpl_for_editor(self, file_path):
        """DPL formatını editor için parse et"""
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
        
        # Editor data'yı oluştur
        for index in sorted(files.keys()):
            entry = {
                'title': titles.get(index, f'İstasyon {index}'),
                'tvg_name': '',
                'tvg_logo': '',
                'group_title': authors.get(index, 'Genel'),
                'url': files[index]
            }
            self.editor_data.append(entry)
    
    def parse_extinf_for_editor(self, line):
        """EXTINF satırını editor için parse et"""
        entry = {
            'name': '',
            'url': '',
            'logo': '',
            'group': '',
            'tvg_name': ''
        }
        
        # tvg-logo çıkar
        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        if logo_match:
            entry['logo'] = logo_match.group(1)
        
        # tvg-name çıkar
        name_match = re.search(r'tvg-name="([^"]*)"', line)
        if name_match:
            entry['tvg_name'] = name_match.group(1)
        
        # group-title çıkar
        group_match = re.search(r'group-title="([^"]*)"', line)
        if group_match:
            entry['group'] = group_match.group(1)
        
        # Title çıkar (virgülden sonraki kısım)
        title_match = re.search(r',(.+)$', line)
        if title_match:
            entry['name'] = title_match.group(1).strip()
        
        return entry
    
    def update_editor_treeview(self):
        """Editor treeview'ini güncelle"""
        # Mevcut verileri temizle
        for item in self.editor_tree.get_children():
            self.editor_tree.delete(item)
        
        # Yeni verileri ekle
        for i, entry in enumerate(self.editor_data):
            values = (
                entry.get('name', ''),
                entry.get('url', ''),
                entry.get('logo', ''),
                entry.get('group', ''),
                entry.get('tvg_name', '')
            )
            # Alternatif satır rengi için tag
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.editor_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Sürükle-bırak handler'ı güncelle
        if self.editor_data and not self.drag_drop_handler:
            from drag_drop_helper import DragDropTreeview
            self.drag_drop_handler = DragDropTreeview(
                self.editor_tree, 
                self.editor_data, 
                self.update_editor_treeview
            )
        
        # Zebra stripe renklerini yeniden uygula
        self.apply_zebra_stripes()
    
    def on_tree_select(self, event):
        """Treeview seçim olayı"""
        selection = self.editor_tree.selection()
        if selection:
            item = selection[0]
            index = self.editor_tree.index(item)
            
            if 0 <= index < len(self.editor_data):
                entry = self.editor_data[index]
                
                # Detay alanlarını doldur
                self.detail_name.set(entry.get('name', ''))
                self.detail_url.set(entry.get('url', ''))
                self.detail_logo.set(entry.get('logo', ''))
                self.detail_group.set(entry.get('group', ''))
                self.detail_tvg_name.set(entry.get('tvg_name', ''))
    
    def add_new_station(self):
        """Yeni istasyon ekle"""
        # Boş bir istasyon ekle
        new_station = {
            'name': 'Yeni İstasyon',
            'url': 'http://',
            'logo': '',
            'group': 'Genel',
            'tvg_name': ''
        }
        
        self.editor_data.append(new_station)
        self.update_editor_treeview()
        
        # Yeni eklenen istasyonu seç
        children = self.editor_tree.get_children()
        if children:
            last_item = children[-1]
            self.editor_tree.selection_set(last_item)
            self.editor_tree.focus(last_item)
            self.on_tree_select(None)
        
        self.status_callback("Yeni istasyon eklendi")
    

    
    def delete_selected_station(self):
        """Seçili istasyonu sil"""
        selection = self.editor_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Silinecek istasyonu seçin!")
            return
        
        item = selection[0]
        index = self.editor_tree.index(item)
        
        if 0 <= index < len(self.editor_data):
            station_name = self.editor_data[index].get('name', 'Bilinmeyen')
            
            if messagebox.askyesno("Onay", f"'{station_name}' istasyonu silinecek. Emin misiniz?"):
                del self.editor_data[index]
                self.update_editor_treeview()
                self.clear_details()
                self.status_callback(f"İstasyon silindi: {station_name}")
    

    
    def apply_changes(self):
        """Değişiklikleri uygula"""
        selection = self.editor_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Güncellenecek istasyonu seçin!")
            return
        
        item = selection[0]
        index = self.editor_tree.index(item)
        
        if 0 <= index < len(self.editor_data):
            # Detay alanlarındaki bilgileri al
            self.editor_data[index]['name'] = self.detail_name.get()
            self.editor_data[index]['url'] = self.detail_url.get()
            self.editor_data[index]['logo'] = self.detail_logo.get()
            self.editor_data[index]['group'] = self.detail_group.get()
            self.editor_data[index]['tvg_name'] = self.detail_tvg_name.get()
            
            # Treeview'i güncelle
            self.update_editor_treeview()
            
            # Aynı istasyonu tekrar seç
            children = self.editor_tree.get_children()
            if index < len(children):
                new_item = children[index]
                self.editor_tree.selection_set(new_item)
                self.editor_tree.focus(new_item)
            
            self.status_callback("İstasyon bilgileri güncellendi")
    
    def clear_details(self):
        """Detay alanlarını temizle"""
        self.detail_name.set('')
        self.detail_url.set('')
        self.detail_logo.set('')
        self.detail_group.set('')
        self.detail_tvg_name.set('')
    
    def save_editor_file(self):
        """Düzenlenmiş playlist dosyasını kaydet - çoklu format desteği"""
        if not self.editor_data:
            messagebox.showwarning("Uyarı", "Kaydedilecek veri yok!")
            return
        
        # Son kullanılan klasörü al
        initial_dir = "."
        if self.db_manager:
            initial_dir = self.db_manager.get_last_directory("playlist_editor", "save")
        
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
            self.db_manager.set_last_directory("playlist_editor", "save", filename)
        
        try:
            # Dosya uzantısına göre format belirle
            file_ext = Path(filename).suffix.lower()
            
            if file_ext in ['.m3u', '.m3u8']:
                self.save_as_m3u_editor(filename)
            elif file_ext == '.pls':
                self.save_as_pls_editor(filename)
            elif file_ext == '.dpl':
                self.save_as_dpl_editor(filename)
            else:
                # Varsayılan olarak m3u8 formatında kaydet
                self.save_as_m3u_editor(filename)
            
            self.status_callback(f"Playlist kaydedildi: {filename}")
            messagebox.showinfo("Başarılı", f"Playlist başarıyla kaydedildi!\n\nFormat: {file_ext.upper()}\nToplam İstasyon: {len(self.editor_data)}")
            
        except Exception as e:
            error_msg = f"Kaydetme hatası: {str(e)}"
            self.status_callback(error_msg)
            messagebox.showerror("Hata", error_msg)
    
    def save_as_m3u_editor(self, filename):
        """M3U/M3U8 formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            
            for entry in self.editor_data:
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
    
    def save_as_pls_editor(self, filename):
        """PLS formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("[playlist]\n")
            f.write(f"NumberOfEntries={len(self.editor_data)}\n")
            
            for i, entry in enumerate(self.editor_data, 1):
                f.write(f"File{i}={entry.get('url', '')}\n")
                f.write(f"Title{i}={entry.get('title', '')}\n")
    
    def save_as_dpl_editor(self, filename):
        """DPL formatında kaydet"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("DAUMPLAYLIST\n")
            
            # İlk URL'yi playname olarak ayarla
            if self.editor_data:
                f.write(f"playname={self.editor_data[0].get('url', '')}\n")
            
            f.write("topindex=0\n")
            f.write("saveplaypos=0\n")
            
            for i, entry in enumerate(self.editor_data, 1):
                f.write(f"{i}*file*{entry.get('url', '')}\n")
                f.write(f"{i}*title*{entry.get('title', '')}\n")
                f.write(f"{i}*author*{entry.get('group_title', 'Genel')}\n")
    
    def load_group_list(self):
        """Grup listesini veritabanından yükle"""
        if not self.db_manager:
            return
        
        try:
            # Veritabanından grupları al
            groups_str = self.db_manager.get_setting('playlist_groups', '')
            if groups_str:
                groups = groups_str.split('|')
                self.group_combo['values'] = sorted(set(groups))
            else:
                # Varsayılan gruplar
                default_groups = ['Genel', 'Müzik', 'Haber', 'Spor', 'Türkiye', 'Dünya']
                self.group_combo['values'] = default_groups
                self.save_group_list(default_groups)
        except Exception as e:
            # Hata durumunda varsayılan gruplar
            self.group_combo['values'] = ['Genel', 'Müzik', 'Haber', 'Spor']
    
    def save_group_list(self, groups):
        """Grup listesini veritabanına kaydet"""
        if not self.db_manager:
            return
        
        try:
            # Boş ve tekrar eden grupları temizle
            clean_groups = list(set([g.strip() for g in groups if g.strip()]))
            groups_str = '|'.join(clean_groups)
            self.db_manager.set_setting('playlist_groups', groups_str)
        except Exception as e:
            pass
    
    def on_group_changed(self, event=None):
        """Grup değiştirildiğinde"""
        current_group = self.detail_group.get().strip()
        if current_group and current_group not in self.group_combo['values']:
            # Yeni grup eklendi
            current_groups = list(self.group_combo['values'])
            current_groups.append(current_group)
            self.group_combo['values'] = sorted(set(current_groups))
            self.save_group_list(current_groups)
    
    def on_station_double_click(self, event):
        """Tabloda radyo istasyonuna çift tıklandığında çal"""
        selection = self.editor_tree.selection()
        if not selection:
            return
        
        try:
            # Seçili öğenin bilgilerini al
            item = selection[0]
            values = self.editor_tree.item(item)['values']
            
            if len(values) >= 2:
                station_name = values[0]  # İstasyon adı
                url = values[1]          # Stream URL
                
                # URL geçerli mi kontrol et
                if not url or url.strip() == '':
                    self.status_callback("Geçersiz URL")
                    return
                
                # Ana penceredeki VLC player'a erişim için callback kullan
                if hasattr(self, 'play_callback') and self.play_callback:
                    self.play_callback(url, station_name)
                else:
                    self.status_callback(f"Çalmaya çalışılıyor: {station_name}")
                    
        except Exception as e:
            self.status_callback(f"Çalma hatası: {str(e)}")
    
    def set_play_callback(self, callback):
        """Ana pencereden çalma callback'ini ayarla"""
        self.play_callback = callback
    
    def apply_zebra_stripes(self):
        """Zebra stripe renklerini uygula"""
        try:
            children = self.editor_tree.get_children()
            for i, child in enumerate(children):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                current_tags = self.editor_tree.item(child, 'tags')
                # Sadece zebra stripe tag'ini güncelle, diğerlerini koru
                new_tags = [t for t in current_tags if t not in ('evenrow', 'oddrow')]
                new_tags.append(tag)
                self.editor_tree.item(child, tags=new_tags)
        except:
            pass
    
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