# Profile artwork

The README embeds three self-contained SVGs. The original photo remains at
`profile-photo.jpg`; only the derived ASCII portrait appears on the profile.

## Regenerate the portrait and info card

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
```

`prep_photo.py` uses OpenCV GrabCut with foreground seeds matching the supplied
photo, crops to the face and shoulders, and enhances local contrast. For a
different photo, update its outline, foreground seeds, and crop coordinates.
The prepared grayscale image is saved to `data/source-prepped.png`.

Edit `make_info_card.py` to change the bio. Keep the text in the README in sync.
The portrait prints once, row by row; the other cards fade in once. Reduced-motion
preferences disable these effects. Set `STATIC=1` when running a renderer to
emit a still SVG for previews, then regenerate without it before committing.

## Refresh contributions

Python 3.12's standard library is sufficient; no pip packages or personal access
token are needed.

```sh
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
```

The fetcher reads GitHub's public contribution HTML, including tooltip counts,
and validates a complete, contiguous calendar before replacing the saved JSON.
If fetching or parsing fails, the workflow stops and retains the last committed
graph. Dates follow UTC. Streaks are calculated within the displayed calendar;
an unfinished zero-contribution day does not break yesterday's current streak.

`.github/workflows/update-profile-art.yml` refreshes the calendar daily at
06:17 UTC (11:47 IST), on relevant changes pushed to `main`, or when manually run
from the repository's Actions tab. GitHub schedules can be delayed. The workflow
uses the repository's built-in token with `contents: write` to commit only the
calendar JSON and heatmap. No portrait dependencies are installed in CI.

Commit and push the source files and generated SVGs to enable this on GitHub.
The public contribution HTML is an undocumented interface; a markup change may
require updating the parser.
