from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt  
from styles import GameStyles
import sys

class Player:
    """Класс для создания игроков"""
    def __init__(self, symbol: str, color: str):
        self.symbol = symbol
        self.color = color

class Board:
    """Класс для создания поля 3x3 для крестиков-ноликов"""
    def __init__(self):
        self.cells = [" "]*9
    
    def make_move(self, player: Player, x: int, y: int) -> bool:
        """
        Пытается сделать ход игрока в указанную позицию
        Возвращает True если ход допустим, иначе False
        """
        move_position = x + y*3
        if self.cells[move_position] != " " or not 0<=x<3 or not 0<=y<3:
            return False
        self.cells[move_position] = player.symbol
        return True

    def get_board(self) -> list[str]:
        """ Возвращает текущее состояние игрового поля """
        return self.cells
    
    def is_full(self) -> bool:
        return " " not in self.cells

class Game:
    """ Класс для создания игры """
    winning_combinations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]

    def __init__(self, player1: Player, player2: Player):
        self.players = [player1, player2]
        self.current_player_index = 0
        self.state = "in game"
        self.winner = ""
        self.board = Board()

    def get_current_player(self) -> Player:
        """ Возвращает текущего игрока """
        return self.players[self.current_player_index]
    
    def next_player(self):
        if self.current_player_index < (len(self.players)-1):
            self.current_player_index += 1
        else:
            self.current_player_index = 0

    @staticmethod
    def has_winner(board: list[str], symbol: str) -> bool:
        for comb in Game.winning_combinations:
            if all(board[i] == symbol for i in comb):
                return True
        return False
    
    def is_game_over(self) -> bool:
        return self.state == "finished"

    def update_game_state(self):
        board = self.board
        cells = board.get_board()
        current_player = self.get_current_player()

        if self.has_winner(cells, current_player.symbol):
            self.winner = current_player.symbol
            self.state = "finished"

        if board.is_full():
            self.winner = "even score"
            self.state = "finished"

class Window(QMainWindow):
    """ Создает окно игры """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe")
        self.setFixedSize(700, 700)
        self.setStyleSheet(GameStyles.background_style)

        # Используем QStackedWidget для переключения между экранами
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Создаем экраны
        self.menu_widget = QWidget()
        self.game_widget = QWidget()
        self.retry_menu_widget = QWidget()
        
        # Добавляем их в стак для переключения
        self.stack.addWidget(self.menu_widget)
        self.stack.addWidget(self.game_widget)
        self.stack.addWidget(self.retry_menu_widget)
        
        # Подгатавливаем виджеты для экранов
        self.setup_menu()
        self.setup_game()
        self.setup_retry_menu()
        
        self.stack.setCurrentWidget(self.menu_widget)

    def setup_menu(self):
        """ Подготавливает главное меню """
        layout = QVBoxLayout() # Холст для виджетов

        title = QLabel("Выберите режим:") # Заголовок меню
        title.setStyleSheet(GameStyles.menu_title_style)
        layout.addWidget(title, alignment=Qt.AlignCenter)

        btn_local = QPushButton("Локальная игра") # Кнопка локальной игры
        btn_local.clicked.connect(lambda: self.on_local_game_click()) 
        btn_local.setFixedSize(250, 65)
        btn_local.setStyleSheet(GameStyles.menu_button_style)
        layout.addWidget(btn_local, alignment=Qt.AlignCenter)

        layout.addStretch() # Заполняем пустое пространство между краями экрана и виджетами
        layout.setContentsMargins(50, 250, 50, 250) # Окончательно выравниваем виджеты
        
        self.menu_widget.setLayout(layout) # Подготовка окончена, сохраняем

    def setup_game(self):
        """ Подготавливает меню для игры """
        main_layout = QVBoxLayout() # Холст для виджетов
        self.grid_layout = QGridLayout() # Холст-сетка для игрового поля

        # Выравниваем кнопки
        self.grid_layout.setHorizontalSpacing(0) 
        self.grid_layout.setVerticalSpacing(10) 
    
        self.grid_layout.setContentsMargins(80, 20, 80, 20) # Создаем отступы для содержимого

        self.game_label = QLabel() # Отображает текущего игрока
        self.game_label.setAlignment(Qt.AlignCenter)
        self.game_label.setFixedHeight(50)
        self.game_label.setStyleSheet(GameStyles.game_label_style)
        main_layout.addWidget(self.game_label)
        
        # Создаем кнопки игрового поля
        self.buttons = []
        for row in range(3):
            for col in range(3):
                btn = QPushButton()
                btn.setFixedSize(160, 160)  
                btn.setStyleSheet(GameStyles.game_button_style)
                btn.clicked.connect(lambda _, r=row, c=col: self.on_cell_click(r, c))
                self.grid_layout.addWidget(btn, row, col)
                self.buttons.append(btn)
        
        main_layout.addLayout(self.grid_layout) # Добавляем холст-сетку с игровым полем на главный холст
        self.game_widget.setLayout(main_layout) # Подготовка окончена, сохраняем

    def setup_retry_menu(self):
        """ Подготавливает меню результата """
        main_layout = QVBoxLayout() # Главный холст

        main_layout.addStretch() # Заполняем пустое пространство
        main_layout.setContentsMargins(50, 125, 50, 275) # Создаем отступы для содержимого
        
        self.retry_label = QLabel() # Отображает результат игры
        self.retry_label.setAlignment(Qt.AlignCenter)
        self.retry_label.setFixedHeight(50)
        self.retry_label.setStyleSheet(GameStyles.menu_title_style)
        main_layout.addWidget(self.retry_label)

        btn_retry = QPushButton("Играть заново") # Кнопка для повторной игры
        btn_retry.clicked.connect(self.restart_game)
        btn_retry.setFixedSize(250, 65)
        btn_retry.setStyleSheet(GameStyles.menu_button_style)
        main_layout.addWidget(btn_retry, alignment=Qt.AlignCenter)

        btn_menu = QPushButton("Меню") # Кнопка для выхода в меню
        btn_menu.clicked.connect(self.back_to_menu)
        btn_menu.setFixedSize(250, 65)
        btn_menu.setStyleSheet(GameStyles.menu_button_style)
        main_layout.addWidget(btn_menu, alignment=Qt.AlignCenter)

        self.retry_menu_widget.setLayout(main_layout) # Подготовка окончена, сохраняем

    def on_cell_click(self, row, col):
        """ Обрабатывает клик по клетке игрового поля """
        # Проверяем, что игра активна
        if not hasattr(self, 'game') or self.game.state != "in game":
            return
        
        btn: QPushButton = self.buttons[row*3 + col] # Получаем кнопку по координатам
        
        # Игнорируем занятые клетки
        if btn.text():
            return
        
        # Обновляем UI и игровое состояние
        current_player = self.game.get_current_player()
        btn.setText(current_player.symbol) 
        btn.setStyleSheet(f"{GameStyles.game_button_style}".replace("{color}", current_player.color))
    
        # Обновляем игровую логику
        if self.game.board.make_move(current_player, row, col):
            self.game.update_game_state()
            if self.game.is_game_over():
                self.show_game_result()

        # Переключаем игрока
        self.game.next_player()
        self.game_label.setText(f"Ход: {self.game.get_current_player().symbol}")

    def show_game_result(self):
        """ Переключает в меню результата """
        winner = self.game.winner
        if winner == "even score":
            msg = "Ничья!"
        else:
            msg = f"Победил: {winner}"
        
        self.retry_label.setText(msg)
        self.stack.setCurrentWidget(self.retry_menu_widget)  
    
    def on_local_game_click(self):
        """ Обрабатывает клик по кнопке создания локальной игры """
        self.game = Game(Player("O", "blue"), Player("X", "red"))
        self.game_label.setText(f"Ход: {self.game.get_current_player().symbol}")
        self.clear_board()
        self.stack.setCurrentWidget(self.game_widget)  

    def restart_game(self):
        self.stack.setCurrentWidget(self.game_widget)
        self.on_local_game_click()

    def back_to_menu(self):
        self.stack.setCurrentWidget(self.menu_widget)

    def clear_board(self):
        for btn in self.buttons:
            btn.setText("")
            btn.setStyleSheet(GameStyles.game_button_style)
        
def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    main()