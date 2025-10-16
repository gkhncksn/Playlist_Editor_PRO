#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="veriler.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanını başlat ve tabloları oluştur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Ayarlar tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Trigger for updated_at
                cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS update_settings_timestamp 
                    AFTER UPDATE ON settings
                    BEGIN
                        UPDATE settings SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
                    END
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Veritabanı başlatma hatası: {e}")
    
    def get_setting(self, key, default_value=None):
        """Ayar değerini getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else default_value
        except Exception as e:
            print(f"Ayar okuma hatası: {e}")
            return default_value
    
    def set_setting(self, key, value):
        """Ayar değerini kaydet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value) 
                    VALUES (?, ?)
                ''', (key, value))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ayar kaydetme hatası: {e}")
            return False
    
    def get_all_settings(self):
        """Tüm ayarları getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                return dict(cursor.fetchall())
        except Exception as e:
            print(f"Ayarları okuma hatası: {e}")
            return {}
    
    def delete_setting(self, key):
        """Ayarı sil"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ayar silme hatası: {e}")
            return False
    
    def migrate_from_ini(self, ini_file_path):
        """INI dosyasından SQLite'a geçiş"""
        if not os.path.exists(ini_file_path):
            return False
        
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(ini_file_path, encoding='utf-8')
            
            # INI dosyasındaki tüm ayarları SQLite'a aktar
            for section in config.sections():
                for key, value in config.items(section):
                    setting_key = f"{section.lower()}.{key}"
                    self.set_setting(setting_key, value)
            
            return True
        except Exception as e:
            print(f"INI geçiş hatası: {e}")
            return False
    
    def get_last_directory(self, module_name, operation_type):
        """Son kullanılan klasörü getir"""
        key = f"last_dir.{module_name}.{operation_type}"
        return self.get_setting(key, os.path.expanduser("~"))
    
    def set_last_directory(self, module_name, operation_type, directory_path):
        """Son kullanılan klasörü kaydet"""
        if directory_path and os.path.exists(directory_path):
            # Eğer dosya yolu verilmişse, klasör yolunu çıkar
            if os.path.isfile(directory_path):
                directory_path = os.path.dirname(directory_path)
            
            key = f"last_dir.{module_name}.{operation_type}"
            return self.set_setting(key, directory_path)
        return False