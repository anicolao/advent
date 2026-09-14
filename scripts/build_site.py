"""Dependency-free static Pages build from the frozen annual editions."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def decode(choice, inverse):
    label = choice['first']
    result = [inverse[label]]
    for op in choice['ops']:
        if op['kind'] == 'run':
            assert isinstance(op['count'], int) and op['count'] > 0
            result.extend(inverse[label+i] for i in range(1, op['count']+1))
            label += op['count']
        else:
            assert op['kind'] == 'join'
            label = op['target']
            result.append(inverse[label])
    return result


def paths(day):
    answer = [v for row in day['sudoku']['solution'] for v in row]
    return [decode(next(c for c in i['choices'] if c['digit'] == answer[i['cell']]), day['inverse']) for i in day['instructions']]


def tile_svg(day, mode, font=7.1):
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="6.6in" height="6.6in" viewBox="-3 -3 66 66">',
           f'<title>December {day["day"]} · {html.escape(mode)}</title>',
           '<rect x="-3" y="-3" width="66" height="66" fill="white"/>',
           '<rect x="0" y="0" width="60" height="60" fill="none" stroke="#aaa" stroke-width="0.06"/>']
    if mode != 'art':
        for i in range(1, 6):
            out.append(f'<path d="M{i*10} 0V60 M0 {i*10}H60" fill="none" stroke="#ddd" stroke-width="0.06"/>')
        for i in range(6):
            out.append(f'<g font-family="Arial" font-size="1.25" fill="#444" text-anchor="middle"><text x="{i*10+5}" y="-1.3">{chr(65+i)}</text><text x="-1.7" y="{i*10+5}">{i+1}</text></g>')
        for index, ((px, py), label, (x, y)) in enumerate(zip(day['points'], day['labels'], day['label_positions'])):
            # Reproduce Mathpub's saved collision-aware label centres and guides.
            if ((x-px)**2+(y-py)**2)**.5*7.2 > 7:
                dx, dy = x-px, y-py
                t = max(abs(dx)/(len(str(label))*font/28.8+.08), abs(dy)/(font/14.4+.08))
                ex, ey = (x-dx/t, y-dy/t) if t > 1 else (px, py)
                out.append(f'<path d="M{px} {py}L{ex} {ey}" stroke="#888" stroke-width="{.8/7.2}"/>')
            out.append(f'<circle data-node="{index}" cx="{px}" cy="{py}" r=".09" fill="#111"/>')
            out.append(f'<text x="{x}" y="{y+.29}" text-anchor="middle" font-family="Arial" font-size="{font/7.2}" textLength="{len(str(label))*font/14.4}" lengthAdjust="spacingAndGlyphs" fill="#737373">{label}</text>')
    if mode != 'dots':
        for route in paths(day):
            coords = ' '.join(f'{day["points"][v][0]},{day["points"][v][1]}' for v in route)
            out.append(f'<polyline data-stroke="true" points="{coords}" fill="none" stroke="#151515" stroke-width=".15" stroke-linecap="round" stroke-linejoin="round"/>')
    return ''.join(out)+'</svg>'


def scene_svg(days):
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 302 302"><title>Completed 2026 Christmas scene</title><rect x="-1" y="-1" width="302" height="302" fill="white"/>']
    for day in days:
        out.append(f'<g transform="translate({60*(day["tile_column"]-1)} {60*(day["tile_row"]-1)})">')
        for route in paths(day):
            coords = ' '.join(f'{day["points"][v][0]},{day["points"][v][1]}' for v in route)
            out.append(f'<polyline points="{coords}" fill="none" stroke="#151515" stroke-width=".15" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append('</g>')
    return ''.join(out)+'</svg>'


DESCRIPTIONS = {
    'christmas-room-numbered-grid-v3': 'One number per dot, short connections and explicit joins. The final prototype before the book.',
    'christmas-room-numbered-grid-v2': 'Exact junctions and short hops, with two numbers per dot.',
    'christmas-room-numbered-grid': 'The first Sudoku lookup with numbered reference dots and decoy paths.',
    'christmas-room-reference-grid': 'Uniform reference grids at three resolutions.',
    'christmas-room-proof': 'The generated source and its actual vector reduction.',
    'nativity-reduction-proof': 'A detailed nativity reduction trial that did not transfer well.',
    'advent-organic-village': 'Twenty-five connected daily puzzles with more organic village forms.',
    'advent-winter-village': 'The first complete advent village.',
    'dot-to-dot-winter-window': 'An intricate window illustration with separate strokes.',
    'dot-to-dot-winter-window-draft': 'An earlier window construction.',
    'dot-to-dot-reindeer': 'An early silhouette experiment.',
}


def gallery():
    cards = []
    for folder in sorted((ROOT/'runs').iterdir()):
        if not folder.is_dir():
            continue
        entry = next((f for f in ('index.html', 'assembly.html', 'instructions.html') if (folder/f).exists()), None)
        if not entry:
            continue
        name = folder.name
        title = name.replace('-', ' ').title()
        description = DESCRIPTIONS.get(name, 'Marker-palette mosaic study. Compare the source, tile layout and finished artwork.')
        cards.append(f'<article class="archive-card"><h2><a href="../runs/{name}/{entry}">{html.escape(title)}</a></h2><p>{html.escape(description)}</p></article>')
    return ''.join(cards)


def build(out):
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT/'site', out, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('annual.html','print.html'))
    for template in ('annual.html','print.html'):
        (out/template).unlink(missing_ok=True)
    # Explicit allowlist: never publish .git, tooling, sibling publications or caches.
    for name in ('runs', 'inputs', 'palettes'):
        shutil.copytree(ROOT/name, out/name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
    for path in ROOT.glob('*.md'):
        shutil.copy2(path, out/path.name)
    for path in ROOT.glob('*art.png'):
        shutil.copy2(path, out/path.name)
    shutil.copy2(ROOT/'frixion.png', out/'frixion.png')
    archive = out/'experiments/index.html'
    archive.parent.mkdir(exist_ok=True)
    archive.write_text((ROOT/'site/experiments/index.html').read_text().replace('__GALLERY__', gallery()))
    template = (ROOT/'site/annual.html').read_text()
    for edition in sorted((ROOT/'editions').iterdir()):
        data = json.loads((edition/'calendar.json').read_text())
        provenance = json.loads((edition/'provenance.json').read_text())
        assert hashlib.sha256((edition/'calendar.json').read_bytes()).hexdigest() == provenance['calendar_sha256']
        year = str(data['year']); dest = out/year; dest.mkdir(exist_ok=True)
        shutil.copy2(edition/'calendar.json', dest/'calendar.json')
        shutil.copy2(edition/'provenance.json', dest/'provenance.json')
        def page(folder, day, prefix):
            folder.mkdir(parents=True, exist_ok=True)
            boot = json.dumps(dict(year=data['year'],day=day,base=prefix))
            content = template.replace('__BOOT__',boot).replace('__ASSET__',prefix+'../assets/').replace('__HOME__',prefix+'../').replace('__YEAR__',year)
            (folder/'index.html').write_text(content)
        page(dest, None, './')
        for day in data['days']:
            number=f'{day["day"]:02}'
            page(dest/'day'/number, day['day'], '../../')
            assets=dest/'tiles'/number;assets.mkdir(parents=True,exist_ok=True)
            for mode in ('dots','art','solved'):
                (assets/f'{mode}.svg').write_text(tile_svg(day,mode,data['label_font']))
        (dest/'scene.svg').write_text(scene_svg(data['days']))
        print_dir=dest/'print';print_dir.mkdir(exist_ok=True)
        (print_dir/'index.html').write_text((ROOT/'site/print.html').read_text().replace('__YEAR__',year))
    (out/'.nojekyll').touch()
    print(f'Site built at {out}')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'_site')
    build(parser.parse_args().output)
