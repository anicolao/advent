import json
import math
from pathlib import Path
import unittest
from dot_to_dot.numbered_grid import solve
from dot_to_dot.numbered_grid_v3 import decode

class SingleNumberJoinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[1]
        cls.d=json.loads((root/'runs/christmas-room-numbered-grid-v3/puzzle.json').read_text())
        cls.previous=json.loads((root/'runs/christmas-room-numbered-grid-v2/puzzle.json').read_text())

    def test_geometry_unchanged_and_one_number_per_dot(self):
        d=self.d
        self.assertEqual(d['points'],self.previous['points'])
        self.assertEqual(d['real_paths'],self.previous['real_paths'])
        self.assertEqual(sorted(d['labels']),list(range(1,len(d['points'])+1)))
        for v,label in enumerate(d['labels']):self.assertEqual(d['inverse'][label],v)

    def test_all_commands_decode_and_joins_stay_short(self):
        d=self.d;real={v for p in d['real_paths'] for v in p};joins=0
        for item,path in zip(d['instructions'],d['real_paths']):
            correct=item['choices'][d['solution'][item['cell']]-1]
            self.assertEqual(decode(correct,d['inverse']),path)
            pattern=lambda choice:[(op['kind'],op.get('count')) for op in choice['ops']]
            for choice in item['choices']:
                nodes=decode(choice,d['inverse'])
                self.assertEqual(nodes,choice['nodes'])
                self.assertEqual(pattern(choice),pattern(correct))
                self.assertEqual(len(nodes)-1,choice['length'])
                self.assertTrue(all(math.dist(d['points'][a],d['points'][b])<=3+1e-8 for a,b in zip(nodes,nodes[1:])))
                if choice is not correct:self.assertFalse(real.intersection(nodes))
            joins+=sum(op['kind']=='join' for op in correct['ops'])
        self.assertEqual(joins,d['report']['join_connections'])

    def test_sudoku_and_rc_lookup(self):
        d=self.d
        self.assertEqual(solve(d['sudoku']),[d['solution']])
        self.assertEqual([i['cell'] for i in d['instructions']],[i for i,v in enumerate(d['sudoku']) if not v])
        for item in d['instructions']:
            self.assertEqual(item['name'],f'R{item["cell"]//9+1}C{item["cell"]%9+1}')

if __name__=='__main__':unittest.main()
