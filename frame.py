# frame.py modifications

import pygame as pg
from anim import Animate
import g


class Frame:
    def __init__(self, main, center, gap=g.FRAME_GAP):
        self.main = main
        self.gap = gap
        self.turn = 1  # 1 for Player 1 (Orange), -1 for Player 2 (Red)
        self.remove = False
        self.center = center
        
        # Calculate board dimensions
        self.board_width = g.GRID_COLS * gap
        self.board_height = g.GRID_ROWS * gap
        
        # Calculate board corners
        left = center[0] - self.board_width / 2
        right = center[0] + self.board_width / 2
        top = center[1] - self.board_height / 2
        bottom = center[1] + self.board_height / 2
        
        # Board outline points
        self.points = [
            [left, top],
            [right, top],
            [right, bottom],
            [left, bottom]
        ]
        
        # Create grid lines points
        self.grid_lines = []
        
        # Vertical lines
        for i in range(1, g.GRID_COLS):
            x = left + i * gap
            self.grid_lines.append(([x, top], [x, bottom]))
            
        # Horizontal lines
        for i in range(1, g.GRID_ROWS):
            y = top + i * gap
            self.grid_lines.append(([left, y], [right, y]))
            
        # Initialize the game board (0 = empty, 1 = player 1, -1 = player 2)
        self.board = [[0 for _ in range(g.GRID_COLS)] for _ in range(g.GRID_ROWS)]
        self.moves = [[None for _ in range(g.GRID_COLS)] for _ in range(g.GRID_ROWS)]
        
        # Create column rects for click detection (only need tops of columns)
        self.column_rects = []
        for col in range(g.GRID_COLS):
            x = left + col * gap
            self.column_rects.append(pg.Rect(x, top - gap, gap, gap))
            
        # Visual feedback for hover
        self.hover_col = -1
        
        # Initialize animations for board outline
        self.animations = [
            Animate(main, 500 + i * 100).line(self.points[i], 
                                            self.points[(i + 1) % len(self.points)])
            for i in range(len(self.points))
        ]
        
        # Add animations for grid lines
        for line in self.grid_lines:
            self.animations.append(Animate(main, 800).line(line[0], line[1]))

    def detect_click(self, pos):
        for col, rect in enumerate(self.column_rects):
            if rect.collidepoint(pos):
                # Find the lowest empty row in this column
                row = self.get_next_open_row(col)
                if row is not None:  # Column not full
                    # Update the board
                    self.board[row][col] = self.turn
                    
                    # Calculate token position
                    token_x = rect.centerx
                    token_y = self.center[1] - self.board_height/2 + (row + 0.5) * self.gap
                    
                    # Create token animation
                    self.moves[row][col] = Token(self.main, 
                                               self.turn,
                                               (token_x, token_y),
                                               row)
                    
                    # Check for win
                    if self.check_win(row, col):
                        self.main.score[0 if self.turn == 1 else 1] += 1
                        self.reset()
                    # Switch turns
                    self.turn *= -1
                    self.main.set_turn()
                    return True
        return False
    
    def get_next_open_row(self, col):
        """Find the lowest empty row in the given column"""
        for row in range(g.GRID_ROWS - 1, -1, -1):
            if self.board[row][col] == 0:
                return row
        return None  # Column is full
    
    def update_hover(self, pos):
        """Update hover effect for columns"""
        self.hover_col = -1
        for col, rect in enumerate(self.column_rects):
            if rect.collidepoint(pos) and self.get_next_open_row(col) is not None:
                self.hover_col = col
                break
    
    def reset(self, wait=True):
        for row in range(g.GRID_ROWS):
            for col in range(g.GRID_COLS):
                if self.moves[row][col] is not None:
                    self.moves[row][col].wait_and_remove = True
                    if wait:
                        ticks = pg.time.get_ticks()
                        self.moves[row][col].remove_time = (
                            2 * self.moves[row][col].blink_count * 
                            self.moves[row][col].blink_dur + ticks
                        )
                    else:
                        self.moves[row][col].remove_time = 0
                        
        # Clear board after animation
        self.board = [[0 for _ in range(g.GRID_COLS)] for _ in range(g.GRID_ROWS)]
        self.moves = [[None for _ in range(g.GRID_COLS)] for _ in range(g.GRID_ROWS)]

    def check_win(self, row, col):
        """Check for 4 in a row starting from the last move"""
        player = self.board[row][col]
        
        # Check horizontal
        for c in range(max(0, col - 3), min(col + 1, g.GRID_COLS - 3)):
            if (self.board[row][c] == player and 
                self.board[row][c+1] == player and 
                self.board[row][c+2] == player and 
                self.board[row][c+3] == player):
                self.highlight_win([(row, c), (row, c+1), (row, c+2), (row, c+3)])
                return True
                
        # Check vertical
        if row <= g.GRID_ROWS - 4:
            if (self.board[row][col] == player and 
                self.board[row+1][col] == player and 
                self.board[row+2][col] == player and 
                self.board[row+3][col] == player):
                self.highlight_win([(row, col), (row+1, col), (row+2, col), (row+3, col)])
                return True
                
        # Check diagonal (positive slope)
        for r, c in [(row + i, col - i) for i in range(4)]:
            if (0 <= r + 3 < g.GRID_ROWS and 0 <= c + 3 < g.GRID_COLS and
                self.board[r][c] == player and 
                self.board[r+1][c+1] == player and 
                self.board[r+2][c+2] == player and 
                self.board[r+3][c+3] == player):
                self.highlight_win([(r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)])
                return True
                
        # Check diagonal (negative slope)
        for r, c in [(row - i, col - i) for i in range(4)]:
            if (0 <= r < g.GRID_ROWS - 3 and 0 <= c < g.GRID_COLS - 3 and
                self.board[r][c] == player and 
                self.board[r+1][c+1] == player and 
                self.board[r+2][c+2] == player and 
                self.board[r+3][c+3] == player):
                self.highlight_win([(r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)])
                return True
        
        # Check for tie (full board)
        is_full = all(self.board[0][c] != 0 for c in range(g.GRID_COLS))
        if is_full:
            self.reset()
            return False
            
        return False
    
    def highlight_win(self, positions):
        """Highlight the winning tokens"""
        for row, col in positions:
            if self.moves[row][col] is not None:
                self.moves[row][col].blink = True
                self.moves[row][col].blink_start = pg.time.get_ticks()

    def setup_remove(self, dur=500, animate=False):
        if not self.remove:
            self.remove = True
            self.remove_time = pg.time.get_ticks() + dur
            if animate:
                for i in self.animations:
                    i.setup_remove(dur)

    def draw(self):
        # Draw board background
        board_rect = pg.Rect(
            self.center[0] - self.board_width/2,
            self.center[1] - self.board_height/2,
            self.board_width,
            self.board_height
        )
        pg.draw.rect(g.WIN, g.BLUE, board_rect)
        
        # Draw board outline and grid
        for animation in self.animations:
            animation.update()
            
        # Draw tokens
        for row in range(g.GRID_ROWS):
            for col in range(g.GRID_COLS):
                if self.moves[row][col] is not None:
                    self.moves[row][col].draw()
                else:
                    # Draw empty slots
                    x = self.center[0] - self.board_width/2 + (col + 0.5) * self.gap
                    y = self.center[1] - self.board_height/2 + (row + 0.5) * self.gap
                    pg.draw.circle(g.WIN, g.BLACK, (int(x), int(y)), g.CIRCLE_RADIUS)
        
        # Draw hover effect
        if self.hover_col >= 0:
            x = self.center[0] - self.board_width/2 + (self.hover_col + 0.5) * self.gap
            y = self.center[1] - self.board_height/2 - self.gap/2
            color = g.ORANGE if self.turn == 1 else g.RED
            pg.draw.circle(g.WIN, color, (int(x), int(y)), g.CIRCLE_RADIUS)
            
        if self.remove:
            if pg.time.get_ticks() > self.remove_time:
                self.main.reset()


class Token:
    def __init__(self, main, _type, center, row):
        self.main = main
        self.type = _type
        self.center = center
        self.row = row
        self.blink = False
        self.blink_count = 3
        self.blink_dur = 250
        self.blink_start = None
        self.wait_and_remove = False
        self.remove_time = None
        
        # Create token animation
        color = g.ORANGE if _type == 1 else g.RED
        self.animation = Animate(main, color=color).circle(center)

    def draw(self):
        if self.blink:
            if pg.time.get_ticks() < self.blink_start + self.blink_dur:
                self.animation.update()
            elif pg.time.get_ticks() > self.blink_start + 2 * self.blink_dur:
                self.blink_start = pg.time.get_ticks()
                self.blink_count -= 1
                if self.blink_count == 0:
                    self.blink = False
        else:
            self.animation.update()

        if self.wait_and_remove:
            if pg.time.get_ticks() > self.remove_time:
                self.animation.setup_remove()
                self.main.frame.setup_remove()
                self.wait_and_remove = False