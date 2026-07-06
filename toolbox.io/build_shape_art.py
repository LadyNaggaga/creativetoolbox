"""Generate the 'shape of it' architecture diagrams for the cloud blog posts.

One monochrome, light-paper SVG per demo, matching the site palette
(--cl-bg #D6D6D4, ink #1A1A1A, faint #6B6B68, mono labels). The four stages are
identical across demos (inputs -> hosted agent -> Toolbox + Tool Search -> MCP
server); only the input roles and the in-the-box tool families differ.

Imported by build_cloud_posts.py (shape_svg / write_shape_art) and runnable
standalone to (re)write assets/art/<slug>-shape.svg.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "assets" / "art"

BG = "#D6D6D4"
BOX = "#cfcfcd"
INK = "#1A1A1A"
FAINT = "#6B6B68"
SANS = "Inter, system-ui, -apple-system, sans-serif"
MONO = "ui-monospace, 'JetBrains Mono', Menlo, monospace"

# Per-demo content. inputs = the roles feeding the one agent; chips = hero-tool
# families that live in the box; toolbox = the toolbox resource name.
SHAPES = {
    "pizza-shop-ops": {
        "inputs": ["crew"],
        "toolbox": "pizza-shop-ops",
        "chips": ["oven", "orders", "inventory", "kb", "delivery"],
    },
    "mars-greenhouse-ops": {
        "inputs": ["crew"],
        "toolbox": "mars-greenhouse-ops",
        "chips": ["sensors", "irrigation", "power", "guides", "crew"],
    },
    "squad-room": {
        "inputs": ["lead", "researcher", "builder"],
        "toolbox": "squad-room",
        "chips": ["repo", "ci", "issues", "releases", "design", "kb"],
    },
}


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _stage(x, y, w, h, title, sub):
    """A stage box with a bold sans title and a mono subtitle."""
    cx = x + w / 2
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
        f'fill="{BOX}" stroke="{INK}" stroke-width="2"/>',
        f'<text x="{cx:.0f}" y="{y + h/2 - 4:.0f}" text-anchor="middle" '
        f'font-family="{SANS}" font-weight="700" font-size="19" fill="{INK}">{_esc(title)}</text>',
    ]
    if sub:
        out.append(
            f'<text x="{cx:.0f}" y="{y + h/2 + 22:.0f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="13" fill="{FAINT}">{_esc(sub)}</text>'
        )
    return "\n".join(out)


def _arrow(x1, y1, x2, y2, label="", label_y=None, dashed=False):
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    out = [
        f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
        f'stroke="{INK}" stroke-width="2" marker-end="url(#arrow)"{dash}/>'
    ]
    if label:
        mx = (x1 + x2) / 2
        ly = label_y if label_y is not None else y1 - 10
        out.append(
            f'<text x="{mx:.0f}" y="{ly:.0f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="13" fill="{INK}">{_esc(label)}</text>'
        )
    return "\n".join(out)


def shape_svg(slug: str) -> str:
    cfg = SHAPES[slug]
    W, H = 1320, 400
    cy = 160  # vertical center of the main row
    # main-row boxes
    ax, aw = 330, 250   # hosted agent
    tx, tw = 680, 300   # toolbox
    mx, mw = 1070, 220  # mcp server
    bh = 120
    by = cy - bh / 2
    lbl_y = by - 12     # connector labels sit above the boxes

    p = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="{MONO}">',
        f'<title>{_esc(slug)} — the shape of it</title>',
        f'<desc>One endpoint, tiny context: inputs to a hosted Foundry agent, to a '
        f'Toolbox with Tool Search, to an MCP server on Azure Container Apps. CC0.</desc>',
        '<defs>',
        f'  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>',
        '</defs>',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>',
        f'<text x="30" y="40" font-size="15" fill="{FAINT}">// the shape of it — big box, tiny context</text>',
    ]

    # inputs (left) -> agent
    inputs = cfg["inputs"]
    ix, iw = 40, 170
    if len(inputs) == 1:
        p.append(_stage(ix, cy - 40, iw, 80, inputs[0], ""))
        p.append(_arrow(ix + iw, cy, ax, cy, "asks", label_y=lbl_y))
    else:
        n = len(inputs)
        ih, gap = 52, 14
        total = n * ih + (n - 1) * gap
        top = cy - total / 2
        for i, role in enumerate(inputs):
            ry = top + i * (ih + gap)
            rcy = ry + ih / 2
            p.append(
                f'<rect x="{ix}" y="{ry:.0f}" width="{iw}" height="{ih}" rx="4" '
                f'fill="{BOX}" stroke="{INK}" stroke-width="2"/>'
            )
            p.append(
                f'<text x="{ix + iw/2:.0f}" y="{rcy + 5:.0f}" text-anchor="middle" '
                f'font-family="{SANS}" font-weight="700" font-size="17" fill="{INK}">{_esc(role)}</text>'
            )
            p.append(_arrow(ix + iw, rcy, ax, cy))
        p.append(
            f'<text x="{(ix + iw + ax)/2:.0f}" y="{cy - total/2 - 8:.0f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="13" fill="{INK}">the same one box</text>'
        )

    # main row
    p.append(_stage(ax, by, aw, bh, "hosted agent", "Foundry · gpt-4o"))
    p.append(_stage(tx, by, tw, bh, "Toolbox + Tool Search", "Foundry · toolbox_search_preview"))
    p.append(_stage(mx, by, mw, bh, "MCP server", "Azure Container Apps"))

    p.append(_arrow(ax + aw, cy, tx, cy, "tool_search", label_y=lbl_y))
    p.append(_arrow(tx + tw, cy, mx, cy, "call_tool", label_y=lbl_y))

    # return path (dashed): mcp -> agent, tool result flows back
    ry = by + bh + 46
    p.append(f'<line x1="{mx + mw/2:.0f}" y1="{by + bh:.0f}" x2="{mx + mw/2:.0f}" y2="{ry:.0f}" '
             f'stroke="{FAINT}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    p.append(f'<line x1="{mx + mw/2:.0f}" y1="{ry:.0f}" x2="{ax + aw/2:.0f}" y2="{ry:.0f}" '
             f'stroke="{FAINT}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    p.append(f'<line x1="{ax + aw/2:.0f}" y1="{ry:.0f}" x2="{ax + aw/2:.0f}" y2="{by + bh:.0f}" '
             f'stroke="{FAINT}" stroke-width="1.6" stroke-dasharray="6 5" marker-end="url(#arrow)"/>')
    p.append(f'<text x="{(mx + mw/2 + ax + aw/2)/2:.0f}" y="{ry - 8:.0f}" text-anchor="middle" '
             f'font-family="{MONO}" font-size="13" fill="{FAINT}">tool result flows back — model never sees the full list</text>')

    # in-the-box chips strip
    chips = cfg["chips"]
    strip_y = 320
    p.append(f'<text x="30" y="{strip_y + 5:.0f}" font-family="{MONO}" font-size="14" '
             f'font-weight="700" fill="{INK}">in the box:</text>')
    cx = 168
    for chip in chips:
        cw = 26 + len(chip) * 10
        p.append(f'<rect x="{cx}" y="{strip_y - 18:.0f}" width="{cw}" height="30" rx="15" '
                 f'fill="none" stroke="{INK}" stroke-width="1.6"/>')
        p.append(f'<text x="{cx + cw/2:.0f}" y="{strip_y + 3:.0f}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="14" fill="{INK}">{_esc(chip)}</text>')
        cx += cw + 14
    p.append(f'<text x="{cx + 6}" y="{strip_y + 3:.0f}" font-family="{MONO}" font-size="15" '
             f'fill="{FAINT}">…</text>')
    p.append(f'<text x="30" y="{H - 16}" font-family="{MONO}" font-size="14" fill="{FAINT}">'
             f'many tools in the box · exactly 2 (tool_search + call_tool) in the model\u2019s context</text>')

    p.append('</svg>')
    return "\n".join(p)


def write_shape_art():
    ART.mkdir(parents=True, exist_ok=True)
    for slug in SHAPES:
        (ART / f"{slug}-shape.svg").write_text(shape_svg(slug), encoding="utf-8")
        print(f"wrote assets/art/{slug}-shape.svg")


if __name__ == "__main__":
    write_shape_art()
