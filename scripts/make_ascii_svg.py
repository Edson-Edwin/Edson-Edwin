"""Convert the prepared portrait into a monochrome, self-typing SVG."""

from html import escape
from pathlib import Path

from PIL import Image
from svg_utils import start, static, text

ROOT = Path(__file__).resolve().parents[1]
RAMP = " .`:-=+*cs#%@"


def main():
    columns, rows = 90, 49
    image = Image.open(ROOT / "data/source-prepped.png").convert("L")
    image = image.resize((columns, rows), Image.Resampling.LANCZOS)
    lines = ["".join(RAMP[round((255 - image.getpixel((x, y))) / 255 * (len(RAMP) - 1))]
                     for x in range(columns)) for y in range(rows)]
    svg = start(370, 420, "ASCII portrait of Edson Edwin Ninan", "portrait.txt")
    svg.append(text(18, 62, "$ cat portrait.txt", "accent", 11))
    svg.append('<style>@media (prefers-reduced-motion: reduce) { .portrait-row { clip-path: none; } .cursor { display: none; } }</style>')
    for i, line in enumerate(lines):
        y = 81 + i * 6.35
        begin = i * .055 + .2
        if not static():
            # Base width stays full so SVG viewers without animation still show the portrait.
            svg.append(
                f'<defs><clipPath id="row-{i}"><rect x="18" y="{y-6}" width="334" height="7">'
                f'<set attributeName="width" to="0" begin="0s" end="{begin:.3f}s"/>'
                f'<animate attributeName="width" values="0;334" dur=".14s" begin="{begin:.3f}s" fill="freeze"/>'
                '</rect></clipPath></defs>'
            )
        clip = '' if static() else f' clip-path="url(#row-{i})"'
        svg.append(f'<text x="18" y="{y:.2f}" class="portrait-row" fill="#c9d1d9" font-family="monospace" font-size="6.18" xml:space="preserve" textLength="334" lengthAdjust="spacingAndGlyphs"{clip}>{escape(line)}</text>')
    svg.append(text(18, 403, "EDSON / BACKEND & CLOUD", "muted", 9))
    svg.append('</svg>')
    (ROOT / "edson-ascii.svg").write_text("\n".join(svg) + "\n")
    print("Wrote edson-ascii.svg")


if __name__ == "__main__":
    main()
