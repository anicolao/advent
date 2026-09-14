"""Calendar geometry invariants: exact daily counts and honest shared drawing."""
from collections import Counter
import json
from pathlib import Path
import unittest

from advent.geometry import make_graphs, trails, clip
from advent.build import scene_xy
from dot_to_dot.multistroke import validate

OUT=Path(__file__).resolve().parents[1]/'runs/advent-organic-village'


class AdventGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.graphs,cls.metadata=make_graphs()

    def test_every_day_has_243_unique_used_lattice_points(self):
        self.assertEqual(len(self.graphs),25)
        for g in self.graphs:
            with self.subTest(day=g['day']):
                self.assertEqual(len(g['locations']),243)
                self.assertEqual(len(set(map(tuple,g['locations']))),243)
                self.assertEqual({i for edge in g['edges'] for i in edge},set(range(243)))
                self.assertTrue(((g['locations']%3)==0).all())
                self.assertTrue(((g['locations']>=0)&(g['locations']<=300)).all())

    def test_strokes_cover_each_art_edge_once_without_pen_lift_connectors(self):
        for g in self.graphs:
            strokes=trails(g)
            drawn=Counter(tuple(sorted((a,b))) for s in strokes for a,b in zip(s,s[1:]))
            self.assertEqual(drawn,Counter(g['edges']))
            self.assertTrue(all(len(s)>=2 for s in strokes))

    def test_shared_seam_clipping(self):
        for a,b in [((200,80),(380,180)),((250,280),(360,390)),((140,295),(470,308))]:
            left=clip(a,b,0,0);right=clip(a,b,300,0)
            if left and right:
                self.assertEqual(left[-1],(right[0][0]+300,right[0][1]))
        self.assertIsNone(clip((10,10),(20,20),300,300))

    def test_every_noncollapsed_crossing_is_present_on_both_sheets(self):
        from advent.artwork import artwork
        checked=0; original=artwork()
        for i,g in enumerate(self.graphs):
            r,c=divmod(i,5)
            for neighbour in ([i+1] if c<4 else [])+([i+5] if r<4 else []):
                rr,cc=divmod(neighbour,5)
                for path in original:
                    for a,b in zip(path['xy'],path['xy'][1:]):
                        left=clip(a,b,c*300,r*300)
                        right=clip(a,b,cc*300,rr*300)
                        if not left or not right:continue
                        first={(x+c*300,y+r*300) for x,y in left}
                        second={(x+cc*300,y+rr*300) for x,y in right}
                        shared=first&second
                        for x,y in shared:
                            self.assertIn((x-c*300,y-r*300),set(map(tuple,g['locations'])))
                            self.assertIn((x-cc*300,y-rr*300),set(map(tuple,self.graphs[neighbour]['locations'])))
                            checked+=1
        self.assertGreater(checked,100)

    def test_deterministic_art_and_trails(self):
        from advent.artwork import artwork
        self.assertEqual(artwork(),artwork())
        for g in self.graphs:self.assertEqual(trails(g),trails(g))


class AdventArtifactTests(unittest.TestCase):
    def test_all_exported_days_and_scene_coordinates(self):
        calendar=json.loads((OUT/'calendar.json').read_text())
        self.assertEqual(calendar['printed_dot_count'],6075)
        self.assertEqual(len(calendar['days']),25)
        graphs,_=make_graphs()
        for d,g in zip(calendar['days'],graphs):
            with self.subTest(day=d['day']):
                self.assertEqual(validate(d)['status'],'passed')
                directory=OUT/f'day-{d["day"]:02}'
                self.assertEqual(json.loads((directory/'points.json').read_text()),d)
                for f in ['index.html','instructions.html','source.svg','connected.svg','dots.svg','source.png','connected.png','dots.png']:
                    self.assertTrue((directory/f).stat().st_size>0)
                xy=[scene_xy(d,p) for p in d['points']]
                def key(a,b):return tuple(sorted((tuple(round(v,5) for v in a),tuple(round(v,5) for v in b))))
                actual=Counter(key(xy[a-1],xy[b-1]) for a,b in d['edges'])
                r,c=divmod(d['day']-1,5)
                coords=[(x+c*300,y+r*300) for x,y in g['locations']]
                expected=Counter(key(coords[a],coords[b]) for a,b in g['edges'])
                self.assertEqual(actual,expected)
                report=json.loads((directory/'validation.json').read_text())
                self.assertEqual(report['label_overlap_pairs'],[])
        self.assertTrue((OUT/'tile-review.png').exists())
        self.assertEqual((OUT/'tile-review.html').read_text().count('alt="Completed day '),25)
        for name in ['puzzles','solutions','stroke-guides']:
            self.assertEqual((OUT/f'{name}.html').read_text().count('<section class="sheet">'),25)


if __name__=='__main__':unittest.main()
