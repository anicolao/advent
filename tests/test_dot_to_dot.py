import copy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import numpy as np
from dot_to_dot.pipeline import align, crossings, sample, svg, validate

ROOT=Path(__file__).resolve().parents[1]


class DotToDotTests(unittest.TestCase):
    def test_exact_budget_and_determinism(self):
        angles=np.linspace(0,2*np.pi,2000,endpoint=False)
        outline=np.stack([600+400*np.cos(angles),600+350*np.sin(angles)],axis=1)
        points,_=sample(outline,243)
        self.assertEqual(len(points),243)
        a,metadata=align(points,12)
        b,_=align(points,12)
        np.testing.assert_array_equal(a,b)
        self.assertEqual(crossings(a),[])
        self.assertEqual(len(set(map(tuple,a))),243)

    def test_crossing_and_nonadjacent_touch_detection(self):
        self.assertTrue(crossings(np.array([[0,0],[10,10],[0,10],[10,0]])))
        self.assertTrue(crossings(np.array([[0,0],[10,0],[10,10],[5,0],[0,10]])))
        self.assertEqual(crossings(np.array([[0,0],[10,0],[10,10],[0,10]])),[])

    def test_saved_puzzle_and_svg_share_exact_geometry(self):
        data=json.loads((ROOT/'runs/dot-to-dot-reindeer/points.json').read_text())
        self.assertEqual(validate(data)['points'],243)
        ns={'s':'http://www.w3.org/2000/svg'}
        unsolved=ET.fromstring(svg(data,False))
        solved=ET.fromstring(svg(data,True))
        self.assertEqual(len(unsolved.findall('s:circle',ns)),243)
        self.assertEqual(len(unsolved.findall('s:text',ns)),243)
        self.assertEqual(len(unsolved.findall('s:polyline',ns)),0)
        self.assertEqual([x.attrib for x in unsolved.findall('s:circle',ns)],
                         [x.attrib for x in solved.findall('s:circle',ns)])
        poly=solved.find('s:polyline',ns).attrib['points'].split()
        expected=[f'{p["x"]},{p["y"]}' for p in data['points']]
        self.assertEqual(poly,expected+[expected[0]])
        broken=copy.deepcopy(data)
        broken['edges'][-1]=[243,2]
        with self.assertRaisesRegex(ValueError,'Edges'):
            validate(broken)
        broken=copy.deepcopy(data)
        broken['points'][1]['x']=broken['points'][0]['x']
        broken['points'][1]['y']=broken['points'][0]['y']
        with self.assertRaisesRegex(ValueError,'duplicated'):
            validate(broken)


if __name__=='__main__':
    unittest.main()
