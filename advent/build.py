"""Build the 25-sheet advent dot-to-dot and an honest assembled canvas reveal."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import shutil

import numpy as np
from PIL import Image, ImageDraw
from dot_to_dot.multistroke import draw_svg, draw_png, validate
from dot_to_dot.pipeline import place_labels
from .geometry import make_graphs, trails
from .artwork import artwork

ROOT=Path(__file__).resolve().parent.parent


def daily_data(graph):
    paths=trails(graph);random.Random(1200+graph['day']).shuffle(paths)
    lookup={};points=[];strokes=[];edges=[]
    for path in paths:
        ids=[]
        for vertex in path:
            if vertex not in lookup:
                lookup[vertex]=len(points)+1
                x,y=graph['locations'][vertex]
                points.append(dict(id=len(points)+1,x=int(100+x*10/3),y=int(100+y*10/3)))
            ids.append(lookup[vertex])
        start=len(edges);edges.extend([a,b] for a,b in zip(ids,ids[1:]))
        strokes.append(dict(id=len(strokes)+1,points=ids,start_edge=start,end_edge=len(edges)))
    expected=Counter(tuple(sorted((lookup[a],lookup[b]))) for a,b in graph['edges'])
    if Counter(tuple(sorted(e)) for e in edges)!=expected:raise ValueError('Trail decomposition changed the art')
    labels,overlaps=place_labels(np.array([(p['x'],p['y']) for p in points]))
    if overlaps:
        labels,overlaps=place_labels(np.array([(p['x'],p['y']) for p in points]),radii=(12,18,25,32,42,52))
    for p,l in zip(points,labels):p['label']=l
    if overlaps:raise ValueError(f'Day {graph["day"]}: overlapping number labels {overlaps}')
    row,col=divmod(graph['day']-1,5)
    data=dict(schema_version=2,mode='multi_stroke',width=1200,height=1200,point_count=243,closed=False,
              day=graph['day'],row=row+1,column=col+1,crop_bounds=[100,100,1100,1100],
              points=points,strokes=strokes,edges=edges,
              rules='Follow each listed stroke sequence; lift the pen between rows. Shared dots may be revisited. Numbers are not one global sequence.')
    report=validate(data)
    report.update(label_overlap_pairs=overlaps,original_vertices=graph['original_vertices'],
                  subdivided_segments=graph['subdivisions'],omitted_segments=graph['omitted_texture_segments'])
    return data,report


def scene_xy(data,p):
    return ((data['column']-1)*300+(p['x']-100)*.3,(data['row']-1)*300+(p['y']-100)*.3)


def scene_svg(days,dots=False,grid=False):
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1500 1500" width="1500" height="1500"><rect width="1500" height="1500" fill="white"/>']
    for d in days:
        xy=[scene_xy(d,p) for p in d['points']]
        if not dots:
            for a,b in d['edges']:
                x,y=xy[a-1];u,v=xy[b-1]
                out.append(f'<path d="M{x} {y}L{u} {v}" stroke="#172b38" stroke-width="1.2" fill="none"/>')
        else:
            for x,y in xy:out.append(f'<circle cx="{x}" cy="{y}" r="1" fill="#172b38"/>')
    if grid:
        for i in range(1,5):out.append(f'<path d="M{i*300} 0V1500 M0 {i*300}H1500" stroke="#bd8458" stroke-dasharray="5 5" fill="none"/>')
        for d in days:out.append(f'<text x="{(d["column"]-1)*300+12}" y="{(d["row"]-1)*300+28}" font-size="23" fill="#994f22">{d["day"]}</text>')
    return ''.join(out)+'</svg>'


def scene_png(days,dots=False):
    im=Image.new('RGB',(2000,2000),'white');draw=ImageDraw.Draw(im)
    for d in days:
        xy=[tuple(v*4/3 for v in scene_xy(d,p)) for p in d['points']]
        if dots:
            for x,y in xy:draw.ellipse((x-1.4,y-1.4,x+1.4,y+1.4),fill='#172b38')
        else:
            for a,b in d['edges']:draw.line((xy[a-1],xy[b-1]),fill='#172b38',width=2)
    return im


STYLE='''<style>*{box-sizing:border-box}body{font:14px system-ui;color:#172b38;max-width:980px;margin:24px auto}h1{font-size:23px}h2{font-size:18px}p{line-height:1.5}svg{display:block;width:100%;height:auto}.sheet{break-after:page}.sheet:last-child{break-after:auto}.pattern{position:relative}.crop{position:absolute;inset:8.3333%;border:1px dashed #bd8458;pointer-events:none}.sequences{columns:2;column-gap:30px;font-size:12px;line-height:1.6}.seq{break-inside:avoid;margin:0 0 9px}a{color:#315f51}@page{size:A4;margin:12mm}@media print{body{margin:0;max-width:none}.noprint{display:none}.sheet{height:270mm;overflow:hidden}h1{margin:0 0 4mm}.pattern{width:186mm;height:186mm}.sequences{font-size:9px;line-height:1.45}}</style>'''


def write_prints(out,days):
    puzzles=[];answers=[];instructions=[]
    for d in days:
        n=d['day'];position=f'row {d["row"]}, column {d["column"]}'
        for target,lines in [(puzzles,False),(answers,True)]:
            svg=draw_svg(d,lines,not lines,not lines)
            target.append(f'<section class="sheet"><h1>December {n} · {position}</h1><p>243 dots · {len(d["strokes"])} strokes. Follow the separate stroke guide; lift your pen between rows.</p><div class="pattern">{svg}<div class="crop"></div></div><p>After drawing, trim on the dashed square (155 mm). Keep this page upright and assemble rows 1–5, left to right. Neighbouring sheets share their edge dots.</p></section>')
        rows=''.join(f'<p class="seq"><b>{s["id"]}.</b> '+ ' → '.join(map(str,s['points']))+'</p>' for s in d['strokes'])
        instructions.append(f'<section class="sheet"><h1>December {n} · stroke guide</h1><p>Connect only the numbers listed in each row. Lift the pen between rows. Shared dots may be revisited.</p><div class="sequences">{rows}</div></section>')
    for name,pages in [('puzzles',puzzles),('solutions',answers),('stroke-guides',instructions)]:
        (out/f'{name}.html').write_text(f'<!doctype html><meta charset="utf-8"><title>Advent {name}</title>{STYLE}<p class="noprint"><a href="index.html">Calendar</a> · Print at 100%, A4, no browser headers.</p>'+''.join(pages))
    (out/'assembly.html').write_text(f'<!doctype html><meta charset="utf-8"><title>Advent assembly map</title>{STYLE}<h1>Advent village · assembly map</h1><p>25 squares, 5 rows × 5 columns. Top left is December 1, bottom right is December 25. Trim each finished sheet to its dashed square. Each square is 155 mm at 100% A4 printing; the assembled scene is 775 × 775 mm.</p>'+scene_svg(days,grid=True))


def build(output):
    out=Path(output)
    if out.exists():raise ValueError('Choose a fresh output directory')
    graphs,metadata=make_graphs();out.mkdir(parents=True)
    days=[];reports=[]
    template=(ROOT/'dot_to_dot/multistroke.html').read_text()
    for graph in graphs:
        data,report=daily_data(graph);days.append(data);reports.append(report)
        n=data['day'];directory=out/f'day-{n:02}';directory.mkdir()
        (directory/'points.json').write_text(json.dumps(data,indent=2)+'\n')
        (directory/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
        for name,lines,numbers,dots in [('source',True,False,False),('connected',True,True,True),('answer',True,False,True),('dots',False,True,True),('dots-unlabelled',False,False,True)]:
            (directory/f'{name}.svg').write_text(draw_svg(data,lines,numbers,dots))
            draw_png(data,lines,numbers,dots).save(directory/f'{name}.png')
        source='data:image/png;base64,'+base64.b64encode((directory/'source.png').read_bytes()).decode()
        html=template.replace('__SOURCE__',source).replace('__DATA__',json.dumps(data))
        html=html.replace('Winter mystery · adult dot-to-dot',f'December {n} · Advent dot-to-dot').replace('One dot at a time.',f'December {n}.')
        html=html.replace('A hidden-picture drawing experiment',f'<a href="../index.html">← Advent calendar</a> · Row {data["row"]}, column {data["column"]}')
        (directory/'index.html').write_text(html)
        rows=''.join(f'<p class="seq"><b>{s["id"]}.</b> '+ ' → '.join(map(str,s['points']))+'</p>' for s in data['strokes'])
        (directory/'instructions.html').write_text(f'<!doctype html><meta charset="utf-8"><title>December {n} strokes</title>{STYLE}<h1>December {n} · stroke guide</h1><p>Lift the pen between rows; shared dots can be revisited.</p><div class="sequences">{rows}</div>')
        print(f'Day {n:02}: 243 dots, {len(data["edges"])} lines, {len(data["strokes"])} strokes; labels clear',flush=True)
    calendar=dict(schema_version=1,title='The Christmas village',rows=5,columns=5,printed_dot_count=6075,days=days)
    (out/'calendar.json').write_text(json.dumps(calendar,indent=2)+'\n')
    (out/'authored-artwork.json').write_text(json.dumps(dict(paths=artwork()),indent=2)+'\n')
    for name,dots in [('full-scene',False),('all-dots',True)]:
        (out/f'{name}.svg').write_text(scene_svg(days,dots));scene_png(days,dots).save(out/f'{name}.png')
    (out/'index.html').write_text((Path(__file__).with_name('calendar.html')).read_text().replace('__DATA__',json.dumps(calendar)))
    reference=ROOT/'inputs/advent/winter-village-reference.png'
    shutil.copyfile(reference,out/'generated-reference.png')
    shutil.copyfile(ROOT/'inputs/advent/winter-village-prompt.txt',out/'source-prompt.txt')
    metadata.update(created_at=datetime.now(timezone.utc).isoformat(),days=25,printed_dot_count=6075,
                    total_segments=sum(len(d['edges']) for d in days),reports=reports,
                    reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                    note='6075 printed locations; seam dots are repeated on neighbouring sheets. No raster answer layer. Concealment and daily artistic balance require human review.')
    (out/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    write_prints(out,days)
    from .review import write_review
    write_review(out)
    print(f'Calendar: {out}/index.html',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    build(parser.parse_args().output)
