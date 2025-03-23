# main.py modifications

import pygame as pg
from anim import Animate
import g
from frame import Frame
import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gettext import gettext as _


# The main controller
class Main:
    def __init__(self, journal=True):
        self.journal = journal
        self.running = True
        self.canvas = None
        self.score = [0, 0]
        self.show_help = False

    def set_canvas(self, canvas):
        self.canvas = canvas
        pg.display.set_caption(_("Connect Four"))

    def write_file(self, file_path):
        pass

    def read_file(self, file_path):
        pass

    def quit(self):
        self.running = False

    def check_events(self):
        mouse_pos = pg.mouse.get_pos()
        self.frame.update_hover(mouse_pos)  # Update hover effect
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.VIDEORESIZE:
                pg.display.set_mode(event.size, pg.RESIZABLE)
                break
            if event.type == pg.MOUSEBUTTONUP:
                if self.help_pos.collidepoint(mouse_pos):
                    self.show_help = not self.show_help
                if self.show_help == True: 
                    break
                if self.canvas is not None:
                    self.canvas.grab_focus()
                if self.frame.detect_click(mouse_pos):
                    self.set_turn()
                if self.reset_rect.collidepoint(mouse_pos):
                    self.frame.reset(False)
                    self.score = [0, 0]

    def draw_help(self):
        pg.draw.circle(
            g.WIN,
            g.GREY,
            self.help_pos.center,
            40,
        )
        if self.show_help:
            width = self.close_text.get_width()
            height = self.close_text.get_height()
            close_rect = (
                (3 * g.WIDTH + g.FRAME_GAP * g.GRID_COLS - 2 * width) // 4,
                (g.HEIGHT * 0.5 - g.FRAME_GAP * g.GRID_ROWS/2 - height) // 2
            )
            g.WIN.blit(
                self.close_text, close_rect
            )
            pg.draw.rect(
                g.WIN,
                g.GREY,
                pg.Rect(
                    50,
                    (g.HEIGHT - g.FRAME_GAP * g.GRID_ROWS) // 2 - 10,
                    g.WIDTH - 100,
                    g.FRAME_GAP * g.GRID_ROWS + 20,
                ),
            )
            g.WIN.blit(
                self.help_img,
                (
                    (g.WIDTH - self.help_img.get_width()) // 2,
                    (g.HEIGHT - g.FRAME_GAP * g.GRID_ROWS) // 2,
                ),
            )
            for i, text in enumerate(self.help_text):
                g.WIN.blit(
                    text,
                    (
                        (g.WIDTH - text.get_width()) // 2,
                        g.HEIGHT // 2 + 40 + 40 * i,
                    ),
                )
        else:
            width = self.question_text.get_width()
            height = self.question_text.get_height()
            question_rect = (
                (3 * g.WIDTH + g.FRAME_GAP * g.GRID_COLS - 2 * width) // 4,
                (g.HEIGHT * 0.5 - g.FRAME_GAP * g.GRID_ROWS/2 - height) // 2
            )
            g.WIN.blit(
                self.question_text, question_rect
            )

    def draw(self):
        g.WIN.fill(g.BLACK)
        tt_width = self.turn_text.get_width()
        tt_height = self.turn_text.get_height()
        tt_rect = (
            (g.WIDTH - g.FRAME_GAP * g.GRID_COLS - 2 * tt_width) / 4,
            (g.HEIGHT * 0.5 - g.FRAME_GAP * g.GRID_ROWS/2 - tt_height) // 2
        )
        g.WIN.blit(
            self.turn_text, tt_rect
        )
        self.frame.draw()
        self.circle_orange.update()
        self.circle_red.update()
        scorex = self.font.render(str(self.score[0]), True, g.WHITE)
        scoreo = self.font.render(str(self.score[1]), True, g.WHITE)
        g.WIN.blit(
            scorex,
            (
                (g.WIDTH - g.FRAME_GAP * g.GRID_COLS - 2 * scorex.get_width()) / 4,
                (g.HEIGHT / 2 + g.FRAME_GAP / 4),
            ),
        )
        sc_width = scorex.get_width()
        g.WIN.blit(
            scoreo,
            (
                g.WIDTH - (g.WIDTH - g.FRAME_GAP * g.GRID_COLS + 2 * sc_width) / 4,
                (g.HEIGHT / 2 + g.FRAME_GAP / 4),
            ),
        )
        # self.draw_help()
        pg.draw.rect(g.WIN, g.GREY, self.reset_rect)
        pg.draw.circle(
            g.WIN,
            g.GREY,
            (int(self.reset_rect.x), int(self.reset_rect.centery)),
            self.reset_rect.height // 2,
        )
        pg.draw.circle(
            g.WIN,
            g.GREY,
            (int(self.reset_rect.right), int(self.reset_rect.centery)),
            self.reset_rect.height // 2,
        )
        g.WIN.blit(
            self.reset_text,
            (
                g.WIDTH / 2 - self.reset_text.get_width() / 2,
                g.HEIGHT - self.reset_text.get_height() - 70,
            ),
        )
        pg.display.update()

    def reset(self):
        self.frame = Frame(self, (g.WIDTH / 2, g.HEIGHT / 2))
        self.set_turn()

    def set_turn(self):
        self.turn_text = pg.font.Font(None, 64).render(
            [_("Red Turn"), "", _("Orange Turn")][self.frame.turn + 1],
            True,
            g.WHITE
        )

    # The main loop
    def run(self):
        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                pg.display.set_mode(event.size, pg.RESIZABLE)
                break
        g.init()
        pg.font.init()
        
        self.reset_text = pg.font.Font(None, 56).render(
            _("Reset"),
            True,
            g.WHITE
        )
        self.question_text = pg.font.Font(None, 72).render("?", True, g.WHITE)
        self.close_text = pg.font.Font(None, 64).render("X", True, g.WHITE)
        self.help_text = [
            pg.font.Font(None, 36).render(
                i,
                True,
                g.WHITE,
            )
            for i in (
                _("Players take turns dropping colored tokens from the top."),
                _("The tokens fall to the lowest available space in the column."),
                _("The first player to get four tokens in a row (horizontally,"),
                _("vertically, or diagonally) wins the game!"),
            )
        ]
        self.help_pos = pg.Rect(
            (3 * g.WIDTH + g.FRAME_GAP * g.GRID_COLS) // 4 - 40,
            (g.HEIGHT * 0.5 - g.FRAME_GAP * g.GRID_ROWS/2) // 2 - 40,
            80,
            80,
        )
        self.reset_rect = pg.Rect(
            g.WIDTH / 2 - self.reset_text.get_width() / 2,
            g.HEIGHT - self.reset_text.get_height() - 80,
            self.reset_text.get_width(),
            self.reset_text.get_height() + 20,
        )
        self.font = pg.font.Font(None, 72)
        self.circle_orange = Animate(self, color=g.ORANGE).circle(
            (
                (g.WIDTH - g.FRAME_GAP * g.GRID_COLS) / 4,
                g.HEIGHT / 2 - g.FRAME_GAP / 4
            ),
            30,
            0  # Filled circle
        )
        self.circle_red = Animate(self, color=g.RED).circle(
            (
                g.WIDTH - (g.WIDTH - g.FRAME_GAP * g.GRID_COLS) / 4,
                g.HEIGHT / 2 - g.FRAME_GAP / 4
            ),
            30,
            0  # Filled circle
        )

        if self.canvas is not None:
            self.canvas.grab_focus()

        self.reset()
        self.clock = pg.time.Clock()
        while self.running:
            if self.journal:
                # Pump GTK messages.
                while Gtk.events_pending():
                    Gtk.main_iteration()

            self.check_events()
            self.draw()
            self.clock.tick(g.FPS)
        pg.display.quit()
        pg.quit()
        sys.exit(0)


# Test if the script is directly ran
if __name__ == "__main__":
    pg.init()
    pg.display.set_mode((1024, 768))
    main