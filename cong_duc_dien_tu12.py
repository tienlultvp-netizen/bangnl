#!/usr/bin/env python3
"""Công Đức Điện Tử - bản game có thử thách và lên level.

Cách chơi:
- Bấm "Bắt đầu" để vào level 1.
- Click trúng Mỏ Neon để cộng điểm level.
- Mỗi level có mục tiêu điểm + giới hạn thời gian.
- Trượt mục tiêu khi hết giờ => thua, cần chơi lại.
"""

from __future__ import annotations

import random
import tkinter as tk

BG_COLOR = "#090c18"
NEON_MAIN = "#00e5ff"
TEXT_COLOR = "#d8f7ff"
GLOW_PALETTE = ["#00e5ff", "#7a7dff", "#ff4fd8", "#7dffb3", "#ffd166"]


class CyberWoodenFishApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Công Đức Điện Tử • Game")
        self.root.geometry("980x620")
        self.root.minsize(820, 540)
        self.root.configure(bg=BG_COLOR)

        # Game state
        self.level = 1
        self.total_merit = 0
        self.level_score = 0
        self.target_score = 0
        self.time_left = 0
        self.combo = 0
        self.game_running = False

        # Fish position/bounds
        self.cx = 490
        self.cy = 330
        self.body_rx = 170
        self.body_ry = 86

        # UI
        self.title_label = tk.Label(
            root,
            text="🕹️ CÔNG ĐỨC ĐIỆN TỬ: THỬ THÁCH TÂM TĨNH",
            fg=NEON_MAIN,
            bg=BG_COLOR,
            font=("Consolas", 20, "bold"),
        )
        self.title_label.pack(pady=(12, 4))

        self.top_info = tk.Label(
            root,
            text="Level: 1 | Điểm level: 0/0 | Tổng công đức: 0 | Thời gian: 0s | Combo: x0",
            fg="#ffe76a",
            bg=BG_COLOR,
            font=("Consolas", 13, "bold"),
        )
        self.top_info.pack(pady=(0, 8))

        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bottom_bar = tk.Frame(root, bg=BG_COLOR)
        self.bottom_bar.pack(fill="x", pady=(6, 12))

        self.status_label = tk.Label(
            self.bottom_bar,
            text="Nhấn 'Bắt đầu' để chơi.",
            fg="#8ac8ff",
            bg=BG_COLOR,
            font=("Segoe UI", 11),
        )
        self.status_label.pack(side="left", padx=12)

        self.start_button = tk.Button(
            self.bottom_bar,
            text="Bắt đầu / Chơi lại",
            command=self.start_game,
            bg="#10264d",
            fg="#d5f4ff",
            activebackground="#1a3d7a",
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            font=("Segoe UI", 10, "bold"),
        )
        self.start_button.pack(side="right", padx=12)

        self.canvas.bind("<Button-1>", self.on_tap)
        self.canvas.bind("<Configure>", self.on_resize)

        # Canvas item references
        self.fish_items: list[int] = []
        self.glow_ring_ids: list[int] = []
        self.core_item_id: int | None = None
        self.glow_phase = 0

        self.draw_fish()
        self.animate_glow()

    # ------------------------ Level config ------------------------
    def get_level_target(self, level: int) -> int:
        return 6 + level * 3

    def get_level_time(self, level: int) -> int:
        return max(10, 20 - level // 2)

    def get_move_interval_ms(self, level: int) -> int:
        return max(260, 900 - level * 60)

    # ------------------------ Game flow ------------------------
    def start_game(self) -> None:
        self.level = 1
        self.total_merit = 0
        self.start_level(reset_total=False)
        self.status_label.config(text="Bắt đầu! Click trúng Mỏ Neon để vượt thử thách.")

    def start_level(self, reset_total: bool = False) -> None:
        if reset_total:
            self.total_merit = 0

        self.level_score = 0
        self.combo = 0
        self.target_score = self.get_level_target(self.level)
        self.time_left = self.get_level_time(self.level)
        self.game_running = True
        self.update_hud()
        self.random_reposition_fish()
        self.schedule_countdown()
        self.schedule_fish_movement()

    def schedule_countdown(self) -> None:
        if not self.game_running:
            return

        if self.time_left <= 0:
            self.handle_time_up()
            return

        self.time_left -= 1
        self.update_hud()
        self.root.after(1000, self.schedule_countdown)

    def schedule_fish_movement(self) -> None:
        if not self.game_running:
            return

        self.random_reposition_fish()
        self.draw_fish()
        self.root.after(self.get_move_interval_ms(self.level), self.schedule_fish_movement)

    def handle_time_up(self) -> None:
        if self.level_score >= self.target_score:
            self.advance_level()
            return

        self.game_running = False
        self.status_label.config(
            text=(
                f"Hết giờ! Bạn đạt {self.level_score}/{self.target_score}. "
                "Nhấn 'Bắt đầu / Chơi lại' để thử lại."
            )
        )

    def advance_level(self) -> None:
        self.level += 1
        self.status_label.config(text=f"🎉 Qua màn! Lên level {self.level}.")
        self.start_level()

    # ------------------------ Rendering ------------------------
    def on_resize(self, _event: tk.Event) -> None:
        if not self.game_running:
            self.cx = (self.canvas.winfo_width() or 980) // 2
            self.cy = (self.canvas.winfo_height() or 440) // 2 + 8
            self.draw_fish()

    def random_reposition_fish(self) -> None:
        w = max(760, self.canvas.winfo_width())
        h = max(360, self.canvas.winfo_height())

        margin_x = self.body_rx + 30
        margin_y = self.body_ry + 30

        self.cx = random.randint(margin_x, max(margin_x, w - margin_x))
        self.cy = random.randint(margin_y, max(margin_y, h - margin_y))

    def draw_fish(self) -> None:
        for item in self.fish_items:
            self.canvas.delete(item)
        self.fish_items.clear()
        self.glow_ring_ids.clear()

        for i, width in enumerate((3.2, 2.7, 2.2)):
            glow = self.canvas.create_oval(
                self.cx - self.body_rx - 10 - i * 7,
                self.cy - self.body_ry - 10 - i * 7,
                self.cx + self.body_rx + 10 + i * 7,
                self.cy + self.body_ry + 10 + i * 7,
                outline=GLOW_PALETTE[(self.glow_phase + i) % len(GLOW_PALETTE)],
                width=width,
            )
            self.fish_items.append(glow)
            self.glow_ring_ids.append(glow)

        body = self.canvas.create_oval(
            self.cx - self.body_rx,
            self.cy - self.body_ry,
            self.cx + self.body_rx,
            self.cy + self.body_ry,
            fill="#0f1731",
            outline=NEON_MAIN,
            width=4,
        )
        self.fish_items.append(body)
        self.core_item_id = body

        self.fish_items.append(
            self.canvas.create_line(
                self.cx - 90,
                self.cy,
                self.cx + 90,
                self.cy,
                fill=NEON_MAIN,
                width=3,
            )
        )

        self.fish_items.append(
            self.canvas.create_oval(
                self.cx - 26,
                self.cy - 26,
                self.cx + 26,
                self.cy + 26,
                fill="#101f45",
                outline=NEON_MAIN,
                width=3,
            )
        )

        self.fish_items.append(
            self.canvas.create_text(
                self.cx,
                self.cy,
                text="MỎ",
                fill=TEXT_COLOR,
                font=("Consolas", 14, "bold"),
            )
        )

    def animate_glow(self) -> None:
        if self.glow_ring_ids:
            self.glow_phase = (self.glow_phase + 1) % len(GLOW_PALETTE)
            for i, ring_id in enumerate(self.glow_ring_ids):
                self.canvas.itemconfig(
                    ring_id,
                    outline=GLOW_PALETTE[(self.glow_phase + i) % len(GLOW_PALETTE)],
                )
        self.root.after(170, self.animate_glow)

    # ------------------------ Interaction ------------------------
    def on_tap(self, event: tk.Event) -> None:
        if not self.game_running:
            self.status_label.config(text="Game chưa chạy. Bấm 'Bắt đầu / Chơi lại'.")
            return

        if self.is_hit(event.x, event.y):
            self.handle_hit(event.x, event.y)
        else:
            self.handle_miss(event.x, event.y)

    def is_hit(self, x: int, y: int) -> bool:
        # Kiểm tra điểm có nằm trong ellipse thân Mỏ hay không.
        dx = (x - self.cx) / self.body_rx
        dy = (y - self.cy) / self.body_ry
        return dx * dx + dy * dy <= 1.0

    def handle_hit(self, x: int, y: int) -> None:
        self.combo += 1
        bonus = 1 if self.combo % 5 == 0 else 0
        gain = 1 + bonus

        self.level_score += gain
        self.total_merit += gain

        self.flash_hit_effect()
        self.spawn_floating_text(x, y, f"+{gain} Công Đức", "#ffee8a")
        self.status_label.config(text="Cốc... Cốc... Trúng!")
        self.play_tap_sound()

        if self.level_score >= self.target_score:
            self.advance_level()
            return

        self.update_hud()

    def handle_miss(self, x: int, y: int) -> None:
        self.combo = 0
        self.time_left = max(0, self.time_left - 2)
        self.spawn_floating_text(x, y, "Trượt! -2s", "#ff8ab0")
        self.status_label.config(text="Trượt rồi! Cẩn thận, mất 2 giây.")
        self.update_hud()

        if self.time_left <= 0:
            self.handle_time_up()

    def flash_hit_effect(self) -> None:
        if not self.core_item_id:
            return

        self.canvas.itemconfig(self.core_item_id, outline="#b9fbff")
        burst_color = random.choice(GLOW_PALETTE)
        for ring_id in self.glow_ring_ids:
            self.canvas.itemconfig(ring_id, outline=burst_color)
        self.root.after(75, lambda: self.canvas.itemconfig(self.core_item_id, outline=NEON_MAIN))

    def spawn_floating_text(self, x: int, y: int, text: str, color: str) -> None:
        tid = self.canvas.create_text(
            x + random.randint(-10, 10),
            y + random.randint(-8, 8),
            text=text,
            fill=color,
            font=("Consolas", 13, "bold"),
        )
        self.animate_text_float(tid, life=20)

    def animate_text_float(self, text_id: int, life: int) -> None:
        if life <= 0:
            self.canvas.delete(text_id)
            return
        self.canvas.move(text_id, random.randint(-1, 1), -2)
        self.root.after(45, lambda: self.animate_text_float(text_id, life - 1))

    # ------------------------ Util ------------------------
    def play_tap_sound(self) -> None:
        try:
            import winsound  # type: ignore

            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            self.root.bell()

    def update_hud(self) -> None:
        self.top_info.config(
            text=(
                f"Level: {self.level} | Điểm level: {self.level_score}/{self.target_score} | "
                f"Tổng công đức: {self.total_merit} | Thời gian: {self.time_left}s | Combo: x{self.combo}"
            )
        )


def main() -> None:
    root = tk.Tk()
    CyberWoodenFishApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
