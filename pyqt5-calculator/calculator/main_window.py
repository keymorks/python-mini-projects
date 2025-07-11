from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon
from pathlib import Path
from styles import Styles
from button_grid import ButtonGrid
from calculator_logic import CalculatorLogic
import os

class MainWindow(QMainWindow):
    """ Создает окно приложения """
    def __init__(self):
        super().__init__()
        self.setGeometry(680, 400, 320, 480)
        self.setFixedSize(320, 480)
        self.setStyleSheet(Styles.window_style)

        # Настройка названия окна
        self.setWindowTitle("Calculator")
        self.setWindowIconText("Calculator")
        QCoreApplication.setApplicationName("Calculator")

        # Настройка иконки окна
        icon_path = os.path.join(Path(__file__).parent, "icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.user_input = []
        self.main_widget = QWidget() # Создаем главный виджет

        self.setup_main_window() # Подготавливаем элементы окна

        self.setCentralWidget(self.main_widget) # Указываем виджет как центральный

    def setup_main_window(self):
        """ Подготавливает элементы окна """
        # Создаем главный холст
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Область прокрутки для поля вывода
        self.scroll_area = QScrollArea()
        self.scroll_area.setFixedHeight(80)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # type: ignore
        self.scroll_area.setStyleSheet(Styles.scroll_area_style)
        
        # Поле вывода выражения и его результата
        self.text = QLabel("Введите пример..")
        self.text.setFixedHeight(75)
        self.scroll_area.setWidget(self.text)
        main_layout.addWidget(self.scroll_area)

        # Сетка кнопок
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setVerticalSpacing(0)
        grid_layout.setHorizontalSpacing(0)

        ButtonGrid.create_buttons(self, grid_layout)
        main_layout.addLayout(grid_layout) # Добавляем на главный холст сетку кнопок

    def on_button_click(self, symbol: str):
        """ Обрабатывает нажатие цифровых кнопок и операторов """
        self.user_input.append(symbol)
        display_text = ''.join(self.user_input)
        self.text.setText(display_text)
        self.text.setMinimumWidth(self.text.fontMetrics().boundingRect(display_text).width() + 30)
        self.scroll_to_end()

    def scroll_to_end(self):
        """ Прокручивает поле прокрутки до конца """
        scroll_bar = self.scroll_area.horizontalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())  # type: ignore

    def update_scroll_size(self):
        """ Обновляет размер поля прокрутки """
        self.scroll_area.setMinimumWidth(self.text.sizeHint().width() + 30)

    def on_equal(self):
        """ 
        Обрабатывает нажатие кнопки "="
        1. Подгатавливает выражение
        2. При помощи класса CalculatorLogic получает результат выражения
        3. Обновляет текст на дисплее
        """
        try:
            remove_chars = " []',"
            translation_table = str.maketrans('', '', remove_chars)
            s = str(self.user_input).translate(translation_table)

            s = s.replace('--', '+').replace('+-', '-').replace('-+', '-').replace('++', '+')

            for char in "+-*/()":
                s = s.replace(char, f' {char} ')
            
            tokens = s.split()

            i = 0
            while i < len(tokens):
                if tokens[i] == '-' and (i == 0 or tokens[i-1] in '+-*/(') and i+1 < len(tokens):
                    tokens[i+1] = '-' + tokens[i+1]
                    del tokens[i]
                else:
                    i += 1

            recourse = CalculatorLogic()
            self.result = recourse.a(tokens)
            result_str = str(round(self.result, 2))
            self.text.setText(result_str)
            self.user_input.clear()
            self.user_input.append(result_str)
            self.update_scroll_size()
            self.scroll_to_end()
        
        except ZeroDivisionError:
            self.clear_input("Деление на ноль.")
        except IndexError:
            self.clear_input("Незакрытая скобка.")
        except Exception:
            self.clear_input("Ошибка в выражении")

    def on_backspace(self):
        """ 
        Обрабатывает клик по кнопке "⌫" 
        Удаляет поледний символ
        """
        if self.user_input:
            self.user_input.pop(-1)
            display_text = ''.join(self.user_input)
            self.text.setText(display_text if display_text else "Введите пример..")
        else:
            self.clear_input()
        self.update_scroll_size()

    def clear_input(self, message: str | None="Введите пример.."):
        """ 
        Обрабатывает клик по кнопке очищения ("C")
        Полностью очищает экран
        """
        self.user_input.clear()
        self.text.setText(str(message))
        self.update_scroll_size()