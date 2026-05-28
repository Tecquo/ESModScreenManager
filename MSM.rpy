init -1 python:
    import builtins

    class ModScreenManagerConfig:
        """Конфигурация параметров мода."""
        # Основные параметры
        MOD_NAME = u"Мой мод"  # Название Вашего мода
        MOD_ID = "my_mod" # Префикс Вашего мода
        MOD_SAVE_IDENTIFIER = "MyMod"  # Идентификатор в названии сохранения
        RENPY_MIN_VERSION = "7.0"  # Минимальная совместимая версия Ren'Py

        # Замена имени окна БЛ на имя своего мода
        MOD_REPLACE_WINDOW_NAME = False

        # Пути к ресурсам
        MOD_CURSOR_PATH = False
        MOD_MENU_MUSIC = False
        
        # Оригинальные настройки Летонька
        # Захардкодил на случай кодеров, которые с помощью своих версий скриптов для замены интерфейса меняют их на свои до отработки этого скрипта для замены интерфейса, чтобы точно заменились на стандартные  
        ORIGINAL_NAME = u"Бесконечное лето"
        ORIGINAL_CURSOR_PATH = "images/misc/mouse/1.png"
        ORIGINAL_MENU_MUSIC = "sound/music/blow_with_the_fires.ogg"
        
        # Экраны для замены
        DEFAULT_SCREENS = [
            "main_menu",
            "game_menu_selector",
            "quit",
            "say",
            "preferences",
            "save",
            "load",
            "nvl",
            "choice",
            "text_history_screen",
            "history",
            "yesno_prompt",
            "skip_indicator",
            "help",
        ]
        
        # логгер
        LOGGING = False
        LOG_LEVEL = 10  # DEBUG
    
    class ModScreenManager:
        """
        Менеджер для управления заменой экранов в Ren'Py.
        
        Обеспечивает безопасную замену экранов с резервным копированием,
        обработкой ошибок и поддержкой частичной замены.
        """
        
        def __init__(self, config=ModScreenManagerConfig):
            """
            Инициализация менеджера экранов.

            Args:
                config: Класс конфигурации с параметрами мода
            """
            self.config = config
            self.original_config = {}
            self.active_screens = set()
            self.is_active = False

            self.activate_screens_after_load()

            # логгер
            logger_name = u'ModScreenManager [{}]'.format(self.config.MOD_NAME)
            self.logger = ModScreenManagerLogger(
                name=logger_name,
                level=self.config.LOG_LEVEL if self.config.LOGGING else ModScreenManagerLogger.ERROR + 10,
                enabled=self.config.LOGGING
            )

        def check_compatibility(self):
            """
            Проверка совместимости с текущей версией Ren'Py.
            
            Проверяет:
            - Минимальную версию
            - Максимальную версию (должна быть < 8.0, т.к. Ren'Py 8 использует Python 3
                и не поддерживает прямую замену экранов через renpy.display.screen.screens)
            
            Returns:
                bool: True если версия совместима, False иначе
            """
            try:
                current_version = renpy.version_tuple[:2]
                min_version = tuple(builtins.map(int, self.config.RENPY_MIN_VERSION.split('.')))
                max_version = (7, 99)  # Любая версия RenPy 7.x
                
                if current_version < min_version:
                    self.logger.warning(
                        u"Версия Ren'Py {} слишком старая (требуется {}+)".format(
                            '.'.join(builtins.map(str, current_version)),
                            self.config.RENPY_MIN_VERSION
                        )
                    )
                    return False
                
                if current_version >= (8, 0):
                    self.logger.error(
                        u"Ren'Py {} не поддерживается! Замена экранов работает только на Ren'Py 7.x".format(
                            '.'.join(builtins.map(str, current_version))
                        )
                    )
                    return False
                
                return True
            except Exception as e:
                self.logger.error(u"Ошибка проверки совместимости: {}".format(e))
                return False
        
        def validate_configuration(self):
            errors = []
            
            # game_menu_selector должен быть в DEFAULT_SCREENS. иначе - отъёбываем. Нехуй не отключать свой интерфейс при выходе.
            if 'game_menu_selector' not in self.config.DEFAULT_SCREENS:
                errors.append(u"Экран 'game_menu_selector' отсутствует в DEFAULT_SCREENS\nЕго наличие обязательно для отключения интерфейса при выходе из мода")
            
            if errors:
                for error in errors:
                    self.logger.error(error)
                return False
            
            self.logger.debug(u"Валидация конфигурации пройдена успешно")
            return True
        
        def _screen_exists(self, screen_name):
            """
            Проверка существования экрана.
            
            Args:
                screen_name: Имя экрана для проверки
                
            Returns:
                bool: True если экран существует
            """
            return (screen_name, None) in renpy.display.screen.screens
        
        def _backup_config(self):
            """
            Создание резервной копии конфигурации БЛ.
            """
            try:
                self.original_config = {
                    'window_title': config.window_title,
                    'main_menu_music': config.main_menu_music
                }
                self.logger.debug("Конфигурация сохранена")
            except Exception as e:
                self.logger.error(u"Ошибка сохранения конфигурации: {}".format(e))
        
        def _restore_config(self):
            """
            Восстановление оригинальной конфигурации БЛ.
            """
            try:
                if self.original_config:
                    if self.config.MOD_REPLACE_WINDOW_NAME:
                        config.window_title = self.original_config['window_title']
                    renpy.config.mouse_displayable = None
                    config.main_menu_music = self.original_config['main_menu_music']
                else:
                    if self.config.MOD_REPLACE_WINDOW_NAME:
                        config.window_title = self.config.ORIGINAL_NAME
                    renpy.config.mouse_displayable = None
                    config.main_menu_music = self.config.ORIGINAL_MENU_MUSIC
                    
                self.logger.debug("Конфигурация восстановлена")
            except Exception as e:
                self.logger.error(u"Ошибка восстановления конфигурации: {}".format(e))
        
        def _apply_mod_config(self):
            """
            Применение конфигурации мода.
            """
            try:
                if self.config.MOD_REPLACE_WINDOW_NAME:
                    config.window_title = self.config.MOD_NAME
                if self.config.MOD_CURSOR_PATH:
                    renpy.config.mouse_displayable = MouseDisplayable(self.config.MOD_CURSOR_PATH, 0, 0)
                if self.config.MOD_MENU_MUSIC:
                    config.main_menu_music = self.config.MOD_MENU_MUSIC
                self.logger.debug("Конфигурация мода применена")
            except Exception as e:
                self.logger.error(u"Ошибка применения конфигурации мода: {}".format(e))
        
        def save_screens(self, screen_names=None):
            """
            Сохранение оригинальных экранов.
            
            Args:
                screen_names: Список имен экранов для сохранения.
                    Если None, сохраняются все экраны из конфигурации.
            
            Returns:
                bool: True если сохранение успешно
            """
            if screen_names is None:
                screen_names = self.config.DEFAULT_SCREENS

            saved_count = 0
            for name in screen_names:
                try:
                    if self._screen_exists(name):
                        original_key = (name, None)
                        backup_key = ("mod_backup_{}".format(name), None)

                        # Сохраняем только если еще не сохранен
                        if backup_key not in renpy.display.screen.screens:
                            renpy.display.screen.screens[backup_key] = renpy.display.screen.screens[original_key]
                            saved_count += 1
                            self.logger.debug(u"Экран '{}' сохранен".format(name))
                    else:
                        self.logger.warning(u"Экран '{}' не найден".format(name))

                except (KeyError, AttributeError) as e:
                    self.logger.error(u"Ошибка сохранения экрана '{}': {}".format(name, e))

            if saved_count > 0:
                self.logger.debug(u"Сохранено {} экранов".format(saved_count))
            else:
                self.logger.debug(u"Все экраны уже были сохранены ранее")
            return True  # Возвращаем True если нет ошибок, даже если ничего не сохранили
        
        def activate_screens(self, screen_names=None, partial=False):
            """
            Активация модифицированных экранов.
            
            Args:
                screen_names: Список имен экранов для замены.
                    Если None, заменяются все экраны из конфигурации.
                partial: Если True, добавляет экраны к уже активным.
                    Если False, заменяет все активные экраны.
            
            Returns:
                bool: True если активация успешна
            """
            if not self.check_compatibility():
                self.logger.warning("Проверка совместимости не пройдена")
            
            if not self.validate_configuration():
                self.logger.error("Валидация конфигурации не пройдена.")
                return False
                
            if screen_names is None:
                screen_names = self.config.DEFAULT_SCREENS
            
            # проверяем, не активны ли уже все запрошенные экраны
            if not partial:
                requested_set = set(screen_names)
                if self.is_active and requested_set == self.active_screens:
                    self.logger.debug(u"Запрошенные экраны уже активны, пропускаем активацию")
                    return True
                # Если не частичная замена и активны другие экраны, деактивируем их
                elif self.is_active:
                    self.deactivate_screens()
                
            # сохраняем экраны перед заменой, чтобы точно никто не забыл сохранить
            if not self.save_screens(screen_names):
                self.logger.error("Не удалось сохранить экраны")
                return False
                
            # сохраняем конфиг перед первой активацией
            if not self.is_active:
                self._backup_config()
                
            activated_count = 0
            for name in screen_names:
                try:
                    mod_screen_name = "{}_{}".format(self.config.MOD_ID, name)
                    
                    if self._screen_exists(mod_screen_name):
                        original_key = (name, None)
                        mod_key = (mod_screen_name, None)
                        
                        renpy.display.screen.screens[original_key] = renpy.display.screen.screens[mod_key]
                        self.active_screens.add(name)
                        activated_count += 1
                        self.logger.debug(u"Экран '{}' активирован".format(name))
                    else:
                        self.logger.warning(u"Модифицированный экран '{}' не найден".format(mod_screen_name))
                        
                except (KeyError, AttributeError) as e:
                    self.logger.error(u"Ошибка активации экрана '{}': {}".format(name, e))
                    
            if activated_count > 0:
                self._apply_mod_config()
                self.is_active = True
                self.logger.debug(u"Активировано {} экранов".format(activated_count))
                
            return activated_count > 0
        
        def deactivate_screens(self, screen_names=None):
            """
            Деактивация модифицированных экранов и восстановление оригиналов.
            
            Args:
                screen_names: Список имен экранов для восстановления.
                    Если None, восстанавливаются все активные экраны.
            
            Returns:
                bool: True если деактивация успешна
            """
            if screen_names is None:
                screen_names = list(self.active_screens)
                
            restored_count = 0
            for name in screen_names:
                try:
                    original_key = (name, None)
                    backup_key = ("mod_backup_{}".format(name), None)
                    
                    if backup_key in renpy.display.screen.screens:
                        renpy.display.screen.screens[original_key] = renpy.display.screen.screens[backup_key]
                        self.active_screens.discard(name)
                        restored_count += 1
                        self.logger.debug(u"Экран '{}' восстановлен".format(name))
                    else:
                        self.logger.warning(u"Резервная копия экрана '{}' не найдена".format(name))
                        
                except (KeyError, AttributeError) as e:
                    self.logger.error(u"Ошибка восстановления экрана '{}': {}".format(name, e))
                    
            # восстанавливаем конфиг если все экраны деактивированы
            if not self.active_screens:
                self._restore_config()
                self.is_active = False
                
            self.logger.debug(u"Восстановлено {} экранов".format(restored_count))
        
        def toggle_screen(self, screen_name):
            """
            Переключение состояния отдельного экрана.
            
            Args:
                screen_name: Имя экрана для переключения
                
            Returns:
                bool: True если экран теперь активен, False если деактивирован
            """
            if screen_name in self.active_screens:
                self.deactivate_screens([screen_name])
                return False
            else:
                self.activate_screens([screen_name], partial=True)
                return True
        
        def get_status(self):
            """
            Получение текущего статуса менеджера.
            
            Returns:
                dict: Словарь с информацией о состоянии
            """
            return {
                'is_active': self.is_active,
                'active_screens': list(self.active_screens),
                'total_screens': len(self.config.DEFAULT_SCREENS)
            }
        
        def after_load_callback(self):
            """
            Автоматическая активация мода после загрузки сохранения.
            Активируется если в имени сохранения есть идентификатор мода.
            """
            try:
                global save_name
                if (self.config.MOD_SAVE_IDENTIFIER in save_name) or (self.config.MOD_NAME in save_name):
                    self.activate_screens()
                    self.logger.debug("Мод активирован после загрузки")
            except NameError:
                # save_name может быть не определен
                self.logger.error("save_name не определен")
            except Exception as e:
                self.logger.error(u"Ошибка автоактивации: {}".format(e))

        def activate_screens_after_load(self):
            """Добавляем написанный нами коллбэк в список коллбэков после загрузки сохранения"""
            config.after_load_callbacks.append(self.after_load_callback)
