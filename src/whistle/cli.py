"""whistle CLI entry point."""
import argparse
import sys
from pathlib import Path

from PIL import Image

from .vectorize import vectorize_sprite, runs_to_rect_xml, sheet_apng
from .eyes import eyes_js_xml
from .theme import state_svg, write_theme, STATE_ANIMS


def parse_coord(s: str) -> tuple[int, int]:
    x, y = s.split(",")
    return int(x), int(y)


# Spritesheet → clawd state mapping: (row, frames, ms/frame).
# Rows are 0-indexed top-down; sleeping/waking reuse the idle row at
# slower/faster playback (no dedicated sleep art in most sheets).
SHEET_STATES = {
    "idle": (0, 6, 125),
    "thinking": (7, 6, 150),
    "working": (8, 6, 90),
    "error": (5, 8, 80),
    "attention": (4, 5, 100),
    "notification": (3, 4, 110),
    "sleeping": (0, 6, 300),
    "waking": (0, 6, 80),
}


def build_sheet_theme(args) -> int:
    """Slice spritesheet rows into per-state APNGs (no eyes — frame art has
    its own). Cell size defaults to sheet width/8 (rows are 8 frames wide)."""
    if not args.sheet.exists():
        print(f"error: sheet not found: {args.sheet}", file=sys.stderr)
        return 1
    with Image.open(args.sheet) as im:
        sheet_w, sheet_h = im.size
    cell_w, cell_h = args.sheet_cell or (sheet_w // 8, sheet_h // 9)

    states = {
        state: sheet_apng(args.sheet, cell_w, cell_h, row, frames, duration)
        for state, (row, frames, duration) in SHEET_STATES.items()
    }
    write_theme(args.out, theme_id=args.name, name=args.display_name or args.name, svg_files=states)
    print(f"✓ wrote {args.out / args.name} (APNG frame animation)")
    print("  restart clawd-on-desk and right-click → Theme → select to enable")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        prog="whistle",
        description="Turn a character image into a clawd-on-desk theme.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Build a theme from an image or spritesheet")
    src = b.add_mutually_exclusive_group(required=True)
    src.add_argument("--image", type=Path, help="static sprite PNG/GIF (SVG theme)")
    src.add_argument("--sheet", type=Path, help="animation spritesheet (APNG theme)")
    b.add_argument("--sheet-cell", type=parse_coord, default=None,
                   help="spritesheet cell size w,h (default: auto from sheet size)")
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
        if args.sheet:
            return build_sheet_theme(args)
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

        # Per-state animation, all sharing the sprite + eyes markup.
        origin_cx = content_x + content_w / 2
        origin_cy = -3.0 + content_h / 2
        states = {
            state: state_svg(state, sprite_xml, eyes_xml, origin_cx, origin_cy)
            for state in STATE_ANIMS
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
