import argparse
from .pipeline import build

parser = argparse.ArgumentParser(description='Convert a closed line-art contour into an honest dot-to-dot')
parser.add_argument('--source', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--prompt')
parser.add_argument('--points', type=int, default=243)
parser.add_argument('--grid', type=float, default=18)
args = parser.parse_args()
build(args.source, args.output, args.points, args.grid, args.prompt)
