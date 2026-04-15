---
name: whistle
description: Turn any character image into an animated clawd-on-desk desktop-pet theme with eye tracking. Use when the user wants to replace clawd's default crab with their own character, or build a custom pet theme from a static sprite.
---

# whistle

## When to invoke

- User says "make my character into a clawd-on-desk theme"
- User says "I want a desktop pet of <character> with <image>"
- User wants eye-tracking or per-state animation on a custom sprite

## Inputs

- **image** (required): path to a PNG/GIF with transparent background. Recommended 256×256 or larger, square-ish, character centered.
- **name** (required): theme id (kebab-case).
- **eye_left, eye_right** (optional): pixel coordinates of eye centers in the source image. If omitted, auto-detect blue/navy clusters in upper-central region.
- **config** (optional): YAML file for advanced customization (tint, decorations, state timing).
- **out** (optional): output directory. Default `~/Library/Application Support/clawd-on-desk/themes/`.

## Process

1. Run `whistle build --image <path> --name <name>`.
2. Tool emits SVG + APNG state files + theme.json.
3. Instruct user to restart clawd-on-desk and select the theme from right-click menu.

## Verification

Validate the output directory by running:
```
node clawd-on-desk/scripts/validate-theme.js <out-dir>/<name>
```

If validation passes, eye tracking should work on idle state and all 8 base states should render.

## Notes

- Image must have a transparent background (alpha channel) or a uniform background color that can be keyed out.
- For SD/chibi sprites the pipeline works best; photographic sprites will look strange once vectorized.
- Character IP: this tool does not fetch or redistribute images. The user provides them.
