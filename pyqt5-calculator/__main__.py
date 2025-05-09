from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QTextCodec
from PyQt5.QtGui import QIcon
from pathlib import Path
import sys
import os


class Window(QMainWindow):
    def __init__(self):
        self.j = []

        # Создание и настройка окна
        super(Window, self).__init__()
        QTextCodec.setCodecForLocale(QTextCodec.codecForName("UTF-8"))
        self.setGeometry(700, 400, 320, 480)  
        self.setFixedSize(320, 480)
        self.setStyleSheet("background-color: #ffffff;")

        self.setWindowTitle("Calculator")
        self.setWindowIconText("Calculator")

        icon_path = os.path.join(Path(__file__).parent, "icon.png")
        self.setWindowIcon(QIcon(icon_path))
        QCoreApplication.setApplicationName("Calculator")

        os.environ['QT_QPA_PLATFORM'] = 'xcb' 
        os.environ['QT_XCB_NATIVE_PAINTING'] = '0'
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_STYLE_OVERRIDE'] = 'Fusion'

        os.environ['RESOURCE_NAME'] = "calculator"
        os.environ['WM_CLASS'] = "calculator,Calculator"
        os.environ['XDG_CURRENT_DESKTOP'] = "GNOME" 

        # Создание кнопок и поля вывода результата
        self.area = QtWidgets.QScrollArea(self)  
        self.area.horizontalScrollBar().setStyleSheet("""QScrollBar:horizontal {
                                    border: none;
                                    background: #f0f0f0;
                                    height: 10px;
                                    margin: 0px;
                                }
                                QScrollBar::handle:horizontal {
                                    background: #ff9500;
                                    min-width: 20px;
                                    border-radius: 5px;
                                }
                                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                                    background: none;
                                }
                                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                                    background: none;
                                }
                                QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {
                                    background: #ff9500;
                                }
                                """)
        self.area.setGeometry(0, 0, 320, 80)  
        self.area.setWidgetResizable(True)
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  

        self.scroll_widget = QtWidgets.QWidget()  
        self.area.setWidget(self.scroll_widget) 

        self.text = QtWidgets.QLabel(self.scroll_widget)  
        self.text.setText("Введите пример..")
        self.text.setStyleSheet("font-size: 20px; padding: 5px;")  
        self.text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.text.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.scroll_widget.setLayout(QtWidgets.QHBoxLayout())
        self.scroll_widget.layout().addWidget(self.text)
        self.scroll_widget.layout().setContentsMargins(0, 0, 0, 0)

        buttons = [
            {"text": "+", "pos": (0, 80), "style": "white", "connect": "Update"},
            {"text": "-", "pos": (80, 80), "style": "white", "connect": "Update"},
            {"text": "*", "pos": (160, 80), "style": "white", "connect": "Update"},
            {"text": "/", "pos": (240, 80), "style": "white", "connect": "Update"},
            {"text": "7", "pos": (0, 160), "style": "white", "connect": "Update"},
            {"text": "8", "pos": (80, 160), "style": "white", "connect": "Update"},
            {"text": "9", "pos": (160, 160), "style": "white", "connect": "Update"},
            {"text": "4", "pos": (0, 240), "style": "white", "connect": "Update"},
            {"text": "5", "pos": (80, 240), "style": "white", "connect": "Update"},
            {"text": "6", "pos": (160, 240), "style": "white", "connect": "Update"},
            {"text": "1", "pos": (0, 320), "style": "white", "connect": "Update"},
            {"text": "2", "pos": (80, 320), "style": "white", "connect": "Update"},
            {"text": "3", "pos": (160, 320), "style": "white", "connect": "Update"},
            {"text": "0", "pos": (0, 400), "style": "white", "connect": "Update"},
            {"text": "(", "pos": (80, 400), "style": "white", "connect": "Update"},
            {"text": ")", "pos": (160, 400), "style": "white", "connect": "Update"},
            {"text": ".", "pos": (240, 400), "style": "white", "connect": "Update"},
            {"text": "=", "pos": (240, 320), "style": "orange", "connect": "Result",},
            {"text": "⌫", "pos": (240, 240), "style": "orange", "connect": "Pop"},
            {"text": "C", "pos": (240, 160), "style": "orange", "connect": "Clear"},
        ]

        for btn in buttons:
            self.button = QtWidgets.QPushButton(btn["text"], self)
            if btn["connect"] == "Update":
                self.button.clicked.connect(lambda _, t=btn["text"]: self.UpdateText(t))
            elif btn["connect"] == "Result":
                self.button.clicked.connect(lambda: self.Result())
            elif btn["connect"] == "Pop":
                self.button.clicked.connect(lambda: self.PopText())
            elif btn["connect"] == "Clear":
                self.button.clicked.connect(lambda: self.ClearText())

            self.button.setFixedSize(80, 80)
            self.button.setStyleSheet("font-size: 20px;")
            self.button.move(*btn["pos"])
            if btn["style"] == "white":
                self.button.setStyleSheet("""QPushButton {
                                        background-color: #ffffff;
                                        color: black;
                                        border-radius: 10px;
                                        border: 2px solid #dedede;
                                        font-size: 18px;
                                        font-weight: bold;
                                    }
                                    QPushButton:pressed {
                                        background-color: #f6f6f6;
                                    }
                                    """)
            elif btn["style"] == "orange":
                self.button.setStyleSheet("""QPushButton {
                                        background-color: #ff8e00;
                                        color: white;
                                        border-radius: 10px;
                                        border: 2px solid #f18600;
                                        font-size: 18px;
                                        font-weight: bold;
                                    }
                                    QPushButton:pressed {
                                        background-color: #f18600;
                                    }
                                    """)
            elif btn["style"] == "longorange":
                self.button.setFixedSize(80, 160)
                self.button.setStyleSheet("""QPushButton {
                                        background-color: #ff8e00;
                                        color: white;
                                        border-radius: 10px;
                                        border: 2px solid #f18600;
                                        font-size: 18px;
                                        font-weight: bold;
                                    }
                                    QPushButton:pressed {
                                        background-color: #f18600;
                                    }
                                    """)

        self.show()
        sys.exit(app.exec_())

    def UpdateText(self, symbol: str):
        if symbol == '-' and (not self.j or self.j[-1] in '+-*/('):
            self.j.append(symbol)
        else:
            self.j.append(symbol)

        self.text.setText(
            str(self.j)
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace(",", "")
            .replace(" ", "")
        )
        self.scroll_to_end()

    def a(self, tokens):
        result = self.b(tokens)
        while len(tokens) > 0 and tokens[0] in ("+", "-"):
            token = tokens.pop(0)
            right = self.b(tokens)
            if token == "+":
                result += right
            else:
                result -= right
        return result

    def b(self, tokens):
        result = self.c(tokens)
        while len(tokens) > 0 and tokens[0] in ("*", "/"):
            token = tokens.pop(0)
            right = self.c(tokens)
            if token == "*":
                result *= right
            else:
                result /= right
        return result

    def c(self, tokens):
        token = tokens.pop(0)
        if token == "(":
            result = self.a(tokens)
            tokens.pop(0)
        else:
            result = float(token)
        return result

    def scroll_to_end(self):
        scroll_bar = self.area.horizontalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def Result(self):
        try:
            tokens = (
            str(self.j)
                .replace('--', '+')
                .replace('+-', '-')
                .replace('-+', '-')
                .replace('++', '+')
                .replace(" ", "")
                .replace("+", " + ")
                .replace("-", " - ")
                .replace("*", " * ")
                .replace("/", " / ")
                .replace("(", " ( ")
                .replace(")", " ) ")
                .replace("[", "")
                .replace("]", "")
                .replace(",", "")
                .replace("'", "")
                .split()
            )

            i = 0
            while i < len(tokens):
                if tokens[i] == '-' and (i == 0 or tokens[i-1] in '+-*/('):
                    tokens[i+1] = '-' + tokens[i+1]
                    del tokens[i]
                i += 1

            self.result = self.a(tokens)
            self.text.setText(str(round(self.result, 2)))
            self.j.clear()
            self.j.append(str(round(self.result, 2)))
        
        except ZeroDivisionError:
            self.text.setText("Деление на ноль.")
            self.j = []
        except IndexError:
            self.text.setText("Незакрытая скобка.")
            self.j = []
        except Exception:
            self.text.setText("Ошибка в выражении")
            self.j = []

    def PopText(self):
        if self.j:
            self.j.pop(-1)
            self.text.setText(
                str(self.j)
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .replace(",", "")
                .replace(" ", "")
            )
            if(len(self.j)==0):
                self.text.setText("Введите пример..")
        else:
            self.text.setText("Введите пример..")

    def ClearText(self):
        self.j.clear()
        self.text.setText("Введите пример..")


if __name__ == "__main__":
    # Создание приложения
    app = QApplication(sys.argv)
    window = Window()