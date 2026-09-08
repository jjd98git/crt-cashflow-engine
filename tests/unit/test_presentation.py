"""The shared chart conventions (``crt.presentation``): the stack order puts every
Original Note directly under its retained H tranche between B-3H (bottom) and A-H (top),
and an H tranche's colour is a lighter tint of its Note's hue."""

from __future__ import annotations

import colorsys

import pytest

from crt.io.deal_terms import NOTE_CLASSES, TRANCHE_ORDER
from crt.presentation import (
    NOTE_H_PAIRS,
    STACK_ORDER_BOTTOM_UP,
    STACK_ORDER_TOP_DOWN,
    TRANCHE_COLOURS,
    tranche_colour,
    tranche_colour_css,
)

pytestmark = pytest.mark.fast


def test_stack_order_is_first_loss_to_senior_with_each_note_under_its_h() -> None:
    assert STACK_ORDER_BOTTOM_UP == (
        "B-3H", "B-2H", "B-1H", "M-2B", "M-2BH", "M-2A", "M-2AH", "M-1", "M-1H", "A-1", "A-1H", "A-H",
    )
    assert STACK_ORDER_BOTTOM_UP[0] == "B-3H" and STACK_ORDER_BOTTOM_UP[-1] == "A-H"
    assert sorted(STACK_ORDER_BOTTOM_UP) == sorted(TRANCHE_ORDER)  # every tranche once
    for note in NOTE_CLASSES:
        assert NOTE_H_PAIRS[note] == note + "H"
        position = STACK_ORDER_BOTTOM_UP.index(note)
        assert STACK_ORDER_BOTTOM_UP[position + 1] == NOTE_H_PAIRS[note], note
    assert STACK_ORDER_TOP_DOWN == tuple(reversed(STACK_ORDER_BOTTOM_UP))


def _rgb(hex_colour: str) -> tuple[int, int, int]:
    return int(hex_colour[0:2], 16), int(hex_colour[2:4], 16), int(hex_colour[4:6], 16)


def _hue_and_lightness(hex_colour: str) -> tuple[float, float]:
    r, g, b = (channel / 255 for channel in _rgb(hex_colour))
    hue, lightness, _ = colorsys.rgb_to_hls(r, g, b)
    return hue, lightness


def test_h_tranche_is_a_lighter_tint_of_its_note() -> None:
    for note, h_tranche in NOTE_H_PAIRS.items():
        note_colour = tranche_colour(note)
        h_colour = tranche_colour(h_tranche)
        assert note_colour != h_colour
        note_hue, note_lightness = _hue_and_lightness(note_colour)
        h_hue, h_lightness = _hue_and_lightness(h_colour)
        assert abs(note_hue - h_hue) < 0.02, (note, note_colour, h_colour)  # same hue family
        assert h_lightness > note_lightness + 0.15, (note, note_colour, h_colour)
        # Each channel moved 45 % of the way to white.
        for note_channel, h_channel in zip(_rgb(note_colour), _rgb(h_colour), strict=True):
            assert h_channel == note_channel + round((255 - note_channel) * 45 / 100)


def test_palette_covers_every_tranche_exactly_once() -> None:
    assert set(TRANCHE_COLOURS) == set(TRANCHE_ORDER)
    assert len(set(TRANCHE_COLOURS.values())) == len(TRANCHE_ORDER)  # all distinct
    for tranche, colour in TRANCHE_COLOURS.items():
        assert len(colour) == 6 and int(colour, 16) >= 0
        assert colour == colour.upper()
        assert tranche_colour_css(tranche) == "#" + colour
    assert tranche_colour("B-3H") == "FF0000"  # first loss stays pure red
    assert tranche_colour("A-H") == "1F3864"
    with pytest.raises(KeyError):
        tranche_colour("Z-9")
