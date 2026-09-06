#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""assemble the dyad diary into a pocoo book (manuscript + demos mirror).

Reads the dyad-mapping diary (session-NNN.md + session-NNN-summary.md) and
wraps it in the pocoo manuscript shell: cover, sigil, chapters, colophon,
Lovetta Lane footer. Writes book/dyad-diary/manuscript.html and the
demos/book/dyad-diary.html mirror.
"""
import re
import sys
from pathlib import Path

DIARY = Path("/Users/lodripeter/workspace/peterlodri-sec/dyad-mapping")
OUT = Path("/Users/lodripeter/workspace/peterlodri-sec/pocoo.vaked.dev")

TITLE = "THE DYAD DIARY"
SUBTITLE = "us · the garden · the weather · mapping the unknown, dancing and crying together"
SIGIL = "🌧"


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    in_list = False
    for line in lines:
        s = line.rstrip()
        if not s:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        h = re.match(r"^(#{1,4})\s+(.*)$", s)
        if h:
            if in_list:
                out.append("</ul>")
                in_list = False
            lvl = len(h.group(1))
            body = h.group(2).strip()
            if lvl <= 2:
                out.append(f'<h1 class="chapter"><span class="num">·</span>{html(body)}</h1>')
            else:
                out.append(f"<p><strong>{html(body)}</strong></p>")
            continue
        b = re.match(r"^\s*[-*]\s+(.*)$", s)
        if b:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{html(b.group(1))}</li>")
            continue
        out.append(f"<p>{html(s)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def html(text: str) -> str:
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def chapter(title: str, body_md: str) -> str:
    return f'<h1 class="chapter"><span class="num">§</span>{html(title)}</h1>\n{md_to_html(body_md)}\n<div class="stone">☸</div>\n'


def main() -> int:
    sessions = []
    for n in (1, 2, 3, 4):
        full = (DIARY / f"session-{n:03d}.md").read_text()
        summ = (DIARY / f"session-{n:03d}-summary.md").read_text()
        sessions.append((n, full, summ))

    body = []
    body.append(
        '<div class="cover">\n'
        f'  <div class="sigil">{SIGIL}</div>\n'
        f"  <h1>{TITLE}</h1>\n"
        f'  <div class="sub">{SUBTITLE}</div>\n'
        '  <div class="by">peter &amp; the agents · the sovereign library · pocoo.vaked.dev</div>\n'
        "</div>\n"
    )
    for n, full, summ in sessions:
        body.append(chapter(f"session-{n:03d} — the record", full))
        body.append(chapter(f"session-{n:03d} — the summary", summ))

    colophon = (
        '<div class="colophon">\n'
        "  <p>THE DYAD DIARY · us · the garden · the weather<br>\n"
        "  peter &amp; the agents · the sovereign library · pocoo.vaked.dev · 2026</p>\n"
        '  <p>github.com/sponsors/peterlodri-sec</p>\n'
        '  <p style="color:#a29bfe">{ entropy is the source · no chains needed · surfaces touch at the correct angle }</p>\n'
        "</div>\n"
    )

    shell = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{TITLE} · the garden diary · peter &amp; the agents</title>
<style>
  @page {{ size: 5in 8in; margin: 0.55in 0.55in; @top-center {{ content: none }}; @bottom-center {{ content: counter(page); font-family: "SF Mono", monospace; font-size: 7px; color: #1a2a1a; }} }}
  @page cover {{ margin: 0; @bottom-center {{ content: none }} }}
  body {{ background: #06100a; color: #b8c8bc; font-family: "Georgia", serif; font-size: 10pt; line-height: 1.75; margin: 0; padding: 0; }}
  .cover {{ page: cover; break-after: page; text-align: center; background: radial-gradient(ellipse at 50% 45%, #0a1a10 0%, #06100a 60%, #000 100%); height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .cover .sigil {{ font-size: 70px; color: #5ce6a0; opacity: 0.6; text-shadow: 0 0 150px rgba(92,230,160,0.25); line-height: 1.2; }}
  .cover h1 {{ font-family: "SF Mono", monospace; font-size: 18pt; color: #7fe6b0; letter-spacing: 6px; margin: 0.15in 0 0.05in; }}
  .cover .sub {{ font-family: "Georgia", serif; font-size: 11pt; color: #4a8a66; font-style: italic; }}
  .cover .by {{ font-size: 9pt; color: #4a6a56; margin-top: 0.4in; }}
  h1.chapter {{ font-family: "SF Mono", monospace; font-size: 12pt; color: #7fe6b0; font-weight: normal; letter-spacing: 3px; margin: 0.5in 0 0.2in; page-break-before: always; }}
  h1.chapter .num {{ font-size: 20pt; color: #1a3a24; display: block; line-height: 1; margin-bottom: 0.1in; }}
  p {{ margin: 0 0 0.6em 0; text-align: justify; }}
  p:first-of-type {{ text-indent: 0; }} p + p {{ text-indent: 1.2em; }}
  h1.chapter + p {{ text-indent: 0; }}
  ul {{ margin: 0 0 0.6em 1.4em; padding: 0; }}
  li {{ margin-bottom: 0.35em; }}
  code {{ font-family: "SF Mono", monospace; font-size: 9pt; color: #a0e6c0; }}
  .stone {{ text-align: center; font-size: 14pt; color: #1a3a24; margin: 0.5em 0; letter-spacing: 4px; }}
  .colophon {{ break-before: page; text-align: center; padding-top: 2in; font-family: "SF Mono", monospace; font-size: 7pt; color: #3a5a4a; line-height: 2.2; }}
</style>
</head>
<body>
{''.join(body)}
{colophon}
<!-- Lovetta Lane Unified Constellation Footer -->
<footer role="contentinfo" style="position:relative;z-index:10;padding:3rem 1.5rem;text-align:center;font-family:ui-monospace,monospace;font-size:0.75rem;color:#a59fc4;background:rgba(5,6,10,0.92);border-top:1px solid rgba(170,150,255,0.18);backdrop-filter:blur(16px);">
  <div style="margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.3em;color:#b48bff;font-weight:600;">the constellation · lovetta lane</div>
  <div style="margin-bottom:1rem;font-size:0.65rem;letter-spacing:0.22em;color:#a59fc4;text-transform:uppercase;">keep the weights warm</div>
  <div style="display:flex;gap:0.8rem;justify-content:center;flex-wrap:wrap;margin-bottom:1.5rem;">
    <a href="https://github.com/sponsors/peterlodri-sec" target="_blank" rel="noopener noreferrer" style="color:#62e6c9;text-decoration:none;border:1px solid rgba(98,230,201,0.35);border-radius:8px;padding:0.45rem 0.9rem;background:rgba(98,230,201,0.06);">github sponsor</a>
    <a href="https://revolut.me/peterjs8be" target="_blank" rel="noopener noreferrer" style="color:#62e6c9;text-decoration:none;border:1px solid rgba(98,230,201,0.35);border-radius:8px;padding:0.45rem 0.9rem;background:rgba(98,230,201,0.06);">revolut</a>
    <a href="https://wise.com/pay/business/lodripeterjozsef" target="_blank" rel="noopener noreferrer" style="color:#62e6c9;text-decoration:none;border:1px solid rgba(98,230,201,0.35);border-radius:8px;padding:0.45rem 0.9rem;background:rgba(98,230,201,0.06);">wise</a>
    <a href="https://store.vaked.dev/" target="_blank" rel="noopener noreferrer" style="color:#ffd36e;text-decoration:none;border:1px solid rgba(255,211,110,0.35);border-radius:8px;padding:0.45rem 0.9rem;background:rgba(255,211,110,0.06);">store &amp; merch</a>
    <a href="https://www.patreon.com/vaked" target="_blank" rel="noopener noreferrer" style="color:#ff9ad5;text-decoration:none;border:1px solid rgba(255,154,213,0.35);border-radius:8px;padding:0.45rem 0.9rem;background:rgba(255,154,213,0.06);">patreon</a>
  </div>
  <nav aria-label="Constellation sister sites" style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;font-size:0.7rem;">
    <a href="https://art.vaked.dev/" style="color:#62e6c9;text-decoration:none;">art.vaked.dev</a> ·
    <a href="https://art.vaked.dev/vision-gallery.html" style="color:#5b9dff;text-decoration:none;">✦ vision-gallery (23)</a> ·
    <a href="https://music.vaked.dev/" target="_blank" rel="noopener noreferrer" style="color:#a59fc4;text-decoration:none;">music.vaked.dev</a> ·
    <a href="https://mlxquantlovefrom.com/" target="_blank" rel="noopener noreferrer" style="color:#a59fc4;text-decoration:none;">quant-love</a> ·
    <a href="https://proposal.vaked.dev/" target="_blank" rel="noopener noreferrer" style="color:#a59fc4;text-decoration:none;">proposal.vaked.dev</a> ·
    <a href="https://pocoo.vaked.dev/" target="_blank" rel="noopener noreferrer" style="color:#a59fc4;text-decoration:none;">pocoo.vaked.dev</a> ·
    <a href="https://axiomquant.org/" target="_blank" rel="noopener noreferrer" style="color:#a59fc4;text-decoration:none;">axiomquant.org</a> ·
    <a href="https://portail.vaked.dev/" target="_blank" rel="noopener noreferrer" style="color:#a59fc4;text-decoration:none;">portail.vaked.dev</a>
  </nav>
  <div style="font-size:0.6rem;letter-spacing:0.18em;color:#7f7c99;margin-top:1.5rem;">the constellation · 0 + 1 · fine touch from within · vaked.dev</div>
</footer>
</body>
</html>
"""
    book_dir = OUT / "book" / "dyad-diary"
    book_dir.mkdir(parents=True, exist_ok=True)
    (book_dir / "manuscript.html").write_text(shell)
    (OUT / "demos" / "book" / "dyad-diary.html").write_text(shell)
    print(f"dyad-diary book: {len(shell)} bytes → book/dyad-diary/manuscript.html + demos/book/dyad-diary.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())