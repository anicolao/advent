from collections import Counter
import json
from pathlib import Path
import unittest
from dot_to_dot.reference_grid import convert,decompose,grid_svg,remove_padding

ROOT=Path(__file__).resolve().parents[1]

class ReferenceGridTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=json.loads((ROOT/'runs/christmas-room-proof/calendar.json').read_text())['days']
  cls.graphs=json.loads((ROOT/'runs/christmas-room-proof/graphs.json').read_text())
  cls.data=json.loads((ROOT/'runs/christmas-room-reference-grid/grids.json').read_text())
 def test_every_drawn_edge_is_a_retained_snapped_source_edge(self):
  for n,days in self.data['variants'].items():
   n=int(n)
   for d,source,g in zip(days,self.source,self.graphs):
    prepared=remove_padding(source,g)
    expected={tuple(sorted((d['source_to_grid'][a-1],d['source_to_grid'][b-1]))) for a,b in prepared['edges'] if d['source_to_grid'][a-1]!=d['source_to_grid'][b-1]}
    self.assertEqual(Counter(tuple(sorted(e)) for e in d['edges']),Counter(expected))
    self.assertTrue(all(1<=v<=n*n for e in d['edges'] for v in e))
    flattened=[]
    for stroke in d['strokes']:
     self.assertEqual(stroke['start_edge'],len(flattened))
     flattened.extend([a,b] for a,b in zip(stroke['points'],stroke['points'][1:]))
     self.assertEqual(stroke['end_edge'],len(flattened))
    self.assertEqual(flattened,d['edges'])
 def test_identical_blank_sheets_with_unused_points(self):
  for n,days in self.data['variants'].items():
   n=int(n);blank=grid_svg(n)
   self.assertEqual(blank.count('<circle '),n*n)
   self.assertEqual((ROOT/f'runs/christmas-room-reference-grid/blank-grid-{n}.svg').read_text(),blank)
   for d in days:
    self.assertEqual(d['printed_reference_points'],n*n)
    self.assertLess(d['active_reference_points'],n*n)
 def test_reproduction_and_large_node_ids(self):
  self.assertEqual(decompose({(1000,2000),(2000,3000),(3000,1000),(9,10)}),decompose({(1000,2000),(2000,3000),(3000,1000),(9,10)}))
  for n in [16,31,61]:
   source=remove_padding(self.source[13],self.graphs[13])
   self.assertEqual(convert(source,n),self.data['variants'][str(n)][13])

if __name__=='__main__':unittest.main()
