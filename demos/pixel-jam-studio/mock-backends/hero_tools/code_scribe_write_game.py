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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700&display=swap">
<style>
  :root {
    --cl-bg:    #D6D6D4;
    --cl-ink:   #1A1A1A;
    --cl-faint: #6B6B68;
    --cl-line:  #1A1A1A;
    --cl-mono:  'JetBrains Mono', ui-monospace, Menlo, monospace;
    --cl-sans:  'Inter', system-ui, sans-serif;
  }
  html, body { margin:0; padding:0; background:var(--cl-bg); color:var(--cl-ink); font-family:var(--cl-mono); }
  .wrap { max-width:820px; margin:0 auto; padding:2rem 1.25rem; }
  h1 { font-family:var(--cl-sans); font-weight:700; font-size:1.6rem; margin:0 0 .3rem; border-bottom:2px solid var(--cl-line); padding-bottom:.3rem; }
  .sub { font-size:12px; color:var(--cl-faint); margin:0 0 1rem; }
  .sub::before { content:"// "; }
  .stage { border:1px solid var(--cl-line); background:var(--cl-bg); padding:0; }
  canvas { display:block; margin:0 auto; background:var(--cl-bg); image-rendering:pixelated; image-rendering:crisp-edges; }
  .hud { display:flex; justify-content:space-between; gap:1rem; padding:.5rem .8rem; border-top:1px solid var(--cl-line); font-family:var(--cl-mono); font-size:.85rem; }
  .hud .tag { font-weight:700; border:1px solid var(--cl-line); padding:0 .5ch; }
  .foot { margin-top:.7rem; font-size:11px; color:var(--cl-faint); }
  .foot::before { content:"// "; }
  .keys { margin-top:.4rem; font-size:11px; color:var(--cl-faint); }

  /* intro screen */
  .intro { width:720px; height:420px; padding:2rem 2.4rem; display:flex; align-items:center; justify-content:center; }
  .intro-inner { width:100%; }
  .intro-tag { font-family:var(--cl-mono); font-size:.72rem; font-weight:700; letter-spacing:.08em;
               border:1px solid var(--cl-line); display:inline-block; padding:.15rem .55rem; margin-bottom:.9rem; }
  .intro-title { font-family:var(--cl-sans); font-weight:700; font-size:1.7rem; margin:0 0 1rem;
                 border-bottom:1px solid var(--cl-line); padding-bottom:.4rem; }
  .story { font-family:var(--cl-mono); font-size:.92rem; line-height:1.55; color:var(--cl-ink);
           background:transparent; border:0; margin:0; white-space:pre-wrap; min-height:9.5em; }
  .story .cursor { display:inline-block; width:.55ch; background:var(--cl-ink); animation: cl-blink 1.05s steps(1) infinite; margin-left:1px; }
  @keyframes cl-blink { 50% { opacity: 0; } }
  .controls-row { margin-top:1.1rem; display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
  .controls { font-family:var(--cl-mono); font-size:.8rem; color:var(--cl-faint); display:flex; gap:.9rem; flex-wrap:wrap; }
  .controls .tag { font-family:var(--cl-mono); font-weight:700; color:var(--cl-ink);
                   border:1px solid var(--cl-line); padding:0 .5ch; margin-right:.35ch; }
  .start-btn { font-family:var(--cl-mono); font-weight:700; font-size:.95rem;
               background:var(--cl-ink); color:var(--cl-bg); border:1px solid var(--cl-line);
               padding:.55rem 1.2rem; cursor:pointer; letter-spacing:.06em; }
  .start-btn:hover { background:var(--cl-bg); color:var(--cl-ink); }
  .start-btn:focus { outline:2px solid var(--cl-ink); outline-offset:2px; }
</style>
</head>
<body>
<div class="wrap">
<h1>__TITLE__</h1>
<p class="sub">emitted by code_scribe.write_game · theme: __THEME__ · bgm: __BGM__</p>
<div class="stage">
  <div id="intro" class="intro">
    <div class="intro-inner">
      <div class="intro-tag">PIXEL JAM · ISSUE #042</div>
      <h2 class="intro-title">__TITLE__</h2>
      <pre id="story" class="story" aria-live="polite"></pre>
      <div id="controls-row" class="controls-row" hidden>
        <div class="controls">
          <span><span class="tag">← →</span> move</span>
          <span><span class="tag">A / D</span> move</span>
          <span><span class="tag">P</span> pause</span>
          <span><span class="tag">R</span> restart</span>
        </div>
        <button id="start" class="start-btn">▶ START</button>
      </div>
    </div>
  </div>
  <canvas id="game" width="720" height="420" hidden></canvas>
  <div id="hud-row" class="hud" hidden>
    <span><span class="tag">SCORE</span> <span id="score">0</span></span>
    <span><span class="tag">LIVES</span> <span id="lives">3</span></span>
    <span><span class="tag">THEME</span> __THEME__</span>
  </div>
</div>
<p class="keys" id="keys-foot" hidden>← → or A / D to move · P to pause · R to restart</p>
<p class="foot">one endpoint, many tools, flat cost — this game was written by a single tool call.</p>
</div>

<script>
const W=720, H=420;
const INK   = "#1A1A1A";
const PAPER = "#D6D6D4";
const FAINT = "#6B6B68";
const PX = 4;  // pixel scale — big and readable

const STORY = [
  "> location: aisle 4, after hours.",
  "> the vending machine hums. it should not hum.",
  "",
  "you are the last soda can on the shelf.",
  "the ghosts of every expired candy bar drift down,",
  "hungry for a fizzy soul.",
  "",
  "grab the good candy. dodge the ghosts.",
  "score high enough and the machine goes quiet again.",
  "",
  "> ready when you are, jammer.",
].join("\n");

// typewriter
const storyEl = document.getElementById("story");
const ctrlRow = document.getElementById("controls-row");
const startBtn = document.getElementById("start");
let typed = 0;
function type(){
  if (typed <= STORY.length){
    storyEl.innerHTML = STORY.slice(0, typed).replace(/</g,"&lt;") + '<span class="cursor">&nbsp;</span>';
    typed++;
    // pause a beat on newlines and periods for rhythm
    const c = STORY[typed-2] || "";
    const delay = (c === "\n") ? 80 : (".!,>".includes(c) ? 90 : 22);
    setTimeout(type, delay);
  } else {
    storyEl.innerHTML = STORY.replace(/</g,"&lt;") + '<span class="cursor">&nbsp;</span>';
    ctrlRow.hidden = false;
    startBtn.focus();
  }
}
setTimeout(type, 300);

startBtn.addEventListener("click", startGame);
document.addEventListener("keydown", e => {
  if (!started && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); startGame(); }
});

let started = false;
function startGame(){
  if (started) return;
  started = true;
  document.getElementById("intro").hidden = true;
  document.getElementById("game").hidden = false;
  document.getElementById("hud-row").hidden = false;
  document.getElementById("keys-foot").hidden = false;
  try { ac = ac || new (window.AudioContext||window.webkitAudioContext)(); } catch(_){}
  loop();
}  // pixel scale — big and readable

// 12-column pixel sprites (X = ink, . = paper). Drawn ~48px tall for high contrast.
function parseSprite(rows){
  const grid = rows.map(r => r.split(""));
  return { w: grid[0].length, h: grid.length, grid };
}
const SPRITES = {
  player: parseSprite([
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
  ]),
  enemy: parseSprite([
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
  ]),
  item: parseSprite([
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
  ]),
};

const cvs = document.getElementById("game");
const ctx = cvs.getContext("2d");
const keys = {};
let player, enemies, items, score, lives, tick, paused, dead;

function drawSprite(sprite, cx, cy, scale){
  scale = scale || PX;
  const ox = cx - (sprite.w*scale)/2;
  const oy = cy - (sprite.h*scale)/2;
  ctx.fillStyle = INK;
  for (let y=0; y<sprite.h; y++){
    for (let x=0; x<sprite.w; x++){
      if (sprite.grid[y][x] === "X") ctx.fillRect(ox + x*scale, oy + y*scale, scale, scale);
    }
  }
}

function reset(){
  player = { x: W/2, y: H-46, w: 40, h: 48, speed: 5 };
  enemies = []; items = [];
  score = 0; lives = 3; tick = 0; paused = false; dead = false;
}
reset();

document.addEventListener("keydown", e => {
  keys[e.key.toLowerCase()] = true;
  if (e.key==="p"||e.key==="P") paused = !paused;
  if (e.key==="r"||e.key==="R") reset();
  if (["ArrowLeft","ArrowRight"," "].includes(e.key)) e.preventDefault();
});
document.addEventListener("keyup", e => { keys[e.key.toLowerCase()] = false; });

// tiny WebAudio synth
let ac;
function beep(freq, dur, type, gain){
  try {
    ac = ac || new (window.AudioContext||window.webkitAudioContext)();
    const o = ac.createOscillator(), g = ac.createGain();
    o.type = type || "square"; o.frequency.value = freq;
    g.gain.value = gain || 0.04;
    o.connect(g); g.connect(ac.destination);
    o.start(); o.stop(ac.currentTime + dur);
  } catch(_){}
}
const sfx = {
  coin: () => { beep(880, 0.06); setTimeout(()=>beep(1320, 0.08), 60); },
  hit:  () => { beep(120, 0.18, "sawtooth", 0.06); },
  over: () => { beep(220,0.2); setTimeout(()=>beep(160,0.25),150); setTimeout(()=>beep(110,0.35),350); },
};
cvs.addEventListener("click", () => { try { ac = ac || new (window.AudioContext||window.webkitAudioContext)(); } catch(_){} });

function spawnEnemy(){ enemies.push({ x: 40 + Math.random()*(W-80), y:-30, w:40, h:48, vy: 1.6 + Math.random()*1.4, bob: Math.random()*Math.PI*2 }); }
function spawnItem(){ items.push({ x: 40 + Math.random()*(W-80), y:-30, w:40, h:48, vy: 2.2 + Math.random() }); }

function hit(a,b){
  return Math.abs(a.x-b.x) < (a.w+b.w)/2 - 8 && Math.abs(a.y-b.y) < (a.h+b.h)/2 - 8;
}

function step(){
  if (keys["arrowleft"]||keys["a"])  player.x = Math.max(24, player.x - player.speed);
  if (keys["arrowright"]||keys["d"]) player.x = Math.min(W-24, player.x + player.speed);
  tick++;
  if (tick % 55 === 0) spawnEnemy();
  if (tick % 70 === 0) spawnItem();
  enemies.forEach(e => { e.y += e.vy; e.bob += 0.1; e.x += Math.sin(e.bob)*0.8; });
  items.forEach(i => i.y += i.vy);
  enemies = enemies.filter(e => {
    if (hit(player, e)) { lives--; sfx.hit(); if (lives<=0){ dead=true; sfx.over(); } return false; }
    return e.y < H+40;
  });
  items = items.filter(i => {
    if (hit(player, i)) { score += 10; sfx.coin(); return false; }
    return i.y < H+40;
  });
}

function drawGrid(){
  ctx.fillStyle = PAPER;
  ctx.fillRect(0,0,W,H);
  // faint 20px grid lines to feel like graph paper
  ctx.strokeStyle = "rgba(26,26,26,0.06)";
  ctx.lineWidth = 1;
  for (let x=0; x<W; x+=20){ ctx.beginPath(); ctx.moveTo(x+0.5,0); ctx.lineTo(x+0.5,H); ctx.stroke(); }
  for (let y=0; y<H; y+=20){ ctx.beginPath(); ctx.moveTo(0,y+0.5); ctx.lineTo(W,y+0.5); ctx.stroke(); }
  // ground line
  ctx.strokeStyle = INK; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, H-16); ctx.lineTo(W, H-16); ctx.stroke();
}

function render(){
  drawGrid();
  items.forEach(i => drawSprite(SPRITES.item, i.x, i.y));
  enemies.forEach(e => drawSprite(SPRITES.enemy, e.x, e.y));
  drawSprite(SPRITES.player, player.x, player.y);

  if (paused) overlay("PAUSED", "press P to resume");
  if (dead)   overlay("GAME OVER", "press R to restart · score: " + score);
}

function overlay(title, sub){
  ctx.fillStyle = PAPER; ctx.fillRect(W/2-180, H/2-50, 360, 100);
  ctx.strokeStyle = INK; ctx.lineWidth = 1; ctx.strokeRect(W/2-180, H/2-50, 360, 100);
  ctx.fillStyle = INK; ctx.textAlign="center";
  ctx.font = "700 22px Inter, system-ui, sans-serif";
  ctx.fillText(title, W/2, H/2-4);
  ctx.font = "12px 'JetBrains Mono', monospace";
  ctx.fillStyle = FAINT;
  ctx.fillText(sub, W/2, H/2+22);
}

function hud(){
  document.getElementById("score").textContent = score;
  document.getElementById("lives").textContent = Math.max(0, lives);
}

function loop(){
  if (!started) return;
  if (!paused && !dead) step();
  render(); hud();
  requestAnimationFrame(loop);
}
</script>
</body>
</html>
"""


def run(args):
    a = args or {}
    theme = a.get("theme", "Haunted Vending Machine")
    bgm = a.get("bgm", "midnight-arcade-loop.chip")
    title = f"Pixel Jam — {theme}"

    html = (GAME_HTML
            .replace("__TITLE__", title)
            .replace("__THEME__", theme)
            .replace("__BGM__", bgm))

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    lines = html.count("\n") + 1
    return f"wrote {out_path}  ({lines} lines, {len(html)} bytes) — open it in a browser to play"
