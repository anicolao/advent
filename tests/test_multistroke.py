import copy
from collections import Counter
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from dot_to_dot.multistroke import draw_svg,validate
from dot_to_dot.winter_scene import artwork

ROOT=Path(__file__).resolve().parents[1]


class MultiStrokeTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'runs/dot-to-dot-winter-window/points.json').read_text())

    def test_every_source_segment_and_only_source_segments(self):
        result=validate(self.data)
        self.assertEqual(result['points'],243)
        self.assertEqual(result['strokes'],50)
        self.assertEqual(result['segments'],277)
        source=Counter(tuple(sorted((tuple(a),tuple(b)))) for s in artwork() for a,b in zip(s['xy'],s['xy'][1:]))
        def xy(i):
            p=self.data['points'][i-1]
            return (p['x'],p['y'])
        rendered=Counter(tuple(sorted((xy(a),xy(b)))) for a,b in self.data['edges'])
        self.assertEqual(source,rendered)
        self.assertEqual(len({tuple(p) for s in artwork() for p in s['xy']}),243)

    def test_pen_lifts_have_no_connectors(self):
        altered=copy.deepcopy(self.data)
        left,right=altered['strokes'][:2]
        altered['edges'].insert(left['end_edge'],[left['points'][-1],right['points'][0]])
        with self.assertRaisesRegex(ValueError,'connector'):
            validate(altered)

    def test_solved_and_unsolved_have_identical_dots(self):
        ns={'s':'http://www.w3.org/2000/svg'}
        before=ET.fromstring(draw_svg(self.data))
        after=ET.fromstring(draw_svg(self.data,True))
        self.assertEqual(len(before.findall('s:line',ns)),0)
        self.assertEqual(len(after.findall('s:line',ns)),277)
        self.assertEqual(len(before.findall('s:circle',ns)),243)
        self.assertEqual([x.attrib for x in before.findall('s:circle',ns)],
                         [x.attrib for x in after.findall('s:circle',ns)])
        self.assertEqual([x.attrib for x in before.findall('s:text',ns)],
                         [x.attrib for x in after.findall('s:text',ns)])

    def test_default_view_has_no_hint_or_source_layer(self):
        template=(ROOT/'dot_to_dot/multistroke.html').read_text()
        self.assertIn('id="hint" type="checkbox">',template)
        self.assertNotIn('drawImage',template)
        run=json.loads((ROOT/'runs/dot-to-dot-winter-window/run.json').read_text())
        self.assertEqual(run['label_overlap_pairs'],[])


if __name__=='__main__':
    unittest.main()
