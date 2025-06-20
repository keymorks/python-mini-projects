import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
import uvicorn
from typing import Dict

class ConnectionManager():
    def __init__(self):
        # Создает переменную для хранения сокетов типа: [game_id: [player_id: WebSocket],]
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
          
    async def connect(self, websocket: WebSocket, game_id: int, player_name: str):
        """ Асинхронно разрешаем подключение и добавляем в список активных подключений """
        await websocket.accept() # Разрешаем соединение
        if game_id not in self.active_connections: # Если лобби игры не созданно
            self.active_connections[game_id] = {} # Создаем лобби
        self.active_connections[game_id][player_name] = websocket # Добавляем id и WebSocket в лобби

    async def disconnect(self, game_id: int, player_name: str):
        """ Удаляет пользователя из списка комнаты """
        if game_id in self.active_connections and player_name in self.active_connections[game_id]:
            del self.active_connections[game_id][player_name]
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                   
    async def broadcast(self, game_id: int, message: str):
        if game_id in self.active_connections:
            for ws in self.active_connections[game_id].values():
                await ws.send_text(message)

    async def broadcast_game_state(self, manager: 'ConnectionManager', gamemanager: 'GameManager', game_id: int):
        game_state = gamemanager.get_game_state(game_id)
        if game_state:
            await manager.broadcast(game_id, json.dumps(game_state))

    async def broadcast_game_over(self, manager: 'ConnectionManager', gamemanager: 'GameManager', game_id: int):
        winner = gamemanager.games[game_id]["game"].winner
        if winner == "draw":
            message = json.dumps({
                "type": "game_over",
                "winner": "Ничья!"
            })
        else:
            message = json.dumps({
                "type": "game_over",
                "winner": winner
            })

        await manager.broadcast(game_id, message)

class Player:
    """Класс для создания игроков"""
    def __init__(self, name: str, symbol: str, color: str):
        self.name = name
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
            self.winner = current_player.name
            self.state = "finished"

        if board.is_full():
            self.winner = "draw"
            self.state = "finished"


class GameManager:
    def __init__(self):
        self.games = {}

    def connect_to_game(self, game_id: int, player_name: str):
        print(self.games) 

        if game_id not in self.games:
            self.games[game_id] = {
                "game": None,
                "players": {}
            }

        self.games[game_id]["players"][player_name] = Player(player_name, "O", "blue") if len(self.games[game_id]["players"]) == 0 else Player(player_name, "X", "red")

        if len(self.games[game_id]["players"]) >= 2:
            self.games[game_id]["game"] = Game(*self.games[game_id]["players"].values())

        print(self.games) 

    def disconnect_from_game(self, game_id: int, player_name: str):
        del self.games[game_id]["players"][player_name]
        del self.games[game_id]["game"]

    def get_game_state(self, game_id: int):
        if game_id not in self.games:
            return None 
        
        if not self.games[game_id]["game"]:
            return None
        
        game: Game = self.games[game_id]["game"]
        state = {
            "type": "state",
            "board": game.board.get_board(),
            "current_player": game.get_current_player().name,
            "state": game.state,
            "winner": game.winner
        }

        print(state)
        return state

    def make_move(self, game_id: int, player_name: str, x: int, y: int):
        if game_id not in self.games:
            return 
        
        game: Game = self.games[game_id]["game"]

        if len(game.players) < 2:
            return

        if game.board.cells[y*3 + x] != " ":
            return 
        
        print("Дошло до проверки на наличие в игре")
        if player_name not in self.games[game_id]["players"]:
            return
        print("Перешло проверку на наличие в игре")

        current_player: Player = game.get_current_player()
        
        print("Дошло до проверки")
        if not self.games[game_id]["players"][player_name].name == current_player.name:
            return 
        
        print("Дошло до хода")
        game.board.make_move(current_player, x, y)

        game.update_game_state()

        state = game.state

        if state == "finished":
            return

        game.next_player()

app = FastAPI()
app.state.connectionmanager = ConnectionManager()
app.state.gamemanager = GameManager()

@app.get("/")
def get(request: Request):
	return "server is working"

@app.websocket("/ws/{game_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_name: str):
    connectionmanager: ConnectionManager = websocket.app.state.connectionmanager
    gamemanager: GameManager = websocket.app.state.gamemanager

    await connectionmanager.connect(websocket, game_id, player_name)
    gamemanager.connect_to_game(game_id, player_name)
    
    while True:
        try:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message["type"] == "get_state":
                    await connectionmanager.broadcast_game_state(connectionmanager, gamemanager, game_id)

                elif message["type"] == "make_move":
                    row = message["row"]
                    col = message["col"]
            
                    gamemanager.make_move(game_id, player_name, col, row)
                    await connectionmanager.broadcast_game_state(connectionmanager, gamemanager, game_id)
                    game_state = gamemanager.games[game_id]["game"].state
                    print(gamemanager.games)
                    print(gamemanager.games[game_id]["game"].board.get_board())
                    print(game_state)
                    print(gamemanager.games[game_id]["game"].winner)
                    
                    if game_state == "finished":
                        await connectionmanager.broadcast_game_over(connectionmanager, gamemanager, game_id)
                        del gamemanager.games[game_id]
                    else:
                        await connectionmanager.broadcast_game_state(connectionmanager, gamemanager, game_id)
            except Exception as e:
                print(f"Server error: {e}")
        except WebSocketDisconnect:
            gamemanager.disconnect_from_game(game_id, player_name)
            await connectionmanager.disconnect(game_id, player_name)

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", ws_ping_interval=20, ws_ping_timeout=20)