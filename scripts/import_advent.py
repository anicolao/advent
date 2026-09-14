"""Freeze a finished Mathpub edition; never regenerate puzzles or label positions."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--edition', default='2026-2026-moderate')
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    edition = source/'advent/editions'/args.edition
    manifest = json.loads((edition/'manifest.json').read_text())
    year = manifest['year']
    out = ROOT/'editions'/str(year)
    if out.exists():
        raise SystemExit(f'{out} already exists. Published editions are immutable; review corrections explicitly.')
    preview = edition/'preview.html'
    payload = re.search(r'<script id="book-data" type="application/json">(.*?)</script>', preview.read_text(), re.S)
    if not payload:
        raise ValueError('Cannot find validated preview data')
    data = json.loads(payload.group(1))
    assert data['year'] == year and data['assembly_grid'] == manifest['assembly_grid']
    hashes = {'manifest.json': digest(edition/'manifest.json'), 'preview.html': digest(preview)}
    for day in data['days']:
        path = edition/f'day-{day["day"]:02}.json'
        original = json.loads(path.read_text())
        for key in day.keys() - {'label_positions'}:
            assert day[key] == original[key], (path.name, key, 'preview is stale')
        day['approved_paths'] = original['real_paths']
        hashes[path.name] = digest(path)
    data['title'] = manifest['title']
    data['series'] = manifest['series']
    data['tile_inches'] = 6
    provenance = dict(year=year, edition=args.edition,
                      source_repository='sudoku-challenges',
                      source_commit=subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
                      source_files=hashes, label_font_tex_points=data['label_font'],
                      note='Exact saved edition data and validated label positions; no puzzle regeneration.')
    out.mkdir(parents=True)
    target = out/'calendar.json'
    target.write_text(json.dumps(data, separators=(',', ':'))+'\n')
    provenance['calendar_sha256'] = digest(target)
    (out/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(f'Imported {year}: {len(data["days"])} days; {data["label_font"]} pt source labels; {digest(target)}')


if __name__ == '__main__':
    main()
