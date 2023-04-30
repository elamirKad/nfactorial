import random
import os
import sys
import time

import pygame
from threading import Thread
import socket
import ast
import argparse
from bot.final_bot import predict_next_move


pygame.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (171, 191, 38),
    8192: (143, 188, 38),
    16384: (115, 185, 38),
    32768: (87, 182, 38),
    65536: (59, 179, 38),
    131072: (31, 176, 38),
    262144: (0, 173, 38),
    524288: (0, 162, 255),
    1048576: (0, 143, 255),
}


class Board:
    def __init__(self, clientsocket, score, size, state=None):
        self.clientsocket = clientsocket
        self.size = size
        if state is None:
            self.board = self.create_board(size)
        else:
            self.board = state
        self.score = score
        self.tile_size = 80
        self.padding = 10
        self.screen_size = (self.tile_size * size + self.padding * (size + 1)+200,
                            self.tile_size * size + self.padding * (size + 1)+100)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.stats = {}
        pygame.display.set_caption("Game")

    @classmethod
    def create_board(cls, size):
        return [[0 for x in range(size)] for y in range(size)]

    def calculate_score(self, increase):
        self.score += increase

    def check_cell_empty(self, x, y):
        return self.board[x][y] == 0

    def create_random_tile(self):
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    empty_cells.append((i, j))

        if empty_cells:
            x, y = random.choice(empty_cells)
            self.board[x][y] = random.choice([2, 4])
            return True
        else:
            return False

    def draw_sidebar(self):
        sidebar_width = 200
        sidebar_x = self.tile_size * self.size + self.padding * (self.size + 2)
        sidebar_y = 0
        sidebar_height = self.tile_size * self.size + self.padding * (self.size + 1) + 100
        sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_width, sidebar_height)
        pygame.draw.rect(self.screen, GREY, sidebar_rect)

        font = pygame.font.SysFont(None, 20)
        y_offset = self.padding * 2
        for username, score in self.stats.items():
            score_text = font.render(f"{username}: {score}", True, BLACK)
            self.screen.blit(score_text, (sidebar_x + self.padding, sidebar_y + y_offset))
            y_offset += font.size(f"{username}: {score}")[1] + self.padding

    def draw_board(self):
        self.screen.fill(WHITE)
        font = pygame.font.SysFont(None, 40)
        score_text = font.render(f"Your score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (self.padding, self.padding))

        for i, row in enumerate(self.board):
            for j, tile in enumerate(row):
                tile_rect = pygame.Rect((j + 1) * self.padding + j * self.tile_size,
                                        (i + 1) * self.padding + i * self.tile_size + 100,
                                        self.tile_size, self.tile_size)
                if tile in TILE_COLORS:
                    tile_color = TILE_COLORS[tile]
                else:
                    tile_color = GREY
                pygame.draw.rect(self.screen, tile_color, tile_rect)
                if tile != 0:
                    tile_text = font.render(str(tile), True, BLACK)
                    text_rect = tile_text.get_rect(center=tile_rect.center)
                    self.screen.blit(tile_text, text_rect)

            if i < self.size - 1:
                line_rect = pygame.Rect(self.padding, (i + 2) * self.padding + (i + 1) * self.tile_size + 100,
                                        self.tile_size * self.size + self.padding * (self.size + 1) - 2 * self.padding,
                                        self.padding)
                pygame.draw.rect(self.screen, BLACK, line_rect)

        self.draw_sidebar()
        pygame.display.flip()

    def move_up(self):
        increase = 0
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == 0: continue
                for k in range(i-1, -1, -1):
                    if self.board[i][j] == self.board[k][j]:
                        increase += self.board[i][j]
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

        result = self.create_random_tile()
        self.calculate_score(increase)
        self.draw_board()
        return result

    def move_down(self):
        self.board = self.board[::-1]
        increase = 0
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == 0: continue
                for k in range(i-1, -1, -1):
                    if self.board[i][j] == self.board[k][j]:
                        increase += self.board[i][j]
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
        result = self.create_random_tile()
        self.calculate_score(increase)
        self.draw_board()
        return result

    def move_left(self):
        increase = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                for k in range(j-1, -1, -1):
                    if self.board[i][j] == self.board[i][k]:
                        increase += self.board[i][j]
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
        result = self.create_random_tile()
        self.calculate_score(increase)
        self.draw_board()
        return result

    def move_right(self):
        increase = 0
        for i in range(len(self.board)):
            self.board[i] = self.board[i][::-1]
            for j in range(len(self.board[i])):
                for k in range(j-1, -1, -1):
                    if self.board[i][j] == self.board[i][k]:
                        increase += self.board[i][j]
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
        result = self.create_random_tile()
        self.calculate_score(increase)
        self.draw_board()
        return result

    def reset_game(self):
        self.create_board(self.size)
        self.create_random_tile()
        self.create_random_tile()

    def show_game_over_screen(self):
        game_over_screen = pygame.Surface(self.screen.get_size())
        game_over_screen.fill(WHITE)
        font = pygame.font.SysFont(None, 60)

        message = font.render("Game over", True, BLACK)
        message_rect = message.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2 - 50))
        game_over_screen.blit(message, message_rect)

        self.screen.blit(game_over_screen, (0, 0))
        pygame.display.flip()

    def get_current_state(self):
        matrix = self.board
        score = self.score
        return (matrix, score, ())

    def handle_bot_move(self, move):
        move_func = {
            "left": self.move_left,
            "right": self.move_right,
            "up": self.move_up,
            "down": self.move_down
        }

        if move in move_func:
            return move_func[move]()
        else:
            raise ValueError(f"Invalid move: {move}")


def fetch_stats(clientsocket, board):
    while True:
        try:
            stats = clientsocket.recv(1024).decode()
            command, stats = stats.split('\r\n')
            for stat in stats.split(';'):
                user, score = stat.split(':')
                score = int(score)
                board.stats[user] = score
            # print(board.stats)
            board.draw_sidebar()
            pygame.display.flip()
        except:
            pass


def has_no_zeros(arr):
    for row in arr:
        for elem in row:
            if elem == 0:
                return True
    return False


def connect_to_server(username, password):
    clientsocket = socket.socket()
    clientsocket.connect((socket.gethostname(), 2048))
    auth_msg = f'AUTH\r\n{username}\r\n{password}'
    auth_msg = auth_msg.encode().decode('unicode_escape').encode("raw_unicode_escape")
    clientsocket.send(auth_msg)
    return clientsocket


def process_auth_result(auth_result):
    command, record, score, state = auth_result.split('\r\n')
    score = int(score)
    size = 0
    if state != 'None':
        state = ast.literal_eval(state)
        state = [[int(cell) if isinstance(cell, str) and cell.isdigit() else cell
                  for cell in row] for row in state]
        size = len(state)
        if not has_no_zeros(state):
            state = 'None'
    return score, state, size


def handle_key_event(event, board):
    if event.key == pygame.K_LEFT:
        return board.move_left()
    elif event.key == pygame.K_RIGHT:
        return board.move_right()
    elif event.key == pygame.K_UP:
        return board.move_up()
    elif event.key == pygame.K_DOWN:
        return board.move_down()


def send_score(clientsocket, board):
    while True:
        time.sleep(2)
        send = f'UPD\r\n{board.score}\r\n{board.board}'
        clientsocket.send(send.encode().decode('unicode_escape').encode("raw_unicode_escape"))



def main(username, password, size, use_bot=False):
    clientsocket = connect_to_server(username, password)
    auth_result = clientsocket.recv(1024).decode()
    score, state, prev_size = process_auth_result(auth_result)

    if state == 'None':
        board = Board(clientsocket, 0, size)
        board.create_random_tile()
        board.create_random_tile()
    else:
        board = Board(clientsocket, score, prev_size, state)

    board.draw_board()

    stats_thread = Thread(target=fetch_stats, args=(clientsocket, board,))
    stats_thread.daemon = True
    stats_thread.start()

    score_thread = Thread(target=send_score, args=(clientsocket, board,))
    score_thread.daemon = True
    score_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if use_bot and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                use_bot = False

            # if not use_bot and event.type == pygame.KEYDOWN:
            #     if not handle_key_event(event, board):
            #         board.show_game_over_screen()

        if use_bot:
            try:
                current_state = board.get_current_state()
                best_move = predict_next_move(current_state)
                board.handle_bot_move(best_move)
                board.draw_board()
            except:
                break

    board.show_game_over_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="The username")
    parser.add_argument("-p", "--password", help="The password")
    parser.add_argument("-d", "--difficulty", type=int, choices=[1, 2, 3], default=1,
                        help="The difficulty level: 1 (easy), 2 (medium), or 3 (hard)")
    parser.add_argument("-b", "--bot", action="store_true", help="Use bot to play the game")
    args = parser.parse_args()
    username = args.username
    password = args.password
    difficulty = args.difficulty
    use_bot = args.bot
    size = 6 - difficulty
    main(username, password, size, use_bot)
