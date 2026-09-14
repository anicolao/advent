import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image

from mosaic.pipeline import build, load_palette, nearest, normalize, validate

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.palette_path = ROOT / "palettes/clickart.json"
        self.palette = load_palette(self.palette_path)

    def test_exact_colour_and_tie(self):
        for colour in self.palette["colours"]:
            self.assertEqual(nearest(colour["rgb"], self.palette["colours"]), colour["id"])
        colours = [dict(id="first", rgb=[0, 0, 0]), dict(id="second", rgb=[2, 0, 0])]
        self.assertEqual(nearest((1, 0, 0), colours), "first")

    def test_subdivision_preserves_independent_cells_and_print_grids(self):
        source = self.root / "fine.png"
        img = Image.new("RGB", (135, 135))
        img.putdata([tuple(self.palette["colours"][(x*3+y*7+x*y)%13]["rgb"])
                     for y in range(135) for x in range(135)])
        img.save(source)
        output = self.root / "fine"
        result = build(source, self.palette_path, output, resampling="nearest", subdivision=3)
        self.assertEqual(result["cells"], 18225)
        self.assertEqual(validate(output)["status"], "passed")
        with Image.open(output / "mosaic.png") as saved:
            self.assertEqual(saved.tobytes(), img.tobytes())
        for day, xy in [(1, (0, 0)), (5, (108, 0)), (6, (0, 27)), (25, (108, 108))]:
            with Image.open(output / "tiles" / f"day-{day:02d}.png") as tile:
                self.assertEqual(tile.size, (27, 27))
                self.assertEqual(tile.getpixel((0, 0)), img.getpixel(xy))
        with Image.open(output / "preview.png") as preview:
            self.assertEqual(preview.size, (1080, 1080))

        class Grids(HTMLParser):
            def __init__(self):
                super().__init__()
                self.patterns = []
                self.active = False
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "table" and attrs.get("class") == "pattern":
                    self.patterns.append([])
                    self.active = True
                if tag == "td" and self.active:
                    self.patterns[-1].append(attrs["style"])
            def handle_endtag(self, tag):
                if tag == "table":
                    self.active = False

        for filename in ("assembly.html", "colouring.html"):
            parsed = Grids()
            parsed.feed((output / filename).read_text())
            self.assertEqual(len(parsed.patterns), 25)
            self.assertTrue(all(len(grid) == 729 for grid in parsed.patterns))
            for index, style in enumerate(parsed.patterns[0]):
                y, x = divmod(index, 27)
                self.assertEqual('border-top:1.5pt' in style, y % 3 == 0)
                self.assertEqual('border-left:1.5pt' in style, x % 3 == 0)
                if filename == "colouring.html":
                    self.assertIn('background:#FFFFFF', style)
        data = json.loads((output / "mosaic.json").read_text())
        data["subdivision"] = 1
        (output / "mosaic.json").write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "geometry"):
            validate(output)

    def test_subdivision_rejects_small_source_and_invalid_factor(self):
        source = self.root / "small.png"
        Image.new("RGB", (45, 45), "white").save(source)
        with self.assertRaisesRegex(ValueError, "at least 135"):
            build(source, self.palette_path, self.root / "bad", subdivision=3)
        with self.assertRaisesRegex(ValueError, "Subdivision"):
            build(source, self.palette_path, self.root / "bad", subdivision=2)

    def test_nearest_preserves_sampled_colour_and_revalidates(self):
        source = self.root / "pixel-art.png"
        img = Image.new("RGB", (90, 90), "white")
        dark = tuple(self.palette["colours"][1]["rgb"])
        for y in range(1, 90, 2):
            for x in range(1, 90, 2):
                img.putpixel((x, y), dark)
        img.save(source)
        output = self.root / "nearest"
        build(source, self.palette_path, output, resampling="nearest")
        with Image.open(output / "mosaic.png") as saved:
            self.assertEqual(set(saved.get_flattened_data()), {dark})
        self.assertEqual(validate(output)["status"], "passed")
        run = json.loads((output / "run.json").read_text())
        run["settings"]["resampling"] = "BOX"
        (output / "run.json").write_text(json.dumps(run))
        with self.assertRaisesRegex(ValueError, "reduced.png"):
            validate(output)

    def test_invalid_palettes(self):
        for mutation in ("duplicate_id", "duplicate_rgb", "no_white", "short", "mismatch"):
            p = json.loads(json.dumps(self.palette))
            if mutation == "duplicate_id":
                p["colours"][1]["id"] = p["colours"][0]["id"]
            elif mutation == "duplicate_rgb":
                p["colours"][1].update(hex="#FFFFFF", rgb=[255, 255, 255])
            elif mutation == "no_white":
                p["colours"][0].update(hex="#FEFEFE", rgb=[254, 254, 254])
            elif mutation == "short":
                p["colours"].pop()
            else:
                p["colours"][0]["rgb"] = [0, 0, 0]
            path = self.root / "palette.json"
            path.write_text(json.dumps(p))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                load_palette(path)

    def test_normalization(self):
        path = self.root / "source.png"
        Image.new("RGBA", (50, 60), (255, 0, 0, 0)).save(path)
        with self.assertRaisesRegex(ValueError, "not square"):
            normalize(path)
        normalized, info = normalize(path, True)
        self.assertEqual(normalized.size, (50, 50))
        self.assertEqual(info["crop_box"], [0, 5, 50, 55])
        self.assertEqual(normalized.getpixel((0, 0)), (255, 255, 255))
        Image.new("RGB", (44, 44)).save(path)
        with self.assertRaisesRegex(ValueError, "at least"):
            normalize(path)
        Image.new("RGBA", (45, 45), (255, 0, 0, 128)).save(path)
        self.assertEqual(normalize(path)[0].getpixel((0, 0)), (255, 127, 127))

    def test_exif_orientation_and_multiframe(self):
        path = self.root / "oriented.png"
        img = Image.new("RGB", (45, 45), "white")
        img.putpixel((0, 0), (255, 0, 0))
        exif = Image.Exif()
        exif[274] = 6
        img.save(path, exif=exif)
        self.assertEqual(normalize(path)[0].getpixel((44, 0)), (255, 0, 0))
        path = self.root / "animated.gif"
        img.save(path, save_all=True, append_images=[Image.new("RGB", (45, 45), "black")])
        with self.assertRaisesRegex(ValueError, "Multi-frame"):
            normalize(path)

    def test_artifacts_reproducibility_and_tampering(self):
        source = self.root / "source.png"
        img = Image.new("RGB", (45, 45))
        # Asymmetric, varying pattern crosses every tile boundary.
        img.putdata([tuple(self.palette["colours"][(x*3+y*7+x*y)%13]["rgb"])
                     for y in range(45) for x in range(45)])
        img.save(source)
        output = self.root / "run"
        self.assertEqual(build(source, self.palette_path, output)["status"], "passed")
        self.assertEqual((output / "source.png").read_bytes(), source.read_bytes())
        with Image.open(output / "mosaic.png") as saved:
            self.assertEqual(saved.tobytes(), img.tobytes())
        for day, xy in [(1, (0, 0)), (5, (36, 0)), (6, (0, 9)), (25, (36, 36))]:
            with Image.open(output / "tiles" / f"day-{day:02d}.png") as tile:
                self.assertEqual(tile.getpixel((0, 0)), img.getpixel(xy))
        second = self.root / "repeat"
        build(source, self.palette_path, second)
        self.assertEqual((output / "mosaic.json").read_bytes(), (second / "mosaic.json").read_bytes())
        with self.assertRaisesRegex(ValueError, "already exists"):
            build(source, self.palette_path, output)
        tile_path = output / "tiles/day-05.png"
        with Image.open(tile_path) as tile:
            changed = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        changed.save(tile_path)
        with self.assertRaisesRegex(ValueError, "reassembly"):
            validate(output)


if __name__ == "__main__":
    unittest.main()
