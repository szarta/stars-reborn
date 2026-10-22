"""
Procedural "unknown planet" icon generator for Stars Reborn.

Produces a single 100x100 RGBA PNG showing a stylized line-art sphere — used
in the planet detail panel and the left-column planet header when the player
has never surveyed a planet. The aesthetic is a topographic-survey sketch:
crisp ink contours over a faint disc fill, deterministic from a fixed seed
so the asset is reproducible.

Usage:
    python tools/generate_unknown_planet.py
    python tools/generate_unknown_planet.py --out assets/png/planets/unknown.png
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 100
INK = np.array([34, 40, 56], dtype=np.float32)  # cool charcoal
FILL = np.array([225, 228, 235], dtype=np.float32)  # faint blue-grey wash
FILL_ALPHA = 110  # 0..255 (~43%)
DEFAULT_SEED = 7  # picked by eye for a nice mix of contours + craters


def sphere_coords(size: int):
    xs = np.linspace(-1.0, 1.0, size, dtype=np.float32)
    ys = np.linspace(-1.0, 1.0, size, dtype=np.float32)
    nx, ny = np.meshgrid(xs, ys)
    r2 = nx * nx + ny * ny
    mask = r2 <= 1.0
    z = np.zeros_like(nx)
    z[mask] = np.sqrt(1.0 - r2[mask])
    return nx, ny, z, mask, r2


def rotate_yaw_pitch(nx, ny, z, yaw: float, pitch: float):
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    x1 = cy * nx + sy * z
    z1 = -sy * nx + cy * z
    y2 = cp * ny - sp * z1
    z2 = sp * ny + cp * z1
    return x1, y2, z2


def make_field(seed: int, grid: int = 32) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.rand(grid, grid, grid).astype(np.float32)


def sample_value_noise(field: np.ndarray, x, y, z) -> np.ndarray:
    g = field.shape[0]
    x = np.mod(x, g)
    y = np.mod(y, g)
    z = np.mod(z, g)
    x0 = np.floor(x).astype(np.int32) % g
    y0 = np.floor(y).astype(np.int32) % g
    z0 = np.floor(z).astype(np.int32) % g
    x1 = (x0 + 1) % g
    y1 = (y0 + 1) % g
    z1 = (z0 + 1) % g
    fx = x - np.floor(x)
    fy = y - np.floor(y)
    fz = z - np.floor(z)
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    fz = fz * fz * (3 - 2 * fz)
    c000 = field[x0, y0, z0]
    c100 = field[x1, y0, z0]
    c010 = field[x0, y1, z0]
    c110 = field[x1, y1, z0]
    c001 = field[x0, y0, z1]
    c101 = field[x1, y0, z1]
    c011 = field[x0, y1, z1]
    c111 = field[x1, y1, z1]
    c00 = c000 * (1 - fx) + c100 * fx
    c10 = c010 * (1 - fx) + c110 * fx
    c01 = c001 * (1 - fx) + c101 * fx
    c11 = c011 * (1 - fx) + c111 * fx
    c0 = c00 * (1 - fy) + c10 * fy
    c1 = c01 * (1 - fy) + c11 * fy
    return c0 * (1 - fz) + c1 * fz


def fbm(field, x, y, z, octaves=4, lacunarity=2.0, persistence=0.55, scale=3.0):
    total = np.zeros_like(x, dtype=np.float32)
    amp = 1.0
    freq = scale
    max_amp = 0.0
    for _ in range(octaves):
        total = total + amp * sample_value_noise(field, x * freq, y * freq, z * freq)
        max_amp += amp
        amp *= persistence
        freq *= lacunarity
    return total / max_amp


def stroke_band(value: np.ndarray, level: float, width: float) -> np.ndarray:
    """Soft Gaussian band where `value` crosses `level`. Returns 0..1."""
    d = (value - level) / max(width, 1e-6)
    return np.exp(-(d * d))


def antialiased_disc_alpha(r2: np.ndarray, size: int) -> np.ndarray:
    r = np.sqrt(r2)
    edge_start = 1.0 - (1.0 / (size / 2))
    return np.clip((1.0 - r) / max(1.0 - edge_start, 1e-6), 0.0, 1.0)


def generate_unknown_planet(seed: int = DEFAULT_SEED, size: int = SIZE) -> Image.Image:
    nx, ny, z, mask, r2 = sphere_coords(size)
    sx, sy, sz = rotate_yaw_pitch(nx, ny, z, yaw=0.85, pitch=0.18)

    # Single low-frequency noise layer drives the continent boundaries. The
    # icon needs to read at 32px in the UI, so we keep features broad and
    # avoid overlapping strokes that turn into stipple.
    field = make_field(seed, grid=24)
    contour = fbm(field, sx, sy, sz, octaves=2, scale=1.8, persistence=0.5)

    lo, hi = np.percentile(contour[mask], [3, 97])
    contour = np.clip((contour - lo) / max(hi - lo, 1e-6), 0.0, 1.0)

    # Two contour levels = a few sweeping coastline-like curves across the disc.
    line = np.zeros_like(contour, dtype=np.float32)
    for lvl, w, strength in (
        (0.40, 0.025, 0.95),
        (0.62, 0.025, 0.85),
    ):
        line = np.maximum(line, stroke_band(contour, lvl, w) * strength)

    # A small handful of crater rings, hand-placed in normalized disc coords
    # (cx, cy in [-1, 1], radius in disc units). Foreshortened toward the limb
    # so they sit on the sphere rather than floating in 2D.
    craters = [
        (-0.30, -0.18, 0.16),
        (0.22, 0.30, 0.12),
        (0.45, -0.35, 0.09),
        (-0.45, 0.28, 0.10),
        (0.05, -0.55, 0.08),
    ]
    for cx, cy, rad in craters:
        # Sphere-surface distance from crater centre, approximated via the
        # great-circle distance in 2D after compressing along the limb.
        dx = nx - cx
        dy = ny - cy
        # Foreshorten by local z so craters near the limb get squashed.
        local_z = np.sqrt(np.clip(1.0 - cx * cx - cy * cy, 1e-3, 1.0))
        d = np.sqrt(dx * dx + dy * dy) / max(rad, 1e-3)
        ring = stroke_band(d, 1.0, 0.10) * local_z
        line = np.maximum(line, ring * 0.85)

    # Limb (disc edge) stroke — crisp ring just inside the antialiased edge.
    r = np.sqrt(r2)
    limb = np.exp(-(((r - 0.965) / 0.012) ** 2)) * (r <= 1.0)
    line = np.maximum(line, limb * 1.0)

    # Mask everything to the disc.
    line *= mask

    # Compose: faint fill underneath, ink lines on top, antialiased disc alpha.
    rgb = np.empty((size, size, 3), dtype=np.float32)
    rgb[..., :] = FILL
    # Blend ink over fill weighted by line strength.
    line_a = np.clip(line, 0.0, 1.0)[..., None]
    rgb = rgb * (1.0 - line_a) + INK * line_a

    fill_alpha = (FILL_ALPHA / 255.0) + (1.0 - FILL_ALPHA / 255.0) * line[..., None].squeeze(-1)
    fill_alpha = np.clip(fill_alpha, 0.0, 1.0)
    disc_alpha = antialiased_disc_alpha(r2, size)
    alpha = fill_alpha * disc_alpha * 255.0

    rgba = np.concatenate([rgb, alpha[..., None]], axis=-1)
    rgba = np.clip(rgba, 0, 255).astype(np.uint8)
    img = Image.fromarray(rgba, mode="RGBA")
    _draw_question_mark(img, size)
    return img


_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
)


def _load_question_font(px: int) -> ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, px)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_question_mark(img: Image.Image, size: int):
    """Centred solid-black '?' overlay — marks the planet as unsurveyed."""
    draw = ImageDraw.Draw(img)
    font = _load_question_font(int(size * 0.72))
    bbox = draw.textbbox((0, 0), "?", font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) // 2 - bbox[0]
    y = (size - h) // 2 - bbox[1]
    draw.text((x, y), "?", fill=(0, 0, 0, 255), font=font)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("assets/png/planets/unknown.png"))
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    img = generate_unknown_planet(seed=args.seed)
    img.save(args.out, optimize=True)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
