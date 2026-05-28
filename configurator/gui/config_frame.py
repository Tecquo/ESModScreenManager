"""фрейм конфигурации - форма с полями настроек"""

import os
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import Callable, Optional
from .widgets.tooltip import Tooltip
from core.config_data import FIELD_METADATA, ConfigData


class ConfigFrame(ctk.CTkFrame):
    """фрейм с формой конфигурации"""
    
    def __init__(self, parent, on_path_change: "Callable[[], None] | None" = None, **kwargs):
        """
        инициализация фрейма конфигурации
        
        Args:
            parent: родительский виджет
            on_path_change: колбэк при изменении пути
            **kwargs: доп. аргументы для CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        self.on_path_change = on_path_change
        
        # хранилище полей
        self.fields = {}
        self.checkboxes = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """создать все виджеты формы"""
        
        # заголовок
        title = ctk.CTkLabel(
            self,
            text="Настройка конфигурации",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # === Обязательные поля ===
        required_section = ctk.CTkFrame(self, fg_color="transparent")
        required_section.pack(fill="x", padx=20, pady=5)
        
        # MOD_NAME
        self._create_field_with_tooltip(
            required_section,
            field_key='mod_name',
            label_text="Название мода:",
            default_value="Мой мод"
        )
        
        # MOD_ID
        self._create_field_with_tooltip(
            required_section,
            field_key='mod_id',
            label_text="Префикс мода:",
            default_value="my_mod"
        )
        
        # MOD_SAVE_IDENTIFIER
        self._create_field_with_tooltip(
            required_section,
            field_key='mod_save_identifier',
            label_text="ID сохранения:",
            default_value="MyMod"
        )
        
        # RENPY_MIN_VERSION
        self._create_field_with_tooltip(
            required_section,
            field_key='renpy_min_version',
            label_text="Версия Ren'Py:",
            default_value="7.0"
        )
        
        # разделитель
        sep1 = ctk.CTkFrame(self, height=2, fg_color="#3b3b3b")
        sep1.pack(fill="x", padx=20, pady=15)
        
        # === Опциональные поля ===
        optional_section = ctk.CTkFrame(self, fg_color="transparent")
        optional_section.pack(fill="x", padx=20, pady=5)
        
        # MOD_REPLACE_WINDOW_NAME
        self._create_checkbox_with_tooltip(
            optional_section,
            field_key='replace_window_name',
            label_text="Заменить название окна"
        )
        
        # путь к курсору
        cursor_frame = ctk.CTkFrame(optional_section, fg_color="transparent")
        cursor_frame.pack(fill="x", pady=5)
        
        cursor_label = ctk.CTkLabel(cursor_frame, text="Путь к курсору:", width=150, anchor="w")
        cursor_label.pack(side="left")
        
        self.fields['cursor_path'] = ctk.CTkEntry(cursor_frame, placeholder_text="images/cursor.png")
        self.fields['cursor_path'].pack(side="left", fill="x", expand=True, padx=5)
        
        # тултип для курсора
        Tooltip(
            self.fields['cursor_path'],
            **FIELD_METADATA['cursor_path']
        )
        
        # путь к музыке
        music_frame = ctk.CTkFrame(optional_section, fg_color="transparent")
        music_frame.pack(fill="x", pady=5)
        
        music_label = ctk.CTkLabel(music_frame, text="Путь к музыке:", width=150, anchor="w")
        music_label.pack(side="left")
        
        self.fields['menu_music'] = ctk.CTkEntry(music_frame, placeholder_text="music/main_menu.ogg")
        self.fields['menu_music'].pack(side="left", fill="x", expand=True, padx=5)
        
        # тултип для музыки
        Tooltip(
            self.fields['menu_music'],
            **FIELD_METADATA['menu_music']
        )
        
        # разделитель
        sep2 = ctk.CTkFrame(self, height=2, fg_color="#3b3b3b")
        sep2.pack(fill="x", padx=20, pady=15)
        
        # === Логирование ===
        logging_section = ctk.CTkFrame(self, fg_color="transparent")
        logging_section.pack(fill="x", padx=20, pady=5)
        
        # чекбокс логирования
        self._create_checkbox_with_tooltip(
            logging_section,
            field_key='logging',
            label_text="Включить логирование"
        )
        
        # уровень логов
        log_level_frame = ctk.CTkFrame(logging_section, fg_color="transparent")
        log_level_frame.pack(fill="x", pady=5)
        
        log_level_label = ctk.CTkLabel(log_level_frame, text="Уровень логов:", width=150, anchor="w")
        log_level_label.pack(side="left")
        
        self.fields['log_level'] = ctk.CTkOptionMenu(
            log_level_frame,
            values=["DEBUG (10)", "INFO (20)", "WARNING (30)", "ERROR (40)"],
            width=150
        )
        self.fields['log_level'].set("INFO (20)")
        self.fields['log_level'].pack(side="left", padx=5)
        
        # тултип
        Tooltip(
            log_level_frame,
            **FIELD_METADATA['log_level']
        )
    
    def _create_field_with_tooltip(self, parent, field_key: str, label_text: str, 
                                   default_value: str = ""):
        """создать текстовое поле с тултипом"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        label = ctk.CTkLabel(frame, text=label_text, width=150, anchor="w")
        label.pack(side="left")
        
        entry = ctk.CTkEntry(frame)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # устанавливаем реальное значение по умолчанию
        if default_value:
            entry.insert(0, default_value)
        
        self.fields[field_key] = entry
        
        # тултип если есть
        if field_key in FIELD_METADATA:
            # используем обычный tk.Label для отображения (?) - он корректно обрабатывает события мыши
            # bg убираем - будет использовать системный по умолчанию
            tooltip_label = tk.Label(
                frame,
                text="(?)",
                width=3,
                font=("TkDefaultFont", 12, "bold"),
                fg="#888888",
                cursor="question_arrow"
            )
            tooltip_label.pack(side="left", padx=2)
            print(f"Creating tooltip for field: {field_key}, widget: {tooltip_label}")  # DEBUG
            
            Tooltip(
                tooltip_label,
                **FIELD_METADATA[field_key]
            )
    
    def _create_checkbox_with_tooltip(self, parent, field_key: str, label_text: str):
        """создать чекбокс с тултипом"""
        checkbox = ctk.CTkCheckBox(parent, text=label_text)
        checkbox.pack(anchor="w", pady=5)
        
        self.checkboxes[field_key] = checkbox
        
        # тултип если есть
        if field_key in FIELD_METADATA:
            # используем обычный tk.Label для отображения (?) - он корректно обрабатывает события мыши
            # bg убираем - будет использовать системный по умолчанию
            tooltip_label = tk.Label(
                parent,
                text="(?)",
                width=3,
                font=("TkDefaultFont", 12, "bold"),
                fg="#888888",
                cursor="question_arrow"
            )
            tooltip_label.pack(anchor="w", pady=2)
            print(f"Creating tooltip for checkbox: {field_key}, widget: {tooltip_label}")  # DEBUG
            
            Tooltip(
                tooltip_label,
                **FIELD_METADATA[field_key]
            )
    
    def get_config(self) -> ConfigData:
        """
        получить конфиг из формы
        
        Returns:
            ConfigData с текущими значениями
        """
        # парсим уровень логов
        log_level_str = self.fields['log_level'].get()
        log_level = 20
        if "DEBUG" in log_level_str:
            log_level = 10
        elif "INFO" in log_level_str:
            log_level = 20
        elif "WARNING" in log_level_str:
            log_level = 30
        elif "ERROR" in log_level_str:
            log_level = 40
        
        return ConfigData(
            mod_name=self.fields['mod_name'].get() or "Мой мод",
            mod_id=self.fields['mod_id'].get() or "my_mod",
            mod_save_identifier=self.fields['mod_save_identifier'].get() or "MyMod",
            renpy_min_version=self.fields['renpy_min_version'].get() or "7.0",
            replace_window_name=self.checkboxes['replace_window_name'].get() == 1,
            cursor_path=self.fields['cursor_path'].get() or None,
            menu_music=self.fields['menu_music'].get() or None,
            logging=self.checkboxes['logging'].get() == 1,
            log_level=log_level,
        )
    
    def set_config(self, config: ConfigData):
        """
        заполнить форму из ConfigData
        
        Args:
            config: конфиг для установки
        """
        self.fields['mod_name'].delete(0, "end")
        self.fields['mod_name'].insert(0, config.mod_name)
        
        self.fields['mod_id'].delete(0, "end")
        self.fields['mod_id'].insert(0, config.mod_id)
        
        self.fields['mod_save_identifier'].delete(0, "end")
        self.fields['mod_save_identifier'].insert(0, config.mod_save_identifier)
        
        self.fields['renpy_min_version'].delete(0, "end")
        self.fields['renpy_min_version'].insert(0, config.renpy_min_version)
        
        self.checkboxes['replace_window_name'].select() if config.replace_window_name else \
            self.checkboxes['replace_window_name'].deselect()
        
        if config.cursor_path:
            self.fields['cursor_path'].insert(0, config.cursor_path)
        
        if config.menu_music:
            self.fields['menu_music'].insert(0, config.menu_music)
        
        self.checkboxes['logging'].select() if config.logging else \
            self.checkboxes['logging'].deselect()
        
        # уровень логов
        if config.log_level == 10:
            self.fields['log_level'].set("DEBUG (10)")
        elif config.log_level == 20:
            self.fields['log_level'].set("INFO (20)")
        elif config.log_level == 30:
            self.fields['log_level'].set("WARNING (30)")
        elif config.log_level == 40:
            self.fields['log_level'].set("ERROR (40)")
    
    def set_enabled(self, enabled: bool):
        """включить/выключить все поля формы"""
        state = "normal" if enabled else "disabled"
        
        for field in self.fields.values():
            field.configure(state=state)
        
        for checkbox in self.checkboxes.values():
            checkbox.configure(state=state)
