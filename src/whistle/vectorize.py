"""Sprite → SVG vector rects (RLE-merged per row)."""
from pathlib import Path
from PIL import Image


def vectorize_sprite(
    image_path: Path,
    grid_size: int = 96,
    eye_mask_boxes: list[tuple[int, int, int, int]] | None = None,
    sclera_color: tuple[int, int, int, int] = (240, 244, 251, 255),
) -> tuple[list[tuple[float, float, float, tuple[int, int, int]]], int]:
    """Downsample sprite to grid_size × grid_size and RLE-merge horizontal runs.

    Returns (runs, grid) where runs is list of (x, y, w, (r,g,b)).
    If eye_mask_boxes given, those regions are flattened to sclera_color
    (so the caller can overlay their own #eyes-js group).
    """
    img = Image.open(image_path).convert("RGBA")

    # Optional eye-pupil erase
    if eye_mask_boxes:
        px = img.load()

        def is_iris_like(r: int, g: int, b: int) -> bool:
            return b > 130 and r < 100 and (b - r) > 30

        for x0, y0, x1, y1 in eye_mask_boxes:
            for y in range(y0, y1):
                for x in range(x0, x1):
                    r, g, b, a = px[x, y]
                    if a > 0 and is_iris_like(r, g, b):
                        px[x, y] = sclera_color

    small = img.resize((grid_size, grid_size), Image.NEAREST)
    px = small.load()
    runs = []
    for y in range(grid_size):
        run_start = None
        run_color = None
        for x in range(grid_size):
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
            runs.append((run_start, y, grid_size - run_start, run_color))
    return runs, grid_size


def runs_to_rect_xml(
    runs,
    grid: int,
    viewbox_origin: tuple[float, float] = (-4.0, -3.0),
    viewbox_size: tuple[float, float] = (23.0, 20.0),
) -> str:
    """Serialize RLE runs into SVG <rect> xml fragment in viewBox coordinates."""
    ox, oy = viewbox_origin
    vw, vh = viewbox_size
    cw = vw / grid
    ch = vh / grid
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
