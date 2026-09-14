import argparse
import json
import sys

from .pipeline import build, validate


def main():
    parser = argparse.ArgumentParser(description="Build exact 45×45 or 135×135 marker mosaics")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("--source", required=True)
    create.add_argument("--palette", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--generation", help="JSON containing source prompt and generation metadata")
    create.add_argument("--centre-crop", action="store_true")
    create.add_argument("--resampling", choices=["box", "nearest"], default="box",
                        help="BOX averages regions; nearest preserves flat pixel-art colours")
    create.add_argument("--subdivision", type=int, choices=[1, 3], default=1,
                        help="Subdivide each original position into 1x1 or 3x3 colours")
    check = commands.add_parser("validate")
    check.add_argument("directory")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = validate(args.directory)
        else:
            result = build(args.source, args.palette, args.output, args.generation, args.centre_crop, args.resampling, args.subdivision)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"mosaic: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
