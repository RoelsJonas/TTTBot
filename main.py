import numpy as np
import sdl2
import sdl2.ext

# initialize constants
WIDTH = 600
HEIGHT = 600
COLORS = [
    sdl2.ext.Color(0, 0, 0),  # 0 = black
    sdl2.ext.Color(255, 0, 0),  # 1 = red
    sdl2.ext.Color(0, 255, 0),  # 2 = green
    sdl2.ext.Color(0, 0, 255),  # 3 = blue
    sdl2.ext.Color(64, 64, 64),  # 4 = dark gray
    sdl2.ext.Color(128, 128, 128),  # 5 = mid gray
    sdl2.ext.Color(192, 192, 192),  # 6 = light gray
    sdl2.ext.Color(255, 255, 255),  # 7 = white
]

CORNERS = [(0, 0), (0, 2), (2, 0), (2, 2)]
SIDES = [(0, 1), (1, 0), (2, 1), (1, 2)]


class Board:
    board = np.zeros((3, 3), int)  # initialize the board on all zeros. (0 = nothing, 1 = white, 2 = black)
    white = True  # set what color the player is using
    mouse_position = [WIDTH // 2, HEIGHT // 2]
    renderer = ""
    window = ""
    factory = ""
    running = True
    completed = False
    turn = 1
    clicked = False
    counter = 0
    ManagerFont = ""
    text = ""
    text2 = ""

    def __init__(self):
        # initialize the window
        self.window = sdl2.ext.Window("TTTBot", size=(WIDTH, HEIGHT))
        self.window.show()

        # create a renderer
        self.renderer = sdl2.ext.Renderer(self.window)

        self.factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=self.renderer)
        self.FontWin = sdl2.ext.FontManager(font_path="resources/OpenSans.ttf", size=50, color=COLORS[2])
        self.FontTie = sdl2.ext.FontManager(font_path="resources/OpenSans.ttf", size=50, color=COLORS[4])
        self.FontLose = sdl2.ext.FontManager(font_path="resources/OpenSans.ttf", size=50, color=COLORS[1])
        self.text2 = self.factory.from_text("Press space to restart", fontmanager = self.FontTie)
        # set mousemovents to relative mode
        sdl2.SDL_SetRelativeMouseMode(True)

    def render(self):
        self.counter -= 1
        self.renderer.fill((0, 0, WIDTH, HEIGHT), COLORS[5])  # create a gray background
        width_part = WIDTH // 3
        height_part = HEIGHT // 3

        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                if self.board[i, j] == 1:
                    self.renderer.fill((width_part * i, height_part * j, width_part, height_part), COLORS[7])
                elif self.board[i, j] == 2:
                    self.renderer.fill((width_part * i, height_part * j, width_part, height_part), COLORS[0])

        # create the grid using red lines
        for i in range(1, 3):
            self.renderer.fill((width_part * i - 5, 0, 10, HEIGHT), COLORS[1])
            self.renderer.fill((0, height_part * i - 5, WIDTH, 10), COLORS[1])

        # render the cursor
        self.renderer.fill((self.mouse_position[0], self.mouse_position[1], 5, 5), COLORS[3])

        if self.completed:
            self.renderer.copy(self.text,dstrect=(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 100))
            self.renderer.copy(self.text2,dstrect=(WIDTH//2 - 150, HEIGHT//2 + 75, 300, 75))
        # push the changed output of the renderer to the player
        self.renderer.present()

    def registerInputs(self):
        key_states = sdl2.SDL_GetKeyboardState(None)
        events = sdl2.ext.get_events()
        width_part = WIDTH // 3
        height_part = HEIGHT // 3
        if key_states[sdl2.SDL_SCANCODE_ESCAPE]:
            self.running = False
        if key_states[sdl2.SDL_SCANCODE_SPACE] and self.counter <= 0:
            self.reset()
        for e in events:
            if e.type == sdl2.SDL_MOUSEMOTION:
                self.mouse_position[0] += e.motion.xrel
                self.mouse_position[1] += e.motion.yrel
            elif e.type == sdl2.SDL_MOUSEBUTTONDOWN and not self.completed:
                for i in range(3):
                    for j in range(3):
                        if i * width_part < self.mouse_position[0] < (i + 1) * width_part:
                            if j * height_part < self.mouse_position[1] < (j + 1) * height_part:
                                if self.board[i, j] == 0:
                                    self.board[i, j] = 1
                                    self.checkCompletion()
                                    self.moveBot()
                                    self.checkCompletion()

    def moveWinBlock(self, spots, win):
        for spot in spots:
            if spot[0] == 0:
                if self.board[1, spot[1]] == win and self.board[2, spot[1]] == win:
                    self.board[spot[0], spot[1]] = 2
                    return True

            if spot[0] == 1:
                if self.board[0, spot[1]] == win and self.board[2, spot[1]] == win:
                    self.board[spot[0], spot[1]] = 2
                    return True

            if spot[0] == 2:
                if self.board[0, spot[1]] == win and self.board[1, spot[1]] == win:
                    self.board[spot[0], spot[1]] = 2
                    return True

            if spot[1] == 0:
                if self.board[spot[0], 1] == win and self.board[spot[0], 2] == win:
                    self.board[spot[0], spot[1]] = 2
                    return True

            if spot[1] == 1:
                if self.board[spot[0], 0] == win and self.board[spot[0], 2] == win:
                    self.board[spot[0], spot[1]] = 2
                    return True

            if spot[1] == 2:
                if self.board[spot[0], 0] == win and self.board[spot[0], 1] == win:
                    self.board[spot[0], spot[1]] = 2
                    return True

            if spot == (1, 1):
                if (self.board[0, 0] == win and self.board[2, 2] == win) or (
                        self.board[2, 0] == 2 and self.board[0, 2]):
                    self.board[1, 1] = 2
                    return True

            if spot == (0, 0):
                if self.board[1, 1] == win and self.board[2, 2] == win:
                    self.board[0, 0] = 2
                    return True

            if spot == (2, 2):
                if self.board[1, 1] == win and self.board[0, 0] == win:
                    self.board[2, 2] = 2
                    return True

            if spot == (0, 2):
                if self.board[1, 1] == win and self.board[2, 0] == win:
                    self.board[0, 2] = 2
                    return True

            if spot == (2, 0):
                if self.board[1, 1] == win and self.board[0, 2] == win:
                    self.board[2, 0] = 2
                    return True

    def moveFork(self, spots):
        for spot in spots:
            if spot in CORNERS:
                owned = 0
                for c in CORNERS:
                    if self.board[c[0], c[1]] == 2:
                        owned += 1
                if owned >= 2:
                    self.board[spot[0], spot[1]] = 2
                    return True

    def moveBlockFork(self, spots):
        for spot in spots:
            if spot in SIDES:
                owned = 0
                for c in CORNERS:
                    if self.board[c[0], c[1]] == 1:
                        owned += 1
                if owned >= 2:
                    self.board[spot[0], spot[1]] = 2
                    return True

    def moveBot(self):
        if not self.completed:
            moved = False
            spots = self.findSpots()
            selected = None

            # 1 check if the bot can win
            moved = self.moveWinBlock(spots, 2)

            # 2 check if the bot can block the player from winning
            if not moved:
                moved = self.moveWinBlock(spots, 1)

            # 3 create fork
            if not moved:
                moved = self.moveFork(spots)

            # 4 block fork by forcing oponent to block
            if not moved:
                moved = self.moveBlockFork(spots)

            # 5 check if center is available
            if not moved:
                for spot in spots:
                    if spot == (1, 1):
                        self.board[1, 1] = 2
                        moved = True
                        break

            # 6 oposite corner
            if not moved:
                for spot in spots:
                    if self.board[0, 0] == 1 and spot == (2, 2):
                        self.board[2, 2] = 2
                        moved = True
                        break
                    elif self.board[2, 2] == 1 and spot == (0, 0):
                        if not moved:
                            self.board[0, 0] = 2
                        moved = True
                        break
                    elif self.board[2, 0] == 1 and spot == (0, 2):
                        if not moved:
                            self.board[0, 2] = 2
                        moved = True
                        break
                    elif self.board[0, 2] == 1 and spot == (2, 0):
                        if not moved:
                            self.board[2, 0] = 2
                        moved = True
                        break

            # 7 empty corner
            if not moved:
                for spot in spots:
                    if not moved and spot in CORNERS:
                        self.board[spot[0], spot[1]] = 2
                        moved = True
                        break

            # 8 empty side
            if not moved:
                for spot in spots:
                    if spot in SIDES:
                        self.board[spot[0], spot[1]] = 2
                        moved = True
                        break

    def findSpots(self):
        spots = []
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    spots.append((i, j))
        return spots

    def checkCompletion(self):
        # check rows and columns for victory
        for i in range(3):
            if self.board[i, 0] == self.board[i, 1] and self.board[i, 1] == self.board[i, 2]:
                if self.board[i, 0] != 0:
                    self.complete(self.board[i, 0])
            elif self.board[0, i] == self.board[1, i] and self.board[1, i] == self.board[2, i]:
                if self.board[0, i] != 0:
                    self.complete(self.board[0, i])

        # check diagonals for victory
        if self.board[1, 1] != 0:
            if self.board[0, 0] == self.board[1, 1] and self.board[1, 1] == self.board[2, 2]:
                self.complete(self.board[1, 1])
            elif self.board[2, 0] == self.board[1, 1] and self.board[1, 1] == self.board[0, 2]:
                self.complete(self.board[1, 1])

        # check for tie
        empty = False
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    empty = True
        if not empty:
            self.complete(0)

    def complete(self, player):
        if not self.completed:
            if player == 0:
                self.text = self.factory.from_text("You tied", fontmanager = self.FontTie)
            elif player == 1:
                self.text = self.factory.from_text("You won", fontmanager = self.FontWin)
            else:
                self.text = self.factory.from_text("You loose", fontmanager = self.FontLose)
            self.completed = True

    def reset(self):
        self.counter = 500
        self.board = np.zeros((3,3), int)
        self.completed = False
        self.white = not self.white
        if not self.white:
            self.moveBot()

def main():
    # create the board object
    board = Board()

    while board.running:
        board.registerInputs()
        board.render()

if __name__ == '__main__':
    main()
