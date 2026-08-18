"""Tests for tripta_fittings.presets — ASME BPE preset table."""

import pytest

from tripta_fittings.presets import (
    PRESETS,
    normalizar_nombre,
    preset_por_indice,
    preset_por_nombre,
)


# ── helpers ──────────────────────────────────────────────────────────────

EXPECTED_PRESET_NAMES = [
    '1/2" · Mini',
    '3/4" · Mini',
    '1" · TC50',
    '1.5" · TC64',
    '2" · TC64',
    '2.5" · TC77',
    '3" · TC91',
    '4" · TC119',
    '6" · TC167',
    '8" · TC218',
    '10" · TC268',
    '12" · TC319',
]

# Each row: (preset_name, field_name, expected_value)
CRITICAL_VALUES = [
    # 1.5" TC64
    ('1.5" · TC64', 'ferrule_od', 63.90),
    ('1.5" · TC64', 'bead_distance', 50.70),
    ('1.5" · TC64', 'tube_od', 38.10),
    ('1.5" · TC64', 'tube_id', 34.80),
    ('1.5" · TC64', 'tube_height_corta', 12.7),
    ('1.5" · TC64', 'tube_height_larga', 28.6),
    ('1.5" · TC64', 'gasket_thickness', 2.25),
    # 12" TC319
    ('12" · TC319', 'ferrule_od', 332.00),
    ('12" · TC319', 'bead_distance', 318.10),
    ('12" · TC319', 'tube_od', 304.80),
    ('12" · TC319', 'tube_id', 298.70),
    ('12" · TC319', 'tube_height_corta', 19.1),
    ('12" · TC319', 'tube_height_larga', 44.5),
    ('12" · TC319', 'gasket_thickness', 2.75),
    # 1/2" Mini
    ('1/2" · Mini', 'ferrule_od', 25.20),
    ('1/2" · Mini', 'tube_od', 12.70),
    ('1/2" · Mini', 'tube_id', 9.40),
    ('1/2" · Mini', 'gasket_thickness', 1.4),
    # 3/4" Mini
    ('3/4" · Mini', 'ferrule_od', 29.20),
    ('3/4" · Mini', 'tube_od', 19.05),
    ('3/4" · Mini', 'tube_id', 15.75),
    ('3/4" · Mini', 'gasket_thickness', 1.4),
]


# ── Tests ────────────────────────────────────────────────────────────────


class TestPresetCount:
    """PRESETS must contain exactly 12 rows."""

    def test_length(self):
        assert len(PRESETS) == 12


class TestPresetStructure:
    """Each preset dict must expose all required snake_case keys."""

    REQUIRED_KEYS = {
        'preset',
        'dn',
        'ferrule_od',
        'bead_distance',
        'tube_od',
        'tube_id',
        'tube_height_corta',
        'tube_height_larga',
        'gasket_thickness',
        'standard',
    }

    def test_keys_present(self):
        for p in PRESETS:
            assert self.REQUIRED_KEYS <= set(p.keys()), (
                f"Preset {p.get('preset')} missing keys: "
                f"{self.REQUIRED_KEYS - set(p.keys())}"
            )


class TestPresetNames:
    """All 12 preset display-names match the expected list."""

    def test_all_names(self):
        names = [p['preset'] for p in PRESETS]
        assert names == EXPECTED_PRESET_NAMES


class TestCriticalValues:
    """Spot-check critical numeric values for the most-used presets."""

    @pytest.mark.parametrize('name,field,expected', CRITICAL_VALUES)
    def test_value(self, name, field, expected):
        p = preset_por_nombre(name)
        assert p is not None, f"Preset '{name}' not found"
        assert p[field] == pytest.approx(expected), (
            f"{name}.{field}: expected {expected}, got {p[field]}"
        )


class TestPresetPorIndice:
    """preset_por_indice returns the correct row by 0-based index."""

    def test_first(self):
        p = preset_por_indice(0)
        assert p is not None
        assert p['preset'] == '1/2" · Mini'
        assert p['ferrule_od'] == pytest.approx(25.20)

    def test_last(self):
        p = preset_por_indice(11)
        assert p is not None
        assert p['preset'] == '12" · TC319'
        assert p['ferrule_od'] == pytest.approx(332.00)

    def test_out_of_range(self):
        assert preset_por_indice(99) is None
        assert preset_por_indice(-1) is None


class TestPresetPorNombre:
    """preset_por_nombre finds a preset by normalized name."""

    def test_exact(self):
        p = preset_por_nombre('1.5" · TC64')
        assert p is not None
        assert p['dn'] == 'TC64'

    def test_varied_spacing(self):
        """Tolerates various whitespace around the '·' separator."""
        for name in [
            '1.5"·TC64',
            '1.5" · TC64',
            '1.5"  ·  TC64',
            '1.5"\t·\tTC64',
        ]:
            p = preset_por_nombre(name)
            assert p is not None, f"Failed for: {name!r}"
            assert p['preset'] == '1.5" · TC64'

    def test_not_found(self):
        assert preset_por_nombre('NOEXISTE') is None


class TestNormalizarNombre:
    """normalizar_nombre strips extra whitespace around '·'."""

    def test_identity(self):
        assert normalizar_nombre('1.5" · TC64') == '1.5" · TC64'

    def test_strips_whitespace(self):
        assert normalizar_nombre('1.5"  ·  TC64') == '1.5" · TC64'

    def test_no_spaces(self):
        assert normalizar_nombre('1.5"·TC64') == '1.5" · TC64'

    def test_tab_separator(self):
        assert normalizar_nombre('1.5"\t·\tTC64') == '1.5" · TC64'
