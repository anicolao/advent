import csv
import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from scripts.build_site import CANONICAL_ORIGIN, decode, paths, tile_svg
from dot_to_dot.numbered_grid import solve

ROOT=Path(__file__).resolve().parents[1]


class FrozenAdventTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=ROOT/'editions/2026/calendar.json'
        cls.data=json.loads(cls.path.read_text())

    def test_permanent_qr_targets(self):
        expected=[{'day':day,'url':f'{CANONICAL_ORIGIN}/2026/day/{day:02}/'} for day in range(1,26)]
        self.assertEqual(json.loads((ROOT/'links/2026-days.json').read_text()),expected)
        with (ROOT/'links/2026-days.csv').open(newline='') as f:
            rows=[{'day':int(row['day']),'url':row['url']} for row in csv.DictReader(f)]
        self.assertEqual(rows,expected)
        self.assertEqual((ROOT/'site/CNAME').read_text().strip(),'advent.annasdadpress.com')

    def test_snapshot_hash_and_day_order(self):
        provenance=json.loads((self.path.parent/'provenance.json').read_text())
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),provenance['calendar_sha256'])
        self.assertEqual([d['day'] for d in self.data['days']],list(range(1,26)))
        self.assertEqual(self.data['assembly_grid'],[[25,24,23,22,21],[16,17,18,19,20],[15,14,13,12,11],[6,7,8,9,10],[5,4,3,2,1]])
        for day in self.data['days']:
            self.assertEqual(self.data['assembly_grid'][day['tile_row']-1][day['tile_column']-1],day['day'])

    def test_all_sudoku_solutions_are_legal_and_unique(self):
        expected=set(range(1,10))
        for day in self.data['days']:
            with self.subTest(day=day['day']):
                puzzle=[v for row in day['sudoku']['puzzle'] for v in row]
                answer=[v for row in day['sudoku']['solution'] for v in row]
                for r in range(9):self.assertEqual(set(answer[r*9:r*9+9]),expected)
                for c in range(9):self.assertEqual(set(answer[c::9]),expected)
                for r in (0,3,6):
                    for c in (0,3,6):self.assertEqual({answer[(r+y)*9+c+x] for y in range(3) for x in range(3)},expected)
                self.assertTrue(all(not p or p==s for p,s in zip(puzzle,answer)))
                self.assertEqual(solve(puzzle),[answer])

    def test_all_drawing_choices_and_approved_paths(self):
        for day in self.data['days']:
            with self.subTest(day=day['day']):
                n=len(day['points'])
                self.assertEqual(sorted(day['labels']),list(range(1,n+1)))
                self.assertEqual(len(day['label_positions']),n)
                for node,label in enumerate(day['labels']):self.assertEqual(day['inverse'][label],node)
                for instruction in day['instructions']:
                    self.assertEqual(sorted(c['digit'] for c in instruction['choices']),list(range(1,10)))
                    for choice in instruction['choices']:
                        self.assertEqual(decode(choice,day['inverse']),choice['nodes'])
                self.assertEqual(paths(day),day['approved_paths'])

    def test_three_svg_modes_and_six_inch_scale(self):
        ns={'s':'http://www.w3.org/2000/svg'}
        for day in self.data['days']:
            for mode in ('dots','art','solved'):
                svg=ET.fromstring(tile_svg(day,mode,self.data['label_font']))
                self.assertEqual(svg.attrib['width'],'6.6in')
                self.assertEqual(svg.attrib['viewBox'],'-3 -3 66 66')
                # 60 of 66 viewbox units at 6.6 in is exactly a six-inch border.
                self.assertAlmostEqual(6.6*60/66,6)
                self.assertEqual(len(svg.findall('s:circle',ns)),0 if mode=='art' else len(day['points']))
                self.assertEqual(len(svg.findall('s:polyline',ns)),0 if mode=='dots' else len(day['approved_paths']))
                if mode=='art':self.assertEqual(len(svg.findall('s:text',ns)),0)


if __name__=='__main__':unittest.main()
