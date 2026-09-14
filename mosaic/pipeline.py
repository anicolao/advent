import base64
import csv
import hashlib
import html
import io
import json
import platform
import re
import shutil
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import PIL
from PIL import Image, ImageCms, ImageOps

def geometry(subdivision=1):
    require(type(subdivision) is int and subdivision in (1, 3), "Subdivision must be 1 or 3")
    return dict(width=45*subdivision, height=45*subdivision, tile_width=9*subdivision,
                tile_height=9*subdivision, tile_columns=5, tile_rows=5)


def preview_size(width):
    side = width * (20 if width == 45 else 8)
    return (side, side)

RESAMPLING = {"BOX": Image.Resampling.BOX, "NEAREST": Image.Resampling.NEAREST}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n")


def load_palette(path):
    data = read_json(path)
    require(data.get("colour_space") == "sRGB", "Palette colour_space must be sRGB")
    colours = list(data["colours"])
    if "additional_mosaic_colour" in data:
        colours.insert(0, data["additional_mosaic_colour"])
    require(len(colours) == 13, "Palette must contain exactly 12 colours plus white")
    entries = []
    for c in colours:
        require(isinstance(c.get("id"), str) and bool(c["id"]), "Invalid colour ID")
        require(isinstance(c.get("hex"), str) and re.fullmatch(r"#[0-9a-fA-F]{6}", c["hex"]), "Invalid RGB hex value")
        rgb = [int(c["hex"][i:i+2], 16) for i in (1, 3, 5)]
        require("rgb" not in c or c["rgb"] == rgb, "Palette hex and RGB disagree")
        entries.append(dict(id=c["id"], name=c.get("name", c["id"]), hex=c["hex"].upper(), rgb=rgb))
    require(len({c["id"] for c in entries}) == 13, "Duplicate colour IDs")
    require(len({c["hex"] for c in entries}) == 13, "Duplicate RGB colours")
    require(sum(c["hex"] == "#FFFFFF" for c in entries) == 1, "Palette must include pure white")
    return dict(schema_version=1, id=data.get("id", Path(path).stem), colour_space="sRGB", colours=entries)


def normalize(path, centre_crop=False, minimum_size=45):
    with Image.open(path) as original:
        require(getattr(original, "n_frames", 1) == 1, "Multi-frame images are unsupported")
        img = ImageOps.exif_transpose(original)
        profile = img.info.get("icc_profile")
        alpha = img.convert("RGBA").getchannel("A")
        if profile:
            try:
                colour = img if img.mode in ("RGB", "CMYK", "LAB", "L") else img.convert("RGB")
                rgb = ImageCms.profileToProfile(colour, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                                               ImageCms.createProfile("sRGB"), outputMode="RGB")
            except (ValueError, OSError, ImageCms.PyCMSError) as exc:
                raise ValueError("Unsupported ICC conversion; provide an sRGB image") from exc
            management = "Embedded ICC converted to sRGB"
        else:
            require(img.mode in ("1", "L", "LA", "P", "RGB", "RGBA"),
                    "Unsupported untagged colour mode; provide an sRGB image")
            rgb = img.convert("RGB")
            management = "Untagged image assumed sRGB"
        rgb = Image.composite(rgb, Image.new("RGB", rgb.size, "white"), alpha)
    w, h = rgb.size
    require(min(w, h) >= minimum_size, f"Source must be at least {minimum_size}×{minimum_size} pixels")
    box = [0, 0, w, h]
    if w != h:
        require(centre_crop, "Source is not square; regenerate or use --centre-crop")
        side = min(w, h)
        left, top = (w-side)//2, (h-side)//2
        box = [left, top, left+side, top+side]
        rgb = rgb.crop(box)
    rgb.info.clear()
    return rgb, dict(colour_management=management, crop_box=box, oriented_source_size=[w, h])


def nearest(pixel, colours):
    return min(colours, key=lambda c: sum((p-v)**2 for p, v in zip(pixel, c["rgb"])))["id"]


def quantize(reduced, palette):
    ids = [nearest(p, palette["colours"]) for p in reduced.get_flattened_data()]
    width, height = reduced.size
    return [ids[y*width:(y+1)*width] for y in range(height)]


def render(cells, palette):
    lookup = {c["id"]: tuple(c["rgb"]) for c in palette["colours"]}
    img = Image.new("RGB", (len(cells[0]), len(cells)))
    img.putdata([lookup[c] for row in cells for c in row])
    return img


def tile_cells(cells, day):
    tr, tc = divmod(day-1, 5)
    side = len(cells) // 5
    return [row[tc*side:(tc+1)*side] for row in cells[tr*side:(tr+1)*side]]


def inventory(cells, palette):
    rows = []
    for day in range(26):
        selected = cells if day == 0 else tile_cells(cells, day)
        counts = Counter(c for row in selected for c in row)
        for c in palette["colours"]:
            rows.append(dict(scope="overall" if day == 0 else "tile", day="" if day == 0 else str(day),
                             colour_id=c["id"], count=str(counts[c["id"]])))
    return rows


def guide(path, cells, palette, png, subdivision=1, blank=False):
    esc = html.escape
    colours = {c["id"]: c for c in palette["colours"]}
    width, side = len(cells), len(cells)//5
    labels = {c: str(i).zfill(2) for i, c in enumerate(colours)}

    def grid(rows, numbered=False):
        out = ['<table class="map">' if numbered else '<table class="pattern">']
        for y, row in enumerate(rows):
            out.append('<tr>')
            for x, value in enumerate(row):
                if numbered:
                    out.append(f'<td>Day {value}</td>')
                else:
                    c = colours[value]
                    channels = [v/255 for v in c["rgb"]]
                    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in channels]
                    lum = sum(a*b for a, b in zip(linear, (.2126, .7152, .0722)))
                    ink = '#000000' if lum > .179 else '#FFFFFF'
                    borders = ''
                    if subdivision > 1:
                        for edge, thick in [('top', y % subdivision == 0), ('left', x % subdivision == 0),
                                            ('bottom', y == side-1), ('right', x == side-1)]:
                            if thick:
                                borders += f'border-{edge}:1.5pt solid #111;'
                    background = '#FFFFFF' if blank else c['hex']
                    ink = '#111111' if blank else ink
                    out.append(f'<td style="background:{background};color:{ink};{borders}">{labels[value]}</td>')
            out.append('</tr>')
        out.append('</table>')
        return ''.join(out)

    legend = ''.join(f'<li><span style="background:{c["hex"]}"></span>{labels[c["id"]]} = {esc(c["id"])} '
                     f'{esc(c["name"])} · {c["hex"]}</li>' for c in colours.values())
    encoded = base64.b64encode(png).decode()
    sections = [f'<section><h1>{esc(palette["id"])} Christmas mosaic</h1>'
                f'<p>{width} × {width} cells · 25 tiles · one tile per day, December 1–25. White is filled.</p>'
                f'<img class="preview" alt="Finished mosaic" src="data:image/png;base64,{encoded}">'
                '<h2>Assembly map · ↑ TOP</h2>' + grid([[r*5+c+1 for c in range(5)] for r in range(5)], True)
                + f'<ul class="legend">{legend}</ul></section>']
    for day in range(1, 26):
        rows = tile_cells(cells, day)
        counts = Counter(c for row in rows for c in row)
        summary = ' · '.join(f'{esc(c)}: {counts[c]}' for c in colours)
        tr, tc = divmod(day-1, 5)
        sections.append(f'<section><h1>Day {day}</h1><p>Tile row {tr+1}, column {tc+1} · ↑ TOP</p>'
                        + (f'<p>{side} × {side} colour cells. Heavy lines enclose each original position’s '
                           f'{subdivision} × {subdivision} block.</p>' if subdivision > 1 else '')
                        + grid(rows) + f'<p class="counts">{summary}</p><p>{side*side} colour cells. Keep this orientation when assembling.</p>'
                        + f'<ul class="legend">{legend}</ul></section>')
    Path(path).write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Mosaic assembly</title>'
        '<style>body{font:16px system-ui;margin:24px;color:#171717}section{max-width:760px;margin:0 auto 48px;break-after:page}'
        'section:last-child{break-after:auto}table{border-collapse:collapse}td{text-align:center;border:1px solid #777}'
        '.pattern{width:100%;table-layout:fixed}.pattern td{padding:0;font-weight:500}'
        + f'.pattern td{{height:{540/side:.2f}px;font-size:{14 if side == 9 else 10}px}}'
        +
        '.map td{padding:8px 20px}.preview{width:360px;max-width:100%;image-rendering:pixelated}'
        '.legend{display:flex;flex-wrap:wrap;gap:8px 20px;padding:0;list-style:none;font-size:13px}'
        '.legend span{display:inline-block;width:16px;height:16px;border:1px solid #888;vertical-align:middle;margin-right:6px}'
        '.counts{line-height:1.8}@media print{body{margin:0}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}'
        + f'.pattern{{width:{side*(14 if side == 9 else 6)}mm}}.pattern td{{height:{14 if side == 9 else 6}mm;font-size:{10 if side == 9 else 6.5}pt;line-height:1}}'
        + '.preview{width:65mm}.legend{font-size:8pt;gap:3px 12px}.counts{font-size:9pt;line-height:1.3}'
        'h1{font-size:20pt;margin:0 0 6mm}p{margin:3mm 0}}@page{size:A4;margin:15mm}</style><body>'
        + ''.join(sections) + '</body></html>')


def validate(directory):
    directory = Path(directory)
    palette = load_palette(directory / "palette.json")
    data = read_json(directory / "mosaic.json")
    subdivision = data.get("subdivision", 1)
    shape = geometry(subdivision)
    width, side = shape["width"], shape["tile_width"]
    require(all(data.get(k) == v for k, v in shape.items()), "Incorrect geometry metadata")
    require(data["palette"] == palette, "Mosaic and saved palette disagree")
    cells = data["cells"]
    allowed = {c["id"] for c in palette["colours"]}
    require(len(cells) == width and all(len(row) == width and all(c in allowed for c in row) for row in cells), "Invalid cell matrix")
    expected = render(cells, palette)
    with Image.open(directory / "mosaic.png") as img:
        require(img.mode == "RGB" and img.size == (width, width) and "transparency" not in img.info, "Invalid canonical PNG format")
        require(img.tobytes() == expected.tobytes(), "Canonical pixels differ from cell IDs")
    names = {f"day-{day:02d}.png" for day in range(1, 26)}
    require({p.name for p in (directory / "tiles").glob("*.png")} == names, "Expected exactly 25 tile PNGs")
    assembled = Image.new("RGB", (width, width))
    for day in range(1, 26):
        with Image.open(directory / "tiles" / f"day-{day:02d}.png") as tile:
            require(tile.mode == "RGB" and tile.size == (side, side), "Invalid tile dimensions or mode")
            tr, tc = divmod(day-1, 5)
            assembled.paste(tile, (tc*side, tr*side))
    require(assembled.tobytes() == expected.tobytes(), "Tile reassembly differs")
    with (directory / "inventory.csv").open(newline="") as f:
        require(list(csv.DictReader(f)) == inventory(cells, palette), "Inventory counts differ")
    with Image.open(directory / "preview.png") as preview:
        require(preview.mode == "RGB" and preview.size == preview_size(width), "Invalid preview format")
        require(preview.tobytes() == expected.resize(preview_size(width), Image.Resampling.NEAREST).tobytes(), "Preview is not exact nearest-neighbour enlargement")
    run = read_json(directory / "run.json")
    source = directory / run["source_filename"]
    require(hashlib.sha256(source.read_bytes()).hexdigest() == run["source_sha256"], "Source hash differs")
    require(run["settings"].get("subdivision", 1) == subdivision, "Subdivision settings disagree")
    normalized, _ = normalize(source, run["settings"]["centre_crop"], width)
    method = run["settings"]["resampling"]
    require(method in RESAMPLING, "Unsupported saved resampling method")
    reduced = normalized.resize((width, width), RESAMPLING[method])
    for name, expected_stage in [("normalized.png", normalized), ("reduced.png", reduced)]:
        with Image.open(directory / name) as stage:
            require(stage.mode == "RGB" and stage.size == expected_stage.size and stage.tobytes() == expected_stage.tobytes(), f"{name} differs from recomputed stage")
    require(quantize(reduced, palette) == cells, "Conversion is not reproducible from saved source")
    return dict(status="passed", cells=width*width, tiles=25, colours_used=len(set(c for row in cells for c in row)),
                checks=["canonical PNG and palette", "JSON reconstruction", "tile reassembly", "inventories",
                        "exact preview", "source hash", "intermediate images", "deterministic reconversion"])


def build(source, palette_path, output, generation_path=None, centre_crop=False, resampling="box", subdivision=1):
    start = time.perf_counter()
    source, output = Path(source), Path(output)
    require(not output.exists(), f"Output already exists: {output}; choose a new run directory")
    shape = geometry(subdivision)
    width = shape["width"]
    palette = load_palette(palette_path)
    normalized, normalization = normalize(source, centre_crop, width)
    generation = read_json(generation_path) if generation_path else {"prompt": None, "tool": None}
    method = resampling.upper()
    require(method in RESAMPLING, "Unsupported resampling method")
    reduced = normalized.resize((width, width), RESAMPLING[method])
    cells = quantize(reduced, palette)
    canonical = render(cells, palette)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        source_name = "source" + source.suffix.lower()
        shutil.copyfile(source, staging / source_name)
        normalized.save(staging / "normalized.png")
        reduced.save(staging / "reduced.png")
        canonical.save(staging / "mosaic.png")
        canonical.resize(preview_size(width), Image.Resampling.NEAREST).save(staging / "preview.png")
        write_json(staging / "palette.json", palette)
        write_json(staging / "mosaic.json", dict(schema_version=2, **shape, subdivision=subdivision, palette=palette, cells=cells))
        (staging / "tiles").mkdir()
        for day in range(1, 26):
            render(tile_cells(cells, day), palette).save(staging / "tiles" / f"day-{day:02d}.png")
        with (staging / "inventory.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["scope", "day", "colour_id", "count"])
            writer.writeheader()
            writer.writerows(inventory(cells, palette))
        guide(staging / "assembly.html", cells, palette, (staging / "mosaic.png").read_bytes(), subdivision)
        guide(staging / "colouring.html", cells, palette, (staging / "mosaic.png").read_bytes(), subdivision, blank=True)
        run = dict(schema_version=1, created_at=datetime.now(timezone.utc).isoformat(), generation=generation,
                   source_filename=source_name, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   settings=dict(resampling=method, quantization="squared encoded-sRGB distance", tie_break="palette order",
                                 dithering=False, centre_crop=centre_crop, subdivision=subdivision), normalization=normalization,
                   dependencies=dict(python=platform.python_version(), pillow=PIL.__version__), validation=None)
        write_json(staging / "run.json", run)
        run["validation"] = validate(staging)
        run["processing_seconds"] = round(time.perf_counter()-start, 4)
        write_json(staging / "run.json", run)
        require(not output.exists(), f"Output appeared during build: {output}")
        staging.rename(output)
    except BaseException:
        shutil.rmtree(staging)
        raise
    return dict(output=str(output), **run["validation"])
