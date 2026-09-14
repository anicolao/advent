"""Clip shared vector artwork into 25 exact 243-point daily graphs."""
from collections import defaultdict
import math
import numpy as np
from .artwork import artwork

SIDE=300


def clip(a,b,left,top):
    """Liang–Barsky segment clipping with a shared, snapped seam lattice."""
    x,y=a;dx,dy=b[0]-x,b[1]-y;lo,hi=0.,1.
    for p,q in [(-dx,x-left),(dx,left+SIDE-x),(-dy,y-top),(dy,top+SIDE-y)]:
        if p==0:
            if q<0:return None
        elif p<0:lo=max(lo,q/p)
        else:hi=min(hi,q/p)
    if lo>hi:return None
    points=[tuple(3*round(v/3) for v in (x+t*dx-left,y+t*dy-top)) for t in (lo,hi)]
    return points if points[0]!=points[1] else None


def make_graphs(source=None):
    original=artwork();graphs=[];omitted=[]
    for day in range(25):
        row,col=divmod(day,5);candidates=[]
        for index,path in enumerate(original):
            segments=[]
            for a,b in zip(path['xy'],path['xy'][1:]):
                pair=clip(a,b,col*SIDE,row*SIDE)
                if pair:segments.append(pair)
            if segments:candidates.append((path['priority'],index,segments))
        lookup={};edges=set();boundary=set();skipped=0
        # All seam-touching strokes are retained before optional interior texture.
        candidates.sort(key=lambda item:(not any(0 in p or SIDE in p for pair in item[2] for p in pair),item[0],item[1]))
        for priority,index,segments in candidates:
            new={tuple(p) for pair in segments for p in pair}-set(lookup)
            if len(lookup)+len(new)>243:
                if any(0 in p or SIDE in p for pair in segments for p in pair):raise ValueError(f'Too many seam vertices: day {day+1}')
                if priority<=-2:raise ValueError(f'Required focal detail exceeds the point budget on day {day+1}')
                skipped+=len(segments);continue
            for a,b in segments:
                for p in (a,b):
                    if p not in lookup:lookup[p]=len(lookup)
                    if 0 in p or SIDE in p:boundary.add(p)
                edges.add(tuple(sorted((lookup[a],lookup[b]))))
        locations=[None]*len(lookup)
        for p,i in lookup.items():locations[i]=p
        # Allocate remaining locations along existing lines, without joining strokes.
        initial=len(locations)
        while len(locations)<243:
            candidates=sorted(edges,key=lambda e:math.dist(locations[e[0]],locations[e[1]]),reverse=True)
            for a,b in candidates:
                midpoint=tuple(3*round((u+v)/6) for u,v in zip(locations[a],locations[b]))
                if midpoint in lookup or 0 in midpoint or SIDE in midpoint:continue
                vertex=len(locations);locations.append(midpoint);lookup[midpoint]=vertex
                edges.remove((a,b));edges.update([tuple(sorted((a,vertex))),tuple(sorted((vertex,b)))])
                break
            else:raise ValueError(f'Unable to allocate 243 dots on day {day+1}')
        graphs.append(dict(day=day+1,locations=np.array(locations,float),edges=edges,boundary_points=len(boundary),
                           original_vertices=initial,subdivisions=243-initial,omitted_texture_segments=skipped))
        omitted.append(skipped)
    return graphs,dict(source='Authored vector adaptation of the generated village reference',
                       lattice_spacing=3,scene_size=[1500,1500],original_paths=len(original),
                       omitted_segments_by_day=omitted)


def trails(graph):
    """Edge-disjoint Euler trails; temporary virtual edges are never drawn."""
    edges=sorted(graph['edges']);adj=defaultdict(list)
    for eid,(a,b) in enumerate(edges):adj[a].append((b,eid));adj[b].append((a,eid))
    remaining=set(adj);components=[]
    while remaining:
        stack=[remaining.pop()];component=[]
        while stack:
            v=stack.pop();component.append(v)
            for w,_ in adj[v]:
                if w in remaining:remaining.remove(w);stack.append(w)
        components.append(component)
    result=[];used=set()
    for component in components:
        odd=sorted(v for v in component if len(adj[v])%2)
        virtual=243
        if odd:
            for v in odd:
                eid=len(edges);edges.append((virtual,v));adj[virtual].append((v,eid));adj[v].append((virtual,eid))
            start=virtual
        else:start=min(component)
        stack=[start];path=[]
        while stack:
            v=stack[-1]
            while adj[v] and adj[v][-1][1] in used:adj[v].pop()
            if not adj[v]:path.append(stack.pop())
            else:
                w,eid=adj[v].pop();used.add(eid);stack.append(w)
        path.reverse();stroke=[]
        for v in path:
            if v==virtual:
                if len(stroke)>1:result.append(stroke)
                stroke=[]
            else:stroke.append(v)
        if len(stroke)>1:result.append(stroke)
        adj.pop(virtual,None)
    return result
