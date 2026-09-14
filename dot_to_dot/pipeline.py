import base64
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

SIZE = 1200


def extract(path):
    with Image.open(path) as source:
        gray = np.asarray(source.convert('L'))
    binary = (gray < 160).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError('No dark outline found')
    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) < gray.size * .05:
        raise ValueError('Source needs a large closed outline, not disconnected/open strokes')
    points = contour[:, 0, :].astype(float)
    low, high = points.min(axis=0), points.max(axis=0)
    factor = 1040 / max(high-low)
    points = (points-(low+high)/2)*factor+SIZE/2
    # Stable start: lowest left hoof, keeping the head as a later reveal.
    start = np.argmin(points[:, 0] - points[:, 1]*.25)
    points = np.roll(points, -start, axis=0)
    return points, {'threshold':160, 'external_contours':len(contours),
                    'extraction':'Largest external contour; interior strokes are not part of the puzzle',
                    'source_to_canvas_scale':float(factor)}


def sample(contour, count):
    if count < 12 or count > 1000:
        raise ValueError('Point count must be between 12 and 1000')
    # Retain shape corners, then divide long edges until the exact budget is met.
    epsilon = 1.5
    while True:
        simplified = cv2.approxPolyDP(contour.astype(np.float32).reshape(-1,1,2), epsilon, True)[:,0,:]
        if len(simplified) <= count * .7:
            break
        epsilon *= 1.15
    lengths = np.linalg.norm(np.roll(simplified,-1,axis=0)-simplified,axis=1)
    parts = np.ones(len(simplified), dtype=int)
    for _ in range(count-len(simplified)):
        parts[np.argmax(lengths/parts)] += 1
    result = []
    for i, n in enumerate(parts):
        a, b = simplified[i], simplified[(i+1)%len(simplified)]
        result.extend(a+(b-a)*(j/n) for j in range(n))
    return np.asarray(result, dtype=float), float(epsilon)


def crossings(points):
    def orient(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on_segment(a,b,c):
        return abs(orient(a,b,c)) < 1e-8 and min(a[0],b[0])-1e-8 <= c[0] <= max(a[0],b[0])+1e-8 and min(a[1],b[1])-1e-8 <= c[1] <= max(a[1],b[1])+1e-8
    result = []
    n = len(points)
    for i in range(n):
        a,b = points[i], points[(i+1)%n]
        for j in range(i+2,n):
            if i == 0 and j == n-1:
                continue
            c,d = points[j], points[(j+1)%n]
            if (orient(a,b,c)*orient(a,b,d) < -1e-8 and orient(c,d,a)*orient(c,d,b) < -1e-8) or any((on_segment(a,b,c),on_segment(a,b,d),on_segment(c,d,a),on_segment(c,d,b))):
                result.append([i+1,j+1])
    return result


def align(points, spacing):
    if not 4 <= spacing <= 40:
        raise ValueError('Grid spacing must be between 4 and 40 canvas units')
    axis = np.arange(60, SIZE-59, spacing)
    grid = np.array([(x,y) for y in axis for x in axis])
    costs = cdist(points, grid, metric='sqeuclidean')
    _, indices = linear_sum_assignment(costs)
    targets = grid[indices]
    # Grid snapping is subordinate to keeping the original path simple.
    for strength in (1, .85, .7, .55, .4, .25, 0):
        trial = points + (targets-points)*strength
        distances = cdist(trial,trial)
        np.fill_diagonal(distances,np.inf)
        if distances.min() >= 5 and not crossings(trial):
            return trial, dict(spacing=spacing, origin=[60,60], strength=strength,
                              mean_displacement=float(np.linalg.norm(trial-points,axis=1).mean()),
                              max_displacement=float(np.linalg.norm(trial-points,axis=1).max()))
    raise ValueError('Cannot produce a non-crossing, separated route; simplify the source')


def place_labels(points, radii=(12,18,25,32)):
    font = ImageFont.load_default(size=11)
    boxes, labels = [], [None]*len(points)
    distances = cdist(points,points)
    np.fill_diagonal(distances,np.inf)
    # Place the most crowded labels first.
    for i in np.argsort(distances.min(axis=1)):
        p = points[i]
        text = str(i+1)
        width = font.getlength(text)+2
        height = 12
        best = None
        for radius in radii:
            for angle in np.arange(0, 2*math.pi, math.pi/8):
                center = p+radius*np.array([math.cos(angle), math.sin(angle)])
                box = [center[0]-width/2, center[1]-height/2, center[0]+width/2, center[1]+height/2]
                if min(box) < 8 or box[2] > SIZE-8 or box[3] > SIZE-8:
                    continue
                overlaps = sum(max(0,min(box[2],b[2])-max(box[0],b[0])) *
                               max(0,min(box[3],b[3])-max(box[1],b[1])) for b in boxes)
                hits = np.sum((points[:,0]>box[0]-3)&(points[:,0]<box[2]+3)&
                              (points[:,1]>box[1]-3)&(points[:,1]<box[3]+3))
                score = overlaps*1000 + hits*10000 + radius
                if best is None or score < best[0]:
                    best = (score,box,center)
        _,box,center = best
        boxes.append(box)
        labels[i] = {'x':round(float(center[0]),3),'y':round(float(center[1]),3),'box':[round(float(v),3) for v in box]}
    overlap_pairs = []
    for i,a in enumerate(labels):
        a=a['box']
        for j in range(i+1,len(labels)):
            b=labels[j]['box']
            if min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1]):
                overlap_pairs.append([i+1,j+1])
    return labels, overlap_pairs


def svg(data, lines=False, labels=True):
    points=data['points']
    chunks=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200"><rect width="1200" height="1200" fill="white"/>']
    if lines:
        coords=' '.join(f'{p["x"]},{p["y"]}' for p in points+[points[0]])
        chunks.append(f'<polyline points="{coords}" fill="none" stroke="#182b3b" stroke-width="2" stroke-linejoin="round"/>')
    for p in points:
        chunks.append(f'<circle cx="{p["x"]}" cy="{p["y"]}" r="2.1" fill="#17212b"/>')
        if labels:
            label=p['label']
            chunks.append(f'<text x="{label["x"]}" y="{label["y"]}" text-anchor="middle" dominant-baseline="central" font-family="Arial,sans-serif" font-size="11" fill="#394553">{p["id"]}</text>')
    return ''.join(chunks)+'</svg>'


def raster(data, lines=False, labels=True):
    image=Image.new('RGB',(SIZE,SIZE),'white')
    draw=ImageDraw.Draw(image)
    xy=[(p['x'],p['y']) for p in data['points']]
    if lines:
        draw.line(xy+[xy[0]],fill='#182b3b',width=2)
    font=ImageFont.load_default(size=11)
    for p in data['points']:
        x,y=p['x'],p['y']
        draw.ellipse((x-2,y-2,x+2,y+2),fill='#17212b')
        if labels:
            label=p['label']
            draw.text((label['x'],label['y']),str(p['id']),font=font,anchor='mm',fill='#394553')
    return image


def validate(data):
    points=data['points']
    n=data['point_count']
    if len(points)!=n or [p['id'] for p in points]!=list(range(1,n+1)):
        raise ValueError('Point count or numbering is invalid')
    xy=np.array([(p['x'],p['y']) for p in points])
    if len(set(map(tuple,xy)))!=n or not np.isfinite(xy).all() or xy.min()<0 or xy.max()>SIZE:
        raise ValueError('Coordinates are invalid or duplicated')
    expected=[[i,i+1] for i in range(1,n)]+[[n,1]]
    if data['edges']!=expected:
        raise ValueError('Edges must connect every point in order and close back to 1')
    intersections=crossings(xy)
    if intersections:
        raise ValueError(f'Path has crossings: {intersections}')
    distances=cdist(xy,xy)
    np.fill_diagonal(distances,np.inf)
    if distances.min()<5:
        raise ValueError('Dots are too close')
    return {'status':'passed','points':n,'segments':n,'closed':True,'crossings':0,
            'minimum_dot_spacing':round(float(distances.min()),3)}


def build(source, output, count=243, spacing=18, prompt=None):
    source,output=Path(source),Path(output)
    if output.exists():
        raise ValueError('Output exists; choose a new directory')
    contour,extraction=extract(source)
    sampled,epsilon=sample(contour,count)
    points,grid=align(sampled,spacing)
    labels,overlaps=place_labels(points)
    data={'schema_version':1,'width':SIZE,'height':SIZE,'point_count':count,'closed':True,
          'points':[dict(id=i+1,x=round(float(p[0]),3),y=round(float(p[1]),3),label=labels[i]) for i,p in enumerate(points)],
          'edges':[[i,i+1] for i in range(1,count)]+[[count,1]],'grid':grid}
    result=validate(data)
    metadata={'created_at':datetime.now(timezone.utc).isoformat(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'source_generation':{'tool':'built-in image_gen','model':None,'prompt':Path(prompt).read_text() if prompt else None},
              'extraction':extraction,'approximation_epsilon':epsilon,'grid':grid,'validation':result,
              'label_overlap_pairs':overlaps,'camouflage':'Near-grid alignment only; silhouette may still be recognisable. No decoy dots.'}
    output.mkdir(parents=True)
    shutil.copyfile(source,output/'source.png')
    (output/'points.json').write_text(json.dumps(data,indent=2)+'\n')
    (output/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    for name,lines,numbered in [('dots',False,True),('connected',True,True),('answer',True,False)]:
        (output/f'{name}.svg').write_text(svg(data,lines,numbered))
        raster(data,lines,numbered).save(output/f'{name}.png')
    template=Path(__file__).with_name('viewer.html').read_text().replace('243', str(count))
    image='data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()
    template=template.replace('__SOURCE__',image).replace('__DATA__',json.dumps(data).replace('</','<\\/'))
    (output/'index.html').write_text(template)
    print(json.dumps({'output':str(output),'grid':grid,'validation':result,'label_overlaps':len(overlaps)},indent=2))
