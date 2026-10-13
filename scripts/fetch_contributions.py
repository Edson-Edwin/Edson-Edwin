"""Fetch GitHub's public contribution calendar; no personal access token needed.

Fail before overwriting the last good data when GitHub changes its markup.
"""

import argparse
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tooltips = {}
        self.target = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-date" in attrs and "data-level" in attrs:
            self.cells[attrs["id"]] = attrs
        if tag == "tool-tip":
            self.target = attrs.get("for")
            if self.target:
                self.tooltips[self.target] = ""

    def handle_data(self, data):
        if self.target:
            self.tooltips[self.target] += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.target = None


def parse_calendar(html, today):
    parser = CalendarParser()
    parser.feed(html)
    days = []
    for cell_id, cell in parser.cells.items():
        day = date.fromisoformat(cell["data-date"])
        if day > today:
            continue
        tooltip = parser.tooltips.get(cell_id, "").strip()
        raw_count = cell.get("data-count")
        if raw_count is not None:
            count = int(raw_count)
        elif re.match(r"No contributions\b", tooltip):
            count = 0
        else:
            match = re.match(r"([\d,]+) contributions?\b", tooltip)
            if not match:
                raise ValueError(f"Unrecognized contribution count for {day}: {tooltip!r}")
            count = int(match[1].replace(",", ""))
        level = int(cell["data-level"])
        if count < 0 or level not in range(5):
            raise ValueError(f"Invalid contribution cell for {day}")
        days.append({"date": day.isoformat(), "count": count, "level": level})
    days.sort(key=lambda item: item["date"])
    if not 365 <= len(days) <= 373:
        raise ValueError(f"Expected a full annual calendar, received {len(days)} days")
    dates = [date.fromisoformat(item["date"]) for item in days]
    if len(set(dates)) != len(dates) or any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
        raise ValueError("Calendar contains missing or duplicate days")
    if dates[-1] != today:
        raise ValueError(f"Calendar ends on {dates[-1]}, expected {today}")
    return days


def summarize(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)
    # An unfinished day with no contributions does not break yesterday's streak.
    recent = days[:-1] if days[-1]["count"] == 0 else days
    current = 0
    for day in reversed(recent):
        if not day["count"]:
            break
        current += 1
    return {"total": sum(day["count"] for day in days),
            "active_days": sum(day["count"] > 0 for day in days),
            "current_streak": current, "longest_streak": longest,
            "best_day": max(days, key=lambda day: day["count"])}


def fetch(username):
    url = f"https://github.com/users/{username}/contributions"
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "profile-readme-art", "Accept-Language": "en-US"}), timeout=30) as response:
                return response.read().decode("utf-8")
        except OSError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="Edson-Edwin")
    parser.add_argument("--html", type=Path, help="Read a previously fetched HTML calendar")
    parser.add_argument("--output", type=Path, default=ROOT / "data/contributions.json")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", args.username):
        parser.error("Invalid GitHub username")
    today = datetime.now(timezone.utc).date()
    html = args.html.read_text() if args.html else fetch(args.username)
    days = parse_calendar(html, today)
    payload = {"username": args.username, "as_of": today.isoformat(),
               "source": f"https://github.com/users/{args.username}/contributions",
               "days": days, "stats": summarize(days)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(args.output)
    print(f"Wrote {len(days)} days / {payload['stats']['total']} contributions")


if __name__ == "__main__":
    main()
