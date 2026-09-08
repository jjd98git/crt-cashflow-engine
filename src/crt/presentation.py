"""Presentation conventions shared by every chart: the Excel exporter, the Streamlit GUI
and the browser bridge (``web/engine_bridge.py``) all read the stack order and the
tranche colours from here, so the three never disagree.

Nothing here touches a number the engine produces.  The order and the colours are derived
from ``TRANCHE_ORDER`` and ``NOTE_CLASSES`` in ``crt.io.deal_terms`` (Table 3 of the PPM),
never listed twice.

Stack order (bottom-up).  Every stacked chart puts the first-loss tranche B-3H at the
bottom and the retained senior tranche A-H on top; in between, each Original Note sits
immediately below the retained H tranche that shares its name (A-1 under A-1H, M-1 under
M-1H, M-2A under M-2AH, M-2B under M-2BH), so that the pro rata pair reads as one band of
two shades.  That is the single deviation from a plain reversal of Table 3's order, whose
listing puts the H tranche after (i.e. below, once reversed) its Note.

Colours.  A Note keeps the palette colour of its tranche; its H tranche is the same hue
tinted towards white by ``H_TINT_PERCENT`` percent, so that the pair is visibly the same
family with the retained slice lighter.  Unpaired tranches (A-H, B-1H, B-2H, B-3H) keep
their palette colour unchanged.
"""

from __future__ import annotations

from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER

# The retained H tranche paired pro rata with each Original Note (YAML:
# reference_tranches.structure_note; the same rule as ``DealTerms.pair_of``).
NOTE_H_PAIRS: dict[str, str] = {note: note + "H" for note in NOTE_CLASSES}
_PAIRED_H_TRANCHES: frozenset[str] = frozenset(NOTE_H_PAIRS.values())


def _stack_order_bottom_up() -> tuple[str, ...]:
    """Reverse Table 3's order (first loss first, A-H last) and, within it, emit each
    Note followed by its own H tranche."""
    order: list[str] = []
    for tranche in reversed(TRANCHE_ORDER):
        if tranche in _PAIRED_H_TRANCHES:
            continue  # placed right after its Note below
        order.append(tranche)
        if tranche in NOTE_H_PAIRS:
            order.append(NOTE_H_PAIRS[tranche])
    if sorted(order) != sorted(TRANCHE_ORDER):
        raise ValueError(f"stack order {order} does not cover TRANCHE_ORDER {TRANCHE_ORDER}")
    return tuple(order)


# Bottom of every stack first: B-3H, B-2H, B-1H, M-2B, M-2BH, M-2A, M-2AH, M-1, M-1H,
# A-1, A-1H, A-H.
STACK_ORDER_BOTTOM_UP: tuple[str, ...] = _stack_order_bottom_up()
# Top of the stack first: what a legend that mirrors the stack shows.
STACK_ORDER_TOP_DOWN: tuple[str, ...] = tuple(reversed(STACK_ORDER_BOTTOM_UP))

# Palette (6 hex digits, no '#', as openpyxl wants them): senior tranches in cool blues,
# the subordinate Notes in warm golds/oranges, the B-H tranches in reds with B-3H (first
# loss) pure red.  Paired H tranches are not listed: they are tints of their Note.
_BASE_COLOURS: dict[str, str] = {
    "A-H": "1F3864",
    "A-1": "2E75B6",
    "M-1": "BF9000",
    "M-2A": "ED7D31",
    "M-2B": "C55A11",
    "B-1H": "E97D7D",
    "B-2H": "A61C1C",
    "B-3H": "FF0000",
}
# How far towards white an H tranche's colour is pushed from its Note's (presentation
# choice only; no engine value depends on it).
H_TINT_PERCENT = 45


def _tint_towards_white(hex_colour: str, percent: int) -> str:
    """Move each RGB channel ``percent`` percent of the way from its value to 255 (the
    hue is preserved; integer arithmetic, so the result is exact and reproducible)."""
    if len(hex_colour) != 6:
        raise ValueError(f"colour {hex_colour!r} is not 6 hex digits")
    channels = (int(hex_colour[i : i + 2], 16) for i in (0, 2, 4))
    tinted = (channel + round((255 - channel) * percent / 100) for channel in channels)
    return "".join(f"{value:02X}" for value in tinted)


def tranche_colour(tranche: str) -> str:
    """The chart colour of ``tranche`` as ``RRGGBB`` (no '#').  A paired H tranche is its
    Note's colour tinted; every other tranche is its palette entry."""
    for note, h_tranche in NOTE_H_PAIRS.items():
        if tranche == h_tranche:
            return _tint_towards_white(_BASE_COLOURS[note], H_TINT_PERCENT)
    if tranche not in _BASE_COLOURS:
        raise KeyError(f"{tranche!r} is not a Reference Tranche with a chart colour")
    return _BASE_COLOURS[tranche]


def tranche_colour_css(tranche: str) -> str:
    """The same colour as ``#RRGGBB`` for CSS, Chart.js and Vega-Lite."""
    return "#" + tranche_colour(tranche)


TRANCHE_COLOURS: dict[str, str] = {tranche: tranche_colour(tranche) for tranche in TRANCHE_ORDER}
