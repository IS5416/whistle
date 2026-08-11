"""whistle CLI entry point."""
import argparse
import sys
from pathlib import Path

from PIL import Image

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
    b.add_argument("--grid", type=int, default=160, help="downsample grid size (longest side)")

    args = p.parse_args()

    if args.cmd == "build":
        if not args.image.exists():
            print(f"error: image not found: {args.image}", file=sys.stderr)
            return 1

        # Default eye coords for a 512×512 square canvas, centered
        left = args.eye_left or (207, 277)
        right = args.eye_right or (255, 277)

        img = Image.open(args.image)
        runs, grid_w, grid_h = vectorize_sprite(args.image, grid_size=args.grid)

        # Fit sprite aspect into the 23×20 content box so clawd's normalized
        # layout renders it undistorted.
        aspect = img.width / img.height
        scale = min(23.0 / aspect, 20.0)
        content_w, content_h = aspect * scale, scale
        content_x = -4.0 + (23.0 - content_w) / 2  # center box horizontally

        sprite_xml = runs_to_rect_xml(
            runs, grid_w, grid_h,
            viewbox_origin=(content_x, -3.0),
            viewbox_size=(content_w, content_h),
        )
        eyes_xml = eyes_js_xml(
            left, right,
            sprite_w=img.width, sprite_h=img.height,
            viewbox_origin=(content_x, -3.0),
            viewbox_size=(content_w, content_h),
        )
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
            content_w=content_w,
            content_h=content_h,
        )
        print(f"✓ wrote {args.out / args.name}")
        print("  restart clawd-on-desk and right-click → Theme → select to enable")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
