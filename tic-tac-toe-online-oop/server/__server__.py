from fastapi import FastAPI,WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import uvicorn
import json

class ConnectionManager():
    """ Класс для управления соединением с игроками """
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
          
    async def connect(self, websocket: WebSocket, game_id: int, player_name: str):
        """ При подключении разрешаем соединение и добавляем в список активных подключений """
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}
        self.active_connections[game_id][player_name] = websocket

    async def disconnect(self, game_id: int, player_name: str):
        """ При отключении разрываем соединение и удаляем из списка активных подключений """
        if game_id in self.active_connections and player_name in self.active_connections[game_id]:
            del self.active_connections[game_id][player_name]
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                   
    async def broadcast(self, game_id: int, message: str):
        """ Рассылает всем участникам определенной игры сообщение """
        if game_id in self.active_connections:
            for ws in self.active_connections[game_id].values():
                await ws.send_text(message)

    async def broadcast_game_state(self, gamemanager: 'GameManager', game_id: int):
        """ Рассылает всем участникам определенной игры ее состояние """
        game_state = gamemanager.get_game_state(game_id)
        if game_state:
            await self.broadcast(game_id, json.dumps(game_state))

    async def broadcast_game_over(self, gamemanager: 'GameManager', game_id: int):
        """ Рассылает всем участникам определенной игры сообщение об ее завершении """
        if game_id not in gamemanager.games:
            return
        
        game = gamemanager.games[game_id]
        message = json.dumps({
            "type": "game_over",
            "winner": "Ничья!" if game.winner == "draw" else game.winner
        })
        await self.broadcast(game_id, message)

class Player:
    """Класс для создания игроков"""
    def __init__(self, name: str, symbol: str, color: str):
        self.is_connected: bool = True
        self.name: str = name
        self.symbol: str = symbol
        self.color: str = color

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
    
    def clear_board(self):
        self.cells = [" "]*9

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

    def __init__(self, player1: Player, player2: Optional[Player]):
        self.players = [player1, player2]
        self.current_player_index = 0
        if player2 is not None:
            self.state = "in game"
        else: 
            self.state = "waiting"
        self.winner = ""
        self.board = Board()

    def get_current_player(self) -> Optional[Player]:
        """ Возвращает объект текущего игрока """
        return self.players[self.current_player_index]
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % 2

    def has_winner(self, symbol: str) -> bool:
        """ Проверяет, есть ли на доске выигрышная комбинация для определенного символа """
        board = self.board.get_board()
        for comb in self.winning_combinations:
            if all(board[i] == symbol for i in comb):
                return True
        return False
    
    def is_game_over(self) -> bool:
        return self.state == "finished"

    def update_game_state(self):
        """ Обновляет состояние игры """
        if self.state != "in game":
            return
        
        for player in self.players:
            if player and self.has_winner(player.symbol):
                self.winner = player.name
                self.state = "finished"
                return
        
        if self.board.is_full():
            self.winner = "draw"
            self.state = "finished"

    def reset_game(self):
        """ Сбрасывает состояние игры """
        self.board.clear_board()
        self.winner = ""
        self.current_player_index = 0
        self.state = "in game" if all(p.is_connected for p in self.players if p) else "waiting"

class GameManager:
    """ Класс для управления играми """
    def __init__(self):
        self.games: Dict[int, Game] = {}

    def connect_to_game(self, game_id: int, player_name: str) -> tuple[bool, str]:
        """ 
        Подключает пользователя к игре, если лобби не переполненно и в игре нет участника с тем же именем 
        Возвращает результат попытки присоединиться (True, "" or False, "error message")
        """
        # Если игра еще не была созданна, то создаем ее и добавляем первого игрока
        if game_id not in self.games:
            player1 = Player(player_name, "O", "blue")
            self.games[game_id] = Game(player1, None)
            return True, ""
   
        game = self.games[game_id]

        # Проверяет, есть ли в игре игрок с тем же именем, а также обновляет статус игры
        for player in game.players:
            if player and player.name == player_name:
                if player.is_connected:
                    return False, "Игрок уже подключен"
                player.is_connected = True
                game.state = "in game"
                return True, ""

        # Если игра уже была созданна, а имя игрока не совпадает с именем первого игрока, то добавляем игрока как второго, обновляем статус игры
        if game.players[1] is None:
            player2 = Player(player_name, "X", "red")
            game.players[1] = player2
            game.state = "in game"
            return True, ""
        
        return False, "Лобби переполнено"

    def disconnect_from_game(self, game_id: int, player_name: str):
        """ Отключает игрока с определенным именем от определенной игры """
        if game_id not in self.games:
            return
        
        game = self.games[game_id]

        # Помечаем игроков как отключенных
        for player in game.players:
            if player and player.name == player_name:
                player.is_connected = False
                break
    
        # Если игра была активна, то меняем статус на ожидает
        if game.state == "in game":
            game.state = "waiting"

        # Удаляем игру только если оба игрока отключены
        if all(not player.is_connected for player in game.players if player):
            del self.games[game_id]

    def get_game_state(self, game_id: int) -> Optional[Dict[str, str|object|None]]:
        """ 
        Пытается получить состояние определенной игры 
        Если получилось, возвращает полученное состояние
        """
        if game_id not in self.games:
            return None
        
        game = self.games[game_id]
        current_player = game.get_current_player()

        return {
            "type": "state",
            "board": game.board.get_board(),
            "current_player": current_player.name if current_player else "",
            "state": game.state,
            "winner": game.winner
        }

    def make_move(self, game_id: int, player_name: str, x: int, y: int):
        """ Пытается сделать ход по определенным координатам """
        if game_id not in self.games:
            return 

        game = self.games[game_id]

        if game.state != "in game":
            return

        current_player = game.get_current_player()
        
        if not current_player or current_player.name != player_name:
            return
        
        if not game.board.make_move(current_player, x, y):
            return
        
        game.update_game_state()
        
        if not game.is_game_over():
            game.next_player()

app = FastAPI()
app.state.connectionmanager = ConnectionManager()
app.state.gamemanager = GameManager()

@app.websocket("/ws/{game_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_name: str):
    connectionmanager: ConnectionManager = websocket.app.state.connectionmanager
    gamemanager: GameManager = websocket.app.state.gamemanager

    # Пытаемся подключить пользователя к игре
    success, error_msg = gamemanager.connect_to_game(game_id, player_name)

    # Если не получилось, отправляем сообщение ошибки
    if not success:
        await websocket.accept()
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": error_msg
        }))
        await websocket.close()
        return
    
    # Добавляем игрока в список активных подключений
    await connectionmanager.connect(websocket, game_id, player_name)

    try:
        # Сразу отправляем состояние игры всем игрокам
        await connectionmanager.broadcast_game_state(gamemanager, game_id)
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "get_state":
                """ Если клиент запросил состояние игры, рассылаем его """
                await connectionmanager.broadcast_game_state(gamemanager, game_id)

            elif message["type"] == "make_move":
                """ Если игрок отправил запрос о ходе, пытаемся его сделать """
                try:
                    x = int(message["x"])
                    y = int(message["y"])
                except (KeyError, ValueError):
                    continue
                
                # Пытаемся сделать ход по полученным из запроса координатам
                gamemanager.make_move(game_id, player_name, x, y)
                
                # Отправляем обновленное состояние
                await connectionmanager.broadcast_game_state(gamemanager, game_id)
                
                # Отправляем результат игры если игра завершена
                game = gamemanager.games.get(game_id)
                if game and game.state == "finished":
                    await connectionmanager.broadcast_game_over(gamemanager, game_id)
                    game.reset_game()
    
    except WebSocketDisconnect:
        # При отключении игрока помечаем его в игре отключенным, а также разрываем соединение
        gamemanager.disconnect_from_game(game_id, player_name)
        await connectionmanager.broadcast_game_state(gamemanager, game_id)
        await connectionmanager.disconnect(game_id, player_name)
        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", ws_ping_interval=20, ws_ping_timeout=20)