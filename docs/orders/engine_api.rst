Engine Order-Submission API
===========================

This document defines the JSON shape clients use to submit a player's
turn orders to the engine.  It is the |project| native equivalent of
the binary ``.xN`` file described in :doc:`x_file_format`.

Endpoint
--------

.. code-block:: text

   PUT /games/{game_id}/turns/{year}/orders/{pid}
   Content-Type: application/json

   <Submit-Orders Request body>

A successful response is ``204 No Content`` and signals the engine has
accepted the orders.  Validation failures return ``400`` with an
``error.json`` body identifying the offending order index and reason.
Submitting orders for a turn that is not the current edit turn, or for
a player the caller is not authorised to act for, returns ``409``.

Repeated PUTs are **replacement** operations: the engine stores the
last accepted order list per (game, year, player).  Clients may submit
partial lists incrementally during the edit phase by always sending
the full list — exactly mirroring the original game's behaviour of
re-emitting the entire ``.xN`` file on every save.

Request Envelope
----------------

The request body is a single JSON object with the following fields:

.. list-table::
   :header-rows: 1
   :widths: 22 14 64

   * - Field
     - Type
     - Description
   * - ``schema_version``
     - integer
     - Order-schema major version (currently ``1``).
   * - ``player_id``
     - integer
     - 0-based player id; must match the ``{pid}`` path parameter.
   * - ``turn_year``
     - integer
     - Year of the turn these orders apply to; must match ``{year}``.
   * - ``orders``
     - array
     - Ordered list of order objects (see below).  Empty list is
       valid — equivalent to "submit no changes this turn".

Each order in ``orders`` is a JSON object with a discriminating
``kind`` field.  The engine processes orders strictly in array order;
clients are responsible for emitting orders in the order they want
them applied.

Order Kinds
-----------

Order kinds use a dotted ``category.action`` naming convention.  The
families below cover the 13 confirmed binary record types and provide
named slots for the three unknown opcodes pending oracle work.

Fleet Movement & Route
~~~~~~~~~~~~~~~~~~~~~~

``waypoint.add``
    Append a new waypoint to a fleet's route.

    .. code-block:: json

       {
         "kind": "waypoint.add",
         "fleet_id": 12,
         "after_index": 0,
         "destination": { "x": 2400, "y": 1430 },
         "target": { "kind": "planet", "id": 318 },
         "warp": 7,
         "task": { "kind": "none" }
       }

``waypoint.update``
    Set or change the task on an existing waypoint.  ``task`` is
    authoritative; the encoded form mirrors the original type-5 record
    (one of: ``none``, ``transport``, ``colonize``, ``remote_mining``,
    ``merge_with_fleet``, ``scrap_fleet``, ``lay_minefield``,
    ``patrol``, ``route``, ``transfer_fleet``).

``waypoint.delete``
    Remove waypoint at index ``waypoint_index`` from fleet ``fleet_id``.

``waypoint.repeat``
    Toggle repeat-orders for a fleet.

    .. code-block:: json

       { "kind": "waypoint.repeat", "fleet_id": 12, "enabled": true }

The ``transport`` task carries a per-resource action map:

.. code-block:: json

   {
     "kind": "transport",
     "ironium":   { "action": "load_all" },
     "boranium":  { "action": "load_exact",   "amount": 80 },
     "germanium": { "action": "fill_up_to",   "amount": 40 },
     "colonists": { "action": "unload_exact", "amount": 25 },
     "fuel":      { "action": "fill_up_to",   "amount": 100 }
   }

Action enum: ``none``, ``load_all``, ``unload_all``, ``load_exact``,
``unload_exact``, ``fill_up_to``.  ``amount`` is required for the
``*_exact`` and ``fill_up_to`` actions and is rejected otherwise.

Fleet Composition
~~~~~~~~~~~~~~~~~

``fleet.split``
    Move ships out of a source fleet to a destination fleet (creating
    a new one if ``destination_fleet_id`` is omitted).  ``ship_groups``
    lists per-design selections; future schema versions may model the
    fully unknown bits in the binary type-23 record.

    .. code-block:: json

       {
         "kind": "fleet.split",
         "source_fleet_id": 12,
         "destination_fleet_id": null,
         "ship_groups": [
           { "design_slot": 2, "count": "all" },
           { "design_slot": 3, "count": 4 }
         ]
       }

``fleet.merge``
    Merge one or more source fleets into a destination fleet.

    .. code-block:: json

       { "kind": "fleet.merge",
         "destination_fleet_id": 12,
         "source_fleet_ids": [18, 24] }

``fleet.rename``
    Rename a fleet.  Names are validated against the original 15-char
    limit on import; the engine accepts up to 31 chars natively.

``fleet.set_battle_plan``
    Assign a battle plan slot to a fleet.

Cargo
~~~~~

``cargo.transfer``
    Immediate cargo transfer at the fleet's current planet
    (waypoint-0).  ``direction`` is ``load`` or ``unload``.

    .. code-block:: json

       {
         "kind": "cargo.transfer",
         "fleet_id": 14,
         "planet_id": 605,
         "direction": "load",
         "resources": { "ironium": 5, "colonists": 2 }
       }

Planet
~~~~~~

``planet.set_production_queue``
    Replace the entire production queue at a planet.

    .. code-block:: json

       {
         "kind": "planet.set_production_queue",
         "planet_id": 318,
         "items": [
           { "item": { "kind": "factory" }, "count": 16 },
           { "item": { "kind": "mine" },    "count": 12 },
           { "item": { "kind": "design", "design_slot": 1 }, "count": 1 }
         ]
       }

    The ``item.kind`` enum mirrors the binary ``item_type`` field:
    standard items (``factory``, ``mine``, ``defenses``, …) and
    ``design`` (custom ship/starbase design slot).  ``complete_percent``
    is server-managed and not accepted on input.

``planet.set_packet_target`` *(provisional — pending oracle for type 35)*
    Set the destination of mineral packets launched from a planet's
    mass driver.

    .. code-block:: json

       { "kind": "planet.set_packet_target",
         "planet_id": 318, "target_planet_id": 422 }

``planet.set_route_target`` *(provisional)*
    Set the planet's "route to" target for fleets carrying the Route
    waypoint task.

Research
~~~~~~~~

``research.set_allocation``
    Adjust the research percentage and the current/next research
    fields.  Field enum: ``energy``, ``weapons``, ``propulsion``,
    ``construction``, ``electronics``, ``biology``, ``same_field``.

    .. code-block:: json

       {
         "kind": "research.set_allocation",
         "research_percent": 17,
         "current_field": "energy",
         "next_field": "biology"
       }

Battle Plans
~~~~~~~~~~~~

``battle_plan.upsert``
    Create or update a battle plan slot.  Slots 0–4 are the built-ins
    (``default``, ``kill_starbase``, ``max_def``, ``sniper``,
    ``chicken``).

``battle_plan.delete`` *(future — confirm Stars supports this)*

Ship Designs *(provisional — pending oracle for type 27)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``design.upsert``
    Save a ship or starbase design into a numbered slot.  The schema
    will model hull, slot assignments, and design name once the
    binary layout is decoded.

``design.delete``
    Free a design slot.

Validation Strategy
-------------------

The engine validates each order in three layers, matching the global
:doc:`../validation` strategy:

#. **Structural** — JSON Schema validation against the schemas in
   ``stars-reborn-schemas`` (``request-submit-orders.json`` and the
   per-kind shapes referenced from it).
#. **Rules-logical** — required state for the action exists (the named
   fleet/planet/design exists for this player; component requirements
   for a task are met; battle-plan slot is in range; etc.).
#. **Game-state** — the player is authorised to submit orders for
   ``year`` and the turn is in the edit phase.

A failure at any layer aborts the entire submission with a 4xx
response and an ``error.json`` body that identifies the offending
order index, the layer, and a human-readable reason.  The engine never
applies a partial order list.

Ordering and Dependencies
-------------------------

Some orders depend on others within the same submission:

- ``waypoint.add`` of a route element followed by a ``waypoint.update``
  setting its task is the canonical pattern.  Both can be merged
  client-side into a single ``waypoint.add`` with a non-default
  ``task`` field — the engine treats them as equivalent.
- ``fleet.split`` may reference a fleet created earlier in the same
  submission via ``destination_fleet_id`` once the engine assigns ids
  client-supplied or returned via a sub-batch reservation API
  (TBD; not in v1).

The v1 schema requires that any fleet, planet, or design id referenced
in an order already exists at the start of turn resolution; in-batch
references are rejected.  This matches the behaviour of |original|'s
order processor.

Versioning
----------

Order schemas are versioned by ``schema_version`` in the request
envelope.  Clients should always submit the highest version they
understand.  The engine accepts older versions with the documented
behaviour for that version; new optional fields require a version
bump.  Removing a field or changing semantics requires a major-version
bump and a parallel handler.
