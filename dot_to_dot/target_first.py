"""Target-first source reduction; preserve connected contours before fitting budgets."""
import cv2
import numpy as np
import math
import json
from pathlib import Path
from collections import defaultdict
from advent.geometry import clip


def graphs(source):
 im=cv2.imread(str(source),0)
 if im is None:raise ValueError('Unreadable source')
 im=cv2.resize(im,(1500,1500));ink=(im<130).astype('uint8')*255
 sk=cv2.ximgproc.thinning(ink)>0
 xy=np.argwhere(sk)[:,::-1];index=np.full(sk.shape,-1,int);index[xy[:,1],xy[:,0]]=np.arange(len(xy));adj=defaultdict(list)
 for i,(x,y) in enumerate(xy):
  for dx,dy in [(1,0),(0,1),(1,1),(-1,1)]:
   xx,yy=x+dx,y+dy
   if not(0<=xx<1500 and 0<=yy<1500) or not sk[yy,xx]:continue
   if dx and dy and (sk[y,xx] or sk[yy,x]):continue
   j=int(index[yy,xx]);adj[i].append(j);adj[j].append(i)
 # Consolidate only adjacent branch pixels, never nearby unrelated contours.
 branches={i for i in adj if len(adj[i])>2};centres={};remaining=set(branches)
 while remaining:
  stack=[remaining.pop()];group=[]
  while stack:
   i=stack.pop();group.append(i)
   for j in adj[i]:
    if j in remaining:remaining.remove(j);stack.append(j)
  centre=xy[group].mean(axis=0)
  for i in group:centres[i]=centre
 used=set();paths=[]
 def walk(a,b):
  p=[a];last=a;cur=b;used.add(tuple(sorted((a,b))))
  while True:
   p.append(cur)
   if len(adj[cur])!=2:break
   nxt=next(v for v in adj[cur] if v!=last);e=tuple(sorted((cur,nxt)))
   if e in used:break
   used.add(e);last,cur=cur,nxt
  coords=xy[p].astype(float)
  if p[0] in centres:coords[0]=centres[p[0]]
  if p[-1] in centres:coords[-1]=centres[p[-1]]
  return coords
 for a in sorted(adj,key=lambda i:len(adj[i])==2):
  for b in adj[a]:
   if tuple(sorted((a,b))) not in used:
    path=walk(a,b)
    if np.linalg.norm(np.diff(path,axis=0),axis=1).sum()>=3:paths.append(path)
 # Small filled facial marks vanish under thinning. Preserve their ink extents
 # as tiny closed contours, which still have real drawable edges and no decoys.
 n,labels,stats,cents=cv2.connectedComponentsWithStats(ink)
 for i in range(1,n):
  x,y,w,h,area=stats[i]
  if 6<=area<=160 and w<=18 and h<=18 and sk[labels==i].sum()<6:
   cx,cy=cents[i];rx=max(3,w/2);ry=max(3,h/2)
   paths.append(np.array([(cx-rx,cy),(cx,cy-ry),(cx+rx,cy),(cx,cy+ry),(cx-rx,cy)]))
 result=[];details=[]
 for day in range(25):
  r,c=divmod(day,5);local=[]
  for p in paths:
   if p[:,0].max()<c*300 or p[:,0].min()>(c+1)*300 or p[:,1].max()<r*300 or p[:,1].min()>(r+1)*300:continue
   local.append(p)
  # Increase tolerance before considering any omission. Shared seam strokes use
  # one fixed tolerance so both sides inherit the same crossing point.
  def candidates(epsilon):
   out=[]
   for p in local:
    crosses=(p[:,0].min()<c*300 or p[:,0].max()>(c+1)*300 or p[:,1].min()<r*300 or p[:,1].max()>(r+1)*300)
    simp=cv2.approxPolyDP(p.astype('float32'),1.2 if crosses else epsilon,False)[:,0,:]
    seg=[v for a,b in zip(simp,simp[1:]) if (v:=clip(a,b,c*300,r*300))]
    if seg:out.append((crosses,sum(math.dist(a,b) for a,b in seg),seg))
   return out
  for epsilon in [1.2,1.8,2.6,3.6,5.0,7.0]:
   cand=candidates(epsilon);vertices={p for _,_,seg in cand for e in seg for p in e}
   if len(vertices)<=243:break
  cand.sort(key=lambda item:(not item[0],-item[1]));lookup={};edges=set();omitted=0
  for crosses,length,seg in cand:
   new={p for e in seg for p in e}-set(lookup)
   if len(lookup)+len(new)>243:
    if crosses:raise ValueError(f'Seam budget exhausted on tile {day+1}')
    omitted+=len(seg);continue
   for a,b in seg:
    for p in (a,b):
     if p not in lookup:lookup[p]=len(lookup)
    edges.add(tuple(sorted((lookup[a],lookup[b]))))
  loc=[None]*len(lookup)
  for p,i in lookup.items():loc[i]=p
  initial=len(loc)
  while len(loc)<243:
   for a,b in sorted(edges,key=lambda e:math.dist(loc[e[0]],loc[e[1]]),reverse=True):
    mid=tuple((u+v)/2 for u,v in zip(loc[a],loc[b]))
    if min(math.dist(mid,p) for p in loc)<3.4 or 0 in mid or 300 in mid:continue
    v=len(loc);loc.append(mid);lookup[mid]=v;edges.remove((a,b));edges.update([tuple(sorted((a,v))),tuple(sorted((v,b)))]);break
   else:raise ValueError(f'Cannot allocate 243 separated locations on tile {day+1}')
  result.append(dict(day=day+1,locations=np.array(loc),edges=edges,original_vertices=initial,subdivisions=243-initial,omitted_texture_segments=omitted))
  details.append(dict(day=day+1,epsilon=epsilon,original_vertices=initial,omitted_segments=omitted))
 return result,dict(source_chains=len(paths),skeleton_pixels=int(sk.sum()),tiles=details)


if __name__=='__main__':
 from PIL import Image,ImageDraw
 gs,report=graphs('inputs/target-first/christmas-room-refined.png');out=Path('runs/christmas-room-proof');out.mkdir(exist_ok=True,parents=True)
 im=Image.new('RGB',(2000,2000),'white');d=ImageDraw.Draw(im)
 for g in gs:
  r,c=divmod(g['day']-1,5)
  for a,b in g['edges']:d.line([tuple((v+offset)*4/3 for v,offset in zip(g['locations'][i],[c*300,r*300])) for i in (a,b)],fill='#172b38',width=2)
 im.save(out/'trial-reduced.png')
 (out/'trace-report.json').write_text(json.dumps(report,indent=2))
 (out/'graphs.json').write_text(json.dumps([{**g,'locations':g['locations'].tolist(),'edges':sorted(g['edges'])} for g in gs]))
 print(json.dumps(report),flush=True)
