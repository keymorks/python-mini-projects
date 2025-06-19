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
        winner = gamemanager.games[game_id]["winner"]
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

class GameManager:
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
    def __init__(self):
        self.games = {}

    def connect_to_game(self, game_id: int, player_name: str):
        if game_id not in self.games:
            self.games[game_id] = {
                "board": [" "] * 9,
                "current_player": "O",
                "players": {},
                "state": "in game",
                "winner": ""
            }

        if player_name not in self.games[game_id]["players"]:
            self.games[game_id]["players"][player_name] = "O" if len(self.games[game_id]["players"]) == 0 else "X"

    def get_game_state(self, game_id: int):
        if game_id not in self.games:
            return None 
        
        return {
            "type": "state",
            "board": self.games[game_id]["board"],
            "current_player": self.games[game_id]["current_player"],
            "state": self.games[game_id]["state"],
            "winner": self.games[game_id]["winner"]
        }

    def make_move(self, game_id: int, player_name: str, position: int):
        if game_id not in self.games:
            return 
        
        game = self.games[game_id]

        if len(game["players"]) < 2:
            return

        if game["board"][position] != " ":
            return 
        
        if player_name not in game["players"]:
            game["players"][player_name] = "O" if len(game["players"]) == 0 else "X"

        player_symbol = game["players"][player_name]

        if player_symbol != game["current_player"]:
            return 
        
        game["board"][position] = player_symbol

        self.update_game_state(game_id)
        state = game["state"]

        if state == "finished":
            return

        self.games[game_id]["current_player"] = "O" if self.games[game_id]["current_player"] == "X" else "X"
    
    def update_game_state(self, game_id: int):
        if game_id not in self.games:
            return
        
        game = self.games[game_id]
        board = game["board"]
        current_player = game["current_player"]

        if self.has_winner(board, current_player):
            self.games[game_id]["winner"] = current_player
            self.games[game_id]["state"] = "finished"

        elif self.is_board_full(board):
            self.games[game_id]["winner"] = "draw"
            self.games[game_id]["state"] = "finished"

    def has_winner(self, board: list[str], symbol: str) -> bool:
        for comb in self.winning_combinations:
            if all(board[i] == symbol for i in comb):
                return True
        return False

    def is_board_full(self, board: list[str]) -> bool:
        if " " not in board:
            return True
        return False

app = FastAPI()
app.state.manager = ConnectionManager()
app.state.gamemanager = GameManager()

@app.get("/")
def get(request: Request):
	return "server is working"

@app.websocket("/ws/{game_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_name: str):
    manager: ConnectionManager = websocket.app.state.manager
    gamemanager: GameManager = websocket.app.state.gamemanager

    await manager.connect(websocket, game_id, player_name)
    gamemanager.connect_to_game(game_id, player_name)
    
    while True:
        try:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message["type"] == "get_state":
                    await manager.broadcast_game_state(manager, gamemanager, game_id)

                elif message["type"] == "make_move":
                    position = message["position"]
            
                    gamemanager.make_move(game_id, player_name, position)
                    await manager.broadcast_game_state(manager, gamemanager, game_id)
                    game_state = gamemanager.games[game_id]["state"]
                    
                    if game_state == "finished":
                        await manager.broadcast_game_over(manager, gamemanager, game_id)
                        del gamemanager.games[game_id]
                    else:
                        await manager.broadcast_game_state(manager, gamemanager, game_id)
            except Exception as e:
                print(f"Server error: {e}")
        except WebSocketDisconnect:
            await manager.disconnect(game_id, player_name)

if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", ws_ping_interval=20, ws_ping_timeout=20)