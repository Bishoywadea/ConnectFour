# anim.py modifications

import pygame as pg
from math import sqrt
import g


class Animate:

    def LINEAR(x):
        return x

    def EASE_OUT_QUART(x):
        return 1 - pow(1 - x, 4)

    def EASE_IO_QUART(x):
        return 8 * pow(x, 4) if x < 0.5 else 1 - pow(-2 * x + 2, 4) / 2

    def __init__(self, main, dur=500, color=g.WHITE, fn=EASE_OUT_QUART):
        self.main = main
        self.color = color
        self.function = fn
        self.remove = False
        self.dur = dur
        self.start_time = pg.time.get_ticks()
        self.final_time = self.start_time + dur
        self.type = None
        self.sub_animations = None

    def line(self, p1, p2, width=g.LINE_WIDTH):
        self.type = "line"
        self.finished = False
        self.width = width
        self.p1 = pg.Vector2(p1)
        self.p2 = pg.Vector2(p2)
        self.p = self.p2 - self.p1
        self.length = sqrt(self.p.x ** 2 + self.p.y ** 2)
        return self

    def circle(self, center, radius=g.CIRCLE_RADIUS, width=g.CIRCLE_WIDTH):
        self.type = "circle"
        self.finished = False
        self.width = width
        self.radius = radius
        self.r = radius
        self.center = pg.Vector2(center)
        self.rect = pg.Rect(
            (center[0] - radius, center[1] - radius), (2 * radius, 2 * radius)
        )
        # Add drop animation for tokens
        self.original_center_y = self.center.y
        self.drop_start = self.center.y - g.GRID_ROWS * g.FRAME_GAP
        self.center.y = self.drop_start
        return self

    def cross(self, center, length=g.CROSS_LENGTH, width=g.CROSS_WIDTH):
        # Kept for compatibility, not used in Connect Four
        self.type = "cross"
        points = [
            pg.Vector2(-length, 0),
            pg.Vector2(length, 0),
            pg.Vector2(0, length),
            pg.Vector2(0, -length),
        ]
        for i in range(2):
            points[i] = points[i].rotate(40) + pg.Vector2(center)
            points[i + 2] = points[i + 2].rotate(50) + pg.Vector2(center)

        self.sub_animations = [
            Animate(
                self.main,
                self.dur + i * 150,
                self.color,
                self.function
            ).line(points[i], points[i + 1], width)
            for i in range(0, len(points), 2)
        ]
        return self

    def setup_remove(self, dur=500):
        self.finished = True
        self.remove = True
        self.dur = dur
        self.start_time = pg.time.get_ticks()
        self.final_time = self.start_time + self.dur
        if self.sub_animations is not None:
            for i in self.sub_animations:
                i.setup_remove(dur)

    def update(self, skip=False):
        # Call method recursively
        if self.type == "cross":
            for animation in self.sub_animations:
                animation.update()
            return

        # Calculate the animation
        if not self.finished or self.remove:
            if pg.time.get_ticks() < self.final_time and not skip:
                fraction = (pg.time.get_ticks() - self.start_time) / self.dur
                if fraction < 0.01:
                    fraction += 0.008

                if self.remove:
                    fraction = 1 - fraction

                if self.type == "line":
                    self.p.scale_to_length(
                        self.length * self.function(fraction)
                    )
                elif self.type == "circle":
                    if not self.remove and not self.finished:
                        # Drop animation for tokens
                        drop_distance = self.original_center_y - self.drop_start
                        self.center.y = self.drop_start + drop_distance * self.function(fraction)
                    self.r = self.radius - self.width * self.function(fraction)
            else:
                if self.type == "line":
                    self.p = self.p2 - self.p1
                    if self.remove:
                        self.p = [0, 0]
                if self.type == "circle":
                    if not self.remove:
                        self.center.y = self.original_center_y
                    self.r = self.radius - self.width
                    if self.remove:
                        self.r = self.radius
                self.remove = False
                self.finished = True

        # Draw stuff
        if self.type == "line":
            pg.draw.line(g.WIN,
                         self.color,
                         self.p1,
                         self.p + self.p1,
                         self.width)
        elif self.type == "circle":
            pg.draw.circle(
                g.WIN,
                self.color,
                (int(self.center.x), int(self.center.y)),
                int(self.radius),
            )
            if self.width > 0:  # Only draw inner circle if width > 0
                pg.draw.circle(
                    g.WIN,
                    g.BLACK,
                    (int(self.center.x), int(self.center.y)),
                    int(self.r)
                )