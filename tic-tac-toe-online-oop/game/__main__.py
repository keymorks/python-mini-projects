from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QGridLayout, QLineEdit
from PyQt5 import QtWidgets
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtCore import Qt, QUrl, QTimer
from styles import GameStyles
import sys
import json

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
        """ Возвращает объект текущего игрока """
        return self.players[self.current_player_index]
    
    def next_player(self):
        if self.current_player_index < (len(self.players)-1):
            self.current_player_index += 1
        else:
            self.current_player_index = 0

    @staticmethod
    def has_winner(board: list[str], symbol: str) -> bool:
        """ Проверяет, есть ли на доске выигрышная комбинация для определенного символа """
        for comb in Game.winning_combinations:
            if all(board[i] == symbol for i in comb):
                return True
        return False
    
    def is_game_over(self) -> bool:
        return self.state == "finished"

    def update_game_state(self):
        """ Обновляет состояние игры """
        board = self.board
        cells = board.get_board()
        current_player = self.get_current_player()

        if self.has_winner(cells, current_player.symbol):
            self.winner = current_player.symbol
            self.state = "finished"
            
        elif board.is_full():
            self.winner = "draw"
            self.state = "finished"

class WidgetFactory:
    """ Класс для удобного создания виджетов """
    def create_button(self, text: str, size, style, on_click=None) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.setStyleSheet(style)
        if on_click:
            button.clicked.connect(on_click)
        return button
    
    def create_label(self, text: str, style, font_size=None) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(style)
        if isinstance(font_size, int):
            label.setStyleSheet("font-size: {font_size}px;".replace("{font_size}", str(font_size)))
        return label
    
    def create_line_edit(self, placeholder: str, size, style) -> QLineEdit:
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedSize(*size)
        line_edit.setStyleSheet(style)
        return line_edit

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
        self.online_menu_widget = QWidget()
        
        # Добавляем их в стак для переключения
        self.stack.addWidget(self.menu_widget)
        self.stack.addWidget(self.game_widget)
        self.stack.addWidget(self.retry_menu_widget)
        self.stack.addWidget(self.online_menu_widget)

        self.factory = WidgetFactory()
        
        # Подгатавливаем виджеты для экранов
        self.setup_menu()
        self.setup_game()
        self.setup_retry_menu()

        self.setup_online_menu()
        self.online_game = None
        self.saved_ip = None
        self.saved_game_id = None
        self.seved_player_name = None
        
        self.stack.setCurrentWidget(self.menu_widget)

    def add_to_layout(self, layout: QVBoxLayout, widget, alignment=Qt.AlignCenter): # type: ignore
        layout.addWidget(widget, alignment=alignment)

    def setup_menu(self):
        """ Подготавливает главное меню """
        layout = QVBoxLayout() # Холст для виджетов

        # Заголовок меню
        menu_title = self.factory.create_label("Выберите режим:", GameStyles.menu_title_style) 
        self.add_to_layout(layout, menu_title)

        # Кнопка локальной игры
        local_game_button = self.factory.create_button("Локальная игра", GameStyles.menu_button_size, GameStyles.menu_button_style, self.on_local_game_click) 
        self.add_to_layout(layout, local_game_button)

        # Кнопка онлайн игры
        online_game_button = self.factory.create_button("Онлайн игра", GameStyles.menu_button_size, GameStyles.menu_button_style, self.on_online_game_click) 
        self.add_to_layout(layout, online_game_button)

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

        # Текст для отображения состояния игры
        self.game_label = self.factory.create_label("", GameStyles.game_label_style, 50)
        self.add_to_layout(main_layout, self.game_label)
        
        # Создаем кнопки игрового поля
        self.buttons = []
        for row in range(3):
            for col in range(3):
                btn = QPushButton()
                btn.setFixedSize(*GameStyles.game_button_size)  
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
        
        # Текст для отображения исхода игры
        self.retry_label = self.factory.create_label("", GameStyles.menu_title_style, 25)
        self.add_to_layout(main_layout, self.retry_label)

        # Кнопка играть заново
        retry_button = self.factory.create_button("Играть заново", GameStyles.menu_button_size, GameStyles.menu_button_style, self.restart_game)
        self.add_to_layout(main_layout, retry_button)

        # Кнопка вернуться в меню
        back_to_menu_button = self.factory.create_button("Меню", GameStyles.menu_button_size, GameStyles.menu_button_style, self.back_to_menu)
        self.add_to_layout(main_layout, back_to_menu_button)
        
        self.retry_menu_widget.setLayout(main_layout) # Подготовка окончена, сохраняем

    def setup_online_menu(self):
        """ Подготавливает меню результата """
        main_layout = QVBoxLayout() # Главный холст

        main_layout.addStretch() # Заполняем пустое пространство
        main_layout.setContentsMargins(50, 100, 50, 225) # Создаем отступы для содержимого
        
        # Текст, который отображает статус подключения
        self.status = self.factory.create_label("", GameStyles.menu_title_style, 40)
        self.add_to_layout(main_layout, self.status)

        # Текст для дополнительной информации и ошибок
        self.substatus = self.factory.create_label("", GameStyles.menu_title_style, 20)
        self.add_to_layout(main_layout, self.substatus)

        # Поле для ввода ip
        self.server_ip_input = self.factory.create_line_edit("IP сервера", GameStyles.input_size, GameStyles.input_style)
        self.add_to_layout(main_layout, self.server_ip_input)

        # Поле для ввода ip комнаты
        self.game_id_input = self.factory.create_line_edit("ID игры", GameStyles.input_size, GameStyles.input_style)
        self.add_to_layout(main_layout, self.game_id_input)

        # Поле для ввода имени игрока
        self.nickname_input = self.factory.create_line_edit("Ваш ник", GameStyles.input_size, GameStyles.input_style)
        self.add_to_layout(main_layout, self.nickname_input)

        # Кнопка подключиться
        connect_button = self.factory.create_button("Подключиться", GameStyles.menu_button_size, GameStyles.menu_button_style, self.on_connect_click)
        self.add_to_layout(main_layout, connect_button)

        # Кнопка назад
        back_to_menu_button = self.factory.create_button("Меню", GameStyles.menu_button_size, GameStyles.menu_button_style, self.back_to_menu)
        self.add_to_layout(main_layout, back_to_menu_button)

        self.online_menu_widget.setLayout(main_layout) # Подготовка окончена, сохраняем

    def on_cell_click(self, y: int, x: int):
        """ Обрабатывает клик по клетке игрового поля """
        position = y*3 + x
        btn = self.buttons[position] # Получаем кнопку по координатам
        
        # Если игра запущенна в онлайн режиме, то отправляем запрос о ходе, если нет, то делаем ход в локальной игре
        if self.online_game:
            if self.online_game.status == "Connected":
                self.online_game.make_move(y, x)
        else:
            if not hasattr(self, 'game') or self.game is None:
                return
        
            # Игнорируем занятые клетки
            if btn.text():
                return
            
            # Обновляем UI и игровое состояние
            current_player = self.game.get_current_player()
            btn.setText(current_player.symbol) 
            btn.setStyleSheet(f"{GameStyles.game_button_style}".replace("{color}", current_player.color))
        
            # Обновляем игровую логику
            if self.game.board.make_move(current_player, y, x):
                self.game.update_game_state()
                if self.game.is_game_over():
                    self.show_game_result(self.game.winner)

            # Переключаем игрока
            self.game.next_player()
            self.game_label.setText(f"Ход: {self.game.get_current_player().symbol}")

    def show_game_result(self, winner: str):
        """ Переключает в меню результата """
        if winner == "draw":
            msg = "Ничья!"
        else:
            msg = f"Победил: {winner}"
        
        self.retry_label.setText(msg) # Отображаем результат игры
        self.stack.setCurrentWidget(self.retry_menu_widget)  
    
    def on_local_game_click(self):
        """ Обрабатывает клик по кнопке создания локальной игры """
        self.game = Game(Player("O", GameStyles.color_O), Player("X", GameStyles.color_X))
        self.game_label.setText(f"Ход: {self.game.get_current_player().symbol}")
        self.clear_board()
        self.stack.setCurrentWidget(self.game_widget)  

    def on_online_game_click(self):
        """ Обрабатывает клик по кнопке создания сетевой игры """
        if self.saved_ip:
            self.server_ip_input.setText(self.saved_ip)
        if self.saved_game_id:
            self.game_id_input.setText(self.saved_game_id)
        if self.seved_player_name:
            self.nickname_input.setText(self.seved_player_name)
            
        self.stack.setCurrentWidget(self.online_menu_widget)

    def on_connect_click(self):
        """ Обрабатывает клик по кнопке подключения """
        ip = self.server_ip_input.text().strip()
        game_id = self.game_id_input.text().strip()
        player_name = self.nickname_input.text().strip()

        if not ip:
            self.substatus.setText("Введите IP сервера")
            return
        if not player_name:
            self.substatus.setText("Введите ваш ник")
            return
        if " " in player_name:
            self.substatus.setText("Ник не должен содержать пробелы")
            return
        
        self.saved_ip = ip
        self.saved_game_id = game_id
        self.seved_player_name = player_name

        self.status.setText("Connecting")
        self.substatus.setText("")

        self.online_game = OnlineGame(self.saved_ip, self.saved_game_id, self.seved_player_name, self)

        self.stack.setCurrentWidget(self.game_widget)

    def update_online_board(self, board: list, current_player: str):
        """ Метод для обновления доски онлайн игрой """
        self.clear_board()
        for i, symbol in enumerate(board):
            btn = self.buttons[i]
            if symbol == " ":
                continue
            btn.setText(symbol)
            match symbol:
                case "X":
                    color = GameStyles.color_X
                case "O":
                    color = GameStyles.color_O
                case _:
                    color = GameStyles.color_neutral
            btn.setStyleSheet(GameStyles.game_button_style.replace("{color}", color))

        self.game_label.setText(f"Ход: {current_player}")

    def restart_game(self):
        """ Обрабатывает клик по кнопке играть заново """
        if self.online_game is None:
            self.stack.setCurrentWidget(self.game_widget)
            self.on_local_game_click()
        else:
            # Пересоздаем подключение
            ip = self.saved_ip
            game_id = self.saved_game_id
            player_id = self.seved_player_name
            
            # Закрываем старое подключение
            if self.online_game.websocket:
                self.online_game.websocket.close()
            
            # Создаем новое подключение
            self.online_game = OnlineGame(ip, game_id, player_id, self) # type: ignore
            self.clear_board()
            self.stack.setCurrentWidget(self.game_widget)

    def back_to_menu(self):
        """ Обрабатывает клик по кнопке назад """
        if self.online_game and self.online_game.websocket: 
            self.online_game.websocket.close()
        self.online_game = None
        self.stack.setCurrentWidget(self.menu_widget)

    def clear_board(self):
        """ Очищает доску от старых символов и цветов """
        for btn in self.buttons:
            btn.setText("")
            btn.setStyleSheet(GameStyles.game_button_style.replace("{color}", "black"))
        
class OnlineGame:
    """ Класс, позволяющий создать онлайн игру """
    def __init__(self, ip: str, game_id: str, player_name: str, window: Window):
        self.ip = ip
        self.game_id = game_id
        self.player_name = player_name 
        self.websocket = QWebSocket()
        self.status = "Connecting"
        self.window = window
        self.status_label = window.status
        self.sub_status_label = window.substatus
        self.game_active = True 

        # Подключаем обработчики событий
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_message)
        self.websocket.error.connect(self.on_error)
        
        # Подключение
        url = QUrl(f"ws://{ip}/ws/{game_id}/{player_name}")
        self.websocket.open(url)
    
    def on_connected(self):
        self.set_connection_status("Connected")
        self.set_sub_status("")
        self.window.stack.setCurrentWidget(self.window.game_widget)
        self.get_game_state()

    def on_disconnected(self):
        self.set_connection_status("Disconnected")
        self.set_sub_status("Соединение разорвано")
        self.window.stack.setCurrentWidget(self.window.online_menu_widget)

    def on_message(self, message: str):
        try:
            data = json.loads(message)
            match data["type"]:
                case "state":
                    self.window.update_online_board(data["board"], data["current_player"])

                    if not self.game_active:
                        self.game_active = True
                    
                case "game_over":
                    winner = data["winner"]
                    if winner == "draw":
                        self.window.show_game_result("draw")
                    else:
                        self.window.show_game_result(winner)
                    
                    self.game_active = False
                    
                    QTimer.singleShot(2000, self.get_game_state)
                    
                case "error":
                    error_msg = data["error"]
                    self.set_sub_status(error_msg)
                    self.window.stack.setCurrentWidget(self.window.online_menu_widget)
                case _:
                    print(f"Unknown message type: {data['type']}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def on_error(self, error: str):
        self.set_connection_status("Error")
        self.set_sub_status(str(error))
        self.window.stack.setCurrentWidget(self.window.online_menu_widget)

    def make_move(self, y: int, x: int):
        message = json.dumps({
                "type": "make_move",
                "y": y,
                "x": x
            })
        self.websocket.sendTextMessage(message)

    def get_game_state(self):
        message = json.dumps({
            "type": "get_state",
        })
        self.websocket.sendTextMessage(message)

    def set_connection_status(self, status: str):
        self.status = status
        self.status_label.setText(self.status)

    def set_sub_status(self, status: str):
        self.sub_status_label.setText(status)

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    main()