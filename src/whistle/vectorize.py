"""Sprite → SVG vector rects (RLE-merged per row)."""
import io
from pathlib import Path
from PIL import Image


def vectorize_sprite(
    image_path: Path,
    grid_size: int = 96,
) -> tuple[list[tuple[float, float, float, tuple[int, int, int]]], int, int]:
    """Downsample sprite to a grid_size-limited canvas, RLE-merge runs.

    Canvas keeps the source aspect ratio (grid_size is the longest side), so
    a portrait sprite stays portrait instead of being squished square.

    Returns (runs, grid_w, grid_h): runs is list of (x, y, w, (r,g,b)).
    """
    img = Image.open(image_path).convert("RGBA")

    w, h = img.size
    scale = min(grid_size / w, grid_size / h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    small = img.resize((nw, nh), Image.NEAREST)
    px = small.load()
    runs = []
    for y in range(nh):
        run_start = None
        run_color = None
        for x in range(nw):
            r, g, b, a = px[x, y]
            if a < 32:
                if run_start is not None:
                    runs.append((run_start, y, x - run_start, run_color))
                    run_start = None
                continue
            color = (r, g, b)
            if run_start is None:
                run_start = x
                run_color = color
            elif color != run_color:
                runs.append((run_start, y, x - run_start, run_color))
                run_start = x
                run_color = color
        if run_start is not None:
            runs.append((run_start, y, nw - run_start, run_color))
    return runs, nw, nh


def runs_to_rect_xml(
    runs,
    grid_w: int,
    grid_h: int,
    viewbox_origin: tuple[float, float] = (-4.0, -3.0),
    viewbox_size: tuple[float, float] = (23.0, 20.0),
) -> str:
    """Serialize RLE runs into SVG <rect> xml fragment in viewBox coordinates.

    viewbox_size must match the canvas aspect (grid_w/grid_h) so scaling is
    uniform and the sprite renders undistorted.
    """
    ox, oy = viewbox_origin
    vw, vh = viewbox_size
    cw = vw / grid_w
    ch = vh / grid_h
    lines = []
    for x, y, w, (r, g, b) in runs:
        vx = ox + x * cw
        vy = oy + y * ch
        vw_ = w * cw + 0.01
        vh_ = ch + 0.01
        lines.append(
            f'<rect x="{vx:.3f}" y="{vy:.3f}" width="{vw_:.3f}" '
            f'height="{vh_:.3f}" fill="#{r:02x}{g:02x}{b:02x}"/>'
        )
    return "\n      ".join(lines)


def sheet_apng(
    sheet_path: Path,
    cell_w: int,
    cell_h: int,
    row: int,
    n_frames: int,
    duration_ms: int = 125,
) -> bytes:
    """Slice one row of a spritesheet into an APNG (clawd's frame-animation
    format — same one calico uses, ~125ms/frame)."""
    im = Image.open(sheet_path)
    frames = [
        im.crop((x * cell_w, row * cell_h, (x + 1) * cell_w, (row + 1) * cell_h)).copy()
        for x in range(n_frames)
    ]
    out = io.BytesIO()
    frames[0].save(
        out, format="PNG", save_all=True, append_images=frames[1:],
        duration=duration_ms, loop=0,
    )
    return out.getvalue()
