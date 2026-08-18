"""ASME BPE preset dimensions for tri-clamp ferrules.

Each preset is a dict with snake_case keys matching the original CSV columns.
The canonical display name uses the format ``<size> · <DN>`` (e.g. ``1.5" · TC64``).
"""

from __future__ import annotations

from typing import Optional

# ── Canonical preset data ────────────────────────────────────────────────
# Source of truth: presets.csv from TriptaClamps3D-Web (ASME BPE).

PRESETS: list[dict] = [
    {
        'preset': '1/2" · Mini',
        'dn': 'Mini',
        'ferrule_od': 25.20,
        'bead_distance': 18.66,
        'tube_od': 12.70,
        'tube_id': 9.40,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 1.4,
        'standard': 'ASME BPE',
    },
    {
        'preset': '3/4" · Mini',
        'dn': 'Mini',
        'ferrule_od': 29.20,
        'bead_distance': 23.82,
        'tube_od': 19.05,
        'tube_id': 15.75,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 1.4,
        'standard': 'ASME BPE',
    },
    {
        'preset': '1" · TC50',
        'dn': 'TC50',
        'ferrule_od': 50.40,
        'bead_distance': 37.60,
        'tube_od': 25.40,
        'tube_id': 22.10,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 2.25,
        'standard': 'ASME BPE',
    },
    {
        'preset': '1.5" · TC64',
        'dn': 'TC64',
        'ferrule_od': 63.90,
        'bead_distance': 50.70,
        'tube_od': 38.10,
        'tube_id': 34.80,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 2.25,
        'standard': 'ASME BPE',
    },
    {
        'preset': '2" · TC64',
        'dn': 'TC64',
        'ferrule_od': 74.00,
        'bead_distance': 62.10,
        'tube_od': 50.80,
        'tube_id': 47.50,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 2.25,
        'standard': 'ASME BPE',
    },
    {
        'preset': '2.5" · TC77',
        'dn': 'TC77',
        'ferrule_od': 87.00,
        'bead_distance': 74.96,
        'tube_od': 63.50,
        'tube_id': 60.20,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 2.25,
        'standard': 'ASME BPE',
    },
    {
        'preset': '3" · TC91',
        'dn': 'TC91',
        'ferrule_od': 100.00,
        'bead_distance': 87.80,
        'tube_od': 76.20,
        'tube_id': 72.90,
        'tube_height_corta': 12.7,
        'tube_height_larga': 28.6,
        'gasket_thickness': 2.25,
        'standard': 'ASME BPE',
    },
    {
        'preset': '4" · TC119',
        'dn': 'TC119',
        'ferrule_od': 125.00,
        'bead_distance': 113.00,
        'tube_od': 101.60,
        'tube_id': 97.38,
        'tube_height_corta': 15.9,
        'tube_height_larga': 28.6,
        'gasket_thickness': 2.25,
        'standard': 'ASME BPE',
    },
    {
        'preset': '6" · TC167',
        'dn': 'TC167',
        'ferrule_od': 179.00,
        'bead_distance': 165.40,
        'tube_od': 152.40,
        'tube_id': 146.86,
        'tube_height_corta': 19.1,
        'tube_height_larga': 38.1,
        'gasket_thickness': 2.75,
        'standard': 'ASME BPE',
    },
    {
        'preset': '8" · TC218',
        'dn': 'TC218',
        'ferrule_od': 230.00,
        'bead_distance': 216.30,
        'tube_od': 203.20,
        'tube_id': 197.66,
        'tube_height_corta': 19.1,
        'tube_height_larga': 38.1,
        'gasket_thickness': 2.75,
        'standard': 'ASME BPE',
    },
    {
        'preset': '10" · TC268',
        'dn': 'TC268',
        'ferrule_od': 281.00,
        'bead_distance': 267.20,
        'tube_od': 254.00,
        'tube_id': 248.46,
        'tube_height_corta': 19.1,
        'tube_height_larga': 38.1,
        'gasket_thickness': 2.75,
        'standard': 'ASME BPE',
    },
    {
        'preset': '12" · TC319',
        'dn': 'TC319',
        'ferrule_od': 332.00,
        'bead_distance': 318.10,
        'tube_od': 304.80,
        'tube_id': 298.70,
        'tube_height_corta': 19.1,
        'tube_height_larga': 44.5,
        'gasket_thickness': 2.75,
        'standard': 'ASME BPE',
    },
]


# ── Lookup helpers ───────────────────────────────────────────────────────


def normalizar_nombre(nombre: str) -> str:
    """Normalize a preset name: collapse whitespace around the ``·`` separator.

    Examples::

        >>> normalizar_nombre('1.5"·TC64')
        '1.5" · TC64'
        >>> normalizar_nombre('1.5"  ·  TC64')
        '1.5" · TC64'
    """
    # Split on the middle dot (·), strip each side, rejoin with ' · '
    parts = nombre.split('·')
    return ' · '.join(p.strip() for p in parts)


def preset_por_indice(i: int) -> Optional[dict]:
    """Return preset at 0-based index *i*, or ``None`` if out of range."""
    if 0 <= i < len(PRESETS):
        return PRESETS[i]
    return None


def preset_por_nombre(nombre: str) -> Optional[dict]:
    """Find a preset by normalized display name (tolerates varied whitespace).

    Returns ``None`` when no match is found.
    """
    target = normalizar_nombre(nombre)
    for p in PRESETS:
        if p['preset'] == target:
            return p
    return None
