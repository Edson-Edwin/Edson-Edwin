"""Regression checks for the public HTML parser and streak calculations."""

from datetime import date, timedelta
import unittest

from fetch_contributions import parse_calendar, summarize


class CalendarTests(unittest.TestCase):
    today = date(2026, 10, 13)

    def calendar(self):
        cells = []
        for i in range(367):
            day = self.today - timedelta(days=366-i)
            tooltip = "1,234 contributions" if i == 366 else "No contributions"
            level = 4 if i == 366 else 0
            cells.append(f'<td id="day-{i}" data-date="{day}" data-level="{level}"></td>'
                         f'<tool-tip for="day-{i}">{tooltip} on a date.</tool-tip>')
        return "".join(cells)

    def test_tooltip_counts_and_chronological_order(self):
        days = parse_calendar(self.calendar(), self.today)
        self.assertEqual(days[-1]["count"], 1234)
        self.assertEqual(days[0]["count"], 0)
        self.assertEqual(summarize(days)["total"], 1234)

    def test_unknown_tooltip_fails_instead_of_creating_zero_counts(self):
        with self.assertRaisesRegex(ValueError, "Unrecognized contribution count"):
            parse_calendar(self.calendar().replace("1,234 contributions", "Activity unavailable"), self.today)

    def test_missing_duplicate_and_stale_days_are_rejected(self):
        cases = [
            self.calendar().replace('data-date="2025-10-12"', 'data-date="2025-10-13"'),
            self.calendar().replace('data-date="2025-10-12"', 'data-date="2025-10-11"'),
        ]
        for html in cases:
            with self.subTest(html=html[:80]), self.assertRaises(ValueError):
                parse_calendar(html, self.today)
        with self.assertRaisesRegex(ValueError, "Calendar ends"):
            parse_calendar(self.calendar(), self.today + timedelta(days=1))

    def test_future_cells_are_ignored(self):
        future = '<td id="future" data-date="2026-10-14" data-level="0"></td>'
        self.assertEqual(len(parse_calendar(self.calendar()+future, self.today)), 367)

    def test_current_streak_allows_an_unfinished_today(self):
        for counts, current, longest in [([2, 1, 0], 2, 2), ([2, 0, 1], 1, 1), ([0, 0, 0], 0, 0)]:
            days = [{"date": str(i), "count": count} for i, count in enumerate(counts)]
            with self.subTest(counts=counts):
                stats = summarize(days)
                self.assertEqual(stats["current_streak"], current)
                self.assertEqual(stats["longest_streak"], longest)


if __name__ == "__main__":
    unittest.main()
