from styles import Styles
from button_factory import ButtonFactory
from PyQt5.QtWidgets import QGridLayout

class ButtonGrid():
    @staticmethod
    def create_buttons(window, grid: QGridLayout):
        buttons = [
            "+", "-", "*", "/", 
            "7", "8", "9", "C", 
            "4", "5", "6", "⌫", 
            "1", "2", "3", "=", 
            "0", "(", ")", "."
        ]

        x, y = 1, 1
        callback = None
        for i, button in enumerate(buttons, 1):
            if i in [8, 12, 16]:
                style = Styles.orange_button_style
                match button:
                    case "=": 
                        callback = window.on_equal
                    case "C": 
                        callback = lambda: window.clear_input() # noqa: E731
                    case "⌫": 
                        callback = window.on_backspace
            else:
                style = Styles.white_button_style
                callback = lambda _, b=button: window.on_button_click(b) # noqa: E731
            
            button = ButtonFactory.create_button(button, (80,80), style, callback)

            grid.addWidget(button, y, x)
            x = 1 if x >= 4 else x + 1
            y += 1 if x == 1 else 0
