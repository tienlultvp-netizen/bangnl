#!/usr/bin/env python3
"""Cong Duc Dien Tu (Cyber Wooden Fish)

Mo phong do choi giai toa cang thang theo y tuong trong anh:
- Mo neon o giua man hinh
- Moi lan click se phat am thanh nhe, cong diem "Cong Duc +1"
- Hieu ung chu bay + glitch
- Muc tieu: nhac nho giu tam tinh lang
"""

from __future__ import annotations

import random
import tkinter as tk


BG_COLOR = "#090c18"
NEON_MAIN = "#00e5ff"
NEON_GLOW = "#4b6cff"
TEXT_COLOR = "#d8f7ff"
GLOW_PALETTE = ["#00e5ff", "#7a7dff", "#ff4fd8", "#7dffb3", "#ffd166"]


class CyberWoodenFishApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Công Đức Điện Tử • Cyber Wooden Fish")
        self.root.geometry("900x560")
        self.root.minsize(760, 500)
        self.root.configure(bg=BG_COLOR)

        self.total_merit = 0
        self.floating_labels: list[tuple[int, int]] = []

        self.title_label = tk.Label(
            root,
            text="🕉️ CÔNG ĐỨC ĐIỆN TỬ",
            fg=NEON_MAIN,
            bg=BG_COLOR,
            font=("Consolas", 24, "bold"),
        )
        self.title_label.pack(pady=(14, 4))

        self.subtitle_label = tk.Label(
            root,
            text="Nhấn vào Mỏ Neon để tích đức và thả lỏng tâm trí",
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            font=("Segoe UI", 12),
        )
        self.subtitle_label.pack(pady=(0, 8))

        self.counter_label = tk.Label(
            root,
            text="Tổng công đức: 0",
            fg="#ffe76a",
            bg=BG_COLOR,
            font=("Consolas", 15, "bold"),
        )
        self.counter_label.pack(pady=(0, 8))

        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.status_label = tk.Label(
            root,
            text="Chuẩn: Tư Tiên 4.0 • Gõ để nghe tiếng 'Cốc... Cốc...' điện tử",
            fg="#8ac8ff",
            bg=BG_COLOR,
            font=("Segoe UI", 11),
        )
        self.status_label.pack(pady=(0, 12))

        self.canvas.bind("<Button-1>", self.on_tap)
        self.canvas.bind("<Configure>", self.draw_fish)

        self.fish_items: list[int] = []
        self.glow_ring_ids: list[int] = []
        self.core_item_id: int | None = None
        self.glow_phase = 0
        self.draw_fish()
        self.animate_glow()

    def draw_fish(self, _event: tk.Event | None = None) -> None:
        """Ve hinh mo neon o giua canvas."""
        for item in self.fish_items:
            self.canvas.delete(item)
        self.fish_items.clear()

        w = self.canvas.winfo_width() or 900
        h = self.canvas.winfo_height() or 400
        cx, cy = w // 2, h // 2 + 8

        # Hieu ung glow ngoai
        self.glow_ring_ids.clear()
        for i, alpha_width in enumerate((58, 48, 38)):
            glow = self.canvas.create_oval(
                cx - 185 - i * 7,
                cy - 95 - i * 7,
                cx + 185 + i * 7,
                cy + 95 + i * 7,
                outline=GLOW_PALETTE[(self.glow_phase + i) % len(GLOW_PALETTE)],
                width=alpha_width / 18,
            )
            self.fish_items.append(glow)
            self.glow_ring_ids.append(glow)

        body = self.canvas.create_oval(
            cx - 170,
            cy - 86,
            cx + 170,
            cy + 86,
            fill="#0f1731",
            outline=NEON_MAIN,
            width=4,
        )
        self.fish_items.append(body)
        self.core_item_id = body

        midline = self.canvas.create_line(
            cx - 90,
            cy,
            cx + 90,
            cy,
            fill=NEON_MAIN,
            width=3,
        )
        self.fish_items.append(midline)

        hole = self.canvas.create_oval(
            cx - 26,
            cy - 26,
            cx + 26,
            cy + 26,
            fill="#101f45",
            outline=NEON_MAIN,
            width=3,
        )
        self.fish_items.append(hole)

        label = self.canvas.create_text(
            cx,
            cy,
            text="MỎ",
            fill=TEXT_COLOR,
            font=("Consolas", 14, "bold"),
        )
        self.fish_items.append(label)

        tip = self.canvas.create_text(
            cx,
            cy + 118,
            text="Tap để tích đức • Cốc... Cốc...",
            fill="#6fdfff",
            font=("Segoe UI", 11),
        )
        self.fish_items.append(tip)

    def on_tap(self, event: tk.Event) -> None:
        """Xu ly moi lan nguoi dung click vao canvas."""
        self.total_merit += 1
        self.counter_label.config(text=f"Tổng công đức: {self.total_merit}")

        self.play_tap_sound()
        self.flash_haptic_feedback()
        self.spawn_floating_text(event.x, event.y)

        if self.total_merit % 30 == 0:
            self.status_label.config(text="🎁 Drop duyên lành! Bạn vừa cầu được điều bình an.")
        elif self.total_merit % 9 == 0:
            self.status_label.config(text="Tâm tĩnh hơn một chút... tiếp tục nhé ✨")
        else:
            self.status_label.config(text="Cốc... Cốc... công đức +1")

    def play_tap_sound(self) -> None:
        """Phat am thanh nhe (co fallback cho moi he dieu hanh)."""
        try:
            import winsound  # type: ignore

            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            # fallback truc tiep bang chuong he thong Tk
            self.root.bell()

    def flash_haptic_feedback(self) -> None:
        """Gia lap haptic feedback bang nhay vien neon."""
        if not self.core_item_id:
            return

        # doi mau nhanh de tao cam giac rung nhe
        main_body = self.core_item_id
        self.canvas.itemconfig(main_body, outline="#b9fbff")
        self.root.after(65, lambda: self.canvas.itemconfig(main_body, outline=NEON_MAIN))

        # bung sang da mau cho cac vong glow
        burst_color = random.choice(GLOW_PALETTE)
        for ring_id in self.glow_ring_ids:
            self.canvas.itemconfig(ring_id, outline=burst_color)

    def animate_glow(self) -> None:
        """Tao hieu ung phat sang chuyen mau lien tuc."""
        if self.glow_ring_ids:
            self.glow_phase = (self.glow_phase + 1) % len(GLOW_PALETTE)
            for i, ring_id in enumerate(self.glow_ring_ids):
                color = GLOW_PALETTE[(self.glow_phase + i) % len(GLOW_PALETTE)]
                self.canvas.itemconfig(ring_id, outline=color)

        self.root.after(180, self.animate_glow)

    def spawn_floating_text(self, x: int, y: int) -> None:
        """Tao text bay + glitch 'Công Đức +1'."""
        dx = random.randint(-18, 18)
        dy = random.randint(-8, 8)

        text_id = self.canvas.create_text(
            x + dx,
            y + dy,
            text="Công Đức +1",
            fill="#ffee8a",
            font=("Consolas", 14, "bold"),
        )

        shadow_id = self.canvas.create_text(
            x + dx + 2,
            y + dy + 2,
            text="Công Đức +1",
            fill="#ff2f92",
            font=("Consolas", 14, "bold"),
        )
        self.canvas.tag_lower(shadow_id, text_id)

        self.floating_labels.append((text_id, shadow_id))
        self.animate_floating_text(text_id, shadow_id, life=24)

    def animate_floating_text(self, text_id: int, shadow_id: int, life: int) -> None:
        if life <= 0:
            self.canvas.delete(text_id)
            self.canvas.delete(shadow_id)
            return

        jitter_x = random.randint(-1, 1)
        self.canvas.move(text_id, jitter_x, -2)
        self.canvas.move(shadow_id, -jitter_x, -2)

        # fade gia lap bang thay doi mau theo thoi gian
        fade = max(60, 255 - (24 - life) * 8)
        text_color = f"#{fade:02x}{(fade - 25):02x}8a"
        shadow_color = f"#ff2f{max(40, fade - 80):02x}"
        self.canvas.itemconfig(text_id, fill=text_color)
        self.canvas.itemconfig(shadow_id, fill=shadow_color)

        self.root.after(45, lambda: self.animate_floating_text(text_id, shadow_id, life - 1))


def main() -> None:
    root = tk.Tk()
    app = CyberWoodenFishApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
