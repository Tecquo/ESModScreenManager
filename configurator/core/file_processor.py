"""файловый процессор - копирует шаблоны и меняет плейсхолдеры"""

import os
import shutil
from pathlib import Path
from typing import Tuple, List, Dict, Union
import re


class FileProcessor:
    """обрабатывает копирование шаблонов и замену плейсхолдеров"""
    
    def __init__(self, template_dir: Path):
        """
        инициализация процессора
        
        Args:
            template_dir: путь к папке с шаблонами
        """
        self.template_dir = Path(template_dir)
    
    def copy_and_process(
        self,
        target_dir: Union[Path, str],
        mod_id: str,
        include_test_example: bool = False
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        скопировать шаблоны в папку мода и заменить плейсхолдеры
        
        Args:
            target_dir: папка мода
            mod_id: уникальный ID мода (префикс)
            include_test_example: копировать ли тестовый пример
            
        Returns:
            (успешные файлы, ошибки, пропущенные файлы)
        """
        success_files = []
        errors = []
        skipped_files = []
        
        target_dir = Path(target_dir)
        
        # файлы которые нужно скопировать
        files_to_copy = [
            ('example.rpy.example', 'example.rpy'),
            ('screens.rpy.example', 'screens.rpy'),
        ]
        
        if include_test_example:
            files_to_copy.append(
                ('test_example.rpy.example', 'test_example.rpy')
            )
        
        # также копируем MSM.rpy и logger.rpy если есть
        # ВАЖНО: эти файлы должны находиться в parent директории относительно template_dir
        # (структура: configurator/example/ и configurator/MSM.rpy)
        for core_file in ['MSM.rpy', 'logger.rpy']:
            source = self.template_dir.parent / core_file
            if source.exists():
                files_to_copy.append((core_file, core_file))
            else:
                errors.append(f"Внимание: Не найден файл {core_file} в корневой папке")
        
        for source_name, target_name in files_to_copy:
            source = self.template_dir / source_name
            
            if not source.exists():
                errors.append(f"Шаблон не найден: {source_name}")
                continue
            
            target = target_dir / target_name
            
            # check if target file already exists
            if target.exists():
                skipped_files.append(f"{target_name} (уже существует)")
                continue
            
            try:
                # create target directory if needed
                target.parent.mkdir(parents=True, exist_ok=True)
                
                # read source template
                content = source.read_text(encoding='utf-8')
                
                # replace placeholders
                content = self._replace_placeholders(content, mod_id)
                
                # write to target file
                target.write_text(content, encoding='utf-8')
                
                success_files.append(target_name)
                
            except Exception as e:
                errors.append(f"Ошибка при обработке {source_name}: {str(e)}")
        
        return success_files, errors, skipped_files
    
    def _replace_placeholders(self, content: str, mod_id: str) -> str:
        """
        заменить все 'my_mod' плейсхолдеры на указанный мод айди
        
        Args:
            content: содержимое файла
            mod_id: новый префикс
            
        Returns:
            измененное содержимое
        """
        # используем regex с границами слов для безопасной замены
        # ВАЖНО: более конкретные паттерны должны идти ПЕРЕД общими!
        replacements = [
            # Сначала самые конкретные - полные имена классов/функций
            (r'\bmy_mod_ModScreenManagerConfig\b', f'{mod_id}_ModScreenManagerConfig'),
            # Переменные и функции
            (r'\bmy_mod_screen_manager\b', f'{mod_id}_screen_manager'),
            (r'\bmy_mod_start\b', f'{mod_id}_start'),
            (r'\bmy_mod_exit\b', f'{mod_id}_exit'),
            # Строковые литералы - точное совпадение без лишних пробелов
            (r'"my_mod"', f'"{mod_id}"'),
            (r"'my_mod'", f"'{mod_id}'"),
            # Общий префикс - В КОНЦЕ, после всех конкретных замен
            (r'\bmy_mod_', f'{mod_id}_'),
        ]
        
        result = content
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def validate_mod_id(self, mod_id: str) -> Tuple[bool, str]:
        """
        проверить что мод айди - валидный питоновский идентификатор
        
        Args:
            mod_id: айди для проверки
            
        Returns:
            (валиден, сообщение об ошибке)
        """
        if not mod_id:
            return False, "Префикс мода не может быть пустым"
        
        # проверяем питоновский идентификатор
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', mod_id):
            return False, (
                "Префикс мода должен быть корректным идентификатором Python "
                "(английские буквы, цифры, подчёркивание, не начинается с цифры)"
            )
        
        return True, ""
