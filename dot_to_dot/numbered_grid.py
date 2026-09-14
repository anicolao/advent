"""One-tile Sudoku/start-and-length experiment, with unique dot labels."""
from pathlib import Path
from collections import defaultdict
import json
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs/christmas-room-numbered-grid'
N = 61


def xy(v):
    return (v % N, v // N)


def distance(a, b):
    x, y = xy(a)
    u, v = xy(b)
    return math.hypot(x-u, y-v)


def solve(puzzle, limit=2):
    """Count solutions with MRV search; stop as soon as uniqueness fails."""
    board = puzzle[:]
    results = []
    def visit():
        best = None
        options = None
        for i, digit in enumerate(board):
            if digit:
                continue
            r, c = divmod(i, 9)
            used = set(board[r*9:r*9+9]) | set(board[c::9])
            used |= {board[y*9+x] for y in range(r//3*3, r//3*3+3)
                     for x in range(c//3*3, c//3*3+3)}
            candidates = sorted(set(range(1, 10))-used)
            if not candidates:
                return
            if options is None or len(candidates) < len(options):
                best, options = i, candidates
        if best is None:
            results.append(board[:])
            return
        for digit in options:
            board[best] = digit
            visit()
            if len(results) >= limit:
                break
        board[best] = 0
    visit()
    return results


def build_data():
    rng = random.Random(18243)
    source = json.loads((ROOT/'runs/christmas-room-reference-grid/grids.json').read_text())['variants']['61'][17]
    paths = [[v-1 for v in s['points']] for s in source['strokes']]
    # Reserve all original positions first. Only repeated visits move, never
    # displacing an as-yet-unvisited original vertex.
    reserved = {v for p in paths for v in p}
    occupied = set(reserved)
    visits = defaultdict(list)
    for pi, path in enumerate(paths):
        for vi, v in enumerate(path):
            visits[v].append((pi, vi))
    # Keep the shared coordinate for an interior visit when possible. Move
    # loose ends along their original segment, avoiding arbitrary little hooks.
    anchors = {v: max(items, key=lambda item: int(item[1]>0)+int(item[1]<len(paths[item[0]])-1))
               for v, items in visits.items()}
    def segment_distance(point, a, b):
        x,y = xy(point); ax,ay = xy(a); bx,by = xy(b)
        dx,dy = bx-ax,by-ay
        t = max(0, min(1, ((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
        return math.hypot(x-ax-t*dx,y-ay-t*dy)
    shifted = []
    real = []
    for pi, path in enumerate(paths):
        result = []
        for vi, v in enumerate(path):
            target = v
            if (pi, vi) != anchors[v]:
                neighbours = path[max(0,vi-1):vi]+path[vi+1:vi+2]
                candidates = [i for i in range(N*N) if i not in occupied and distance(v,i)<=2**.5]
                if not candidates:
                    raise ValueError('Cannot separate a junction within one neighbouring grid cell')
                target = min(candidates, key=lambda i:
                             (sum(segment_distance(i,v,w) for w in neighbours)+.08*distance(v,i), i))
                occupied.add(target)
                shifted.append({'from': v, 'to': target, 'distance': distance(v, target)})
            result.append(target)
        real.append(result)
    # Each wrong digit gets a locally coherent path, on unused positions only.
    free = set(range(N*N)) - occupied
    def decoy(length):
        p = [rng.choice(sorted(free))]
        free.remove(p[0])
        while len(p) < length:
            x, y = xy(p[-1])
            nearby = [v for v in sorted(free)
                      if abs(xy(v)[0]-x) <= 5 and abs(xy(v)[1]-y) <= 5]
            if not nearby:
                nearby = sorted(free, key=lambda v: distance(v, p[-1]))[:12]
            p.append(rng.choice(nearby))
            free.remove(p[-1])
        return p

    digits = rng.sample(list(range(1, 10)), 9)
    rows = [b*3+r for b in rng.sample(range(3), 3) for r in rng.sample(range(3), 3)]
    cols = [b*3+c for b in rng.sample(range(3), 3) for c in rng.sample(range(3), 3)]
    solution = [digits[(r*3+r//3+c) % 9] for r in rows for c in cols]
    puzzle = solution[:]
    order = rng.sample(range(81), 81)
    for i in order:
        old = puzzle[i]
        puzzle[i] = 0
        if len(solve(puzzle)) != 1:
            puzzle[i] = old
        if puzzle.count(0) == 48:
            break
    keys = rng.sample([i for i, v in enumerate(puzzle) if not v], len(real))
    routes = []
    instructions = []
    for index, (path, cell) in enumerate(zip(real, keys)):
        choices = []
        for digit in range(1, 10):
            route = path if digit == solution[cell] else decoy(len(path))
            routes.append(route)
            choices.append({'digit': digit, 'nodes': route,
                            'start': [xy(route[0])[0]+1, xy(route[0])[1]+1],
                            'length': len(route)-1})
        instructions.append({'id': index+1, 'cell': cell, 'choices': choices})
    # Fill remaining positions with additional short consecutive paths, so
    # meaningful sequences are not the only locally consecutive numbers.
    while free:
        routes.append(decoy(min(len(free), rng.randint(2, 12))))
    rng.shuffle(routes)
    labels = [0]*(N*N)
    label = 1
    for path in routes:
        for node in path:
            labels[node] = label
            label += 1
    for instruction in instructions:
        for choice in instruction['choices']:
            choice['first'] = labels[choice['nodes'][0]]
    report = {
        'day': 18, 'grid_size': N, 'printed_dots': N*N,
        'real_instructions': len(real), 'real_segments': sum(len(p)-1 for p in real),
        'real_dot_visits': sum(map(len, real)), 'moved_visits': len(shifted),
        'max_move_in_grid_steps': max(s['distance'] for s in shifted),
        'wrong_answer_paths': 8*len(real), 'sudoku_givens': sum(bool(v) for v in puzzle),
        'sudoku_solutions': len(solve(puzzle)),
    }
    return dict(grid_size=N, day=18, labels=labels, instructions=instructions,
                sudoku=puzzle, solution=solution, original_paths=paths,
                real_paths=real, moved=shifted, report=report)


def svg(data, mode):
    margin, step = 100, 36
    size = margin*2+(N-1)*step
    def pos(node):
        x, y = xy(node)
        return (margin+x*step, margin+y*step)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="420mm" viewBox="0 0 {size} {size}"><rect width="100%" height="100%" fill="white"/>']
    if mode in ('blank', 'connected'):
        for i in range(N):
            p = margin+i*step
            out.append(f'<g fill="#56616a" font-family="Arial" font-size="13" text-anchor="middle"><text x="{p}" y="65">{i+1}</text><text x="65" y="{p+4}">{i+1}</text></g>')
        for node, label in enumerate(data['labels']):
            x, y = pos(node)
            out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="#78818a"/><text x="{x}" y="{y-6}" text-anchor="middle" font-family="Arial" font-size="9" fill="#56616a">{label}</text>')
    paths = data['original_paths'] if mode == 'original' else data['real_paths']
    if mode != 'blank':
        for path in paths:
            points = ' '.join('%s,%s'%pos(v) for v in path)
            out.append(f'<polyline points="{points}" fill="none" stroke="#192e39" stroke-width="3" stroke-linejoin="round"/>')
    return ''.join(out)+'</svg>'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build_data()
    (OUT/'puzzle.json').write_text(json.dumps(data, indent=2))
    (OUT/'report.json').write_text(json.dumps(data['report'], indent=2))
    for mode in ('blank', 'connected', 'original', 'answer'):
        (OUT/f'{mode}.svg').write_text(svg(data, mode))
    (OUT/'index.html').write_text(Path(__file__).with_name('numbered_grid.html').read_text().replace('__DATA__', json.dumps(data)))
    rows = []
    for item in data['instructions']:
        cell = item['cell']
        choices = ''.join(f'<td>({c["start"][0]}, {c["start"][1]})<br>{c["length"]} lines</td>' for c in item['choices'])
        rows.append(f'<tr><th>{item["id"]}: R{cell//9+1}C{cell%9+1}</th>{choices}</tr>')
    (OUT/'lookup.html').write_text('<meta charset="utf-8"><title>Tile 18 lookup</title><style>body{font:12px system-ui}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:7px;text-align:center}tr{break-inside:avoid}@page{size:A4 landscape;margin:12mm}</style><h1>Tile 18 · Sudoku lookup</h1><p>For each listed Sudoku cell, use its solved digit to select a column. Start at (column, row); connect successive dot numbers for the stated number of lines. Lift the pen between instructions. There are 38 drawing keys; other Sudoku cells still help solve the puzzle.</p><table><thead><tr><th>Key / Sudoku cell</th>'+''.join(f'<th>Digit {d}</th>' for d in range(1,10))+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
    print(json.dumps(data['report'], indent=2))


if __name__ == '__main__':
    build()
