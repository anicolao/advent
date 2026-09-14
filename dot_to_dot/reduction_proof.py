"""Experimental source-tracing proof, not the authored village production pipeline.

Run from repository root: nix develop -c python -m dot_to_dot.reduction_proof
The raster is only read. Vector exports visualize a lossy skeleton simplification.
"""
import cv2, numpy as np, math, json
from collections import defaultdict
from pathlib import Path
from advent.geometry import clip
from PIL import Image,ImageDraw
src='inputs/art-candidates/01-nativity-stable.png'
im=cv2.imread(src,0);im=cv2.resize(im,(1500,1500));ink=(im<130).astype('uint8')*255
sk=cv2.ximgproc.thinning(ink)>0
xy=np.argwhere(sk)[:,::-1];index=np.full(sk.shape,-1,int);index[xy[:,1],xy[:,0]]=np.arange(len(xy))
adj=defaultdict(list)
for i,(x,y) in enumerate(xy):
 for dx,dy in [(1,0),(0,1),(1,1),(-1,1)]:
  xx,yy=x+dx,y+dy
  if not(0<=xx<1500 and 0<=yy<1500) or not sk[yy,xx]:continue
  if dx and dy and (sk[y,xx] or sk[yy,x]):continue
  j=int(index[yy,xx]);adj[i].append(j);adj[j].append(i)
used=set();paths=[]
def walk(a,b):
 p=[a];last=a;cur=b;used.add(tuple(sorted((a,b))))
 while True:
  p.append(cur)
  if len(adj[cur])!=2:break
  nxt=next(v for v in adj[cur] if v!=last)
  e=tuple(sorted((cur,nxt)))
  if e in used:break
  used.add(e);last,cur=cur,nxt
 return xy[p].astype(float)
for a in sorted(adj,key=lambda x:len(adj[x])==2):
 for b in adj[a]:
  if tuple(sorted((a,b))) not in used:paths.append(walk(a,b))
print('paths',len(paths),flush=True)
# Preserve spatially continuous chains, never cluster nearby unrelated strokes.
output=[];preview=Image.new('RGB',(2000,2000),'white');draw=ImageDraw.Draw(preview)
for day in range(25):
 r,c=divmod(day,5);cand=[]
 for path in paths:
  if len(path)<6:continue
  if path[:,0].max()<c*300 or path[:,0].min()>(c+1)*300 or path[:,1].max()<r*300 or path[:,1].min()>(r+1)*300:continue
  simp=cv2.approxPolyDP(path.astype('float32'),1.7,False)[:,0,:]
  seg=[v for a,b in zip(simp,simp[1:]) if (v:=clip(a,b,c*300,r*300))]
  if seg:
   length=sum(math.dist(a,b) for a,b in seg)
   cand.append((length,seg))
 cand.sort(reverse=True,key=lambda item:item[0]);lookup={};edges=set()
 for length,seg in cand:
  pts={p for e in seg for p in e};new=pts-set(lookup)
  if len(lookup)+len(new)>243:continue
  for a,b in seg:
   for p in (a,b):
    if p not in lookup:lookup[p]=len(lookup)
   edges.add(tuple(sorted((lookup[a],lookup[b]))))
 loc=[None]*len(lookup)
 for p,i in lookup.items():loc[i]=p
 initial_vertices=len(loc)
 while len(loc)<243:
  for a,b in sorted(edges,key=lambda e:math.dist(loc[e[0]],loc[e[1]]),reverse=True):
   mid=tuple(3*round((u+v)/6) for u,v in zip(loc[a],loc[b]))
   if mid in lookup or 0 in mid or 300 in mid:continue
   v=len(loc);loc.append(mid);lookup[mid]=v;edges.remove((a,b));edges.update([tuple(sorted((a,v))),tuple(sorted((v,b)))]);break
  else:raise ValueError(day)
 for a,b in edges:draw.line([((loc[v][0]+c*300)*4/3,(loc[v][1]+r*300)*4/3) for v in (a,b)],fill='#172b38',width=2)
 output.append(dict(day=day+1,locations=loc,edges=sorted(edges),original_vertices=initial_vertices,subdivisions=243-initial_vertices))
out=Path('runs/nativity-reduction-proof');out.mkdir(parents=True,exist_ok=True)
preview.save(out/'reduced.png');(out/'graphs.json').write_text(json.dumps(output))
from advent.build import daily_data,scene_svg,scene_png
from dot_to_dot.multistroke import draw_svg,draw_png
import base64
reports=[];days=[]
template=Path('dot_to_dot/multistroke.html').read_text()
for g in output:
 g.update(locations=np.array(g['locations']),edges=set(map(tuple,g['edges'])),omitted_texture_segments=None)
 d,report=daily_data(g);days.append(d);reports.append(report)
 folder=out/f'day-{d["day"]:02}';folder.mkdir(exist_ok=True)
 (folder/'points.json').write_text(json.dumps(d,indent=2))
 for name,lines,numbers,dots in [('source',True,False,False),('connected',True,True,True),('dots',False,True,True)]:
  (folder/f'{name}.svg').write_text(draw_svg(d,lines,numbers,dots));draw_png(d,lines,numbers,dots).save(folder/f'{name}.png')
 encoded='data:image/png;base64,'+base64.b64encode((folder/'source.png').read_bytes()).decode()
 html=template.replace('__SOURCE__',encoded).replace('__DATA__',json.dumps(d))
 html=html.replace('One dot at a time.',f'Reduction proof · tile {d["day"]}')
 html=html.replace('A hidden-picture drawing experiment','<a href="../index.html">← Source reduction comparison</a>')
 (folder/'index.html').write_text(html)
 seq=''.join('<p><b>'+str(s['id'])+'.</b> '+ ' → '.join(map(str,s['points']))+'</p>' for s in d['strokes'])
 (folder/'instructions.html').write_text('<meta charset="utf-8"><title>Stroke guide</title><h1>Lift your pen between rows</h1>'+seq)
 print(f'Tile {d["day"]}: 243 used dots, {len(d["edges"])} segments',flush=True)
(out/'reduced.svg').write_text(scene_svg(days));scene_png(days).save(out/'reduced.png')
(out/'dots.svg').write_text(scene_svg(days,True));scene_png(days,True).save(out/'dots.png')
(out/'calendar.json').write_text(json.dumps(dict(days=days,printed_dot_count=6075),indent=2))
# Counts and loss are measured, not inferred from the appearance of the output.
report=dict(status='experimental; not accepted artwork',points_per_tile=243,tile_count=25,printed_locations=6075,
            source_skeleton_pixels=int(sk.sum()),source_chains=len(paths),threshold=130,rdp_epsilon=1.7,snap_spacing=3,
            limitations=['Fine detail and facial features are lost','Independent tile budgets can drop continuations at seams','No guarantee of concealment','This is automatic tracing, unlike the authored village adaptation'],validation=reports)
(out/'validation.json').write_text(json.dumps(report,indent=2))
print('Reduction proof exported',flush=True)
