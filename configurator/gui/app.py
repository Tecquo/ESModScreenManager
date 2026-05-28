"""главное окно приложения"""

import os
import sys
import json
import threading
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog
from typing import Optional

from .config_frame import ConfigFrame
from .screens_frame import ScreensFrame
from core import ConfigData, FileProcessor, ConfigGenerator, Validator


class ModScreenManagerApp(ctk.CTk):
    """главное окно приложения"""
    
    # цвета
    COLORS = {
        "dark": {
            "bg": "#1a1a1a",
            "fg": "#2b2b2b",
            "accent": "#3b8ed0",
            "text": "#ffffff",
            "text_secondary": "#cccccc",
            "error": "#ff5555",
            "success": "#50fa7b",
        }
    }
    
    def __init__(self):
        """инициализация приложения"""
        super().__init__()
        
        # определяем директорию шаблонов
        if getattr(sys, 'frozen', False):
            # если запущено как exe
            # _MEIPASS - атрибут PyInstaller, указывающий на директорию с распакованными ресурсами
            meipass = getattr(sys, '_MEIPASS', None)
            base_dir = Path(meipass) if meipass else Path(__file__).parent.parent
        else:
            # если запущено как скрипт
            base_dir = Path(__file__).parent.parent
        
        self.template_dir = base_dir / "example"
        self.project_dir = base_dir
        
        # инициализируем компоненты
        self.file_processor = FileProcessor(self.template_dir)
        self.config_generator = ConfigGenerator()
        self.validator = Validator()
        
        # текущий конфиг
        self.config = ConfigData()
        self.include_test_example = False
        
        # путь к файлу настроек
        self._settings_file = self.project_dir / "configurator_settings.json"
        
        # загружаем сохранённые настройки
        self._load_settings()
        
        # флаг для предотвращения повторного запуска
        self._is_processing = False
        
        # событие для отмены операции
        self._cancel_event = threading.Event()
        
        # ссылка на поток для возможности ожидания при закрытии
        self._processing_thread = None
        
        # настраиваем окно
        self._setup_window()
        
        # создаем виджеты
        self._create_widgets()
        
        # начальное состояние
        self._set_state("initial")
    
    def _setup_window(self):
        """настроить главное окно"""
        self.title("Mod Screen Manager - Конфигуратор")
        self.geometry("800x900")
        
        # делаем окно ресайзабельным
        self.resizable(True, True)
        
        # минимальный размер
        self.minsize(600, 700)
        
        # тема
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # центрируем
        self.update_idletasks()
        width = max(800, self.winfo_reqwidth())
        height = max(900, self.winfo_reqheight())
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # закрытие
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """создать все виджеты"""
        
        # контейнер
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === Шаг 1: Выбор папки ===
        path_section = ctk.CTkFrame(main_container)
        path_section.pack(fill="x", pady=(0, 15))
        
        path_title = ctk.CTkLabel(
            path_section,
            text="Шаг 1: Выбор папки мода",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        path_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        path_frame = ctk.CTkFrame(path_section, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Выберите папку вашего мода...",
            height=40
        )
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.path_entry.bind("<KeyRelease>", self._on_path_change)
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="Обзор",
            width=100,
            height=40,
            command=self._browse_folder
        )
        browse_btn.pack(side="left", padx=(10, 0))
        
        # === Шаг 2: Конфигурация ===
        self.config_frame = ConfigFrame(main_container)
        self.config_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # === Шаг 3: Экраны ===
        self.screens_frame = ScreensFrame(main_container)
        self.screens_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # === Дополнительно ===
        options_section = ctk.CTkFrame(main_container, fg_color="transparent")
        options_section.pack(fill="x", pady=(0, 15))
        
        self.test_example_checkbox = ctk.CTkCheckBox(
            options_section,
            text="Включить тестовый пример (test_example)",
            font=ctk.CTkFont(size=13)
        )
        self.test_example_checkbox.pack(anchor="w", padx=20, pady=10)
        
        # === Статус ===
        self.status_label = ctk.CTkLabel(
            main_container,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            justify="left",
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=(0, 10))
        
        # === Кнопки ===
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x")
        
        self.create_btn = ctk.CTkButton(
            button_frame,
            text="Создать мод",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#3b8ed0",
            hover_color="#2a6fb8",
            command=self._create_mod
        )
        self.create_btn.pack(side="left", fill="x", expand=True)
    
    def _set_state(self, state: str):
        """
        установить состояние приложения
        
        States:
        - initial: путь не выбран, форма выключена
        - ready: путь выбран, форма включена
        - processing: идет работа, форма выключена
        - success: успех
        - error: ошибка
        """
        if state == "initial":
            self.config_frame.set_enabled(False)
            self.screens_frame.set_enabled(False)
            self.test_example_checkbox.configure(state="disabled")
            self.create_btn.configure(state="disabled", text="Создать мод")
            self.status_label.configure(text="")
        
        elif state == "ready":
            self.config_frame.set_enabled(True)
            self.screens_frame.set_enabled(True)
            self.test_example_checkbox.configure(state="normal")
            self.create_btn.configure(state="normal", text="Создать мод")
            self.status_label.configure(text="Настройте конфигурацию и нажмите 'Создать мод'")
        
        elif state == "processing":
            self.config_frame.set_enabled(False)
            self.screens_frame.set_enabled(False)
            self.test_example_checkbox.configure(state="disabled")
            self.create_btn.configure(state="disabled", text="Создание...")
            self.status_label.configure(text="Создание мода...")
        
        elif state == "success":
            self.config_frame.set_enabled(True)
            self.screens_frame.set_enabled(True)
            self.test_example_checkbox.configure(state="normal")
            self.create_btn.configure(state="normal", text="Создать мод снова")
        
        elif state == "error":
            self.config_frame.set_enabled(True)
            self.screens_frame.set_enabled(True)
            self.test_example_checkbox.configure(state="normal")
            self.create_btn.configure(state="normal", text="Создать мод")
    
    def _browse_folder(self):
        """открыть диалог выбора папки"""
        folder = filedialog.askdirectory(
            title="Выберите папку мода",
            initialdir=os.path.expanduser("~")
        )
        
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)
            self._on_path_change()
    
    def _on_path_change(self, event=None):
        """обработка изменения пути"""
        path = self.path_entry.get().strip()
        
        if path and os.path.isdir(path):
            self.config.mod_path = path
            self._set_state("ready")
        else:
            self._set_state("initial")
    
    def _validate(self) -> tuple[bool, str]:
        """
        валидировать текущий конфиг
        
        Returns:
            (валиден, сообщение об ошибке)
        """
        # получаем конфиг из форм
        self.config = self.config_frame.get_config()
        self.config.mod_path = self.path_entry.get().strip()
        self.config.selected_screens = self.screens_frame.get_selected_screens()
        self.config.include_test_example = self.test_example_checkbox.get() == 1
        
        # валидируем
        is_valid, errors = self.validator.validate(self.config)
        
        if not is_valid:
            return False, "\n".join(errors)
        
        # доп. проверка экранов
        is_valid, error = self.screens_frame.validate()
        if not is_valid:
            return False, error
        
        return True, ""
    
    def _create_mod(self):
        """создать мод с текущим конфигом"""
        # проверяем не идет ли уже процесс
        if self._is_processing:
            return
        
        # валидация
        is_valid, error = self._validate()
        
        if not is_valid:
            self._is_processing = False
            self._show_error(error)
            return
        
        # Set flag FIRST to prevent race condition
        self._is_processing = True
        
        # состояние - идет обработка
        self._set_state("processing")
        self.update()
        
        # запускаем в потоке чтобы не зависало
        self._cancel_event.clear()
        thread = threading.Thread(target=self._create_mod_thread)
        thread.daemon = True  # чтобы поток не блокировал выход из приложения
        thread.start()
        self._processing_thread = thread
    
    def _create_mod_thread(self):
        """создание мода в отдельном потоке"""
        try:
            # проверяем не была ли отменена операция
            if self._cancel_event.is_set():
                self.after(0, self._on_processing_cancelled)
                return
            # копируем и обрабатываем файлы
            success_files, errors, skipped = self.file_processor.copy_and_process(
                target_dir=self.config.mod_path,
                mod_id=self.config.mod_id,
                include_test_example=self.config.include_test_example
            )
            
            # проверяем отмену после каждого этапа
            if self._cancel_event.is_set():
                self.after(0, self._on_processing_cancelled)
                return
            
            if errors:
                self.after(0, lambda: self._show_error("\n".join(errors)))
                return
            
            # показываем информацию о пропущенных файлах
            if skipped:
                self._is_processing = False
                self.after(0, lambda: self._show_skipped(skipped))
                return
            
            # генерируем кастомный конфиг
            config_code = self.config_generator.generate(self.config)
            
            # проверяем что файл был создан
            example_path = Path(self.config.mod_path) / "example.rpy"
            if not example_path.exists():
                self.after(0, lambda: self._show_error("Шаблон example.rpy не был создан. Возможно, файл уже существует."))
                return
            
            content = example_path.read_text(encoding='utf-8')
            
            # находим и заменяем класс конфига
            # используем более надёжный подход: ищем конец класса по ключевым словам
            try:
                lines = content.split('\n')
                new_lines = []
                in_config_class = False
                class_start_indent = 0
                class_depth = 0  # отслеживаем глубину для вложенных классов
                
                for line in lines:
                    # Сначала ищем оригинальный класс
                    if 'class my_mod_ModScreenManagerConfig' in line:
                        in_config_class = True
                        # определяем уровень отступа класса
                        class_start_indent = len(line) - len(line.lstrip())
                        class_depth = 1
                        # добавляем новый конфиг вместо старого
                        new_lines.append(config_code)
                        continue
                    
                    # Если оригинальный класс уже заменён, пропускаем (поддержка повторного запуска)
                    # Такой случай возникает если пользователь запустил инструмент повторно
                    if not in_config_class and f'class {self.config.mod_id}_ModScreenManagerConfig' in line:
                        continue
                    
                    if in_config_class:
                        stripped = line.strip()
                        
                        # отслеживаем вложенные классы
                        if stripped.startswith('class '):
                            class_depth += 1
                        
                        # проверяем: вышли из класса если:
                        # 1. строка не пустая и имеет меньший или равный отступ чем класс
                        # 2. и глубина класса вернулась к 1
                        if stripped:
                            current_indent = len(line) - len(line.lstrip())
                            
                            # выходим если отступ меньше или равен уровню класса
                            # и это не строка с атрибутами класса (атрибуты могут иметь меньший отступ)
                            if current_indent <= class_start_indent and class_depth <= 1:
                                # это конец класса
                                in_config_class = False
                                new_lines.append(line)
                        continue
                    
                    new_lines.append(line)
                
                # пишем обратно
                example_path.write_text('\n'.join(new_lines), encoding='utf-8')
                
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Ошибка при обработке класса конфига: {str(e)}"))
                self._is_processing = False
                return
            
            # показываем результат после сброса флага
            self._is_processing = False
            self.after(0, self._show_success)
            
        except Exception as e:
            self._is_processing = False
            self.after(0, lambda: self._show_error(f"Ошибка: {str(e)}"))
            self.after(0, self._set_state, "error")
    
    def _show_success(self):
        """показать сообщение об успехе"""
        self._set_state("success")
        
        message = f"Мод успешно создан!\n\n"
        message += f"Папка: {self.config.mod_path}\n\n"
        message += "Созданные файлы:\n"
        message += "- example.rpy\n"
        message += "- screens.rpy\n"
        
        if self.config.include_test_example:
            message += "- test_example.rpy\n"
        
        message += "- MSM.rpy\n"
        message += "- logger.rpy\n\n"
        
        message += "Редактируйте screens.rpy для своих экранов."
        
        self.status_label.configure(text=message, text_color="#50fa7b")
    
    def _show_error(self, message: str):
        """показать сообщение об ошибке"""
        self._set_state("error")
        self.status_label.configure(text=message, text_color="#ff5555")
    
    def _show_skipped(self, skipped_files: list):
        """показать сообщение о пропущенных файлах"""
        self._set_state("success")
        
        message = "Некоторые файлы уже существуют и были пропущены:\n\n"
        for f in skipped_files:
            message += f"- {f}\n"
        message += "\nУдалите существующие файлы чтобы перезаписать, или выберите другую папку."
        
        self.status_label.configure(text=message, text_color="#ffb86c")
    
    def _on_close(self):
        """обработка закрытия окна"""
        # если идёт обработка - отменяем и ждём завершения потока
        if self._is_processing and self._processing_thread:
            self._cancel_event.set()
            self._processing_thread.join(timeout=2.0)  # ждём максимум 2 секунды
        self.destroy()
    
    def _on_processing_cancelled(self):
        """вызывается при отмене операции"""
        self._is_processing = False
        self._set_state("initial")
        self.status_label.configure(text="Операция отменена", text_color="#ffb86c")

