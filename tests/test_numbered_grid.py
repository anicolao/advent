import json
from pathlib import Path
import unittest

from dot_to_dot.numbered_grid import solve, distance


class NumberedGridTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((Path(__file__).resolve().parents[1]/'runs/christmas-room-numbered-grid/puzzle.json').read_text())

    def test_start_and_count_reconstruct_every_path(self):
        d = self.data
        self.assertEqual(sorted(d['labels']), list(range(1, 3722)))
        inverse = {label: node for node, label in enumerate(d['labels'])}
        for item in d['instructions']:
            for choice in item['choices']:
                col, row = choice['start']
                start = (row-1)*61+col-1
                first = d['labels'][start]
                reconstructed = [inverse[first+i] for i in range(choice['length']+1)]
                self.assertEqual(reconstructed, choice['nodes'])

    def test_correct_keys_preserve_segment_count_and_wrong_keys_use_other_dots(self):
        d = self.data
        real_nodes = {v for p in d['real_paths'] for v in p}
        all_visits = [v for p in d['real_paths'] for v in p]
        self.assertEqual(len(real_nodes), len(all_visits))
        for item, original, actual in zip(d['instructions'], d['original_paths'], d['real_paths']):
            self.assertEqual(item['choices'][d['solution'][item['cell']]-1]['nodes'], actual)
            self.assertEqual(len(original), len(actual))
            self.assertTrue(all(distance(a,b) <= 2**.5 for a,b in zip(original, actual)))
            for ch in item['choices']:
                if ch['digit'] != d['solution'][item['cell']]:
                    self.assertFalse(real_nodes.intersection(ch['nodes']))

    def test_sudoku_unique_and_keys_require_solving(self):
        d = self.data
        self.assertEqual(solve(d['sudoku']), [d['solution']])
        keys = [i['cell'] for i in d['instructions']]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertTrue(all(d['sudoku'][i] == 0 for i in keys))


if __name__ == '__main__':
    unittest.main()
