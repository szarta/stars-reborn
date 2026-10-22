Player Orders
=============

A *turn* in |original| is a deterministic transformation of game state
driven by per-player **orders**.  Each player submits a batch of orders
between turns; the host applies them during turn resolution.

This section covers two related but distinct concerns:

- :doc:`x_file_format` documents the original binary container
  (``.x1`` … ``.x16``) used by |original| to ship orders from a player's
  client back to the host, with byte-level layouts for every order
  record we have decoded.  This is reference material for importing
  legacy save games.

- :doc:`engine_api` defines |project|'s native order-submission API —
  the JSON envelope a client posts to
  ``PUT /games/{id}/turns/{year}/orders/{pid}``.  The Stars Reborn
  engine does not consume the binary format directly; the legacy parser
  converts ``.xN`` files into this JSON shape on import.

.. toctree::
   :maxdepth: 2

   x_file_format
   engine_api
