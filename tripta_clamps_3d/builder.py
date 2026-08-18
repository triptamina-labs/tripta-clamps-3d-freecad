"""Builder FreeCAD — construye sólidos de revolución a partir de perfiles.

Todos los imports de FreeCAD están **dentro de las funciones** para que
el módulo pueda importarse sin FreeCAD (tests puros, linters, etc.).
"""

from __future__ import annotations

from tripta_clamps_3d.constraints import BEAD_RADIUS_DEFAULT, validate_and_clamp_dimensions
from tripta_clamps_3d.geometry import ArcSegment, Line, profile_to_segments
from tripta_clamps_3d.profile_cmds import obtener_perfil


def build_solid(tipo: str, params_dict: dict):  # -> Part.Solid at runtime
    """Construye un sólido de revolución para ``tipo``.

    Pipeline:
        1. Clampa dimensiones (validate_and_clamp_dimensions + BEAD_RADIUS_DEFAULT)
        2. Genera comandos de perfil (obtener_perfil)
        3. Convierte a segmentos geométricos (profile_to_segments)
        4. Construye Part.Wire con LineSegment / Arc (z=0)
        5. Cierra el wire si hace falta
        6. Revuelve 360° alrededor del eje Y
        7. Verifica solidez y devuelve Part.Solid

    Raises:
        RuntimeError: Si la revolución no produce un sólido válido.
    """
    import FreeCAD as App  # type: ignore[import]
    import Part  # type: ignore[import]

    # 1. Clampa
    dims = {
        "tubeID": params_dict["tubeID"],
        "tubeOD": params_dict["tubeOD"],
        "ferruleOD": params_dict["ferruleOD"],
        "beadDistance": params_dict["beadDistance"],
    }
    clamped = validate_and_clamp_dimensions(tipo, dims, BEAD_RADIUS_DEFAULT)
    params = dict(params_dict)
    params.update(clamped)

    # 2. Perfil → comandos
    cmds = obtener_perfil(tipo, params)

    # 3. Comandos → segmentos geométricos
    segments = profile_to_segments(cmds)

    # 4. Segmentos → Part.Edges (Wire)
    edges = []
    for seg in segments:
        if isinstance(seg, Line):
            p1 = App.Vector(seg.p1.x, seg.p1.y, 0.0)
            p2 = App.Vector(seg.p2.x, seg.p2.y, 0.0)
            edges.append(Part.makeLine(p1, p2))
        elif isinstance(seg, ArcSegment):
            # Part.Arc(S, M, E) — los tres puntos definen el arco
            S = App.Vector(seg.start.x, seg.start.y, 0.0)
            M = App.Vector(seg.mid.x, seg.mid.y, 0.0)
            E = App.Vector(seg.end.x, seg.end.y, 0.0)
            arc = Part.Arc(S, M, E)
            edges.append(arc.toShape())
        else:
            raise TypeError(f"Segmento desconocido: {type(seg)}")

    # 5. Cerrar el wire y crear face
    wire = Part.Wire(edges)
    if not wire.isClosed():
        wire = Part.Wire(edges + [edges[0]])  # cerrar con el primero
    face = Part.Face(wire)

    # 6. Revolución 360° alrededor del eje Y
    #    eje: origen (0,0,0) → dirección (0,1,0)
    solid = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 360.0)

    # 7. Verificar solidez
    if not isinstance(solid, Part.Solid):
        # Algunas veces devuelve Compound; intentar fused solid
        if hasattr(solid, 'Solids') and len(solid.Solids) == 1:
            solid = solid.Solids[0]
        else:
            raise RuntimeError(
                f"La revolución de '{tipo}' no produjo un sólido: {type(solid)}"
            )

    return solid
