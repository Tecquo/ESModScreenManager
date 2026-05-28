# Mod Screen Manager

Менеджер экранов для модов на Бесконечное Лето

## Описание

Технический мод для Everlasting Summer, который позволяет заменять экраны интерфейса без конфликтов с другими модами.

## Важно

Mod Screen Manager работает только на Ren'Py 7.x. В восьмой версии архитектура экранов изменилась, и прямая замена через `renpy.display.screen.screens` больше не работает.

## Установка

Скопируйте `MSM.rpy` и `logger.rpy` в папку Вашего мода.

Из `example/` возьмите:
- `example.rpy.example` — настройка конфига и лейблы для теста работы мода
- `screens.rpy.example` — шаблоны экранов

`test_example.rpy.example` копировать необязательно, он нужен только если Вы хотите расширенно проверить работу менеджера экранов.

Переименуйте их в `.rpy` (уберите `.example`).

## Настройка

Откройте `example.rpy` и настройте `my_mod_ModScreenManagerConfig` под свой мод.

Замените `my_mod` на префикс Вашего мода везде в коде (`example.rpy` и `screens.rpy`). Запустите игру и проверьте, что всё работает.

Когда убедитесь, что менеджер работает, замените шаблоны в `screens.rpy` на свои экраны.

## Пример использования

```python
label my_mod_start:
    # Создаем глобальный экземпляр менеджера с нашим кастомным шаблоном
    $ my_mod_screen_manager = ModScreenManager(my_mod_ModScreenManagerConfig)

    # Устанавливаем имя сохранения с идентификатором мода (чтобы экраны автоматически включались при загрузке сохранения Вашего мода)
    $ save_name = my_mod_ModScreenManagerConfig.MOD_SAVE_IDENTIFIER

    # Включаем экраны
    $ my_mod_screen_manager.activate_screens()
    
    "Hello World!"

    jump my_mod_exit

label my_mod_exit:
    # Обязательно выключайте экраны при выходе
    $ my_mod_screen_manager.deactivate_screens()
    return
```