# g.py modifications
# Add these constants and modify existing ones

import pygame as pg

# Declare some constants and variables
FPS = 45
WHITE = pg.Color("#DDDDDD")
BLACK = pg.Color("#1A1A1A")
GREY = pg.Color("#333333")
ORANGE = pg.Color("#FF6600")  # Player 1 color
RED = pg.Color("#FF1F00")     # Player 2 color
BLUE = pg.Color("#3333AA")    # Board color
FRAME_GAP = 80                # Smaller gap for the larger board
LINE_WIDTH = 5                # Thinner lines
CIRCLE_RADIUS = 30            # Smaller tokens
CIRCLE_WIDTH = 0              # Filled circles, not outlines
CROSS_WIDTH = 14              # Not used but kept for compatibility
CROSS_LENGTH = 54             # Not used but kept for compatibility
GRID_ROWS = 6                 # Connect Four is 6 rows
GRID_COLS = 7                 # Connect Four is 7 columns

def init():
    global WIN, WIDTH, HEIGHT
    WIN = pg.display.get_surface()
    WIDTH, HEIGHT = WIN.get_size()