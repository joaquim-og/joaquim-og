#!/usr/bin/env python3
"""Builds index.html: a GitHub-like preview of README.md in dark and light themes."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
md = (ROOT / "README.md").read_text()
SNAKE = '<div class="ph">The contribution snake appears here once the profile is published and its daily job has run.</div>'


def body(theme):
    h = re.sub(r'<picture><source[^>]*srcset="https://raw\.githubusercontent[^>]*>.*?</picture>', SNAKE, md, flags=re.S)
    h = re.sub(r'<source media="\(prefers-color-scheme: dark\)" srcset="([^"]+)">\s*<img ([^>]*?)src="([^"]+)"',
               lambda m: f'<img {m.group(2)}src="{m.group(1) if theme == "dark" else m.group(3)}"', h)
    h = re.sub(r"^## (.+)$", r"<h2>\1</h2>", h, flags=re.M)
    h = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", h)
    return re.sub(r"((?:^- .+\n)+)", lambda m: "<ul>" + "".join(f"<li>{l[2:]}</li>" for l in m.group(1).splitlines()) + "</ul>", h, flags=re.M)


CSS = '''body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;line-height:1.5}
.t{padding:32px 0}.dark{background:#0d1117;color:#e6edf3}.light{background:#fff;color:#1f2328}
.md{max-width:846px;margin:0 auto;padding:24px;border:1px solid;border-radius:6px}.dark .md{border-color:#30363d}.light .md{border-color:#d1d9e0}
h2{font-size:1.5em;border-bottom:1px solid;padding-bottom:.3em;margin:24px 0 16px}.dark h2{border-color:#30363d}.light h2{border-color:#d1d9e0}
a{color:#4493f8}.light a{color:#0969da}img{max-width:100%;vertical-align:middle}sub{font-size:12px}
.lbl{max-width:846px;margin:0 auto 8px;font-size:13px;opacity:.6;padding:0 24px}
.ph{border:1px dashed #8b949e;border-radius:10px;padding:28px;text-align:center;font-size:13px;opacity:.7}'''
(ROOT / "index.html").write_text(
    f'<!doctype html><meta charset="utf8"><title>GitHub profile preview</title><style>{CSS}</style>'
    + "".join(f'<div class="t {t}"><div class="lbl">{t.title()} theme</div><div class="md">{body(t)}</div></div>' for t in ("dark", "light")))
print("index.html written")
