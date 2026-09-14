import json
import math
from pathlib import Path
import unittest
from dot_to_dot.numbered_grid import solve

class NumberedGridV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((Path(__file__).resolve().parents[1]/'runs/christmas-room-numbered-grid-v2/puzzle.json').read_text())

    def test_original_geometry_is_exact(self):
        d=self.d
        for segment in d['provenance']:
            a,b=segment['a'],segment['b']
            points=[d['points'][v] for v in segment['nodes']]
            self.assertEqual(points[0],a)
            self.assertEqual(points[-1],b)
            for p in points:
                self.assertAlmostEqual((p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0]),0)
            self.assertAlmostEqual(sum(math.dist(p,q) for p,q in zip(points,points[1:])),math.dist(a,b))
        self.assertEqual(len(d['provenance']),213)

    def test_short_hops_and_unambiguous_number_lookup(self):
        d=self.d
        labels=[v for pair in d['labels'] for v in pair]
        self.assertEqual(sorted(labels),list(range(1,len(labels)+1)))
        self.assertTrue(all(len(pair)==2 for pair in d['labels']))
        real_nodes={v for p in d['real_paths'] for v in p}
        for item in d['instructions']:
            for choice in item['choices']:
                decoded=d['inverse'][choice['first']:choice['first']+choice['length']+1]
                self.assertEqual(decoded,choice['nodes'])
                self.assertTrue(all(math.dist(d['points'][a],d['points'][b])<=3+1e-8 for a,b in zip(decoded,decoded[1:])))
                if choice['digit']!=d['solution'][item['cell']]:
                    self.assertFalse(real_nodes.intersection(decoded))
        for path,item in zip(d['real_paths'],d['instructions']):
            self.assertEqual(path,item['choices'][d['solution'][item['cell']]-1]['nodes'])

    def test_printed_lookup_order_covers_every_blank(self):
        d=self.d
        self.assertEqual(solve(d['sudoku']),[d['solution']])
        self.assertEqual([item['cell'] for item in d['instructions']],[i for i,v in enumerate(d['sudoku']) if not v])

if __name__=='__main__':unittest.main()
