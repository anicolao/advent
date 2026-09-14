"""Make a sparse-vertex, multi-stroke adult puzzle from authored vector art."""
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
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial.distance import cdist

from .pipeline import place_labels
from .winter_scene import artwork


def validate(data):
    n=data['point_count'];points=data['points']
    if n!=243 or len(points)!=n or [p['id'] for p in points]!=list(range(1,n+1)):
        raise ValueError('Expected exactly 243 numbered points')
    xy=[(p['x'],p['y']) for p in points]
    if len(set(xy))!=n or any(not(0<x<1200 and 0<y<1200) for x,y in xy):
        raise ValueError('Point locations must be unique and on the page')
    edges=[];visited=set()
    for i,stroke in enumerate(data['strokes']):
        ids=stroke['points']
        if stroke['id']!=i+1 or len(ids)<2 or any(p<1 or p>n for p in ids):
            raise ValueError('Invalid stroke IDs')
        if stroke['start_edge']!=len(edges):raise ValueError('Incorrect stroke boundary')
        visited.update(ids)
        edges.extend([a,b] for a,b in zip(ids,ids[1:]))
        if stroke['end_edge']!=len(edges):raise ValueError('Incorrect stroke end')
    if edges!=data['edges']:raise ValueError('Edges disagree with strokes: unexpected connector')
    if visited!=set(range(1,n+1)):raise ValueError('Unused/decoy point')
    if any(a==b for a,b in edges):raise ValueError('Zero-length segment')
    d=cdist(xy,xy);np.fill_diagonal(d,np.inf)
    if d.min()<10:raise ValueError('Dots are too close for this puzzle')
    return dict(status='passed',points=n,segments=len(edges),strokes=len(data['strokes']),
                pen_lifts=len(data['strokes'])-1,minimum_dot_spacing=round(float(d.min()),3),
                all_points_used=True,phantom_connectors=0)


def draw_svg(data, lines=False, numbers=True, dots=True):
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200"><rect width="1200" height="1200" fill="white"/>']
    if lines:
        for a,b in data['edges']:
            p,q=data['points'][a-1],data['points'][b-1]
            out.append(f'<line x1="{p["x"]}" y1="{p["y"]}" x2="{q["x"]}" y2="{q["y"]}" stroke="#172b38" stroke-width="2"/>')
    for p in data['points']:
        if dots:out.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="2.2" fill="#172b38"/>')
        if numbers:
            l=p['label']
            out.append(f'<text x="{l["x"]}" y="{l["y"]}" text-anchor="middle" dominant-baseline="central" font-family="Arial,sans-serif" font-size="11" fill="#394553">{p["id"]}</text>')
    return ''.join(out)+'</svg>'


def draw_png(data,lines=False,numbers=True,dots=True):
    image=Image.new('RGB',(1200,1200),'white');draw=ImageDraw.Draw(image)
    if lines:
        for a,b in data['edges']:
            p,q=data['points'][a-1],data['points'][b-1]
            draw.line([(p['x'],p['y']),(q['x'],q['y'])],fill='#172b38',width=2)
    for p in data['points']:
        if dots:draw.ellipse((p['x']-2,p['y']-2,p['x']+2,p['y']+2),fill='#172b38')
        if numbers:
            l=p['label'];draw.text((l['x'],l['y']),str(p['id']),font=ImageFont.load_default(size=11),anchor='mm',fill='#394553')
    return image


def build(output):
    output=Path(output)
    if output.exists():raise ValueError('Output already exists')
    original=artwork()
    # Order non-outline fragments first. Labels are assigned by first visit, not position.
    order=list(range(len(original)));random.Random(243).shuffle(order)
    order.remove(0);order.append(0)
    lookup={};points=[];strokes=[];edges=[]
    for index in order:
        art=original[index];ids=[]
        for xy in art['xy']:
            xy=tuple(xy)
            if xy not in lookup:
                lookup[xy]=len(points)+1;points.append({'id':len(points)+1,'x':xy[0],'y':xy[1]})
            ids.append(lookup[xy])
        start=len(edges);edges.extend([a,b] for a,b in zip(ids,ids[1:]))
        strokes.append(dict(id=len(strokes)+1,points=ids,start_edge=start,end_edge=len(edges)))
    labels,overlaps=place_labels(np.array([(p['x'],p['y']) for p in points]))
    for p,l in zip(points,labels):p['label']=l
    data=dict(schema_version=2,mode='multi_stroke',width=1200,height=1200,point_count=len(points),
              closed=False,points=points,strokes=strokes,edges=edges,
              rules='Follow each stroke’s listed numbers, then lift the pen. Shared dots may be revisited. Do not connect consecutive labels unless listed.')
    result=validate(data)
    if overlaps:raise ValueError(f'Number labels overlap: {overlaps}')
    output.mkdir(parents=True)
    (output/'points.json').write_text(json.dumps(data,indent=2)+'\n')
    (output/'artwork.json').write_text(json.dumps({'strokes':original},indent=2)+'\n')
    for name,lines,numbers,dots in [('source',True,False,False),('connected',True,True,True),('answer',True,False,True),('dots',False,True,True),('dots-unlabelled',False,False,True)]:
        (output/f'{name}.svg').write_text(draw_svg(data,lines,numbers,dots))
        draw_png(data,lines,numbers,dots).save(output/f'{name}.png')
    reference=Path('inputs/dot-to-dot/winter-window.png')
    shutil.copyfile(reference,output/'generated-reference.png')
    metadata=dict(created_at=datetime.now(timezone.utc).isoformat(),validation=result,label_overlap_pairs=overlaps,
                  source='Authored straight-line adaptation of generated winter-window reference; artwork.json is the final vector source',
                  generated_reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                  source_generator='built-in image_gen',prompt=Path('inputs/dot-to-dot/winter-window-prompt.txt').read_text(),
                  note='No automatically sampled silhouette points, no filler dots, no forced uniform grid. Concealment requires human review.')
    (output/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    template=Path(__file__).with_name('multistroke.html').read_text()
    source='data:image/png;base64,'+base64.b64encode((output/'source.png').read_bytes()).decode()
    (output/'index.html').write_text(template.replace('__SOURCE__',source).replace('__DATA__',json.dumps(data)))
    rows=''.join(f'<tr><th>{s["id"]}</th><td>{" → ".join(map(str,s["points"]))}</td></tr>' for s in strokes)
    (output/'instructions.html').write_text('<!doctype html><meta charset="utf-8"><title>Stroke instructions</title><style>body{font:14px system-ui;max-width:850px;margin:30px auto}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}tr{break-inside:avoid}@page{size:A4;margin:15mm}</style><h1>Winter mystery: stroke instructions</h1><p>243 numbered locations. Follow each row in order, lifting the pen between rows. Shared dots can be used more than once. Never draw a line between different rows.</p><table><tr><th>Stroke</th><th>Connect these numbers</th></tr>'+rows+'</table>')
    print(json.dumps(dict(output=str(output),**result),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    build(parser.parse_args().output)
