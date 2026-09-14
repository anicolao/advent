"""Extract photographed marker colours and render ordered, exact-RGB swatches."""

import hashlib
import io
import json
from pathlib import Path
from statistics import median

from PIL import Image, ImageCms, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SETS = {
    "frixion": {
        "title": "Pilot FriXion Fineliner",
        "size": (1600, 1561),
        "region": "Coloured barrels below the caps, away from lettering and silver bands",
        "names": ["Red", "Pink", "Coral pink", "Orange", "Yellow", "Lime green",
                  "Green", "Light blue", "Blue", "Purple", "Brown", "Black"],
        "centres": [85, 209, 334, 458, 580, 704, 831, 957, 1083, 1210, 1337, 1464],
        "y": (615, 645),
        "half_width": 12,
    },
    "clickart": {
        "title": "Zebra ClickArt",
        "size": (1349, 1600),
        "region": "Coloured push-buttons above the white barrels, below the glare band",
        "names": ["Black", "Blue", "Light blue", "Green", "Lime green", "Yellow",
                  "Orange", "Red", "Pink", "Purple", "Grey", "Brown"],
        "centres": [94, 198, 306, 420, 526, 641, 750, 850, 965, 1064, 1179, 1285],
        "y": (115, 155),
        "half_width": 10,
    },
}


def swatch(palette):
    canvas = Image.new("RGB", (1440, 300), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default(size=28)
    font = ImageFont.load_default(size=15)
    draw.text((24, 16), palette["name"], fill="#171717", font=title_font)
    draw.text((24, 55), "Photographed marker colours | left to right | 12 markers; white excluded",
              fill="#444444", font=font)
    for i, colour in enumerate(palette["colours"]):
        x = 24 + i * 116
        draw.rectangle((x, 92, x + 107, 209), fill=tuple(colour["rgb"]))
        draw.text((x, 218), f'{colour["position"]:02d} {colour["name"]}', fill="#171717", font=font)
        draw.text((x, 244), colour["hex"], fill="#444444", font=font)
    return canvas


def main():
    output = ROOT / "palettes"
    output.mkdir(exist_ok=True)
    palettes = []
    swatches = []
    for key, spec in SETS.items():
        source = ROOT / f"{key}.png"
        with Image.open(source) as original:
            assert original.size == spec["size"], "Source dimensions changed; reselect sampling boxes"
            profile = original.info.get("icc_profile")
            if profile:
                img = ImageCms.profileToProfile(
                    original.convert("RGB"), ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                    ImageCms.createProfile("sRGB"), outputMode="RGB")
                colour_management = "Embedded ICC profile converted to sRGB with Pillow ImageCms"
            else:
                img = original.convert("RGB")
                colour_management = "Untagged source assumed sRGB"
        colours = []
        annotated = img.copy()
        draw = ImageDraw.Draw(annotated)
        for i, (name, x) in enumerate(zip(spec["names"], spec["centres"]), 1):
            box = [x - spec["half_width"], spec["y"][0], x + spec["half_width"], spec["y"][1]]
            pixels = list(img.crop(box).get_flattened_data())
            rgb = [int(median(p[c] for p in pixels)) for c in range(3)]
            colours.append({"id": f"C{i:02d}", "position": i, "name": name,
                            "hex": "#" + "".join(f"{v:02X}" for v in rgb), "rgb": rgb,
                            "sample_box_xyxy": box})
            draw.rectangle(box, outline="white", width=3)
            draw.rectangle([box[0]-2, box[1]-2, box[2]+2, box[3]+2], outline="black", width=2)
            draw.text((box[0], box[1]-25), str(i), fill="white",
                      stroke_width=2, stroke_fill="black", font=ImageFont.load_default(size=20))
        palette = {
            "schema_version": 1, "id": key, "name": spec["title"], "colour_space": "sRGB",
            "order": "left-to-right in source photograph", "source": source.name,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_dimensions": list(img.size),
            "extraction": {"method": "per-channel median of manually selected rectangular samples",
                           "region": spec["region"], "box_convention": "[left, top, right, bottom], right/bottom exclusive",
                           "colour_management": colour_management + "; no exposure or saturation adjustment",
                           "note": "Photographed plastic colours, not calibrated ink measurements. Names are descriptive, not verified manufacturer names."},
            "colours": colours,
            "additional_mosaic_colour": {"id": "C00", "name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]},
        }
        assert len(colours) == len({c["hex"] for c in colours}) == 12
        assert all(c["hex"] != "#FFFFFF" for c in colours)
        (output / f"{key}.json").write_text(json.dumps(palette, indent=2) + "\n")
        preview = swatch(palette)
        preview.save(output / f"{key}-swatch.png")
        annotated.save(output / f"{key}-samples.png")
        # Confirm that exported swatch centres are exactly the JSON RGB values.
        with Image.open(output / f"{key}-swatch.png") as saved:
            for i, colour in enumerate(colours):
                assert saved.getpixel((24 + i * 116 + 50, 150)) == tuple(colour["rgb"])
        palettes.append(palette)
        swatches.append(preview)
    (output / "palettes.json").write_text(json.dumps({"schema_version": 1, "palettes": palettes}, indent=2) + "\n")
    combined = Image.new("RGB", (1440, 600), "white")
    for i, preview in enumerate(swatches):
        combined.paste(preview, (0, i * 300))
    combined.save(output / "swatches.png")
    print("Extracted two ordered 12-colour palettes; swatch RGB checks passed.")


if __name__ == "__main__":
    main()
