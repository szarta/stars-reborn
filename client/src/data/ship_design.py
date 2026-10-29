"""
data/ship_design.py

Pure (Qt-free) logic for the Ship Designer's slot-fill editor: which component
categories a hull slot accepts, and an in-memory design model that tracks
slot assignments and recomputes cost/mass as parts are placed or removed.

Kept Qt-free so the rules are unit-testable headless, and shared by the Ship
Designer dialog. Hull and component dicts are the raw wire shapes served by the
engine (``GET /model/ships/hulls``, ``/model/starbase/hulls``,
``/model/technologies``) — kebab-case keys (``slot-type``, ``max-count``).

Slot-type → accepted-category mapping mirrors the engine's ``SlotType`` bitmask
(engine/src/game/objects/technology.rs); the schema notes composite slot types
"accept multiple component categories" but does not enumerate them, so the
mapping is interpreted here. When the host-side design validator lands
(engine task #145) the engine becomes the authority for legality and derived
combat stats; this module stays the client-side fast path for interactive
editing and the additive cost/mass preview.

:author: Brandon Arrendondo
:license: MIT, see LICENSE.txt for more details.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Component categories that a General Purpose slot admits: every installable
# ship component except engines (engine slots only) and orbital devices
# (stargates / mass drivers — starbase orbital slots only). "planetary" is a
# planetary-defense category, never slot-installed.
_GENERAL_PURPOSE = frozenset(
    {
        "weapons",
        "armor",
        "shields",
        "electrical",
        "mechanical",
        "bombs",
        "mine-layers",
        "mining-robots",
        "scanners",
    }
)

# Slot-type slug → the component categories it accepts. Composite slot types are
# the union of their parts, matching the engine SlotType bit unions (e.g.
# PROTECTION = ARMOR | SHIELDS, ORBITAL_ELECT = ORBITAL | ELECTRICAL). The
# component catalog exposes beam weapons and torpedoes under one "weapons"
# category, so the beam-/torpedo-specific slots accept "weapons" here; the
# engine validator will refine the beam-vs-torpedo split (#145).
SLOT_ACCEPTS: dict[str, frozenset[str]] = {
    "engines": frozenset({"engines"}),
    "weapons": frozenset({"weapons"}),
    "beam-weapons": frozenset({"weapons"}),
    "torpedoes": frozenset({"weapons"}),
    "armor": frozenset({"armor"}),
    "shields": frozenset({"shields"}),
    "protection": frozenset({"armor", "shields"}),
    "electrical": frozenset({"electrical"}),
    "mechanical": frozenset({"mechanical"}),
    "elect-mech": frozenset({"electrical", "mechanical"}),
    "bombs": frozenset({"bombs"}),
    "mine-layers": frozenset({"mine-layers"}),
    "mine-elect-mech": frozenset({"mine-layers", "electrical", "mechanical"}),
    "mining-robots": frozenset({"mining-robots"}),
    "scanners": frozenset({"scanners"}),
    "scanner-elect-mech": frozenset({"scanners", "electrical", "mechanical"}),
    "shield-elect-mech": frozenset({"shields", "electrical", "mechanical"}),
    "armor-scanner-elect-mech": frozenset({"armor", "scanners", "electrical", "mechanical"}),
    "weapon-shield": frozenset({"weapons", "shields"}),
    "orbital": frozenset({"orbital"}),
    "orbital-elect": frozenset({"orbital", "electrical"}),
    "general-purpose": _GENERAL_PURPOSE,
}

_COST_KEYS = ("ironium", "boranium", "germanium", "resources")


def slot_accepts(slot_type: str, component_category: str) -> bool:
    """Whether a slot of ``slot_type`` admits a component of ``component_category``.

    Unknown slot types accept nothing (fail closed) so an unrecognized hull
    slot never silently takes an arbitrary part.
    """
    return component_category in SLOT_ACCEPTS.get(slot_type, frozenset())


@dataclass
class DesignModel:
    """An in-memory ship/starbase design over a live hull layout.

    ``hull`` is a hull dict from the engine's hull catalog (carries ``slots``,
    ``cost``, ``mass``, ``name`` ...). ``assignments`` is parallel to
    ``hull["slots"]``; each entry is ``None`` (empty) or
    ``{"component": <catalog item dict>, "count": int}``.

    The model enforces category compatibility and per-slot ``max-count`` and
    recomputes the additive cost/mass preview. It does NOT compute derived
    combat stats (armor totals, shields, rating, cloak) — those are engine
    formulae (#145) and would desync if duplicated here.
    """

    hull: dict
    name: str = ""
    assignments: list = field(default_factory=list)

    def __post_init__(self) -> None:
        n = len(self.slots)
        if not self.assignments:
            self.assignments = [None] * n
        elif len(self.assignments) != n:
            raise ValueError(f"assignments length {len(self.assignments)} != hull slot count {n}")

    # ── slot accessors ──────────────────────────────────────────────────────
    @property
    def slots(self) -> list[dict]:
        return self.hull.get("slots", [])

    def slot_type(self, index: int) -> str:
        return self.slots[index].get("slot-type", "")

    def slot_max(self, index: int) -> int:
        return int(self.slots[index].get("max-count", 1) or 1)

    def accepts(self, index: int, component: dict) -> bool:
        """Whether ``component`` may be installed in slot ``index``."""
        return slot_accepts(self.slot_type(index), (component or {}).get("category", ""))

    # ── mutation ────────────────────────────────────────────────────────────
    def place(self, index: int, component: dict) -> bool:
        """Install one ``component`` in slot ``index``.

        Returns ``True`` when the slot changed. Fails (returns ``False``) if the
        component's category is incompatible with the slot, or if the slot is
        already full of that same component. Placing a different component into
        an occupied slot replaces its contents (count reset to 1), matching the
        original designer's drag-over-to-replace behavior.
        """
        if not self.accepts(index, component):
            return False
        current = self.assignments[index]
        if current is not None and current["component"].get("slug") == component.get("slug"):
            if current["count"] >= self.slot_max(index):
                return False
            current["count"] += 1
            return True
        self.assignments[index] = {"component": component, "count": 1}
        return True

    def remove_one(self, index: int) -> bool:
        """Remove one part from slot ``index`` (clearing it when it empties).

        Returns ``True`` when the slot changed.
        """
        current = self.assignments[index]
        if current is None:
            return False
        current["count"] -= 1
        if current["count"] <= 0:
            self.assignments[index] = None
        return True

    def clear(self, index: int) -> bool:
        """Empty slot ``index`` entirely. Returns ``True`` when it changed."""
        if self.assignments[index] is None:
            return False
        self.assignments[index] = None
        return True

    # ── derived preview (additive only) ──────────────────────────────────────
    def total_cost(self) -> dict[str, int]:
        """Hull cost plus the cost of every installed part × its count.

        Pure summation of catalog-provided mineral/resource costs — not a game
        formula — so it is safe to compute client-side for a live preview.
        """
        base = self.hull.get("cost", {}) or {}
        total = {k: int(base.get(k, 0) or 0) for k in _COST_KEYS}
        for entry in self.assignments:
            if entry is None:
                continue
            cost = entry["component"].get("cost", {}) or {}
            count = entry["count"]
            for k in _COST_KEYS:
                total[k] += int(cost.get(k, 0) or 0) * count
        return total

    def total_mass(self) -> int:
        """Hull mass plus the mass of every installed part × its count (kT)."""
        total = int(self.hull.get("mass", 0) or 0)
        for entry in self.assignments:
            if entry is None:
                continue
            mass = entry["component"].get("mass", 0) or 0
            total += int(mass) * entry["count"]
        return total

    def filled_slot_count(self) -> int:
        """How many slots hold at least one part (drives the editor summary)."""
        return sum(1 for a in self.assignments if a is not None)
