"""whistle CLI entry point."""
import argparse
import sys
from pathlib import Path

from .vectorize import vectorize_sprite, runs_to_rect_xml
from .eyes import eyes_js_xml
from .theme import idle_svg, write_theme


def parse_coord(s: str) -> tuple[int, int]:
    x, y = s.split(",")
    return int(x), int(y)


def main() -> int:
    p = argparse.ArgumentParser(
        prog="whistle",
        description="Turn a character image into a clawd-on-desk theme.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Build a theme from an image")
    b.add_argument("--image", required=True, type=Path)
    b.add_argument("--name", required=True, help="theme id (kebab-case)")
    b.add_argument("--display-name", default=None, help="human-readable name")
    b.add_argument(
        "--eye-left", type=parse_coord, default=None,
        help="px coords of left-eye center (e.g. 207,277)",
    )
    b.add_argument(
        "--eye-right", type=parse_coord, default=None,
        help="px coords of right-eye center (e.g. 255,277)",
    )
    b.add_argument(
        "--out", type=Path, default=Path.home() / "Library/Application Support/clawd-on-desk/themes",
    )
    b.add_argument("--grid", type=int, default=96, help="downsample grid size")

    args = p.parse_args()

    if args.cmd == "build":
        if not args.image.exists():
            print(f"error: image not found: {args.image}", file=sys.stderr)
            return 1

        # Default eye coords for a 512×512 square canvas, centered
        left = args.eye_left or (207, 277)
        right = args.eye_right or (255, 277)

        # eye mask: small box around each eye
        mask_boxes = [
            (left[0] - 15, left[1] - 15, left[0] + 15, left[1] + 15),
            (right[0] - 15, right[1] - 15, right[0] + 15, right[1] + 15),
        ]

        runs, grid = vectorize_sprite(args.image, grid_size=args.grid, eye_mask_boxes=mask_boxes)
        sprite_xml = runs_to_rect_xml(runs, grid)
        eyes_xml = eyes_js_xml(left, right)
        idle = idle_svg(sprite_xml, eyes_xml)

        # MVP: deliver idle only; other states copy idle placeholder.
        states = {
            "idle": idle,
            "thinking": idle,
            "working": idle,
            "error": idle,
            "attention": idle,
            "notification": idle,
            "sleeping": idle,
            "waking": idle,
        }
        write_theme(
            args.out,
            theme_id=args.name,
            name=args.display_name or args.name,
            svg_files=states,
        )
        print(f"✓ wrote {args.out / args.name}")
        print("  restart clawd-on-desk and right-click → Theme → select to enable")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
