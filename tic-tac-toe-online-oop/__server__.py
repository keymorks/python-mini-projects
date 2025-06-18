import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
import uvicorn
from typing import Dict

games = {}

def connect_to_game(game_id: int, player_id: int):
    if game_id not in games:
        games[game_id] = {
            "board": [" "] * 9,
            "current_player": "O",
            "players": {}
        }

    if player_id not in games[game_id]["players"]:
        games[game_id]["players"][player_id] = "O" if len(games[game_id]["players"]) == 0 else "X"
        print(f"Добавлен игрок id:{player_id}")

def get_game_state(game_id: int):
    if game_id not in games:
        return None  # Или создайте новую игру, если нужно
    
    return {
        "type": "state",
        "board": games[game_id]["board"],
        "current_player": games[game_id]["current_player"]
    }

def make_move(game_id: int, player_id: int, position: int):
    if game_id not in games:
        return 
    
    game = games[game_id]

    if len(game["players"]) < 2:
        return

    if game["board"][position] != " ":
        return 
    
    if player_id not in game["players"]:
        game["players"][player_id] = "O" if len(game["players"]) == 0 else "X"

    player_symbol = game["players"][player_id]

    if player_symbol != game["current_player"]:
        return 
    
    game["board"][position] = player_symbol

    winner = has_winner(game["board"], player_symbol)

    if winner:
        return "win", player_symbol
    
    if is_board_full(game["board"]):
        return "draw", None

    games[game_id]["current_player"] = "O" if games[game_id]["current_player"] == "X" else "X"
    return "continue", None

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


def has_winner(board: list[str], symbol: str) -> bool:
    for comb in winning_combinations:
        if all(board[i] == symbol for i in comb):
            return True
    return False

def is_board_full(board: list[str]) -> bool:
    if " " not in board:
        return True
    return False

app = FastAPI()

class ConnectionManager():
    def __init__(self):
        # Создает переменную для хранения сокетов типа: [game_id: [player_id: WebSocket],]
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
          
    async def connect(self, websocket: WebSocket, game_id: int, player_id: int):
        """ Асинхронно разрешаем подключение и добавляем в список активных подключений """
        await websocket.accept() # Разрешаем соединение
        if game_id not in self.active_connections: # Если лобби игры не созданно
            self.active_connections[game_id] = {} # Создаем лобби
        self.active_connections[game_id][player_id] = websocket # Добавляем id и WebSocket в лобби

    async def disconnect(self, game_id: int, player_id: int):
        """ Удаляет пользователя из списка комнаты """
        if game_id in self.active_connections and player_id in self.active_connections[game_id]:
            del self.active_connections[game_id][player_id]
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                   
    async def broadcast(self, game_id: int, message: str):
        if game_id in self.active_connections:
            for ws in self.active_connections[game_id].values():
                await ws.send_text(message)


manager = ConnectionManager()

@app.get("/")
def get(request: Request):
	return "server is working"

@app.websocket("/ws/{game_id}/{player_id}")
async def connectgame(websocket: WebSocket, game_id: str, player_id: str):
    print(f"К лобби id:{game_id} присоединился игрок id:{player_id}")
    await manager.connect(websocket, int(game_id), int(player_id))
    connect_to_game(int(game_id), int(player_id))
    
    while True:
        try:
            data = await websocket.receive_text()
            print(data if data else None)
            try:
                message = json.loads(data)
                
                if message["type"] == "get_state":
                    print(f"Получено состояние игры id:{game_id} игроком id:{player_id}")
                    game_state = get_game_state(int(game_id))
                    await manager.broadcast(int(game_id), json.dumps(game_state))

                elif message["type"] == "make_move":
                    position = message["position"]

                    print(position)
                    print(get_game_state(int(game_id)))

                    result = make_move(int(game_id), int(player_id), position)
                    
                    if result[0] == "win": # type: ignore
                        winner = json.dumps({
                            "type": "close",
                            "winner": result[1] # type: ignore
                        })
                        await manager.broadcast(int(game_id), winner)
                        if int(game_id) in games:
                            del games[int(game_id)]
                    elif result[0] == "draw": # type: ignore
                        winner = json.dumps({
                            "type": "close",
                            "winner": "Ничья!"
                        })
                        await manager.broadcast(int(game_id), winner)
                        if int(game_id) in games:
                            del games[int(game_id)]
                    else:
                        game_state = get_game_state(int(game_id))
                        await manager.broadcast(int(game_id), json.dumps(game_state))
            except Exception as e:
                print(f"Server error: {e}")
        except WebSocketDisconnect:
            await manager.disconnect(int(game_id), int(player_id))
            print(f"Участник id:{player_id} игры id:{game_id} отключился")

if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")