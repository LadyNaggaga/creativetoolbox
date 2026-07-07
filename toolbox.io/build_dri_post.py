"""Generate blog/dri-oncall-agent.html from demos/dri-oncall-agent/BLOG.md.

Matches the hand-authored style of the other local posts (commandline.css, same
head/style block). Replaces the two ASCII loop diagrams with inline SVG figures
and adds anime.js flourishes (staggered section fade-in + hero pulse).
"""
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SRC = REPO / "demos" / "dri-oncall-agent" / "BLOG.md"
OUT = ROOT / "blog" / "dri-oncall-agent.html"
SLUG = "dri-oncall-agent"

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — toolbox.io</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="../assets/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="../assets/favicon-180.png">
<link rel="stylesheet" href="../assets/commandline.css">
<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>
<style>
 body.cl{{max-width:820px;margin:0 auto;padding:2rem 1.25rem;font-size:15px;}}
 .cl h1{{border-bottom:2px solid var(--cl-line);padding-bottom:.3rem;}}
 .cl pre{{border:1px solid var(--cl-line);padding:12px 14px;overflow:auto;background:#cfcfcd;white-space:pre;}}
 .cl code{{font-family:var(--cl-mono);}}
 .cl ul{{padding-left:1.2rem;}} .cl li{{margin:.2rem 0;}}
 .cl table{{border-collapse:collapse;margin:1rem 0;font-size:.9rem;}}
 .cl th,.cl td{{border:1px solid var(--cl-line);padding:.35rem .6rem;text-align:left;}}
 .cl th{{background:#cfcfcd;}}
 .cl blockquote{{border-left:3px solid var(--cl-line);margin:1rem 0;padding:.2rem .8rem;color:var(--cl-faint);}}
 .nav{{margin-bottom:1rem;}} .nav a{{color:var(--cl-ink);text-decoration:underline;}}
 .badge{{display:inline-block;font-size:.72em;letter-spacing:.04em;border:1px solid var(--cl-line);padding:0 .4ch;text-transform:uppercase;margin-bottom:.6rem;}}
 .figure{{border:1px solid var(--cl-line);margin:1rem 0;background:var(--cl-bg);}}
 .figure .slot,.figure svg{{display:block;width:100%;height:auto;}}
 .figure figcaption{{display:flex;justify-content:space-between;gap:1rem;padding:.4rem .7rem;border-top:1px solid var(--cl-line);font-family:var(--cl-mono);font-size:.78rem;color:var(--cl-faint);}}
 .figure figcaption a,.figure figcaption button{{font:inherit;color:var(--cl-ink);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline;}}
 /* anime.js reveal — hidden until JS enables (or reduced-motion falls back) */
 .cl h2,.cl h3,.cl .figure{{opacity:0;transform:translateY(8px);}}
 .reveal-ready .cl h2,.reveal-ready .cl h3,.reveal-ready .cl .figure{{opacity:1;transform:none;}}
 @media (prefers-reduced-motion: reduce){{
   .cl h2,.cl h3,.cl .figure{{opacity:1;transform:none;}}
 }}
</style></head><body class="cl">
<p class="nav"><a href="../index.html#trends">&larr; back to gallery</a></p>
<span class="badge">agent loop</span>
<h1><a href="https://github.com/LadyNaggaga/creativetoolbox/tree/main/demos/{slug}" style="color:inherit;text-decoration:none">{title}</a></h1>
<p class="nav"><a href="https://github.com/LadyNaggaga/creativetoolbox/tree/main/demos/{slug}">view the demo on GitHub &rarr;</a></p>

<figure class="figure" id="art-figure">
  <div class="slot" aria-label="loading art"></div>
  <figcaption>
    <span>// art for {slug} · four rings, one agent · monochrome · CC0</span>
    <span>
      <a href="../assets/art/{slug}.svg" download>&#8595; svg</a>
      &middot;
      <button type="button" id="art-png">&#8595; png</button>
    </span>
  </figcaption>
</figure>
"""

TAIL = """
<p class="nav" style="margin-top:2rem;">&gt;_ happy building.</p>
<script src="../assets/svg-figure.js"></script>
<script>
(async function () {{
  const f = window.toolboxFigure;
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Inline the hero art + both diagrams so their CSS animations run and PNG export works.
  const artSvg  = await f.inlineSVG('../assets/art/{slug}.svg',
                                    document.querySelector('#art-figure .slot'));
  const loopSvg = await f.inlineSVG('../assets/diagrams/{slug}-loop.svg',
                                    document.querySelector('#loop-figure .slot'));
  const fourSvg = await f.inlineSVG('../assets/diagrams/{slug}-four-loops.svg',
                                    document.querySelector('#four-figure .slot'));
  document.getElementById('art-png').addEventListener('click', () => {{
    f.downloadPNG(artSvg, '{slug}--art.png', 2);
  }});
  document.getElementById('loop-png').addEventListener('click', () => {{
    f.downloadPNG(loopSvg, '{slug}--agent-loop.png', 2);
  }});
  document.getElementById('four-png').addEventListener('click', () => {{
    f.downloadPNG(fourSvg, '{slug}--four-loops.png', 2);
  }});
  const verSvg  = await f.inlineSVG('../assets/diagrams/{slug}-verification.svg',
                                    document.querySelector('#verification-figure .slot'));
  const evtSvg  = await f.inlineSVG('../assets/diagrams/{slug}-events.svg',
                                    document.querySelector('#events-figure .slot'));
  const hillSvg = await f.inlineSVG('../assets/diagrams/{slug}-hillclimbing.svg',
                                    document.querySelector('#hillclimbing-figure .slot'));
  document.getElementById('verification-png').addEventListener('click', () => {{
    f.downloadPNG(verSvg, '{slug}--verification-loop.png', 2);
  }});
  document.getElementById('events-png').addEventListener('click', () => {{
    f.downloadPNG(evtSvg, '{slug}--event-routine-loop.png', 2);
  }});
  document.getElementById('hillclimbing-png').addEventListener('click', () => {{
    f.downloadPNG(hillSvg, '{slug}--hill-climbing-loop.png', 2);
  }});

  // Stagger-reveal the section headers and figures as they enter view.
  document.body.classList.add('reveal-ready');
  if (prefersReducedMotion) return;

  const targets = document.querySelectorAll('.cl h2, .cl h3, .cl .figure');
  targets.forEach(el => {{ el.style.opacity = '0'; el.style.transform = 'translateY(8px)'; }});
  const observer = new IntersectionObserver((entries) => {{
    const shown = entries.filter(e => e.isIntersecting).map(e => e.target);
    if (!shown.length) return;
    anime({{
      targets: shown,
      opacity: [0, 1],
      translateY: [8, 0],
      duration: 500,
      delay: anime.stagger(70),
      easing: 'easeOutCubic'
    }});
    shown.forEach(t => observer.unobserve(t));
  }}, {{ threshold: 0.15 }});
  targets.forEach(t => observer.observe(t));

  // Subtle hero pulse on the title underline.
  anime({{
    targets: '.cl h1',
    borderBottomColor: ['rgba(26,26,26,1)', 'rgba(26,26,26,0.35)', 'rgba(26,26,26,1)'],
    duration: 2400,
    easing: 'easeInOutSine',
    direction: 'alternate',
    loop: true
  }});
}})();
</script>
</body></html>
"""

md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])

LOOP_TOKEN = "DRILOOP1FIGURE"
FOUR_TOKEN = "DRIFOURLOOPSFIGURE"
VER_TOKEN  = "DRIVERIFICATIONFIGURE"
EVT_TOKEN  = "DRIEVENTSFIGURE"
HILL_TOKEN = "DRIHILLCLIMBINGFIGURE"


def _figure(fig_id: str, slug_suffix: str, caption: str, btn_id: str) -> str:
    return (
        f'<figure class="figure" id="{fig_id}">'
        '<div class="slot" aria-label="loading diagram"></div>'
        '<figcaption>'
        f'<span>// {caption}</span>'
        '<span>'
        f'<a href="../assets/diagrams/{SLUG}-{slug_suffix}.svg" download>&#8595; svg</a>'
        ' &middot; '
        f'<button type="button" id="{btn_id}">&#8595; png</button>'
        '</span></figcaption></figure>'
    )


def loop_figure() -> str:
    return _figure("loop-figure", "loop",
                   "loop 1 · the agent loop · dri-oncall-agent", "loop-png")


def four_figure() -> str:
    return _figure("four-figure", "four-loops",
                   "the four loops in one picture · dri-oncall-agent", "four-png")


def verification_figure() -> str:
    return _figure("verification-figure", "verification",
                   "loop 2 · the verification loop · dri-oncall-agent", "verification-png")


def events_figure() -> str:
    return _figure("events-figure", "events",
                   "loop 3 · the event and routine loop · dri-oncall-agent", "events-png")


def hillclimbing_figure() -> str:
    return _figure("hillclimbing-figure", "hillclimbing",
                   "loop 4 · the hill-climbing loop · dri-oncall-agent", "hillclimbing-png")


def swap_fence_after(body_md: str, heading: str, token: str) -> str:
    """Replace the first fenced ``` block after `heading` with `token`."""
    idx = body_md.find(heading)
    if idx == -1:
        return body_md
    m = re.compile(r"```.*?```", re.S).search(body_md, idx)
    if not m:
        return body_md
    return body_md[: m.start()] + token + body_md[m.end() :]


def insert_token_after_heading(body_md: str, heading: str, token: str) -> str:
    """Insert `token` as its own paragraph on the line right after `heading`."""
    lines = body_md.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == heading:
            lines.insert(i + 1, "")
            lines.insert(i + 2, token)
            lines.insert(i + 3, "")
            return "\n".join(lines)
    return body_md


text = SRC.read_text(encoding="utf-8")
lines = text.splitlines()
title = SLUG
for i, ln in enumerate(lines):
    if ln.startswith("# "):
        title = ln[2:].strip()
        lines = lines[i + 1 :]
        break
body_md = "\n".join(lines).strip()

body_md = re.sub(
    r"\]\(\./([^)]+)\)",
    lambda m: f"](https://github.com/LadyNaggaga/creativetoolbox/tree/main/demos/{SLUG}/{m.group(1)})",
    body_md,
)

body_md = swap_fence_after(body_md, "## Loop 1 — the agent loop", LOOP_TOKEN)
body_md = swap_fence_after(body_md, "## Putting the four loops in one picture", FOUR_TOKEN)
body_md = insert_token_after_heading(body_md, "## Loop 2 — the verification loop", VER_TOKEN)
body_md = insert_token_after_heading(body_md, "## Loop 3 — the event and routine loop", EVT_TOKEN)
body_md = insert_token_after_heading(body_md, "## Loop 4 — the hill-climbing loop", HILL_TOKEN)

body_html = md.convert(body_md)
body_html = body_html.replace(f"<p>{LOOP_TOKEN}</p>", loop_figure())
body_html = body_html.replace(f"<p>{FOUR_TOKEN}</p>", four_figure())
body_html = body_html.replace(f"<p>{VER_TOKEN}</p>",  verification_figure())
body_html = body_html.replace(f"<p>{EVT_TOKEN}</p>",  events_figure())
body_html = body_html.replace(f"<p>{HILL_TOKEN}</p>", hillclimbing_figure())

html = HEAD.format(title=title, slug=SLUG) + body_html + TAIL.format(slug=SLUG)
OUT.write_text(html, encoding="utf-8")
print(f"wrote blog/{SLUG}.html  ({title})")
