# whistle

Blow the whistle → any character sprite becomes a living desktop pet.

> A one-command pipeline that turns a static character image into an animated,
> eye-tracking [clawd-on-desk](https://github.com/rullerzhou-afk/clawd-on-desk)
> theme.

## What it does

Give whistle a character image (any pixel or chibi-style PNG/GIF with
transparent background). Get back a clawd-on-desk theme with:

- Vector-encoded sprite rendered as ~1000 SVG `<rect>`s (sanitizer-safe, no raster embed)
- Mouse-following eyes via the `#eyes-js` group clawd-on-desk mutates
- 8 state files (idle / thinking / working / error / attention / notification / sleeping / waking)
  with natural per-state effects (breathe, bounce, shake, jump, blink, Zzz, stretch)
- Optional overlay layers: speech bubble, monitor+keyboard, ERROR mark, sparkles, `!`, `Z` glyphs
- Optional character-customization pass: white streak / ribbon / badge / hoof pattern
  (parameterized — not Teio-specific)

## Install

```bash
pip install -e .  # from the repo root
```

## One-command usage

```bash
whistle build \
    --image ./your-sprite.png \
    --name my-pet \
    --eye-left 207,277 \
    --eye-right 255,277 \
    --out ~/Library/Application\ Support/clawd-on-desk/themes/
```

Then restart clawd-on-desk and right-click → Theme → "my-pet".

## Config file

For more customization (color tints, decorations, per-state animation params):

```bash
whistle build --config ./my-pet.yaml
```

See `examples/config.example.yaml`.

## As a Claude Code skill

`SKILL.md` is included. Add this repo to your `~/.claude/plugins/` and run:

```
/whistle build <image-path>
```

## Design

See `docs/DESIGN.md` — based on a battle-tested 9-iteration review of
clawd-on-desk's sanitizer behavior, SVG eye-tracking conventions, and
Chromium-under-`<object>` CSS animation support.

## License

MIT
