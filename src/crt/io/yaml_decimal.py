"""A YAML SafeLoader whose floats become ``Decimal`` built from the scalar text.

Shared by the deal-terms loader and the scenario-file loader so that no rate or
percentage in any input file ever passes through a Python ``float`` (CLAUDE.md rule 3;
spec 00 section 3.1).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

import yaml


class YamlDecimalError(ValueError):
    """A YAML float scalar could not be read exactly as a Decimal."""


class DecimalSafeLoader(yaml.SafeLoader):
    """SafeLoader with the ``float`` tag constructed as ``Decimal`` from the raw text."""


def _construct_decimal(loader: yaml.SafeLoader, node: yaml.Node) -> Decimal:
    if not isinstance(node, yaml.ScalarNode):
        raise YamlDecimalError(f"float tag on non-scalar node at {node.start_mark}")
    text = str(node.value).replace("_", "")
    try:
        return Decimal(text)
    except InvalidOperation:
        raise YamlDecimalError(f"cannot read {text!r} as Decimal at {node.start_mark}") from None


DecimalSafeLoader.add_constructor("tag:yaml.org,2002:float", _construct_decimal)
