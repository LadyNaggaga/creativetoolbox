"""Hero tool: code_scribe.write_game — the Copilot-SDK-style code emitter.

Writes a complete, self-contained playable HTML5 canvas game to disk from a spec.
This mirrors what a Copilot SDK-powered coding agent would do inside your app:
receive a design brief, then emit real source files.

In the scripted demo the spec is filled in from prior Toolbox calls (theme, sprites,
sfx, bgm). In LIVE mode a real model would call this tool with its own spec.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "game-output"))

GAME_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<style>
  html, body { margin:0; padding:0; background:#0a0518; color:#e4d9ff; font-family: "Courier New", monospace; }
  h1 { text-align:center; margin:12px 0 4px; font-size:20px; color:#c9a8ff; text-shadow:0 0 6px #7a4fff; }
  .sub { text-align:center; font-size:11px; color:#7f6bb0; margin-bottom:8px; }
  canvas { display:block; margin:0 auto; background:#140832; border:2px solid #4a2a8f; box-shadow:0 0 24px #4a2a8f; image-rendering: pixelated; }
  .hud { text-align:center; margin-top:8px; font-size:13px; }
  .foot { text-align:center; font-size:10px; color:#5c4a80; margin-top:6px; }
</style>
</head>
<body>
<h1>__TITLE__</h1>
<div class="sub">arrow keys or A/D to move · P to pause · R to restart</div>
<canvas id="game" width="480" height="360"></canvas>
<div class="hud" id="hud">score: 0 · lives: 3</div>
<div class="foot">emitted by code_scribe.write_game — theme: __THEME__ · bgm: __BGM__</div>

<script>
// ------- config ------
const W=480, H=360;
const PLAYER_SPRITE = "__PLAYER_EMOJI__";
const ENEMY_SPRITE  = "__ENEMY_EMOJI__";
const ITEM_SPRITE   = "__ITEM_EMOJI__";
const BG_TINT       = "__BG_TINT__";

// ------- state ------
const cvs = document.getElementById("game");
const ctx = cvs.getContext("2d");
const keys = {};
let player = { x: W/2, y: H-40, w: 28, h: 28, speed: 4 };
let enemies = [], items = [];
let score = 0, lives = 3, tick = 0, paused = false, dead = false;

document.addEventListener("keydown", e => { keys[e.key.toLowerCase()] = true; if (e.key==="p"||e.key==="P") paused=!paused; if (e.key==="r"||e.key==="R") reset(); });
document.addEventListener("keyup",   e => { keys[e.key.toLowerCase()] = false; });

// ------- audio (tiny WebAudio synth) ------
let ac;
function beep(freq, dur, type="square", gain=0.05) {
  try {
    ac = ac || new (window.AudioContext||window.webkitAudioContext)();
    const o = ac.createOscillator(), g = ac.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.value = gain;
    o.connect(g); g.connect(ac.destination);
    o.start(); o.stop(ac.currentTime + dur);
  } catch(_){}
}
const sfx = {
  coin: () => { beep(880, 0.06); setTimeout(()=>beep(1320, 0.08), 60); },
  hit:  () => { beep(120, 0.18, "sawtooth", 0.08); },
  over: () => { beep(220, 0.2); setTimeout(()=>beep(160,0.25),150); setTimeout(()=>beep(110,0.35),350); },
};

// ------- spawn ------
function spawnEnemy(){ enemies.push({ x: Math.random()*(W-24)+12, y: -20, w: 26, h: 26, vy: 1.4 + Math.random()*1.6, bob: Math.random()*Math.PI*2 }); }
function spawnItem(){ items.push({ x: Math.random()*(W-24)+12, y: -20, w: 22, h: 22, vy: 2.0 + Math.random() }); }

// ------- physics ------
function step(){
  if (keys["arrowleft"]||keys["a"])  player.x = Math.max(14, player.x - player.speed);
  if (keys["arrowright"]||keys["d"]) player.x = Math.min(W-14, player.x + player.speed);

  tick++;
  if (tick % 55 === 0) spawnEnemy();
  if (tick % 75 === 0) spawnItem();

  enemies.forEach(e => { e.y += e.vy; e.bob += 0.1; e.x += Math.sin(e.bob)*0.6; });
  items.forEach(i => i.y += i.vy);

  // collisions
  enemies = enemies.filter(e => {
    if (hit(player, e)) { lives--; sfx.hit(); if (lives<=0){ dead=true; sfx.over(); } return false; }
    return e.y < H+30;
  });
  items = items.filter(i => {
    if (hit(player, i)) { score += 10; sfx.coin(); return false; }
    return i.y < H+30;
  });
}

function hit(a,b){ return Math.abs(a.x-b.x) < (a.w+b.w)/2 - 4 && Math.abs(a.y-b.y) < (a.h+b.h)/2 - 4; }

// ------- render ------
function drawSprite(emoji, x, y, size){
  ctx.font = size + "px serif";
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.fillText(emoji, x, y);
}
function render(){
  // bg
  ctx.fillStyle = BG_TINT; ctx.fillRect(0,0,W,H);
  // scanlines
  ctx.fillStyle = "rgba(255,255,255,0.03)";
  for (let y=0; y<H; y+=3) ctx.fillRect(0,y,W,1);

  items.forEach(i => drawSprite(ITEM_SPRITE, i.x, i.y, 22));
  enemies.forEach(e => drawSprite(ENEMY_SPRITE, e.x, e.y, 28));
  drawSprite(PLAYER_SPRITE, player.x, player.y, 30);

  if (paused){ overlay("PAUSED", "press P to resume"); }
  if (dead){  overlay("GAME OVER", "press R to restart — score: " + score); }
}
function overlay(title, sub){
  ctx.fillStyle = "rgba(10,5,24,0.72)"; ctx.fillRect(0,H/2-46, W, 92);
  ctx.fillStyle = "#e4d9ff"; ctx.textAlign="center";
  ctx.font = "22px monospace"; ctx.fillText(title, W/2, H/2-6);
  ctx.font = "12px monospace"; ctx.fillText(sub, W/2, H/2+22);
}

function hud(){
  document.getElementById("hud").textContent = "score: " + score + " · lives: " + Math.max(0,lives);
}

function reset(){
  enemies=[]; items=[]; score=0; lives=3; tick=0; dead=false; paused=false;
  player.x = W/2;
}

function loop(){
  if (!paused && !dead) step();
  render(); hud();
  requestAnimationFrame(loop);
}
loop();
</script>
</body>
</html>
"""


def _pick(sprites_line, key, default):
    # sprites_line is like "sprites: player=X; enemy=Y; collectible=Z; background=W"
    for part in (sprites_line or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            if key in k:
                return v.strip()
    return default


def run(args):
    a = args or {}
    theme = a.get("theme", "Haunted Vending Machine")
    sprites = a.get("sprites", "")
    bgm = a.get("bgm", "midnight-arcade-loop.chip")
    title = f"Pixel Jam — {theme}"

    # theme-aware emoji picks (fallbacks if sprites text doesn't parse)
    theme_l = theme.lower()
    if "haunted" in theme_l or "vending" in theme_l:
        p, e, i, tint = "🥤", "👻", "🍫", "#1a0a3d"
    elif "gravity" in theme_l:
        p, e, i, tint = "🧑\u200d🚀", "🪨", "💎", "#050820"
    elif "toaster" in theme_l:
        p, e, i, tint = "🧑\u200d🍳", "🍞", "🧈", "#2a1a0a"
    else:
        p, e, i, tint = "🚀", "👾", "⭐", "#0a1030"

    html = (GAME_HTML
            .replace("__TITLE__", title)
            .replace("__THEME__", theme)
            .replace("__BGM__", bgm)
            .replace("__PLAYER_EMOJI__", p)
            .replace("__ENEMY_EMOJI__", e)
            .replace("__ITEM_EMOJI__", i)
            .replace("__BG_TINT__", tint))

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    lines = html.count("\n") + 1
    return f"wrote {out_path}  ({lines} lines, {len(html)} bytes) — open it in a browser to play"
