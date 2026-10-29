"""
data/defaults.py

Default game parameters for the simple New Game path.

All confirmed values are from the original Stars! client.
The Advanced Game path lets the player override any of these.
See stars-reborn-research/knowledge/findings/new_game_defaults.rst.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlanetData:
    """Duck-typed planet object understood by SpaceMap and InfoPanel.

    Field shape mirrors the engine's per-player turn file (PlayerView):
    identity (id, name, x, y) is always present; contents fields are
    populated only for planets the player has observed (penetrating-scan
    range or owned). For never-observed planets contents stay at their
    None / 0 defaults and ``years_since`` is -1.

    See stars-reborn-design/docs/architecture.rst (Per-Player Visibility).
    """

    id: int
    name: str
    x: float
    y: float

    # Identity-adjacent (always present in current engine output).
    homeworld: bool = False
    owner: int | None = None
    population: int = 0
    years_since: int = 0  # 0 = scanned this turn; -1 = never observed.

    # Hab — None for never-observed; concrete value for observed.
    gravity: float | None = None
    temperature: int | None = None
    radiation: int | None = None

    # Mineral concentrations (1..100) — None for never-observed.
    ironium_concentration: int | None = None
    boranium_concentration: int | None = None
    germanium_concentration: int | None = None

    # Surface minerals in kT — 0 default is fine (panels render "0 kT").
    surface_ironium: int = 0
    surface_boranium: int = 0
    surface_germanium: int = 0

    # Installations — 0 default for never-observed and unowned planets.
    factories: int = 0
    mines: int = 0

    # Planet value (0..100 habitable, negative red, capped at -45) computed
    # against the viewing player's race. None for never-observed planets.
    value: int | None = None

    # Resources generated per year — a derived value the engine recomputes each
    # turn, present only for an owned planet. None for unowned/unobserved
    # planets and when the engine cannot compute it (e.g. an AR race). The
    # Status section shows "n/a" while absent.
    resources_per_year: int | None = None

    # Production queue — present (a list, possibly empty) only for planets the
    # viewing player owns; ``None`` for unowned/unobserved planets, since the
    # engine emits build-queue only for owned planets (production is private).
    # Each entry: {"build_object_id", "build_quantity", "build_progress"}.
    build_queue: list[dict] | None = field(default=None)

    # "Route To" destination: planet id arriving route-flagged fleets are sent
    # to, or None for no route. Emitted only for owned planets.
    route_target: int | None = None

    # Starbase stats for an owned planet that has a starbase, or ``None`` when
    # the planet has no starbase (also unowned/unobserved). Snake-keyed dict:
    # {"dock_capacity", "armor", "shields", "damage_percent", "mass_driver",
    # "packet_target"}. The engine does not serialize this yet (parallel to the
    # Status-section fields, task #54); until it does it stays ``None``.
    starbase: dict | None = None

    @classmethod
    def from_turn_planet(cls, p: dict) -> PlanetData:
        """Build a ``PlanetData`` from one entry in the engine's PlayerView.

        The engine emits either an Observed planet (full contents) or an
        Unobserved planet (only id/name/x/y). Wire field names are
        kebab-case per the project schema convention
        (stars-reborn-schemas/response-turn-file.json). Fields absent
        from the JSON — the never-observed case — fall back to the
        dataclass defaults (``None`` for hab/concentrations/value, ``0``
        for surface and installations, ``-1`` for ``years_since``).
        """
        return cls(
            id=p["id"],
            name=p["name"],
            x=float(p["x"]),
            y=float(p["y"]),
            homeworld=p.get("homeworld", False),
            owner=p.get("owner"),
            population=p.get("population", 0),
            years_since=p.get("years-since-last-scan", -1),
            gravity=p.get("gravity"),
            temperature=p.get("temperature"),
            radiation=p.get("radiation"),
            ironium_concentration=p.get("ironium-concentration"),
            boranium_concentration=p.get("boranium-concentration"),
            germanium_concentration=p.get("germanium-concentration"),
            surface_ironium=p.get("surface-ironium", 0),
            surface_boranium=p.get("surface-boranium", 0),
            surface_germanium=p.get("surface-germanium", 0),
            factories=p.get("factories", 0),
            mines=p.get("mines", 0),
            value=p.get("value"),
            resources_per_year=p.get("resources-per-year"),
            build_queue=cls._queue_from_wire(p.get("build-queue")),
            route_target=p.get("route-target"),
            starbase=cls._starbase_from_wire(p.get("starbase")),
        )

    @staticmethod
    def _starbase_from_wire(sb) -> dict | None:
        """Normalize the wire ``starbase`` object (kebab keys) into a
        snake-keyed dict, or ``None`` when the key is absent (no starbase, or
        an unowned planet). The engine does not emit this field yet, so today
        this is always ``None``; the mapping is in place for when it lands."""
        if not sb:
            return None
        return {
            "dock_capacity": sb.get("dock-capacity"),
            "armor": sb.get("armor"),
            "shields": sb.get("shields"),
            "damage_percent": sb.get("damage-percent"),
            "mass_driver": sb.get("mass-driver"),
            "packet_target": sb.get("packet-target"),
        }

    @staticmethod
    def _queue_from_wire(items) -> list[dict] | None:
        """Normalize the wire ``build-queue`` (kebab keys) into snake-keyed
        entries. ``None`` when the key is absent (an unowned planet)."""
        if items is None:
            return None
        return [
            {
                "build_object_id": it["build-object-id"],
                "build_quantity": it.get("build-quantity", 0),
                "build_progress": it.get("build-progress") or 0,
            }
            for it in items
        ]


@dataclass
class MessageData:
    """One per-turn message in the player's turn file.

    Mirrors the engine's ``turn-message`` wire shape (the design-target
    ``schemas/turn.json``): a stable id, the rendered display ``text``, a
    ``message_type`` tag, and optional references to the space object or battle
    the message is about. ``related_object`` is a universe-wide space-object id
    (a planet or fleet) and is the "Goto" subject the Messages pane navigates to.

    ``important`` drives the pane's filter: with the "hide unimportant messages"
    filter on, messages flagged unimportant are hidden. Importance is a property
    of the message that the engine classifies — the client never hardcodes a
    type→importance table (see the data-model invariant in CLAUDE.md). The
    engine does not serialize messages yet (parallel to the Status/Starbase
    fields, tasks #54/#142); until it does, the turn file carries no ``messages``
    and the pane reads empty. ``important`` defaults True so that, once messages
    arrive, an unclassified message is shown rather than silently hidden.
    """

    id: int
    text: str
    message_type: str | None = None
    related_object: int | None = None  # space-object-id (planet or fleet)
    related_battle: int | None = None
    important: bool = True

    @classmethod
    def from_turn_message(cls, m: dict) -> MessageData:
        """Build a ``MessageData`` from one entry in the turn file's
        ``messages`` array. Wire field names are kebab-case per the project
        schema convention; absent fields fall back to the dataclass defaults."""
        return cls(
            id=m.get("id", 0),
            text=m.get("message", ""),
            message_type=m.get("message-type"),
            related_object=m.get("related-object"),
            related_battle=m.get("related-battle"),
            important=m.get("important", True),
        )


@dataclass
class ScoreData:
    """The viewing player's F10 score breakdown from the turn file (see
    docs/mechanics/victory.rst).

    Each category carries its raw ``count`` and the ``points`` it contributes;
    ``total`` is their sum. Points come straight from the engine — the client
    never recomputes the formula (CLAUDE.md data-model invariant). Starbase and
    ship categories read 0 until those models land in the engine.
    """

    total: int = 0
    planet_count: int = 0
    planet_points: int = 0
    starbase_count: int = 0
    starbase_points: int = 0
    unarmed_count: int = 0
    unarmed_points: int = 0
    escort_count: int = 0
    escort_points: int = 0
    capital_count: int = 0
    capital_points: int = 0
    tech_level_sum: int = 0
    tech_points: int = 0
    resource_amount: int = 0
    resource_points: int = 0

    @classmethod
    def from_turn_score(cls, s: dict | None) -> ScoreData | None:
        """Build a ``ScoreData`` from the turn file's ``score`` object, or
        ``None`` when the turn file carries no score (an older engine)."""
        if not s:
            return None
        return cls(
            total=s.get("total", 0),
            planet_count=s.get("planet-count", 0),
            planet_points=s.get("planet-points", 0),
            starbase_count=s.get("starbase-count", 0),
            starbase_points=s.get("starbase-points", 0),
            unarmed_count=s.get("unarmed-count", 0),
            unarmed_points=s.get("unarmed-points", 0),
            escort_count=s.get("escort-count", 0),
            escort_points=s.get("escort-points", 0),
            capital_count=s.get("capital-count", 0),
            capital_points=s.get("capital-points", 0),
            tech_level_sum=s.get("tech-level-sum", 0),
            tech_points=s.get("tech-points", 0),
            resource_amount=s.get("resource-amount", 0),
            resource_points=s.get("resource-points", 0),
        )


# Universe edge length (ly) -> size name, per the engine's DIMENSIONS table
# (engine/src/game/universe/mod.rs). A square map off this table reads "Custom".
_UNIVERSE_SIZES = {400: "Tiny", 800: "Small", 1200: "Medium", 1600: "Large", 2000: "Huge"}


def universe_size_label(width, height) -> str:
    """Human label for a universe of ``width`` x ``height`` ly: the named size
    when it matches the standard square dimensions, else 'Custom'."""
    try:
        w, h = int(width), int(height)
    except (TypeError, ValueError):
        return "n/a"
    name = _UNIVERSE_SIZES.get(w) if w == h else None
    prefix = f"{name} " if name else "Custom "
    return f"{prefix}({w} × {h} ly)"


def game_parameters_rows(
    game_name, year, universe_w, universe_h, planet_count
) -> list[tuple[str, str]]:
    """The Game Parameters shown from data the client already has. Settings the
    engine does not persist yet (victory conditions, play flags, player roster,
    difficulty) are omitted rather than shown as 'n/a' — see the engine
    follow-up."""
    return [
        ("Game Name", str(game_name)),
        ("Year", str(year)),
        ("Universe Size", universe_size_label(universe_w, universe_h)),
        ("Planets", str(planet_count)),
    ]


def _hab_range(axis: dict | None, unit: str) -> str:
    """Display string for one habitat axis from the race's ``hab`` object:
    'Immune', or 'lo – hi<unit>'. Falls back to 'n/a' when bounds are absent."""
    if not axis:
        return "n/a"
    if axis.get("immune"):
        return "Immune"
    lo, hi = axis.get("min"), axis.get("max")
    if lo is None or hi is None:
        return "n/a"
    return f"{lo:g}{unit} – {hi:g}{unit}"


def race_summary(race: dict | None) -> list[tuple[str, list[tuple[str, str]]]]:
    """A read-only summary of a race (the turn file's ``race`` object, snake-keyed)
    as ``(section_title, [(label, value), ...])`` groups for the Race view.

    Returns an empty list when there is no race. Pure/Qt-free so it can be unit
    tested; the dialog only lays the rows out.
    """
    if not race:
        return []
    hab = race.get("hab") or {}
    eco = race.get("economy") or {}
    rc = race.get("research_costs") or {}
    lrts = race.get("lrts") or []

    identity = [
        ("Name", str(race.get("name", "—"))),
        ("Plural", str(race.get("plural_name", "—"))),
        ("Primary Trait", str(race.get("prt", "—"))),
        ("Lesser Traits", ", ".join(lrts) if lrts else "None"),
    ]
    habitability = [
        ("Gravity", _hab_range(hab.get("gravity"), "g")),
        ("Temperature", _hab_range(hab.get("temperature"), "°C")),
        ("Radiation", _hab_range(hab.get("radiation"), "mR")),
        (
            "Growth Rate",
            f"{eco.get('growth_rate')}%" if eco.get("growth_rate") is not None else "n/a",
        ),
    ]
    economy = [
        ("Colonists per Resource", str(eco.get("resource_production", "n/a"))),
        ("Factory Output", str(eco.get("factory_production", "n/a"))),
        ("Factory Cost", str(eco.get("factory_cost", "n/a"))),
        ("Operate Factories", str(eco.get("colonists_operate_factories", "n/a"))),
        ("Mine Output", str(eco.get("mine_production", "n/a"))),
        ("Mine Cost", str(eco.get("mine_cost", "n/a"))),
        ("Operate Mines", str(eco.get("colonists_operate_mines", "n/a"))),
    ]
    research = [
        (field.capitalize(), str(rc.get(field, "n/a")))
        for field in (
            "energy",
            "weapons",
            "propulsion",
            "construction",
            "electronics",
            "biotechnology",
        )
    ]
    return [
        ("Race", identity),
        ("Habitability", habitability),
        ("Economy", economy),
        ("Research Costs", research),
    ]


def find_planet_matches(planets, query: str) -> list[tuple[int, str]]:
    """``(id, name)`` for planets whose name matches ``query`` (case-insensitive
    substring), sorted by name. An empty/blank query matches every planet.

    Find searches all planets, not just observed ones: planet names and
    positions come from the shared .xy data, so a player can jump to any planet
    by name even before scanning its contents.
    """
    q = (query or "").strip().lower()
    out = [(p.id, p.name) for p in planets if not q or q in p.name.lower()]
    out.sort(key=lambda t: t[1])
    return out


def planet_report_rows(planets, player_id) -> list[dict]:
    """Rows for the F3 Planets report: one dict per planet the player can see
    the contents of (observed — ``value`` is set), sorted by name.

    Each row carries the planet ``id`` (for jump-to-planet) plus the columns the
    turn file provides today. ``owned`` flags the player's own worlds. Never-
    observed planets (identity only) are omitted — they have no contents to
    report; they appear once scanning surfaces foreign planets.
    """
    rows: list[dict] = []
    for p in planets:
        if getattr(p, "value", None) is None:
            continue
        rows.append(
            {
                "id": p.id,
                "name": p.name,
                "owned": getattr(p, "owner", None) == player_id,
                "value": getattr(p, "value", 0),
                "population": getattr(p, "population", 0),
                "resources": getattr(p, "resources_per_year", None),
                "mines": getattr(p, "mines", 0),
                "factories": getattr(p, "factories", 0),
                "ironium": getattr(p, "surface_ironium", 0),
                "boranium": getattr(p, "surface_boranium", 0),
                "germanium": getattr(p, "surface_germanium", 0),
            }
        )
    rows.sort(key=lambda r: r["name"])
    return rows


def score_rows(score: ScoreData) -> list[tuple[str, int, int]]:
    """The F10 breakdown table as ``(label, count, points)`` rows, in the
    original Score-sheet order. The row ``count`` is the raw tally the category
    is scored from (planets owned, ships, tech-level sum, annual resources)."""
    return [
        ("Planets", score.planet_count, score.planet_points),
        ("Starbases", score.starbase_count, score.starbase_points),
        ("Unarmed Ships", score.unarmed_count, score.unarmed_points),
        ("Escort Ships", score.escort_count, score.escort_points),
        ("Capital Ships", score.capital_count, score.capital_points),
        ("Tech Levels", score.tech_level_sum, score.tech_points),
        ("Resources", score.resource_amount, score.resource_points),
    ]


# Default game name keyed on (difficulty, universe_size).
# This is a fixed lookup table in the original — NOT randomly generated.
# Confirmed: all Easy entries; Standard/Small.
# Remaining cells (Standard Tiny/Med/Large/Huge; all Harder; all Expert) are unknown.
# See stars-reborn-research/knowledge/findings/new_game_defaults.rst.
GAME_NAME_TABLE: dict[tuple[str, str], str] = {
    ("easy", "tiny"): "Shooting Fish in a Barrel",
    ("easy", "small"): "A Walk in the Park",
    ("easy", "medium"): "Sleepwalking in Paradise",
    ("easy", "large"): "The Big Easy",
    ("easy", "huge"): "Eternal Bliss",
    ("normal", "tiny"): "Duck Hunt",
    ("normal", "small"): "A Barefoot JayWalk",
    ("normal", "medium"): "A Rumble in the Jungle",
    ("normal", "large"): "Infected Root Canal",
    ("normal", "huge"): "Jungle Safari",
    ("tough", "tiny"): "Micro-Hardball",
    ("tough", "small"): "Roller Ball",
    ("tough", "medium"): "Wall Street",
    ("tough", "large"): "Big League",
    ("tough", "huge"): "Long Road to Morning",
    ("expert", "tiny"): "Tough Nuts",
    ("expert", "small"): "Blade Runner",
    ("expert", "medium"): "D-Day",
    ("expert", "large"): "World War III",
    ("expert", "huge"): "Eternity in Hell",
}

_GAME_NAME_FALLBACK = "New Game"


def default_game_name(difficulty: str, universe_size: str) -> str:
    """Return the original game's default name for this difficulty/size pair.
    Falls back to 'New Game' for combinations not yet confirmed."""
    return GAME_NAME_TABLE.get((difficulty, universe_size), _GAME_NAME_FALLBACK)


# Default game flags — all false for the Standard path.
DEFAULT_GAME_FLAGS: dict[str, bool] = {
    "maximum-minerals": False,
    "slow-tech-advances": False,
    "accelerated-play": False,
    "random-events": True,  # "No Random Events" defaults to false → events on
    "ai-alliances": False,
    "public-player-scores": False,
    "galaxy-clumping": False,
}

# Default victory conditions for Standard / Small.
DEFAULT_VICTORY_CONDITIONS: dict = {
    "number-of-conditions-met": 1,
    "minimum-years": 50,
    "percent-planets": 60,
    "tech-level-required": 22,
    "tech-fields": 4,
    "exceeds-second-place-by-percent": 100,
}

# Default AI player count keyed on universe size.
# Confirmed across all four difficulties — size is the sole determiner.
DEFAULT_AI_COUNT: dict[str, int] = {
    "tiny": 1,
    "small": 2,
    "medium": 6,
    "large": 11,
    "huge": 15,
}


def build_new_game_request(
    *,
    universe_size: str,
    difficulty: str,
    race_name: str,
) -> dict:
    """
    Assemble a request-create-new-game.json payload from the simple dialog
    selections plus confirmed defaults.  The game name is looked up from the
    confirmed difficulty × size table.
    """
    game_name = default_game_name(difficulty, universe_size)

    return {
        "game": {
            "name": game_name,
            "human-players": [
                {
                    "id": 0,
                    "race": race_name,
                }
            ],
            "ai-players": [
                {"difficulty": difficulty} for _ in range(DEFAULT_AI_COUNT[universe_size])
            ],
            "player-starting-distance": "moderate",
            "universe": {
                "size": universe_size,
                "density": "normal",
            },
            **DEFAULT_GAME_FLAGS,
            "victory-conditions": DEFAULT_VICTORY_CONDITIONS,
        }
    }
