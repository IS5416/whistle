"""#eyes-js group generator for clawd-on-desk eye tracking."""


def eyes_js_xml(
    left_px: tuple[int, int],
    right_px: tuple[int, int],
    sprite_w: int = 512,
    sprite_h: int = 512,
    viewbox_origin: tuple[float, float] = (-4.0, -3.0),
    viewbox_size: tuple[float, float] = (23.0, 20.0),
    eye_w: float = 0.6,
    eye_h: float = 0.7,
    highlight_w: float = 0.18,
    highlight_h: float = 0.18,
    pupil_color: str = "#2D4F98",
    highlight_color: str = "#3AACDF",
) -> str:
    """Build the <g id='eyes-js'> block with navy pupil + cyan highlight per eye.

    viewbox_origin/size must match the sprite's content box (aspect-matched
    to the source) so eyes land where the erased iris pixels were.
    """
    ox, oy = viewbox_origin
    vw, vh = viewbox_size

    def sx(px: int) -> float:
        return ox + (px / sprite_w) * vw

    def sy(py: int) -> float:
        return oy + (py / sprite_h) * vh

    lx, ly = sx(left_px[0]), sy(left_px[1])
    rx, ry = sx(right_px[0]), sy(right_px[1])

    def eye(cx: float, cy: float) -> str:
        iris = (
            f'<rect x="{cx - eye_w/2:.3f}" y="{cy - eye_h/2:.3f}" '
            f'width="{eye_w}" height="{eye_h}" fill="{pupil_color}"/>'
        )
        hl = (
            f'<rect x="{cx + 0.05:.3f}" y="{cy + 0.10:.3f}" '
            f'width="{highlight_w}" height="{highlight_h}" fill="{highlight_color}"/>'
        )
        return iris + "\n      " + hl

    return (
        '<g id="eyes-js" transform="translate(0,0)">\n      '
        + eye(lx, ly)
        + "\n      "
        + eye(rx, ry)
        + "\n    </g>"
    )
