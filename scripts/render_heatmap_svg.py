"""Render the public calendar as an animated SVG committed to this repo."""

from datetime import date, timedelta
import json
from pathlib import Path
from svg_utils import start, static, text

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main():
    data = json.loads((ROOT / "data/contributions.json").read_text())
    days, stats = data["days"], data["stats"]
    first = date.fromisoformat(days[0]["date"])
    first_sunday = first - timedelta(days=(first.weekday()+1) % 7)
    last = date.fromisoformat(days[-1]["date"])
    weeks = (last - first_sunday).days // 7 + 1
    step = min(14, 748 / weeks)
    svg = start(860, 255, f"GitHub contributions for {data['username']}", "contributions.sh")
    svg.append(text(24, 65, f"{stats['total']:,} contributions", "bright", 16))
    svg.append(text(836, 65, f"{first:%d %b %Y} — {last:%d %b %Y}", "muted", 10, 'text-anchor="end"'))
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        svg.append(text(24, 104+row*14, label, "muted", 9))
    previous_month = None
    for day in days:
        current = date.fromisoformat(day["date"])
        delta = (current-first_sunday).days
        column, row = divmod(delta, 7)
        x, y = 63 + column*step, 95 + row*14
        if current.month != previous_month and (current.day <= 7 or column == 0):
            svg.append(text(round(x, 2), 86, current.strftime("%b"), "muted", 9))
            previous_month = current.month
        effect = '' if static() else f' class="reveal" style="animation-delay:{column*.022+row*.035:.3f}s"'
        svg.append(f'<rect x="{x:.2f}" y="{y}" width="{step-3:.2f}" height="11" rx="2" fill="{PALETTE[day["level"]]}"{effect}><title>{current}: {day["count"]} contributions</title></rect>')
    svg.append(text(63, 212, f"{stats['active_days']} active days  /  {stats['current_streak']} day streak  /  best streak {stats['longest_streak']} days", "muted", 10))
    svg.append(text(63, 237, f"@{data['username']} · refreshed {data['as_of']} UTC", "muted", 9))
    svg.append(text(684, 237, "Less", "muted", 9))
    for i, color in enumerate(PALETTE):
        svg.append(f'<rect x="{714+i*14}" y="228" width="11" height="11" rx="2" fill="{color}"/>')
    svg.append(text(790, 237, "More", "muted", 9))
    svg.append('</svg>')
    (ROOT / "contrib-heatmap.svg").write_text("\n".join(svg) + "\n")
    print("Wrote contrib-heatmap.svg")


if __name__ == "__main__":
    main()
