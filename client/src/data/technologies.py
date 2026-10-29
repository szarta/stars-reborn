"""
data/technologies.py

Pure (Qt-free) helpers for the component technology catalog served by the engine
at ``GET /model/technologies``. Shared by the Technology Browser dialog and the
Ship Designer component picker (category grouping + availability filtering +
icon-filename derivation). No Qt imports so the logic is unit-testable headless.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

# Human-readable labels for the schema's `category` slugs, in the order the
# original Technology Browser's dropdown lists them.
CATEGORY_ORDER = [
    ("armor", "Armor"),
    ("shields", "Shields"),
    ("weapons", "Weapons"),
    ("bombs", "Bombs"),
    ("electrical", "Electrical"),
    ("engines", "Engines"),
    ("mechanical", "Mechanical"),
    ("mine-layers", "Mine Layers"),
    ("mining-robots", "Mining Robots"),
    ("orbital", "Orbital"),
    ("planetary", "Planetary"),
    ("scanners", "Scanners"),
]
CATEGORY_LABELS = dict(CATEGORY_ORDER)


def icon_filename(name: str) -> str:
    """Component display name -> icon filename (``Quick Jump 5`` -> ``Quick-Jump-5.png``)."""
    return "-".join(name.split()) + ".png"


def group_by_category(items: list[dict]) -> tuple[dict[str, list[dict]], list[str]]:
    """Group tech items by ``category`` (catalog order preserved) and return the
    category slugs present, ordered canonically with any unknowns appended."""
    by_category: dict[str, list[dict]] = {}
    for item in items:
        by_category.setdefault(item.get("category", ""), []).append(item)
    ordered = [slug for slug, _ in CATEGORY_ORDER if slug in by_category]
    ordered += [c for c in by_category if c not in CATEGORY_LABELS]
    return by_category, ordered


def component_available(item: dict, prt: str, lrts) -> bool:
    """Whether a race with the given PRT/LRTs can build ``item``.

    Trait-based gate from the item's ``requirement``: null admits everyone; a
    ``prt`` list restricts to those PRTs; an ``lrt`` list requires ALL of them;
    ``mystery-trader`` items are not buildable without a trade. (A current
    tech-level check would make this exact; callers can add it when the client
    player object carries per-field tech levels.)
    """
    req = item.get("requirement")
    if req is None:
        return True
    prt = (prt or "").upper()
    lrt_set = {s.upper() for s in (lrts or [])}
    if req.get("mystery-trader"):
        return False
    prt_list = req.get("prt")
    if prt_list is not None and prt not in {s.upper() for s in prt_list}:
        return False
    lrt_list = req.get("lrt")
    if lrt_list is not None and not {s.upper() for s in lrt_list} <= lrt_set:
        return False
    return True
