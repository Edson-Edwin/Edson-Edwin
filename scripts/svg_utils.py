"""Shared terminal styling for the generated profile SVGs."""

from html import escape
import os

ROOT_STYLE = '''
text { font-family: "DejaVu Sans Mono", Consolas, monospace; }
.muted { fill: #8b949e; }
.bright { fill: #e6edf3; }
.accent { fill: #7ee787; }
@keyframes appear { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
.reveal { animation: appear .35s both; }
@media (prefers-reduced-motion: reduce) { .reveal { animation: none; } }
'''


def static():
    return os.environ.get("STATIC") == "1"


def start(width, height, title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>',
        f'<style>{ROOT_STYLE}</style>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="#0d1117" stroke="#30363d"/>',
        f'<path d="M1 39H{width-1}" stroke="#30363d"/>',
        '<circle cx="19" cy="20" r="4" fill="#ff5f57"/><circle cx="34" cy="20" r="4" fill="#febc2e"/><circle cx="49" cy="20" r="4" fill="#28c840"/>',
        f'<text x="{width-18}" y="24" text-anchor="end" class="muted" font-size="10">{escape(subtitle)}</text>',
    ]


def text(x, y, value, cls="bright", size=12, extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" xml:space="preserve" {extra}>{escape(str(value))}</text>'
