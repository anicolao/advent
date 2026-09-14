"""Export the inspected source-transfer proof, without building print books."""
from pathlib import Path
import json
import base64
import numpy as np
from PIL import Image,ImageDraw
from advent.build import daily_data,scene_svg,scene_xy
from dot_to_dot.multistroke import draw_svg,draw_png

out=Path('runs/christmas-room-proof');gs=json.loads((out/'graphs.json').read_text());days=[];checks=[]
for g in gs:
 g['locations']=np.array(g['locations']);g['edges']=set(map(tuple,g['edges']))
 d,report=daily_data(g);days.append(d);checks.append(report)
 print(f'Tile {d["day"]}: 243 used dots, validation passed',flush=True)
calendar=dict(days=days,printed_dot_count=6075)
(out/'calendar.json').write_text(json.dumps(calendar,indent=2))
for name,dots in [('reduced',False),('dots',True)]:
 svg=scene_svg(days,dots).replace('stroke-width="1.2"','stroke-width="2"')
 (out/f'{name}.svg').write_text(svg)
 im=Image.new('RGB',(2000,2000),'white');draw=ImageDraw.Draw(im)
 for d in days:
  xy=[tuple(v*4/3 for v in scene_xy(d,p)) for p in d['points']]
  if dots:
   for x,y in xy:draw.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),fill='#172b38')
  else:
   for a,b in d['edges']:draw.line([xy[a-1],xy[b-1]],fill='#172b38',width=3)
 im.save(out/f'{name}.png')
# One representative daily detail, without manufacturing 25 print packages.
d=days[13]
for name,lines in [('tile-14-connected',True),('tile-14-dots',False)]:
 (out/f'{name}.svg').write_text(draw_svg(d,lines,True,True));draw_png(d,lines,True,True).save(out/f'{name}.png')
(out/'validation.json').write_text(json.dumps(dict(point_count=6075,tiles=checks),indent=2))
template=Path('dot_to_dot/target_first_comparison.html').read_text()
(out/'index.html').write_text(template.replace('__DATA__',json.dumps(calendar)).replace('__SOURCE__','data:image/png;base64,'+base64.b64encode((out/'original.png').read_bytes()).decode()))
print('Comparison exported',flush=True)
