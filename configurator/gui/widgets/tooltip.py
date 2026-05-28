"""тултипы - подсказки при наведении"""

import customtkinter as ctk
import tkinter as tk


class Tooltip:
    """окно тултипа которое появляется при наведении"""
    
    def __init__(self, widget, title: str, description: str, example: "str | None" = None):
        """
        создать тултип
        
        Args:
            widget: виджет к которому привязываем
            title: заголовок
            description: описание
            example: пример (опционально)
        """
        self.widget = widget
        self.title = title
        self.description = description
        self.example = example
        self.tooltip_window = None
        
        # используем after на виджете чтобы виджет точно был создан
        self.widget.after(100, self._setup_bindings)
    
    def _setup_bindings(self):
        """настроить обработчики событий после создания виджета"""
        try:
            self.widget.bind("<Enter>", lambda e: self._on_enter())
            self.widget.bind("<Leave>", lambda e: self._on_leave())
            self.widget.bind("<Button-1>", lambda e: self._on_click())
        except Exception:
            pass
    
    def _on_click(self, event=None):
        """показать/скрыть тултип по клику"""
        if self.tooltip_window:
            self._on_leave()
        else:
            self._on_enter()
    
    def _on_enter(self, event=None):
        """показать тултип"""
        if self.tooltip_window:
            return
        
        # позиция виджета
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty()
        
        # создаем окошко
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        # делаем окно всегда сверху
        self.tooltip_window.attributes('-topmost', True)
        
        # показываем окно
        self.tooltip_window.deiconify()
        
        # связываем с родительским окном для корректного поведения
        self.tooltip_window.transient(self.widget.winfo_toplevel())
        
        # вычисляем размеры тултипа (примерно)
        tooltip_width = 380
        tooltip_height = 150
        
        # получаем размеры экрана
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        # проверяем границы экрана - не даём тултипу выйти за пределы
        if x + 20 + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        if y + 20 + tooltip_height > screen_height:
            y = y - tooltip_height - 10
        
        self.tooltip_window.wm_geometry(f"+{x + 20}+{y + 20}")
        
        # настраиваем вид - используем обычный tk.Frame вместо CTkFrame
        self.tooltip_window.configure(bg="#2b2b2b")
        
        # контент - используем tk.Frame
        frame = tk.Frame(
            self.tooltip_window,
            bg="#2b2b2b",
            highlightthickness=1,
            highlightbackground="#3b3b3b"
        )
        frame.pack(fill="both", expand=True, padx=4, pady=4)
        
        # заголовок - используем tk.Label
        title_label = tk.Label(
            frame,
            text=self.title,
            font=("TkDefaultFont", 14, "bold"),
            fg="#ffffff",
            bg="#2b2b2b"
        )
        title_label.pack(anchor="w", padx=8, pady=(8, 4))
        
        # разделитель
        sep = tk.Frame(frame, height=1, bg="#3b3b3b")
        sep.pack(fill="x", padx=4, pady=4)
        
        # описание
        desc_label = tk.Label(
            frame,
            text=self.description,
            font=("TkDefaultFont", 12),
            fg="#cccccc",
            bg="#2b2b2b",
            wraplength=350,
            justify="left"
        )
        desc_label.pack(anchor="w", padx=8, pady=4)
        
        # пример (если есть)
        if self.example:
            example_label = tk.Label(
                frame,
                text=f"Пример:\n{self.example}",
                font=("TkDefaultFont", 11),
                fg="#888888",
                bg="#2b2b2b",
                wraplength=350,
                justify="left"
            )
            example_label.pack(anchor="w", padx=8, pady=(4, 8))
        else:
            # отступ снизу
            tk.Label(frame, text="", height=4, bg="#2b2b2b").pack()
    
    def _on_leave(self, event=None):
        """скрыть тултип"""
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except Exception:
                pass  # окно уже может быть уничтожено
            self.tooltip_window = None


class TooltipLabel(ctk.CTkLabel):
    """label со встроенным тултипом"""
    
    def __init__(self, parent, title: str, description: str, example: "str | None" = None, **kwargs):
        """
        создать лейбл с тултипом
        
        Args:
            parent: родительский виджет
            title: заголовок тултипа
            description: описание для тултипа
            example: пример для тултипа
            **kwargs: доп. аргументы для CTkLabel
        """
        super().__init__(parent, **kwargs)
        
        # кнопка помощи
        self.help_button = ctk.CTkButton(
            parent,
            text="(?)",
            width=24,
            height=24,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            border_width=0,
            text_color="#888888",
            hover_color="#555555"
        )
        
        # привязываем тултип
        self.tooltip = Tooltip(self.help_button, title, description, example)


class TooltipCheckBox(ctk.CTkCheckBox):
    """checkbox с тултипом"""
    
    def __init__(self, parent, screen_code: str, screen_name: str, 
                 screen_description: str, **kwargs):
        """
        создать чекбокс с тултипом
        
        Args:
            parent: родительский виджет
            screen_code: кодовое имя экрана
            screen_name: человеческое имя
            screen_description: описание для тултипа
            **kwargs: доп. аргументы для CTkCheckBox
        """
        super().__init__(parent, text=screen_name, **kwargs)
        
        # тултип на виджет
        self.tooltip = Tooltip(
            self,
            screen_name,
            f"Код: `{screen_code}`\n\n{screen_description}",
            f"Техническое имя: {screen_code}"
        )
