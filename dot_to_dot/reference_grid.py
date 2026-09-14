"""Map the accepted room drawing to identical, artwork-independent reference grids."""
from collections import defaultdict
from pathlib import Path
import json
import math
import random
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'runs/christmas-room-proof/calendar.json'
OUT=ROOT/'runs/christmas-room-reference-grid'
SIZES=(16,31,61)


def decompose(edges):
    """Cover every unique undirected edge once, with explicit pen lifts."""
    edges=sorted(edges);adj=defaultdict(list)
    for i,(a,b) in enumerate(edges):adj[a].append((b,i));adj[b].append((a,i))
    remaining=set(adj);components=[];virtual=max(remaining,default=0)+1
    while remaining:
        todo=[remaining.pop()];component=[]
        while todo:
            a=todo.pop();component.append(a)
            for b,_ in adj[a]:
                if b in remaining:remaining.remove(b);todo.append(b)
        components.append(component)
    used=set();result=[];nextid=len(edges)
    for component in components:
        odd=sorted(v for v in component if len(adj[v])%2)
        for v in odd:
            adj[v].append((virtual,nextid));adj[virtual].append((v,nextid));nextid+=1
        todo=[virtual if odd else min(component)];path=[]
        while todo:
            v=todo[-1]
            while adj[v] and adj[v][-1][1] in used:adj[v].pop()
            if not adj[v]:path.append(todo.pop())
            else:
                w,i=adj[v].pop();used.add(i);todo.append(w)
        run=[]
        for v in reversed(path):
            if v==virtual:
                if len(run)>1:result.append(run)
                run=[]
            else:run.append(v)
        if len(run)>1:result.append(run)
        adj.pop(virtual,None)
    return result


def node_xy(node,n):
    return ((node-1)%n,(node-1)//n)


def remove_padding(day,graph):
    """Remove the points added solely to meet the former 243-dot requirement."""
    adjacency=defaultdict(set)
    for a,b in graph['edges']:adjacency[a].add(b);adjacency[b].add(a)
    for v in range(graph['original_vertices'],len(graph['locations'])):
        neighbours=list(adjacency[v])
        if len(neighbours)!=2:raise ValueError('Padding vertex is not a subdivision')
        a,b=neighbours
        adjacency[a].remove(v);adjacency[b].remove(v)
        adjacency[a].add(b);adjacency[b].add(a);del adjacency[v]
    ids={(p['x'],p['y']):p['id'] for p in day['points']}
    mapping={i:ids[(int(100+x*10/3),int(100+y*10/3))] for i,(x,y) in enumerate(graph['locations'])}
    edges={tuple(sorted((mapping[a],mapping[b]))) for a,neighbours in adjacency.items() for b in neighbours}
    return {**day,'edges':sorted(edges),'removed_padding_points':graph['subdivisions']}


def convert(day,n):
    mapped=[];displacements=[]
    for p in day['points']:
        x,y=(p['x']-100)/1000,(p['y']-100)/1000
        ix,iy=int(math.floor(x*(n-1)+.5)),int(math.floor(y*(n-1)+.5))
        mapped.append(iy*n+ix+1)
        displacements.append(math.hypot(ix/(n-1)-x,iy/(n-1)-y)*300)
    edges=set();collapsed=duplicates=0
    for a,b in day['edges']:
        a,b=mapped[a-1],mapped[b-1]
        if a==b:collapsed+=1;continue
        e=tuple(sorted((a,b)))
        if e in edges:duplicates+=1
        edges.add(e)
    paths=decompose(edges);random.Random(911+day['day']).shuffle(paths)
    strokes=[];ordered=[]
    for path in paths:
        start=len(ordered);ordered.extend([a,b] for a,b in zip(path,path[1:]))
        strokes.append(dict(id=len(strokes)+1,points=path,start_edge=start,end_edge=len(ordered)))
    active={v for e in edges for v in e}
    return dict(day=day['day'],row=day['row'],column=day['column'],grid_size=n,
                printed_reference_points=n*n,active_reference_points=len(active),source_points=243,
                edges=ordered,strokes=strokes,source_to_grid=mapped,
                collapsed_segments=collapsed,duplicate_segments=duplicates,
                max_displacement=round(max(displacements),3),
                mean_displacement=round(sum(displacements)/len(displacements),3))


def scene(days,n):
    im=Image.new('RGB',(2000,2000),'white');draw=ImageDraw.Draw(im)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1500"><rect width="1500" height="1500" fill="white"/>']
    for d in days:
        def xy(node):
            x,y=node_xy(node,n)
            return ((d['column']-1)*300+x*300/(n-1),(d['row']-1)*300+y*300/(n-1))
        for a,b in d['edges']:
            x,y=xy(a);u,v=xy(b)
            draw.line([(x*4/3,y*4/3),(u*4/3,v*4/3)],fill='#172b38',width=3)
            svg.append(f'<path d="M{x} {y}L{u} {v}" fill="none" stroke="#172b38" stroke-width="2"/>')
    return im,''.join(svg)+'</svg>'


def grid_svg(n):
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200"><rect width="1200" height="1200" fill="white"/>']
    # Axis coordinates are numbered; the dots themselves are identical everywhere.
    for i in range(n):
        p=100+i*1000/(n-1)
        out.append(f'<text x="{p}" y="77" text-anchor="middle" font-family="Arial" font-size="12">{i+1}</text><text x="77" y="{p+4}" text-anchor="middle" font-family="Arial" font-size="12">{i+1}</text>')
        if i%5==0:
            out.append(f'<path d="M{p} 100V1100 M100 {p}H1100" stroke="#e3e9e4" stroke-width="1"/>')
    for row in range(n):
        for col in range(n):out.append(f'<circle cx="{100+col*1000/(n-1)}" cy="{100+row*1000/(n-1)}" r="1.5" fill="#748579"/>')
    return ''.join(out)+'</svg>'


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    original=json.loads(SOURCE.read_text());variants={};summary={}
    graphs=json.loads((SOURCE.parent/'graphs.json').read_text())
    unpadded=[remove_padding(d,g) for d,g in zip(original['days'],graphs)]
    for n in SIZES:
        days=[convert(d,n) for d in unpadded];variants[str(n)]=days
        im,svg=scene(days,n);im.save(OUT/f'connected-{n}.png');(OUT/f'connected-{n}.svg').write_text(svg)
        (OUT/f'blank-grid-{n}.svg').write_text(grid_svg(n))
        summary[str(n)]=dict(reference_points_per_sheet=n*n,total_segments=sum(len(d['edges']) for d in days),
                            collapsed_segments=sum(d['collapsed_segments'] for d in days),
                            active_points_range=[min(d['active_reference_points'] for d in days),max(d['active_reference_points'] for d in days)],
                            max_displacement=max(d['max_displacement'] for d in days))
        rows=[]
        d=days[13]
        for s in d['strokes']:
            refs=['(%d, %d)'%(node_xy(v,n)[0]+1,node_xy(v,n)[1]+1) for v in s['points']]
            rows.append(f'<p><b>{s["id"]}.</b> '+ ' → '.join(refs)+'</p>')
        (OUT/f'tile-14-guide-{n}.html').write_text('<meta charset="utf-8"><title>Tile 14 coordinate guide</title><style>body{font:14px system-ui;max-width:900px;margin:25px auto}p{break-inside:avoid;line-height:1.6}@page{size:A4;margin:15mm}</style><h1>Tile 14 · coordinate guide</h1><p>Each pair is (column, row). Follow one row at a time, lifting your pen between rows. The blank reference grid is identical for every tile.</p>'+''.join(rows))
    bundle=dict(title='Christmas room · uniform reference grid',variants=variants,source=original)
    (OUT/'grids.json').write_text(json.dumps(bundle,indent=2))
    (OUT/'report.json').write_text(json.dumps(summary,indent=2))
    template=Path(__file__).with_name('reference_grid.html').read_text()
    (OUT/'index.html').write_text(template.replace('__DATA__',json.dumps(bundle)))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':build()
