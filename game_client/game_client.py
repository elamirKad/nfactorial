import random
import os
import keyboard


class Board:
    def __init__(self, size=3):
        self.size = size
        self.board = self.create_board(size)

    @classmethod
    def create_board(cls, size):
        return [[0 for x in range(size)] for y in range(size)]

    def check_cell_empty(self, x, y):
        return self.board[x][y] == 0

    def create_random_tile(self):
        while True:
            x, y = random.randint(0, 2), random.randint(0, 2)
            if self.check_cell_empty(x, y):
                self.board[x][y] = 2
                break

    def draw_board(self):
        os.system('cls')
        for i, row in enumerate(self.board):
            print(' | '.join([str(el) for el in row]))
            if i < self.size - 1:
                print("-" * (self.size ** 2))

    def move_up(self):
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == 0: continue
                for k in range(i-1, -1, -1):
                    if self.board[i][j] == self.board[k][j]:
                        self.board[i][j] = 0
                        self.board[k][j] *= 2
                        break
                    elif self.board[k][j] != 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[k+1][j] = temp
                        break
                    elif k == 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[k][j] = temp

        self.create_random_tile()
        self.draw_board()

    def move_down(self):
        self.board = self.board[::-1]
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == 0: continue
                for k in range(i-1, -1, -1):
                    if self.board[i][j] == self.board[k][j]:
                        self.board[i][j] = 0
                        self.board[k][j] *= 2
                        break
                    elif self.board[k][j] != 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[k+1][j] = temp
                        break
                    elif k == 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[k][j] = temp
        self.board = self.board[::-1]
        self.create_random_tile()
        self.draw_board()

    def move_left(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                for k in range(j-1, -1, -1):
                    if self.board[i][j] == self.board[i][k]:
                        self.board[i][j] = 0
                        self.board[i][k] *= 2
                        break
                    elif self.board[i][k] != 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[i][k+1] = temp
                        break
                    elif k == 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[i][k] = temp
        self.create_random_tile()
        self.draw_board()

    def move_right(self):
        for i in range(len(self.board)):
            self.board[i] = self.board[i][::-1]
            for j in range(len(self.board[i])):
                for k in range(j-1, -1, -1):
                    if self.board[i][j] == self.board[i][k]:
                        self.board[i][j] = 0
                        self.board[i][k] *= 2
                        break
                    elif self.board[i][k] != 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[i][k+1] = temp
                        break
                    elif k == 0:
                        temp = self.board[i][j]
                        self.board[i][j] = 0
                        self.board[i][k] = temp
            self.board[i] = self.board[i][::-1]
        self.create_random_tile()
        self.draw_board()





def main():
    quit_flag = False
    board = Board(3)
    board.create_random_tile()
    board.create_random_tile()
    board.draw_board()
    keyboard.add_hotkey('q', lambda: setattr(quit_flag, 'value', True))
    keyboard.add_hotkey('w', board.move_up)
    keyboard.add_hotkey('s', board.move_down)
    keyboard.add_hotkey('a', board.move_left)
    keyboard.add_hotkey('d', board.move_right)
    while not quit_flag:
        pass


if __name__ == "__main__":
    main()