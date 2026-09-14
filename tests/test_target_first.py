"""Checks for the source-transfer proof, separate from the authored village."""
from collections import Counter
import json
from pathlib import Path
import unittest
from dot_to_dot.multistroke import validate

OUT=Path(__file__).resolve().parents[1]/'runs/christmas-room-proof'

class TargetFirstProofTests(unittest.TestCase):
 def test_exact_budget_and_no_budget_omissions(self):
  data=json.loads((OUT/'calendar.json').read_text());report=json.loads((OUT/'trace-report.json').read_text())
  self.assertEqual(len(data['days']),25)
  self.assertEqual(sum(len(d['points']) for d in data['days']),6075)
  self.assertTrue(all(d['omitted_segments']==0 for d in report['tiles']))
  for d in data['days']:self.assertEqual(validate(d)['status'],'passed')
 def test_exported_edges_match_retained_graph(self):
  data=json.loads((OUT/'calendar.json').read_text());graphs=json.loads((OUT/'graphs.json').read_text())
  for d,g in zip(data['days'],graphs):
   xy=[(p['x'],p['y']) for p in d['points']]
   original=[(int(100+x*10/3),int(100+y*10/3)) for x,y in g['locations']]
   expected=Counter(tuple(sorted((original[a],original[b]))) for a,b in g['edges'])
   actual=Counter(tuple(sorted((xy[a-1],xy[b-1]))) for a,b in d['edges'])
   self.assertEqual(expected,actual)
  self.assertEqual((OUT/'reduced.svg').read_text().count('<path '),sum(len(d['edges']) for d in data['days']))

if __name__=='__main__':unittest.main()
