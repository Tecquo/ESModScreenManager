"""
Mod Screen Manager configurator
тут мы делаем GUI чтобы мододелы не ебали мозг с ручной настройкой
"""

import sys
import os

# получаем корневую папку (родитель configurator)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# переходим в папку configurator
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from gui.app import ModScreenManagerApp


def main():
    """точка входа в приложуху"""
    app = ModScreenManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
