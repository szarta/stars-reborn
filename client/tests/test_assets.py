"""Unit tests for the slug-based icon-path convention (src.data.assets):
component and hull relative paths, hull-variant parsing, and variant discovery.

Pure path logic; no running Qt application."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "client"))

from src.data.assets import (  # noqa: E402
    component_icon_relpath,
    hull_icon_filename,
    hull_variants,
    parse_hull_icon,
)


def test_component_relpath_is_category_slash_slug():
    assert component_icon_relpath("engines", "quick_jump_5") == "engines/quick_jump_5.png"
    # Slugs are filename-safe: punctuation in the display name is already gone.
    assert component_icon_relpath("engines", "settlers_delight") == "engines/settlers_delight.png"


def test_hull_icon_filename():
    assert hull_icon_filename("battle_cruiser", 1) == "battle_cruiser-1.png"
    assert hull_icon_filename("death_star", 3) == "death_star-3.png"
    assert hull_icon_filename("scout") == "scout-1.png"  # default variant


def test_parse_hull_icon_splits_slug_and_variant():
    assert parse_hull_icon("battle_cruiser-1.png") == ("battle_cruiser", 1)
    assert parse_hull_icon("b17_bomber-4.png") == ("b17_bomber", 4)
    # Slug with no -<digits> tail is not a variant file.
    assert parse_hull_icon("scout.png") is None
    assert parse_hull_icon("not-an-icon") is None


def test_hull_variants_discovers_sorted(tmp_path):
    for name in ("cruiser-2.png", "cruiser-1.png", "cruiser-10.png", "scout-1.png", "cruiser.png"):
        (tmp_path / name).write_bytes(b"")
    assert hull_variants(tmp_path, "cruiser") == [1, 2, 10]
    assert hull_variants(tmp_path, "scout") == [1]
    assert hull_variants(tmp_path, "nubian") == []


def test_real_assets_follow_the_convention():
    """Every shipped hull/component icon parses as a valid slug (guards against a
    regression to the old name-based naming)."""
    hulls_dir = REPO / "client" / "assets" / "png" / "hulls"
    for png in hulls_dir.glob("*.png"):
        parsed = parse_hull_icon(png.name)
        assert parsed is not None, f"{png.name} is not <slug>-<variant>.png"
        slug, variant = parsed
        assert slug == slug.lower() and " " not in slug and "-" not in slug
        assert variant >= 1

    comp_dir = REPO / "client" / "assets" / "png" / "components"
    for png in comp_dir.rglob("*.png"):
        stem = png.stem
        assert stem == stem.lower() and " " not in stem and "-" not in stem, png.name
