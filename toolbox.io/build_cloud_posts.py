"""Generate cloud blog HTML pages from each demo's BLOG-CLOUD.md.

Matches the hand-authored look of blog/<slug>.html (commandline.css, same head/style),
so the cloud posts render consistently in the local gallery. No framework, no build step
for the site itself — this just emits static HTML the same way the local posts were authored.
"""
import re
from pathlib import Path

import markdown

from build_shape_art import shape_svg, write_shape_art

ROOT = Path(__file__).resolve().parent            # toolbox.io/
REPO = ROOT.parent                                # creativetoolbox/
DEMOS = REPO / "demos"
OUT = ROOT / "blog"

SLUGS = ["pizza-shop-ops", "mars-greenhouse-ops", "squad-room"]

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — toolbox.io</title>
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="../assets/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="../assets/favicon-180.png">
<link rel="stylesheet" href="../assets/commandline.css">
<style>
 body.cl{{max-width:820px;margin:0 auto;padding:2rem 1.25rem;font-size:15px;}}
 .cl h1{{border-bottom:2px solid var(--cl-line);padding-bottom:.3rem;}}
 .cl pre{{border:1px solid var(--cl-line);padding:12px 14px;overflow:auto;background:#cfcfcd;white-space:pre;}}
 .cl code{{font-family:var(--cl-mono);}}
 .cl ul{{padding-left:1.2rem;}} .cl li{{margin:.2rem 0;}}
 .cl table{{border-collapse:collapse;margin:1rem 0;font-size:.9rem;}}
 .cl th,.cl td{{border:1px solid var(--cl-line);padding:.35rem .6rem;text-align:left;}}
 .cl th{{background:#cfcfcd;}}
 .nav{{margin-bottom:1rem;}} .nav a{{color:var(--cl-ink);text-decoration:underline;}}
 .badge{{display:inline-block;font-size:.72em;letter-spacing:.04em;border:1px solid var(--cl-line);padding:0 .4ch;text-transform:uppercase;margin-bottom:.6rem;}}
 .figure{{border:1px solid var(--cl-line);margin:1rem 0;background:var(--cl-bg);}}
 .figure .slot,.figure svg{{display:block;width:100%;height:auto;min-height:120px;}}
 .figure figcaption{{display:flex;justify-content:space-between;gap:1rem;padding:.4rem .7rem;border-top:1px solid var(--cl-line);font-family:var(--cl-mono);font-size:.78rem;color:var(--cl-faint);}}
 .figure figcaption a,.figure figcaption button{{font:inherit;color:var(--cl-ink);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline;}}
</style></head><body class="cl">
<p class="nav"><a href="../index.html">&larr; back to gallery</a></p>
<span class="badge">cloud</span>
<h1><a href="https://github.com/LadyNaggaga/creativetoolbox/tree/main/demos/{slug}" style="color:inherit;text-decoration:none">{title}</a></h1>
<p class="nav"><a href="https://github.com/LadyNaggaga/creativetoolbox/tree/main/demos/{slug}/cloud">view the cloud demo code on GitHub &rarr;</a></p>
<figure class="figure" id="art-figure">
  <div class="slot" aria-label="loading cloud art"></div>
  <figcaption>
    <span>// cloud art for {slug} · monochrome · CC0</span>
    <span>
      <a href="../assets/art/{slug}-cloud.svg" download>&#8595; svg</a>
      &#183;
      <button type="button" id="art-png">&#8595; png</button>
    </span>
  </figcaption>
</figure>
"""

FIG_STYLE = ""

TAIL = """
<script src="../assets/svg-figure.js"></script>
<script>
(async function () {{
  const f = window.toolboxFigure;
  const artSvg = await f.inlineSVG('../assets/art/{slug}-cloud.svg',
                                   document.querySelector('#art-figure .slot'));
  document.getElementById('art-png').addEventListener('click', () => {{
    f.downloadPNG(artSvg, '{slug}-cloud--art.png', 2);
  }});
}})();
</script>
</body></html>
"""

md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])

SHAPE_TOKEN = "SHAPEDIAGRAMPLACEHOLDER"


def shape_figure(slug: str) -> str:
    """Inline the 'shape of it' SVG in a site figure (CSS scales .figure svg to 100%)."""
    svg = shape_svg(slug)
    svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)  # drop prolog for inline embedding
    return (
        '<figure class="figure">'
        f"{svg}"
        '<figcaption>'
        f'<span>// the shape of it — {slug} · monochrome · CC0</span>'
        f'<span><a href="../assets/art/{slug}-shape.svg" download>&#8595; svg</a></span>'
        '</figcaption></figure>'
    )


def swap_shape_block(body_md: str) -> str:
    """Replace the fenced ASCII block right after '## The shape of it' with a token."""
    idx = body_md.find("## The shape of it")
    if idx == -1:
        return body_md
    m = re.compile(r"```.*?```", re.S).search(body_md, idx)
    if not m:
        return body_md
    return body_md[: m.start()] + SHAPE_TOKEN + body_md[m.end() :]


write_shape_art()  # (re)write assets/art/<slug>-shape.svg for download parity

for slug in SLUGS:
    src = DEMOS / slug / "BLOG-CLOUD.md"
    text = src.read_text(encoding="utf-8")

    # Pull the leading "# Title" out to use as the page H1, drop it from the body.
    lines = text.splitlines()
    title = slug
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            title = ln[2:].strip()
            lines = lines[i + 1 :]
            break
    body_md = "\n".join(lines).strip()

    # Rewrite sibling-markdown links (../pizza-shop-ops/BLOG-CLOUD.md, BLOG.md) to site pages.
    body_md = re.sub(r"\.\./([a-z-]+)/BLOG-CLOUD\.md", r"\1-cloud.html", body_md)
    body_md = re.sub(r"\(BLOG\.md\)", lambda m: f"({slug}.html)", body_md)

    # Swap the "shape of it" ASCII block for the inline SVG diagram (via a token
    # that survives markdown conversion, then restored as raw HTML below).
    body_md = swap_shape_block(body_md)

    md.reset()
    body_html = md.convert(body_md)
    body_html = body_html.replace(f"<p>{SHAPE_TOKEN}</p>", shape_figure(slug))

    html = HEAD.format(title=title, slug=slug) + body_html + TAIL.format(slug=slug)
    (OUT / f"{slug}-cloud.html").write_text(html, encoding="utf-8")
    print(f"wrote blog/{slug}-cloud.html  ({title})")
