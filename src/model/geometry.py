from __future__ import annotations

class Vec2:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def dot(self, rhs: Vec2) -> float:
        return self.x * rhs.x + self.y * rhs.y

    def length_squared(self) -> float:
        return pow(self.x, 2) + pow(self.y, 2)

    def __add__(self, rhs: Vec2) -> Vec2:
        return Vec2(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs: Vec2) -> Vec2:
        return Vec2(self.x - rhs.x, self.y - rhs.y)

    def __mul__(self, rhs: float) -> Vec2:
        return Vec2(self.x * rhs, self.y * rhs)
