python early:
    from builtins import all


    class _MSM_Aliases:
        MOD_NAME = "MOD_NAME"
        MOD_ID = "MOD_ID"
        MOD_SAVE_IDENTIFIER = "MOD_SAVE_IDENTIFIER"
        MOD_REPLACE_WINDOW_NAME = "MOD_REPLACE_WINDOW_NAME"
        MOD_CURSOR_PATH = "MOD_CURSOR_PATH"
        MOD_MENU_MUSIC = "MOD_MENU_MUSIC"

        DEFAULT_SCREENS = "DEFAULT_SCREENS"
        GAME_MENU_SELECTOR = "game_menu_selector"

        LOGGING = "LOGGING"
        LOG_LEVEL = "LOG_LEVEL"

    class _MSMKeywords:
        MANAGER_TAG = "tag"
        MANAGER_CONFIG = "config"
        SUBBLOCK_DELIM = ':'

        MOD_NAME = "mod_name"
        MOD_ID = "mod_id"

        MOD_SAVE_IDENTIFIER = "savename"
        MOD_REPLACE_WINDOW_NAME = "window_name"
        MOD_CURSOR_PATH = "cursor"
        MOD_MENU_MUSIC = "menu_music"

        LOGGING = "logging"
        LOG_LEVEL = "log_level"

        SCREENS_ES_ALL = "es_all"

    def msm_parse_screen_manager_create(lexer):
        data = { }

        data[_MSMKeywords.MANAGER_TAG] = lexer.word()
        lexer.require(_MSMKeywords.SUBBLOCK_DELIM)
        lexer.expect_eol()

        data[_MSMKeywords.MANAGER_CONFIG] = _msm_parse_config(lexer.subblock_lexer())

        return data

    def _msm_parse_config(lexer):
        config = { }
        seen = {
                _MSM_Aliases.MOD_NAME: False,
                _MSM_Aliases.MOD_ID: False,
                _MSM_Aliases.DEFAULT_SCREENS: False
                }

        while lexer.advance():
            if lexer.keyword(_MSMKeywords.MOD_NAME):
                config[_MSM_Aliases.MOD_NAME] = lexer.string()
                seen[_MSM_Aliases.MOD_NAME] = True
            elif lexer.keyword(_MSMKeywords.MOD_ID):
                config[_MSM_Aliases.MOD_ID] = lexer.string()
                seen[_MSM_Aliases.MOD_ID] = True
            elif lexer.keyword(_MSM_Aliases.DEFAULT_SCREENS):
                if lexer.keyword(_MSMKeywords.SCREENS_ES_ALL):
                    config[_MSM_Aliases.DEFAULT_SCREENS] = _MSMKeywords.SCREENS_ES_ALL
                elif lexer.match(_MSMKeywords.SUBBLOCK_DELIM):
                    config[_MSM_Aliases.MOD_NAME] = _msm_parse_default_screens(lexer.subblock_lexer())
                else:
                    renpy.error("Некорректное определение базовых экранов. Доступен параметр 'es_all' или ручная конфигурация в подблоке.")
                seen[_MSM_Aliases.DEFAULT_SCREENS] = True
            
            elif lexer.keyword(_MSMKeywords.MOD_SAVE_IDENTIFIER):
                config[_MSM_Aliases.MOD_SAVE_IDENTIFIER] = lexer.string()
            elif lexer.keyword(_MSMKeywords.MOD_REPLACE_WINDOW_NAME):
                config[_MSM_Aliases.MOD_REPLACE_WINDOW_NAME] = lexer.simple_expression()
            elif lexer.keyword(_MSMKeywords.MOD_CURSOR_PATH):
                config[_MSM_Aliases.MOD_CURSOR_PATH] = lexer.simple_expression()
            elif lexer.keyword(_MSMKeywords.MOD_MENU_MUSIC):
                config[_MSM_Aliases.MOD_MENU_MUSIC] = lexer.simple_expression()
            elif lexer.keyword(_MSMKeywords.LOGGING):
                config[_MSM_Aliases.LOGGING] = lexer.simple_expression()
            elif lexer.keyword(_MSMKeywords.LOG_LEVEL):
                config[_MSM_Aliases.LOG_LEVEL] = lexer.integer()

        if not all(seen.values()):
            missing_keys = [key for key, value in seen.items() if not value]
            missing_names = {
                _MSM_Aliases.MOD_NAME: "название мода",
                _MSM_Aliases.MOD_ID: "идентификатор мода", 
                _MSM_Aliases.DEFAULT_SCREENS: "базовые экраны"
            }
            
            missing_list = ", ".join([missing_names.get(key, key) for key in missing_keys])
            renpy.error("Обязательные параметры конфигурации отсутствуют: {}. Все параметры должны быть определены.".format(missing_list))

        return config

    def _msm_parse_default_screens(lexer):
        screens = set()
        seen = { _MSM_Aliases.GAME_MENU_SELECTOR }

        while lexer.advance():
            screen_name = lexer.string()
            if not screen_name:
                renpy.error("Некорректное название экрана")
            if screen_name in screens:
                renpy.error("Экран '{}' уже был объявлен ранее".format(screen_name))
                
            screens.add(screen_name)
        
        missing_screens = seen - screens
        if missing_screens:
            screen_list = ", ".join(missing_screens)
            renpy.error("Отсутствуют обязательные экраны: {}".format(screen_list))
        
        return screens

    def msm_execute_init_manager_create(data):
        config = data[_MSMKeywords.MANAGER_CONFIG].copy()
        _msm_eval_logger_data(config)
        _msm_eval_optional_data(config)

        screen_manager_config = ModScreenManagerConfig()

        for atribute, value in config.items():
            setattr(screen_manager_config, atribute, value)
        
        if data[_MSMKeywords.MANAGER_TAG] in _msm_defined_managers:
            renpy.error("Менеджер экранов с тегом '{}' уже существует. Теги менеджеров должны быть уникальными.".format(data[_MSMKeywords.MANAGER_TAG]))
        _msm_defined_managers[data[_MSMKeywords.MANAGER_TAG]] = ModScreenManager(screen_manager_config)
    
    def _msm_eval_optional_data(config):
        config[_MSM_Aliases.MOD_REPLACE_WINDOW_NAME] = config.get(_MSM_Aliases.MOD_REPLACE_WINDOW_NAME, False)
        config[_MSM_Aliases.MOD_CURSOR_PATH] = config.get(_MSM_Aliases.MOD_CURSOR_PATH, False)
        config[_MSM_Aliases.MOD_MENU_MUSIC] = config.get(_MSM_Aliases.MOD_MENU_MUSIC, False)

    def _msm_eval_logger_data(config):
        logging = config.get(_MSM_Aliases.LOGGING, "False")
        log_level = config.get(_MSM_Aliases.LOG_LEVEL, "20")

        if logging not in ["False", "True"]:
            renpy.error("Параметр 'logging' должен иметь значение 'True' или 'False'. Получено: '{}'.".format(logging))
        
        config[_MSM_Aliases.LOGGING] = eval(logging)
        config[_MSM_Aliases.LOG_LEVEL] = eval(log_level)

    renpy.register_statement("msm config", msm_parse_screen_manager_create, execute_init=msm_execute_init_manager_create, block="possible")

    #-------------------------------------------------------------------------------------------------------#

    def msm_parse_screen_manager_savename(lexer):
        data = { }

        data[_MSMKeywords.MANAGER_TAG] = lexer.word()
        data[_MSM_Aliases.MOD_SAVE_IDENTIFIER] = lexer.simple_expression()

        lexer.expect_eol()

        return data

    def msm_execute_screen_manager_savename(data):
        screen_manager = _msm_defined_managers.get(data[_MSMKeywords.MANAGER_TAG], None)
        save_name = data[_MSM_Aliases.MOD_SAVE_IDENTIFIER]

        if screen_manager is None:
            renpy.error("Менеджер экранов с тегом '{}' не найден. Убедитесь, что была создана конфигурация для создания менеджера.".format(data[_MSMKeywords.MANAGER_TAG]))
        
        if save_name == "save_name":
            save_name = eval(save_name)

        setattr(screen_manager.config, _MSM_Aliases.MOD_SAVE_IDENTIFIER, save_name)

    renpy.register_statement("msm savename", msm_parse_screen_manager_savename, None, msm_execute_screen_manager_savename)

    #-------------------------------------------------------------------------------------------------------#

    def msm_parse_screen_manager_activate(lexer):
        data = { }
        
        data[_MSMKeywords.MANAGER_TAG] = lexer.word()
        lexer.expect_eol()
        
        return data

    def msm_execute_screen_manager_activate(data):
        screen_manager = _msm_defined_managers.get(data[_MSMKeywords.MANAGER_TAG], None)
        
        if screen_manager is None:
            renpy.error("Менеджер экранов с тегом '{}' не найден. Нельзя активировать несуществующий менеджер.".format(data[_MSMKeywords.MANAGER_TAG]))
        
        screen_manager.activate_screens()

    renpy.register_statement("msm activate", msm_parse_screen_manager_activate, None, msm_execute_screen_manager_activate)

    #-------------------------------------------------------------------------------------------------------#

    def msm_parse_screen_manager_deactivate(lexer):
        data = { }
        
        data[_MSMKeywords.MANAGER_TAG] = lexer.word()
        lexer.expect_eol()
        
        return data

    def msm_execute_screen_manager_deactivate(data):
        screen_manager = _msm_defined_managers.get(data[_MSMKeywords.MANAGER_TAG], None)
        
        if screen_manager is None:
            renpy.error("Менеджер экранов с тегом '{}' не найден. Нельзя деактивировать несуществующий менеджер.".format(data[_MSMKeywords.MANAGER_TAG]))
        
        screen_manager.deactivate_screens()

    renpy.register_statement("msm deactivate", msm_parse_screen_manager_deactivate, None, msm_execute_screen_manager_deactivate)

    #-------------------------------------------------------------------------------------------------------#
