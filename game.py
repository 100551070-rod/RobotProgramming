"""A small, dependency-free Space Invaders game built with tkinter."""

from __future__ import annotations

import random
import time
import tkinter as tk
from dataclasses import dataclass


WIDTH = 800
HEIGHT = 600
PLAYER_WIDTH = 46
PLAYER_HEIGHT = 26
PLAYER_Y = HEIGHT - 58
ALIEN_WIDTH = 28
ALIEN_HEIGHT = 22


@dataclass
class Alien:
    x: float
    y: float
    row: int


@dataclass
class Bullet:
    x: float
    y: float


class SpaceInvaders:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Space Invaders")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            background="#090b1a",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.focus_set()
        self.root.bind_all("<KeyPress>", self.on_key_press)
        self.root.bind_all("<KeyRelease>", self.on_key_release)
        self.canvas.bind("<Button-1>", self.on_click)

        rng = random.Random(7)
        self.stars = [
            (rng.randrange(WIDTH), rng.randrange(HEIGHT), rng.choice((1, 1, 2)))
            for _ in range(75)
        ]
        self.state = "welcome"
        self.keys: set[str] = set()
        self.score = 0
        self.wave = 1
        self.player_x = WIDTH / 2
        self.aliens: list[Alien] = []
        self.player_bullets: list[Bullet] = []
        self.alien_bullets: list[Bullet] = []
        self.alien_direction = 1
        self.fire_cooldown = 0.0
        self.alien_shot_timer = 0.0
        self.last_time = time.perf_counter()

        self.root.after(16, self.tick)

    def reset_wave(self) -> None:
        self.aliens = [
            Alien(150 + column * 58, 90 + row * 42, row)
            for row in range(5)
            for column in range(9)
        ]
        self.alien_direction = 1
        self.alien_shot_timer = 0.8

    def start_game(self) -> None:
        self.state = "playing"
        self.score = 0
        self.wave = 1
        self.player_x = WIDTH / 2
        self.keys.clear()
        self.player_bullets.clear()
        self.alien_bullets.clear()
        self.fire_cooldown = 0.0
        self.reset_wave()
        self.last_time = time.perf_counter()

    def on_key_press(self, event: tk.Event) -> None:
        key = str(event.keysym).lower()
        if self.state == "welcome":
            self.start_game()
        elif self.state == "gameover":
            if key == "r":
                self.start_game()
            elif key == "escape":
                self.root.destroy()
        else:
            self.keys.add(key)

    def on_key_release(self, event: tk.Event) -> None:
        self.keys.discard(str(event.keysym).lower())

    def on_click(self, event: tk.Event) -> None:
        if self.state == "welcome":
            self.start_game()
        elif self.state == "gameover":
            if 205 <= event.x <= 385 and 365 <= event.y <= 420:
                self.start_game()
            elif 415 <= event.x <= 595 and 365 <= event.y <= 420:
                self.root.destroy()

    def finish_game(self) -> None:
        self.state = "gameover"
        self.keys.clear()

    @staticmethod
    def overlaps(
        x1: float,
        y1: float,
        width1: float,
        height1: float,
        x2: float,
        y2: float,
        width2: float,
        height2: float,
    ) -> bool:
        return (
            x1 < x2 + width2
            and x1 + width1 > x2
            and y1 < y2 + height2
            and y1 + height1 > y2
        )

    def update(self, dt: float) -> None:
        direction = int("right" in self.keys or "d" in self.keys) - int(
            "left" in self.keys or "a" in self.keys
        )
        self.player_x += direction * 360 * dt
        half_width = PLAYER_WIDTH / 2
        self.player_x = max(half_width + 10, min(WIDTH - half_width - 10, self.player_x))

        self.fire_cooldown = max(0.0, self.fire_cooldown - dt)
        if ("space" in self.keys or "spacebar" in self.keys) and self.fire_cooldown == 0:
            self.player_bullets.append(Bullet(self.player_x, PLAYER_Y))
            self.fire_cooldown = 0.24

        speed = min(165, 48 + (self.wave - 1) * 16 + (45 - len(self.aliens)) * 0.65)
        next_left = min(alien.x for alien in self.aliens) + self.alien_direction * speed * dt
        next_right = max(alien.x + ALIEN_WIDTH for alien in self.aliens) + (
            self.alien_direction * speed * dt
        )
        if next_left < 24 or next_right > WIDTH - 24:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien.y += 18
        else:
            for alien in self.aliens:
                alien.x += self.alien_direction * speed * dt

        if any(alien.y + ALIEN_HEIGHT >= PLAYER_Y for alien in self.aliens):
            self.finish_game()
            return

        remaining_bullets: list[Bullet] = []
        for bullet in self.player_bullets:
            bullet.y -= 500 * dt
            hit = next(
                (
                    alien
                    for alien in self.aliens
                    if self.overlaps(
                        bullet.x - 3,
                        bullet.y - 9,
                        6,
                        12,
                        alien.x,
                        alien.y,
                        ALIEN_WIDTH,
                        ALIEN_HEIGHT,
                    )
                ),
                None,
            )
            if hit is not None:
                self.aliens.remove(hit)
                self.score += 10
            elif bullet.y > 0:
                remaining_bullets.append(bullet)
        self.player_bullets = remaining_bullets

        if not self.aliens:
            self.wave += 1
            self.player_bullets.clear()
            self.alien_bullets.clear()
            self.reset_wave()

        self.alien_shot_timer -= dt
        if self.alien_shot_timer <= 0:
            shooter = random.choice(self.aliens)
            self.alien_bullets.append(
                Bullet(shooter.x + ALIEN_WIDTH / 2, shooter.y + ALIEN_HEIGHT)
            )
            self.alien_shot_timer = max(0.45, random.uniform(1.15, 2.0) / self.wave)

        remaining_alien_bullets: list[Bullet] = []
        player_left = self.player_x - PLAYER_WIDTH / 2
        for bullet in self.alien_bullets:
            bullet.y += (245 + self.wave * 22) * dt
            if self.overlaps(
                bullet.x - 3,
                bullet.y - 8,
                6,
                12,
                player_left,
                PLAYER_Y,
                PLAYER_WIDTH,
                PLAYER_HEIGHT,
            ):
                self.finish_game()
                return
            if bullet.y < HEIGHT:
                remaining_alien_bullets.append(bullet)
        self.alien_bullets = remaining_alien_bullets

    def draw_button(self, x1: int, y1: int, x2: int, y2: int, label: str) -> None:
        self.canvas.create_rectangle(
            x1, y1, x2, y2, fill="#7138df", outline="#a78bfa", width=2
        )
        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=label,
            fill="white",
            font=("Segoe UI", 13, "bold"),
        )

    def draw(self) -> None:
        self.canvas.delete("all")
        self.canvas.configure(background="#090b1a")
        for x, y, size in self.stars:
            self.canvas.create_oval(
                x, y, x + size, y + size, fill="#777eaa", outline=""
            )

        if self.state == "playing":
            self.canvas.create_text(
                22,
                20,
                anchor="w",
                text=f"PUNTOS  {self.score}",
                fill="#eeeaff",
                font=("Segoe UI", 14, "bold"),
            )
            self.canvas.create_text(
                WIDTH - 22,
                20,
                anchor="e",
                text=f"OLEADA  {self.wave}",
                fill="#c4b5fd",
                font=("Segoe UI", 14, "bold"),
            )
            alien_colors = ("#fb7185", "#fbbf24", "#a78bfa", "#34d399", "#60a5fa")
            for alien in self.aliens:
                color = alien_colors[alien.row]
                x, y = alien.x, alien.y
                self.canvas.create_rectangle(
                    x + 5, y, x + ALIEN_WIDTH - 5, y + 5, fill=color, outline=""
                )
                self.canvas.create_rectangle(
                    x, y + 5, x + ALIEN_WIDTH, y + 16, fill=color, outline=""
                )
                self.canvas.create_rectangle(
                    x + 4, y + 16, x + 9, y + 21, fill=color, outline=""
                )
                self.canvas.create_rectangle(
                    x + ALIEN_WIDTH - 9,
                    y + 16,
                    x + ALIEN_WIDTH - 4,
                    y + 21,
                    fill=color,
                    outline="",
                )
                self.canvas.create_rectangle(
                    x + 7, y + 8, x + 11, y + 12, fill="#090b1a", outline=""
                )
                self.canvas.create_rectangle(
                    x + ALIEN_WIDTH - 11,
                    y + 8,
                    x + ALIEN_WIDTH - 7,
                    y + 12,
                    fill="#090b1a",
                    outline="",
                )

            player_left = self.player_x - PLAYER_WIDTH / 2
            self.canvas.create_rectangle(
                player_left + 7,
                PLAYER_Y + 8,
                player_left + PLAYER_WIDTH - 7,
                PLAYER_Y + PLAYER_HEIGHT,
                fill="#8b5cf6",
                outline="",
            )
            self.canvas.create_rectangle(
                self.player_x - 5,
                PLAYER_Y,
                self.player_x + 5,
                PLAYER_Y + 12,
                fill="#c4b5fd",
                outline="",
            )
            for bullet in self.player_bullets:
                self.canvas.create_rectangle(
                    bullet.x - 2, bullet.y - 8, bullet.x + 2, bullet.y + 5,
                    fill="#e9d5ff", outline=""
                )
            for bullet in self.alien_bullets:
                self.canvas.create_rectangle(
                    bullet.x - 3, bullet.y - 7, bullet.x + 3, bullet.y + 7,
                    fill="#fb7185", outline=""
                )
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT - 12,
                text="MOVER: ← → o A / D     DISPARAR: ESPACIO",
                fill="#858ba9",
                font=("Segoe UI", 10),
            )
        elif self.state == "welcome":
            self.canvas.create_text(
                WIDTH / 2,
                205,
                text="SPACE INVADERS",
                fill="#c4b5fd",
                font=("Segoe UI", 38, "bold"),
            )
            self.canvas.create_text(
                WIDTH / 2,
                266,
                text="¡Defiende la galaxia!",
                fill="#f8fafc",
                font=("Segoe UI", 18),
            )
            self.canvas.create_text(
                WIDTH / 2,
                326,
                text="← → o A / D para moverte     •     ESPACIO para disparar",
                fill="#aab0ca",
                font=("Segoe UI", 12),
            )
            self.draw_button(310, 380, 490, 436, "JUGAR")
            self.canvas.create_text(
                WIDTH / 2,
                472,
                text="Pulsa cualquier tecla o haz clic para empezar",
                fill="#858ba9",
                font=("Segoe UI", 11),
            )
        else:
            self.canvas.create_text(
                WIDTH / 2,
                205,
                text="FIN DEL JUEGO",
                fill="#fb7185",
                font=("Segoe UI", 36, "bold"),
            )
            self.canvas.create_text(
                WIDTH / 2,
                274,
                text=f"Puntuación final: {self.score}",
                fill="#f8fafc",
                font=("Segoe UI", 20, "bold"),
            )
            self.canvas.create_text(
                WIDTH / 2,
                316,
                text=f"Oleada alcanzada: {self.wave}",
                fill="#c4b5fd",
                font=("Segoe UI", 14),
            )
            self.draw_button(205, 365, 385, 420, "VOLVER A JUGAR")
            self.draw_button(415, 365, 595, 420, "SALIR")
            self.canvas.create_text(
                WIDTH / 2,
                456,
                text="Pulsa R para volver a jugar o Esc para salir",
                fill="#858ba9",
                font=("Segoe UI", 11),
            )

    def tick(self) -> None:
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now
        if self.state == "playing":
            self.update(dt)
        self.draw()
        self.root.after(16, self.tick)


def main() -> None:
    root = tk.Tk()
    SpaceInvaders(root)
    root.mainloop()


if __name__ == "__main__":
    main()
