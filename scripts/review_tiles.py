"""Summarize daily colour variety and render the exact tiles separately."""

import argparse
from collections import Counter
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def review(directory):
    directory = Path(directory)
    data = json.loads((directory / "mosaic.json").read_text())
    side = data["tile_width"]
    tile_pixels = side * (180 // side)
    sheet = Image.new("RGB", (1060, 1230), "#F1F0EC")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=16)
    draw.text((20, 14), f'{data["palette"]["id"]} - individual {side}x{side} days', fill="#171717", font=font)
    rows = []
    for day in range(1, 26):
        tr, tc = divmod(day - 1, 5)
        cells = [row[tc*side:(tc+1)*side] for row in data["cells"][tr*side:(tr+1)*side]]
        counts = Counter(c for row in cells for c in row)
        # Exclude one/two-cell edge accidents from the stronger variety measure.
        substantial = sum(n >= 3 for n in counts.values())
        dominant = max(counts.values())
        rows.append(dict(day=day, distinct_colours=len(counts), colours_with_at_least_3_cells=substantial,
                         dominant_colour_cells=dominant, dominant_colour_fraction=round(dominant/(side*side), 4),
                         counts=dict(sorted(counts.items()))))
        x, y = 20 + tc*208, 50 + tr*234
        draw.text((x, y), f'Day {day:02d}', fill="#171717", font=font)
        with Image.open(directory / "tiles" / f"day-{day:02d}.png") as tile:
            sheet.paste(tile.resize((tile_pixels, tile_pixels), Image.Resampling.NEAREST), (x, y+24))
        draw.text((x, y+209), f'{len(counts)} colours · {substantial} substantial', fill="#444444", font=ImageFont.load_default(size=12))
    report = dict(
        note=f"Colour variety is a screening metric, not proof of recognisability. Substantial means at least 3 of {side*side} cells; this absolute threshold is not resolution-normalized.",
        min_distinct_colours=min(r["distinct_colours"] for r in rows),
        min_substantial_colours=min(r["colours_with_at_least_3_cells"] for r in rows),
        max_dominant_fraction=max(r["dominant_colour_fraction"] for r in rows),
        days_with_fewer_than_4_substantial_colours=[r["day"] for r in rows if r["colours_with_at_least_3_cells"] < 4],
        days=rows,
    )
    (directory / "tile-review.json").write_text(json.dumps(report, indent=2) + "\n")
    sheet.save(directory / "daily-preview.png")
    print(directory, json.dumps({k: v for k, v in report.items() if k not in ("days", "note")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+")
    for directory in parser.parse_args().directories:
        review(directory)
