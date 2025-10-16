#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

class DragDropTreeview:
    """Treeview için sürükle-bırak özelliği sağlayan yardımcı sınıf"""
    
    def __init__(self, treeview, data_list, update_callback=None):
        self.treeview = treeview
        self.data_list = data_list
        self.update_callback = update_callback
        self.dragging = False
        self.drag_item = None
        self.drag_start_pos = None
        self.drop_target_item = None
        
        # Görsel geri bildirim için tag'ler oluştur
        self.setup_visual_feedback()
        
        # Sürükle-bırak olaylarını bağla
        self.setup_drag_drop()
    
    def setup_visual_feedback(self):
        """Görsel geri bildirim için tag'leri ayarla"""
        # Bırakma hedefi için mavi renk
        self.treeview.tag_configure('drop_target', background='#ADD8E6', foreground='black')
        # Sürüklenen öğe için hafif gri ve şeffaf görünüm
        self.treeview.tag_configure('dragging', background='#E8E8E8', foreground='#888888')
    
    def setup_drag_drop(self):
        """Sürükle-bırak olaylarını ayarla"""
        # Sol tık ile sürükle-bırak
        self.treeview.bind('<Button-1>', self.on_start_drag, add=True)
        self.treeview.bind('<B1-Motion>', self.on_drag_motion, add=True)
        self.treeview.bind('<ButtonRelease-1>', self.on_end_drag, add=True)
    
    def on_start_drag(self, event):
        """Sürükleme başlangıcı"""
        item = self.treeview.identify_row(event.y)
        
        if item:
            self.drag_item = item
            self.drag_start_pos = (event.x, event.y)
            self.dragging = False
            
            # Seçimi güncelle
            self.treeview.selection_set(item)
            self.treeview.focus(item)
    
    def on_drag_motion(self, event):
        """Sürükleme hareketi"""
        if self.drag_item and self.drag_start_pos:
            # Yeterince hareket edildi mi?
            dx = abs(event.x - self.drag_start_pos[0])
            dy = abs(event.y - self.drag_start_pos[1])
            
            if not self.dragging and (dx > 10 or dy > 10):
                # Sürükleme başladı
                self.dragging = True
                self.treeview.config(cursor="hand2")
                
                # Sürüklenen öğeyi görsel olarak işaretle
                self.treeview.item(self.drag_item, tags=('dragging',))
            
            if self.dragging:
                # Hedef öğeyi bul ve görsel geri bildirim ver
                target_item = self.treeview.identify_row(event.y)
                
                # Önceki hedefi temizle
                if self.drop_target_item and self.drop_target_item != self.drag_item:
                    self.clear_item_tags(self.drop_target_item)
                
                # Yeni hedefi işaretle
                if target_item and target_item != self.drag_item:
                    self.drop_target_item = target_item
                    self.treeview.item(target_item, tags=('drop_target',))
                else:
                    self.drop_target_item = None
    
    def on_end_drag(self, event):
        """Sürükleme bitişi"""
        if self.dragging and self.drag_item:
            target_item = self.treeview.identify_row(event.y)
            
            if target_item and target_item != self.drag_item:
                try:
                    source_index = self.treeview.index(self.drag_item)
                    target_index = self.treeview.index(target_item)
                    
                    if 0 <= source_index < len(self.data_list) and 0 <= target_index < len(self.data_list):
                        # Veriyi taşı
                        item_data = self.data_list.pop(source_index)
                        self.data_list.insert(target_index, item_data)
                        
                        # Callback'i çağır
                        if self.update_callback:
                            self.update_callback()
                        
                except Exception as e:
                    pass  # Sessizce geç
        
        # Temizlik
        self.clear_all_visual_feedback()
        self.dragging = False
        self.drag_item = None
        self.drop_target_item = None
        self.drag_start_pos = None
        self.treeview.config(cursor="")
    
    def clear_item_tags(self, item):
        """Öğenin tag'lerini temizle"""
        try:
            # Mevcut tag'leri al
            current_tags = self.treeview.item(item, 'tags')
            # Sadece zebra stripe tag'lerini koru
            new_tags = [tag for tag in current_tags if tag in ('evenrow', 'oddrow')]
            self.treeview.item(item, tags=new_tags)
        except:
            pass
    
    def clear_all_visual_feedback(self):
        """Tüm görsel geri bildirimleri temizle"""
        try:
            # Tüm öğelerin tag'lerini temizle
            for item in self.treeview.get_children():
                self.clear_item_tags(item)
        except:
            pass


class DragDropListbox:
    """Listbox için sürükle-bırak özelliği sağlayan yardımcı sınıf"""
    
    def __init__(self, listbox, data_list, update_callback=None):
        self.listbox = listbox
        self.data_list = data_list
        self.update_callback = update_callback
        self.dragging = False
        self.drag_index = None
        self.drag_start_pos = None
        self.drop_target_index = None
        self.original_bg = None
        
        # Orijinal arka plan rengini kaydet
        try:
            self.original_bg = self.listbox.cget('bg')
        except:
            self.original_bg = 'white'
        
        # Sürükle-bırak olaylarını bağla
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """Sürükle-bırak olaylarını ayarla"""
        # Sol tık ile sürükle-bırak
        self.listbox.bind('<Button-1>', self.on_start_drag)
        self.listbox.bind('<B1-Motion>', self.on_drag_motion)
        self.listbox.bind('<ButtonRelease-1>', self.on_end_drag)
    
    def on_start_drag(self, event):
        """Sürükleme başlangıcı"""
        index = self.listbox.nearest(event.y)
        
        if 0 <= index < self.listbox.size():
            self.drag_index = index
            self.drag_start_pos = (event.x, event.y)
            self.dragging = False
            
            # Seçimi güncelle
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
    
    def on_drag_motion(self, event):
        """Sürükleme hareketi"""
        if self.drag_index is not None and self.drag_start_pos:
            # Yeterince hareket edildi mi?
            dx = abs(event.x - self.drag_start_pos[0])
            dy = abs(event.y - self.drag_start_pos[1])
            
            if not self.dragging and (dx > 10 or dy > 10):
                # Sürükleme başladı
                self.dragging = True
                self.listbox.config(cursor="hand2")
            
            if self.dragging:
                # Hedef indeksi bul ve görsel geri bildirim ver
                target_index = self.listbox.nearest(event.y)
                
                # Önceki hedefi temizle
                if self.drop_target_index is not None:
                    self.clear_drop_highlight()
                
                # Yeni hedefi işaretle
                if 0 <= target_index < self.listbox.size() and target_index != self.drag_index:
                    self.drop_target_index = target_index
                    self.highlight_drop_target(target_index)
                else:
                    self.drop_target_index = None
    
    def on_end_drag(self, event):
        """Sürükleme bitişi"""
        if self.dragging and self.drag_index is not None:
            target_index = self.listbox.nearest(event.y)
            
            if 0 <= target_index < self.listbox.size() and target_index != self.drag_index:
                if 0 <= self.drag_index < len(self.data_list) and 0 <= target_index < len(self.data_list):
                    try:
                        # Veriyi taşı
                        item_data = self.data_list.pop(self.drag_index)
                        self.data_list.insert(target_index, item_data)
                        
                        # Listbox'ı güncelle
                        self.update_listbox()
                        
                        # Yeni pozisyonu seç
                        self.listbox.selection_clear(0, tk.END)
                        self.listbox.selection_set(target_index)
                        
                        # Callback'i çağır
                        if self.update_callback:
                            self.update_callback()
                        
                    except Exception as e:
                        pass  # Sessizce geç
        
        # Temizlik
        self.clear_all_highlights()
        self.dragging = False
        self.drag_index = None
        self.drop_target_index = None
        self.drag_start_pos = None
        self.listbox.config(cursor="")
    
    def highlight_drop_target(self, index):
        """Bırakma hedefini vurgula"""
        try:
            # Mavi arka plan ile vurgula
            self.listbox.itemconfig(index, bg='#ADD8E6', fg='black')
        except:
            pass
    
    def clear_drop_highlight(self):
        """Bırakma vurgusunu temizle"""
        try:
            if self.drop_target_index is not None:
                self.listbox.itemconfig(self.drop_target_index, bg=self.original_bg, fg='black')
        except:
            pass
    
    def clear_all_highlights(self):
        """Tüm vurguları temizle"""
        try:
            for i in range(self.listbox.size()):
                self.listbox.itemconfig(i, bg=self.original_bg, fg='black')
        except:
            pass
    
    def update_listbox(self):
        """Listbox içeriğini güncelle"""
        # Mevcut seçimi kaydet
        current_selection = self.listbox.curselection()
        
        # Listbox'ı temizle ve yeniden doldur
        self.listbox.delete(0, tk.END)
        
        for item in self.data_list:
            # Her zaman dosya adını göster (tam yol değil)
            from pathlib import Path
            if isinstance(item, str):
                # Eğer item bir dosya yolu ise sadece dosya adını al
                if '/' in item or '\\' in item:
                    display_text = Path(item).name
                else:
                    display_text = item
            else:
                display_text = Path(str(item)).name
            
            self.listbox.insert(tk.END, display_text)


class DragDropMixin:
    """Genel sürükle-bırak işlevselliği için mixin sınıfı"""
    
    @staticmethod
    def enable_drag_drop_for_treeview(treeview, data_list, update_callback=None):
        """Treeview için sürükle-bırak özelliğini etkinleştir"""
        return DragDropTreeview(treeview, data_list, update_callback)
    
    @staticmethod
    def enable_drag_drop_for_listbox(listbox, data_list, update_callback=None):
        """Listbox için sürükle-bırak özelliğini etkinleştir"""
        return DragDropListbox(listbox, data_list, update_callback)