from PyQt5.QtWidgets import QPushButton

class ButtonFactory():
    """ Класс для удобного создания кнопок """
    @staticmethod
    def create_button(text: str, size: tuple, style, callback) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.setStyleSheet(style)
        if callback:
            button.clicked.connect(callback)
        return button