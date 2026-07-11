"""Build a looping gameplay GIF for the pixel-jam-studio blog.

Reproduces the same monochrome ink-on-grey visuals as the emitted game
(same pixel sprites, same grid, same HUD) and simulates ~7s of play so
the blog can show what a run looks like without embedding the whole game.

Output: assets/demo.gif  (loop=0)
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "demo.gif")

# ---- palette (matches commandline.css) ----
PAPER = (214, 214, 212)  # #D6D6D4
INK = (26, 26, 26)       # #1A1A1A
FAINT = (107, 107, 104)  # #6B6B68

# ---- canvas geometry (matches game) ----
W, H = 720, 420
PX = 4

# ---- sprites (same 10x12 grids as the game) ----
def parse(rows):
    return [list(r) for r in rows]

PLAYER = parse([
    "..XXXXXX..",
    ".XXXXXXXX.",
    ".X......X.",
    ".X.XXXX.X.",
    ".X.X..X.X.",
    ".X.XXXX.X.",
    ".X......X.",
    ".X.XXXX.X.",
    ".X.X..X.X.",
    ".X.XXXX.X.",
    ".X......X.",
    ".XXXXXXXX.",
])
ENEMY = parse([
    "..XXXXXX..",
    ".XXXXXXXX.",
    "XX.XX.XX.X",
    "XXXXXXXXXX",
    "XXXXXXXXXX",
    "XX.XXXX.XX",
    "X.XXXXXX.X",
    "XXXXXXXXXX",
    "XXXXXXXXXX",
    "X.X.XX.X.X",
    "X..X..X..X",
    "..........",
])
ITEM = parse([
    "..........",
    "..XXXXXX..",
    ".X......X.",
    ".X.X..X.X.",
    ".X......X.",
    ".X.XXXX.X.",
    ".X.X..X.X.",
    ".X.XXXX.X.",
    ".X......X.",
    ".X.X..X.X.",
    ".X......X.",
    "..XXXXXX..",
])

SPRITE_W = len(PLAYER[0]) * PX  # 40
SPRITE_H = len(PLAYER) * PX     # 48


def _font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\JetBrainsMono-Bold.ttf" if bold else r"C:\Windows\Fonts\JetBrainsMono-Regular.ttf",
        r"C:\Windows\Fonts\consolab.ttf" if bold else r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


F_HUD = _font(18, bold=True)
F_LBL = _font(13, bold=True)
F_SUB = _font(12)
F_TITLE = _font(22, bold=True)


def draw_sprite(draw, sprite, cx, cy):
    ox = int(cx - SPRITE_W / 2)
    oy = int(cy - SPRITE_H / 2)
    for y, row in enumerate(sprite):
        for x, ch in enumerate(row):
            if ch == "X":
                draw.rectangle([ox + x*PX, oy + y*PX, ox + (x+1)*PX - 1, oy + (y+1)*PX - 1], fill=INK)


def draw_grid(draw):
    draw.rectangle([0, 0, W, H], fill=PAPER)
    # faint 20px graph paper (single-pixel dots by drawing short strokes with alpha)
    for x in range(0, W, 20):
        draw.line([(x, 0), (x, H)], fill=(200, 200, 198))
    for y in range(0, H, 20):
        draw.line([(0, y), (W, y)], fill=(200, 200, 198))
    # ground line
    draw.line([(0, H - 16), (W, H - 16)], fill=INK)


def draw_frame(state):
    im = Image.new("RGB", (W, H + 40), PAPER)
    draw = ImageDraw.Draw(im)
    draw_grid(draw)

    for it in state["items"]:
        draw_sprite(draw, ITEM, it["x"], it["y"])
    for en in state["enemies"]:
        draw_sprite(draw, ENEMY, en["x"], en["y"])
    draw_sprite(draw, PLAYER, state["player"]["x"], state["player"]["y"])

    # HUD strip (below game area)
    draw.line([(0, H), (W, H)], fill=INK)
    _chip(draw, 12, H + 10, "SCORE", str(state["score"]))
    _chip(draw, 170, H + 10, "LIVES", str(max(0, state["lives"])))
    _chip(draw, 330, H + 10, "THEME", "Haunted Vending Machine")

    if state.get("overlay"):
        _overlay(draw, state["overlay"][0], state["overlay"][1])

    return im


def _chip(draw, x, y, label, value):
    # [LABEL] value  — sharp-border tag chip like the blog
    lbl_w = int(F_LBL.getlength(label)) + 12
    draw.rectangle([x, y, x + lbl_w, y + 22], outline=INK, width=1, fill=PAPER)
    draw.text((x + 6, y + 3), label, fill=INK, font=F_LBL)
    draw.text((x + lbl_w + 8, y + 3), value, fill=INK, font=F_LBL)


def _overlay(draw, title, sub):
    bx, by, bw, bh = W // 2 - 200, H // 2 - 60, 400, 120
    draw.rectangle([bx, by, bx + bw, by + bh], fill=PAPER, outline=INK, width=1)
    tw = int(F_TITLE.getlength(title))
    draw.text((W // 2 - tw // 2, by + 20), title, fill=INK, font=F_TITLE)
    sw = int(F_SUB.getlength(sub))
    draw.text((W // 2 - sw // 2, by + 60), sub, fill=FAINT, font=F_SUB)


# ---- simulation ----
def simulate(fps=12, seconds=8, seed=42):
    random.seed(seed)
    state = {
        "player": {"x": W // 2, "y": H - 46},
        "enemies": [],
        "items": [],
        "score": 0,
        "lives": 3,
        "overlay": None,
    }
    frames = []

    # scripted movement pattern — smooth left/right zigzag while items/enemies fall
    total = fps * seconds
    for t in range(total):
        # movement: sinusoidal sweep to look intentional
        import math
        target = W // 2 + int(math.sin(t / 8.0) * 220)
        px = state["player"]["x"]
        if target > px:
            state["player"]["x"] = min(px + 10, target)
        elif target < px:
            state["player"]["x"] = max(px - 10, target)

        # spawn
        if t % 8 == 3:
            state["enemies"].append({
                "x": 40 + random.random() * (W - 80),
                "y": -30,
                "vy": 5 + random.random() * 2,
                "bob": random.random() * 6.28,
            })
        if t % 6 == 0:
            state["items"].append({
                "x": 40 + random.random() * (W - 80),
                "y": -30,
                "vy": 7 + random.random() * 2,
            })

        # move
        for e in state["enemies"]:
            e["y"] += e["vy"]
            e["bob"] += 0.2
            e["x"] += math.sin(e["bob"]) * 1.6
        for i in state["items"]:
            i["y"] += i["vy"]

        # collisions
        p = state["player"]
        new_enemies = []
        for e in state["enemies"]:
            if abs(p["x"] - e["x"]) < SPRITE_W - 12 and abs(p["y"] - e["y"]) < SPRITE_H - 12:
                state["lives"] -= 1
                continue
            if e["y"] < H + 40:
                new_enemies.append(e)
        state["enemies"] = new_enemies

        new_items = []
        for i in state["items"]:
            if abs(p["x"] - i["x"]) < SPRITE_W - 12 and abs(p["y"] - i["y"]) < SPRITE_H - 12:
                state["score"] += 10
                continue
            if i["y"] < H + 40:
                new_items.append(i)
        state["items"] = new_items

        frames.append(draw_frame(state))

    # closing "GAME OVER-ish" hold frame with score
    state["overlay"] = ("NICE RUN", f"score: {state['score']} · lives: {max(0,state['lives'])}")
    for _ in range(fps):
        frames.append(draw_frame(state))

    return frames, fps


def main():
    frames, fps = simulate()
    duration = int(1000 / fps)
    # palette-quantize each frame for smaller GIFs
    pal_frames = [f.convert("P", palette=Image.ADAPTIVE, colors=16) for f in frames]
    pal_frames[0].save(
        OUT, save_all=True, append_images=pal_frames[1:],
        duration=duration, loop=0, optimize=True, disposal=2,
    )
    print(f"wrote {OUT} ({len(frames)} frames @ {fps}fps, {os.path.getsize(OUT)//1024} KB)")


if __name__ == "__main__":
    main()
