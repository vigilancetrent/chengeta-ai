# Chengeta AI — Brand Assets

The complete logo and identity system. See [`BRAND_GUIDELINES.md`](../../BRAND_GUIDELINES.md)
for usage rules, colours, and typography.

| File | Format | Use |
|------|--------|-----|
| `logo.svg` | SVG | Primary horizontal lockup (light backgrounds) |
| `logo-white.svg` | SVG | Reversed lockup for dark backgrounds |
| `logo-mono.svg` | SVG | Single-colour lockup (`currentColor`) |
| `icon.svg` | SVG | Memory-vault infinity mark (full colour) |
| `icon-mono.svg` | SVG | Single-colour mark (`currentColor`) |
| `favicon.svg` | SVG | Rounded favicon / app tile |
| `social-banner.svg` | SVG 1500×500 | Social header (X/LinkedIn) |
| `github-banner.svg` | SVG 1280×640 | GitHub social-preview image |

All marks are pure SVG: resolution-independent, themeable, and tiny. The `-mono` variants inherit
the surrounding text colour via `currentColor`, so they adapt to any theme.

## Raster exports (`png/`)

Pre-rendered PNGs for surfaces that cannot consume SVG (PyPI, GitHub social preview, OG images,
app stores). The SVGs above remain the source of truth.

| File | Size | Use |
|------|------|-----|
| `png/icon-512.png` … `icon-32.png` | 512 / 256 / 128 / 64 / 32 | Product icon set (transparent) |
| `png/favicon-16.png`, `favicon-32.png`, `favicon-48.png` | 16 / 32 / 48 | Browser favicons |
| `png/apple-touch-icon-180.png` | 180×180 | iOS home-screen tile |
| `png/logo-600.png`, `logo-1200.png` | 600×144 / 1200×288 | Horizontal lockup (transparent) |
| `png/logo-white-1200.png` | 1200×288 | Reversed lockup for dark backgrounds |
| `png/logo-mono-1200.png` | 1200×288 | Single-colour lockup |
| `png/social-banner.png` | 1500×500 | Social header (X / LinkedIn) |
| `png/github-banner.png` | 1280×640 | GitHub social-preview upload |

## Palette

```
Forest Green   #0F5B3A      Deep Emerald   #1B7F5A
Gold           #C9A227      Bright Emerald #3DBF86
Black          #111111      Light Sand     #F7F3E8
White          #FFFFFF
```

## Regenerating the PNGs

The PNGs in `png/` were rendered from the SVGs with [resvg](https://github.com/linebender/resvg)
(faithful gradients, patterns, and text). To regenerate after editing an SVG, no global install is
needed — run it through `uv` with an ephemeral dependency:

```bash
uv run --with resvg-py python - <<'PY'
import resvg_py
for src, out, w, h in [
    ("icon.svg", "png/icon-512.png", 512, 512),
    ("github-banner.svg", "png/github-banner.png", 1280, 640),
    ("social-banner.svg", "png/social-banner.png", 1500, 500),
    ("logo.svg", "png/logo-1200.png", 1200, 288),
]:
    data = resvg_py.svg_to_bytes(svg_string=open(src, encoding="utf-8").read(), width=w, height=h)
    open(out, "wb").write(bytes(data))
    print("wrote", out)
PY
```

Any tool that rasterises SVG (resvg, Inkscape, `rsvg-convert`, or a headless browser) works
equally well — the SVGs are the source of truth.
