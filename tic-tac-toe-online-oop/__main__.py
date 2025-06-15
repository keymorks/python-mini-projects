class Player:
    def __init__(self, symbol):
        self.symbol = symbol

class Board:
    def __init__(self):
        self.cells = [" "]*9

    def display(self):
        for i in [0,3,6]:
            print(f"{self.cells[i]}|{self.cells[i+1]}|{self.cells[i+2]}\n")
    
    def make_move(self, player: Player, x: int, y: int) -> bool:
        move_position = x + y*3
        if self.cells[move_position] != " " or not -1<x<3 or not -1<y<3:
            return False
        self.cells[move_position] = player.symbol
        return True

    def get_board(self) -> list[str]:
        return self.cells
    
    def is_full(self) -> bool:
        return " " not in self.cells

class Game:
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
        return self.players[self.current_player_index]
    
    def next_player(self):
        if self.current_player_index < (len(self.players)-1):
            self.current_player_index += 1
        else:
            self.current_player_index = 0

    def check_winner(self) -> bool:
        board = self.board
        cells = board.get_board()
        current_player = self.get_current_player()

        for comb in self.winning_combinations:
            if cells[comb[0]] == current_player.symbol and cells[comb[1]] == current_player.symbol and cells[comb[2]] == current_player.symbol:
                self.winner = current_player.symbol
                self.state = "finished"
                return True

        if board.is_full():
            self.winner = "even score"
            self.state = "finished"
            return True
        return False


def main():
    while True:
        player1 = Player("O")
        player2 = Player("X")
        game = Game(player1, player2)
        print("Игра началась")
        while game.state == "in game":
            current_player = game.get_current_player()
            move = input(f"Ход {current_player.symbol}, напишите x и y через ' ': ").split()
            try:
                x = int(move[-2])-1
                y = int(move[-1])-1

                succes = game.board.make_move(current_player, x, y)
                if succes:
                    game.board.display()
                    game.check_winner()

                    if game.state == "finished":
                        if game.winner == "even score":
                            print("Ничья")
                            break
                        else:
                            print(f"Побдил: {game.winner}")
                            break

                    game.next_player()
                else:
                    raise
            except Exception:
                print("Не верные координаты хода")

        if not is_need_new_game():
            break

def is_need_new_game() -> bool:
    while True:
        try:
            is_need_new_game = input("Начать новую игру? (yes/no): ").split()
            if is_need_new_game[-1] == "no":
                return False
            elif is_need_new_game[-1] == "yes":
                return True
        except (ValueError, IndexError):
            pass
 
if __name__ == "__main__":
	main()