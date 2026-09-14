"""Printed lookup and short-hop drawing proof; original geometry is immutable."""
from pathlib import Path
from collections import defaultdict
import json
import math
import random
from dot_to_dot.numbered_grid import solve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'runs/christmas-room-numbered-grid-v2'
MAX_HOP = 3


def cell_name(i):
    return f'{chr(65+i//9)}{i%9+1}'


def sector(p):
    return f'{chr(65+min(5,int(p[0]//10)))}{min(5,int(p[1]//10))+1}'


def build_data():
    rng = random.Random(18244)
    source = json.loads((ROOT/'runs/christmas-room-reference-grid/grids.json').read_text())['variants']['61'][17]
    original = [[((v-1)%61,(v-1)//61) for v in s['points']] for s in source['strokes']]
    points, ids = [], {}
    def point_id(p):
        key = tuple(round(v,8) for v in p)
        if key not in ids:
            ids[key] = len(points)
            points.append(list(p))
        return ids[key]
    original_ids = [[point_id(p) for p in path] for path in original]
    real = []
    provenance = []
    for path in original:
        route = [point_id(path[0])]
        for a,b in zip(path,path[1:]):
            count = math.ceil(math.dist(a,b)/MAX_HOP)
            segment = [route[-1]]
            for k in range(1,count+1):
                v = point_id([a[j]+(b[j]-a[j])*k/count for j in range(2)])
                route.append(v);segment.append(v)
            provenance.append(dict(a=a,b=b,nodes=segment))
        real.append(route)
    real_count = len(points)
    # Fill spatial holes instead of printing only the subject's contours.
    # Jittered candidate positions avoid a straight real line standing out
    # merely because only its intermediate dots are off a regular lattice.
    candidates = [(min(60,max(0,x+rng.uniform(-.5,.5))),min(60,max(0,y+rng.uniform(-.5,.5))))
                  for y in range(0,61,2) for x in range(0,61,2)]
    rng.shuffle(candidates)
    for p in candidates:
        if min(math.dist(p,q) for q in points) >= 1.15:
            point_id(p)
    # Every printed location has two labels, including decoys: shared
    # junctions get no distinctive appearance. Each real path visit consumes
    # a different label slot at the same exact location.
    slots = [2]*len(points)
    for p in real:
        for v in p:
            slots[v] -= 1
    assert min(slots) >= 0
    neighbours = {v:[w for w in range(real_count,len(points))
                     if v!=w and math.dist(points[v],points[w]) <= MAX_HOP]
                  for v in range(real_count,len(points))}
    decoys = []
    available = {v for v in neighbours if slots[v]}
    while available:
        path = [rng.choice(sorted(available))]
        slots[path[0]] -= 1
        if not slots[path[0]]:available.remove(path[0])
        while len(path)<100:
            options = [v for v in neighbours[path[-1]] if v in available and v not in path[-3:]]
            if not options:break
            v = rng.choice(options);path.append(v);slots[v]-=1
            if not slots[v]:available.remove(v)
        decoys.append(path)
    fillers = [[v] for v,count in enumerate(slots) for _ in range(count)]
    routes = [dict(kind='real',nodes=p,index=i) for i,p in enumerate(real)]
    routes += [dict(kind='decoy',nodes=p) for p in decoys]+[dict(kind='filler',nodes=p) for p in fillers]
    rng.shuffle(routes)
    labels = [[] for _ in points]
    inverse = [None]
    real_first = {}
    windows = defaultdict(list)
    for route in routes:
        first = len(inverse)
        if route['kind']=='real':real_first[route['index']] = first
        for v in route['nodes']:
            labels[v].append(len(inverse));inverse.append(v)
        if route['kind']=='decoy':
            for length in set(len(p)-1 for p in real):
                for offset in range(len(route['nodes'])-length):
                    windows[length].append((first+offset,route['nodes'][offset:offset+length+1]))
    assert all(len(x)==2 for x in labels)
    previous = json.loads((ROOT/'runs/christmas-room-numbered-grid/puzzle.json').read_text())
    solution = previous['solution']
    puzzle = solution[:]
    for i in rng.sample(range(81),81):
        old = puzzle[i];puzzle[i] = 0
        if len(solve(puzzle)) != 1:puzzle[i]=old
        if puzzle.count(0)==len(real):break
    assert puzzle.count(0)==len(real)
    keys = [i for i,v in enumerate(puzzle) if not v]
    instructions = []
    for index,(path,cell) in enumerate(zip(real,keys)):
        length = len(path)-1
        assert len(windows[length])>=8, (length,len(windows[length]))
        alternatives = iter(rng.sample(windows[length],8))
        choices = []
        for digit in range(1,10):
            first,nodes = (real_first[index],path) if digit==solution[cell] else next(alternatives)
            choices.append(dict(digit=digit,first=first,length=length,nodes=nodes,
                                sector=sector(points[nodes[0]])))
        instructions.append(dict(id=index+1,cell=cell,name=cell_name(cell),choices=choices))
    report = dict(day=18,printed_dots=len(points),printed_labels=len(inverse)-1,
                  original_segments=len(provenance),short_connections=sum(len(p)-1 for p in real),
                  max_hop=max(math.dist(points[a],points[b]) for p in real for a,b in zip(p,p[1:])),
                  intermediate_points=real_count-len(ids.keys() & {tuple(p) for path in original for p in path}),
                  shifted_original_vertices=0,shared_real_locations=sum(len([v for p in real for v in p if v==i])>1 for i in range(real_count)),
                  lookup_rows=len(instructions),sudoku_givens=sum(bool(v) for v in puzzle),
                  max_original_hop=max(math.dist(a,b) for p in original for a,b in zip(p,p[1:])),
                  shortest_decoy_choice_pool=min(len(windows[len(p)-1]) for p in real))
    return dict(day=18,points=points,labels=labels,inverse=inverse,sudoku=puzzle,solution=solution,
                instructions=instructions,real_paths=real,original_paths=original_ids,
                provenance=provenance,report=report)


def svg(data,mode):
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="380mm" height="380mm" viewBox="0 0 2360 2360"><rect width="2360" height="2360" fill="white"/>']
    def pos(v):return [100+t*36 for t in data['points'][v]]
    if mode in ('blank','connected'):
        for i in range(7):
            p=100+i*360
            out.append(f'<path d="M{p} 100V2260 M100 {p}H2260" stroke="#d9dfdb" stroke-width="1"/>')
        for i in range(6):
            p=280+i*360
            out.append(f'<g font-family="Arial" font-size="24" text-anchor="middle" fill="#56616a"><text x="{p}" y="70">{chr(65+i)}</text><text x="65" y="{p}">{i+1}</text></g>')
        for v,labels in enumerate(data['labels']):
            x,y=pos(v)
            out.append(f'<circle cx="{x}" cy="{y}" r="2.5" fill="#62716c"/><g font-family="Arial" font-size="10" text-anchor="middle" fill="#465650"><text x="{x}" y="{y-7}">{labels[0]}</text><text x="{x}" y="{y+12}">{labels[1]}</text></g>')
    if mode!='blank':
        for path in data['original_paths'] if mode=='original' else data['real_paths']:
            coords=' '.join('%s,%s'%tuple(pos(v)) for v in path)
            out.append(f'<polyline points="{coords}" fill="none" stroke="#192e39" stroke-width="3" stroke-linejoin="round"/>')
    return ''.join(out)+'</svg>'


def print_book(data):
    grid='<table class="sudoku"><tr><th></th>'+''.join(f'<th>{c}</th>' for c in range(1,10))+'</tr>'
    for r in range(9):
        grid+=f'<tr><th>{chr(65+r)}</th>'+''.join(f'<td class="c{c} r{r}">{data["sudoku"][r*9+c] or ""}</td>' for c in range(9))+'</tr>'
    grid+='</table>'
    pages=[f'<section class="page"><h1>Day 18 · solve, look up, connect</h1><p>One tile of the Christmas room. Keep the separate drawing sheet beside this booklet.</p>{grid}<ol><li><b>Solve the Sudoku.</b> Rows are A–I; columns are 1–9. Every originally blank cell has a lookup row. Printed givens have none.</li><li><b>Find the lookup section for that row letter.</b> Within it, find the cell address; move across to the column headed by its solved digit.</li><li><b>Read the entry: sector / start number / +connections.</b> For example, <strong>C2 / 812 / +6</strong> means find dot 812 in drawing sector C2, then connect 813, 814, 815, 816, 817, 818. Stop and lift your pen. This example explains the notation; it is not a puzzle answer.</li><li><b>Tick the lookup row when finished.</b> Work down sections A–I in order. Each instruction starts a separate stroke.</li></ol><p>Each dot has two numbers. They name the <b>same location</b> in two different sequences. Follow only the number you need; do not switch to the other number. This allows lines to meet without gaps.</p><p>The drawing has sectors A–F across and 1–6 down. These are drawing locations, separate from Sudoku addresses. All consecutive steps are at most 1/20 of the drawing square’s width.</p></section>']
    for start in (0,3,6):
        sections=[]
        for r in range(start,start+3):
            rows=[]
            for item in data['instructions']:
                if item['cell']//9!=r:continue
                entries=''.join(f'<td><b>{c["sector"]}</b> / {c["first"]}<br>+{c["length"]}</td>' for c in item['choices'])
                rows.append(f'<tr><th>□ {item["name"]}</th>{entries}</tr>')
            sections.append(f'<h2>Sudoku row {chr(65+r)}</h2><table class="lookup"><thead><tr><th>Cell</th>'+''.join(f'<th>{i}</th>' for i in range(1,10))+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
        pages.append('<section class="page"><h1>Lookup · Sudoku rows '+chr(65+start)+'–'+chr(67+start)+'</h1><p>Find the cell down the left → its solved digit across the top.<br>Each entry is <b>drawing sector / starting dot</b>, then <b>+connections</b>. Lift between rows.</p>'+''.join(sections)+'</section>')
    css='*{box-sizing:border-box}body{margin:0;background:#e7e9e5;color:#20343b;font:12px Arial}.page{width:277mm;height:190mm;margin:12px auto;background:white;padding:3mm;break-after:page;overflow:hidden}.page:last-child{break-after:auto}h1{font-size:20px;margin:0 0 9px}h2{font-size:14px;margin:11px 0 4px}p,li{line-height:1.5}.sudoku{float:left;margin:8px 28px 15px 0;border-collapse:collapse}.sudoku td{width:34px;height:34px;text-align:center;border:1px solid #9baba4;font-size:18px}.sudoku th{padding:6px}.sudoku .c0,.sudoku .c3,.sudoku .c6{border-left:2px solid #20343b}.sudoku .r0,.sudoku .r3,.sudoku .r6{border-top:2px solid #20343b}.sudoku .c8{border-right:2px solid #20343b}.sudoku .r8{border-bottom:2px solid #20343b}ol{padding-left:25px}li{margin:8px 0}.lookup{border-collapse:collapse;width:100%;table-layout:fixed;font-size:11px}.lookup th,.lookup td{border:1px solid #aab8b0;padding:3px;text-align:center}.lookup thead{background:#e9eeea}.lookup th:first-child{width:55px}@page{size:A4 landscape;margin:10mm}@media print{body{background:white}.page{margin:0;padding:3mm;width:277mm;height:190mm}}'
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Day 18 printed Sudoku and lookup</title><style>'+css+'</style>'+''.join(pages)+'</html>'


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    data=build_data()
    (OUT/'puzzle.json').write_text(json.dumps(data,indent=2))
    (OUT/'report.json').write_text(json.dumps(data['report'],indent=2))
    for mode in ('blank','connected','answer','original'):(OUT/f'{mode}.svg').write_text(svg(data,mode))
    (OUT/'lookup.html').write_text(print_book(data))
    (OUT/'index.html').write_text(Path(__file__).with_name('numbered_grid_v2.html').read_text().replace('__DATA__',json.dumps(data)))
    print(json.dumps(data['report'],indent=2))


if __name__=='__main__':build()
