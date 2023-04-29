import random
import os
import sys
import pygame


pygame.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)


class Board:
    def __init__(self, size=3):
        self.size = size
        self.board = self.create_board(size)
        self.score = 0
        self.tile_size = 80
        self.padding = 10
        self.screen_size = (self.tile_size * size + self.padding * (size + 1),
                            self.tile_size * size + self.padding * (size + 1)+100)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Game")

    @classmethod
    def create_board(cls, size):
        return [[0 for x in range(size)] for y in range(size)]

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
            self.board[x][y] = 2
            return True
        else:
            return False

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
                pygame.draw.rect(self.screen, GREY, tile_rect)
                if tile != 0:
                    tile_text = font.render(str(tile), True, BLACK)
                    text_rect = tile_text.get_rect(center=tile_rect.center)
                    self.screen.blit(tile_text, text_rect)

            if i < self.size - 1:
                line_rect = pygame.Rect(self.padding, (i + 2) * self.padding + (i + 1) * self.tile_size + 100,
                                        self.tile_size * self.size + self.padding * (self.size + 1) - 2 * self.padding,
                                        self.padding)
                pygame.draw.rect(self.screen, BLACK, line_rect)

        pygame.display.flip()

    def move_up(self):
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == 0: continue
                for k in range(i-1, -1, -1):
                    if self.board[i][j] == self.board[k][j]:
                        self.score += self.board[i][j]
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
        self.draw_board()
        return result

    def move_down(self):
        self.board = self.board[::-1]
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == 0: continue
                for k in range(i-1, -1, -1):
                    if self.board[i][j] == self.board[k][j]:
                        self.score += self.board[i][j]
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
        self.draw_board()
        return result

    def move_left(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                for k in range(j-1, -1, -1):
                    if self.board[i][j] == self.board[i][k]:
                        self.score += self.board[i][j]
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
        self.draw_board()
        return result

    def move_right(self):
        for i in range(len(self.board)):
            self.board[i] = self.board[i][::-1]
            for j in range(len(self.board[i])):
                for k in range(j-1, -1, -1):
                    if self.board[i][j] == self.board[i][k]:
                        self.score += self.board[i][j]
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


def main():
    board = Board(3)
    board.create_random_tile()
    board.create_random_tile()
    board.draw_board()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not board.move_left():
                        board.show_game_over_screen()
                elif event.key == pygame.K_RIGHT:
                    if not board.move_right():
                        board.show_game_over_screen()
                elif event.key == pygame.K_UP:
                    if not board.move_up():
                        board.show_game_over_screen()
                elif event.key == pygame.K_DOWN:
                    if not board.move_down():
                        board.show_game_over_screen()


if __name__ == "__main__":
    main()