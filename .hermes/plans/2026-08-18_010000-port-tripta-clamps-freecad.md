# Port TriptaClamps3D-Web → Plugin FreeCAD — Plan de Implementación

> **Para Hermes:** implementar con subagent-driven-development, waves de tareas independientes en paralelo, revisión en dos etapas, commits atómicos por tarea, push + PR por ola. Issues de GitHub por cada tarea (epic en #1).

**Goal:** Portar el visor paramétrico de piezas Tri-Clamp (TriptaClamps3D-Web, Three.js + TypeScript) a un workbench/plugin nativo de FreeCAD con objetos paramétricos (`Part::FeaturePython`), panel de control y presets ASME BPE.

**Architecture:** 1) Paquete `tripta_fittings/` con la lógica pura portada 1:1 desde TypeScript (perfiles, constraints, presets) — sin dependencias de FreeCAD, testeable con pytest. 2) Capa FreeCAD: feature paramétrica que construye un wire 2D desde los comandos de perfil y lo revuelve 360° alrededor del eje Y (equivalente a `LatheGeometry` de Three.js). 3) Workbench + panel Qt con los mismos controles que la web. 4) Distribución como addon (package.xml para Addon Manager).

**Tech Stack:** Python 3.x, FreeCAD (PySide/Qt para UI), pytest, freecadcmd (headless) para smoke tests, FreeCAD MCP (neka-nat, RPC 9875) para verificación visual.

---

## Contexto del proyecto fuente (referencia obligatoria)

Repo fuente: `~/repos/TriptaClamps3D-Web` (rama main, commit `ae85560`). Migración TS→JS no relevante; se portan los `.ts`.

### Piezas y parámetros
| Pieza | Parámetros necesarios |
|---|---|
| `ferrula` | tubeID, tubeOD, ferruleOD, beadDistance, beadRadius, tubeHeight, ferrHeight |
| `gasket` | tubeID, ferruleOD, beadDistance, beadRadius, gasketThickness |
| `endcap` | ferruleOD, beadDistance, beadRadius |
| `spool` | tubeID, tubeOD, ferruleOD, beadDistance, spoolLength, beadRadius, tubeHeight, ferrHeight |

Valores por defecto (del store web): beadRadius=1.5, gasketThickness=1.4, ferrHeight=2.0, tubeHeightFijo=28.6, tubeHeights corta/larga=12.7/28.6. Constantes endcap: STEP 2mm, MAX_HEIGHT 5mm, TAPER 20°.

### Convención geométrica
- Perfil 2D en plano (x = radio, y = altura). Three.js `LatheGeometry(points, segments)` revuelve alrededor del **eje Y**.
- Comandos de perfil (`ProfileCommand`): `moveTo(x,y)`, `lineTo(x,y)`, `arc(cx,cy,r,a0,a1,ccw)` — ángulos en radianes, y-up.
- Conversión a FreeCAD: wire en el plano XY, revolución alrededor del eje Y: `wire.revolve(App.Vector(0,0,0), App.Vector(0,1,0), 360)`.
- Arcos: todos los arcos del dominio son semicírculos (a0,a1 ∈ {0, π}). `Part.Arc(C, S, M)` con 3 puntos: S=(cx+r·cos a0, cy+r·sin a0), E=(cx+r·cos a1, cy+r·sin a1), M=(cx+r·cos am, cy+r·sin am) donde **am debe respetar la dirección**: ccw=true → recorrido CCW (a0→a1'), ccw=false → recorrido CW (a0→a1''), mid_angle = a0 + dir·(dist(a0,a1)/2). Las tests de coordenadas (portadas del TS) validan cada arco.
- Revisar casos reales (para testear la dirección): gasket bead superior arc(cy=+em, ccw=false, 0→π pasa por arriba), gasket bead inferior arc(cy=−em), endcap arc(cy=0, ccw=false, π→0), spool arc inferior arc(cy=0) y superior arc(cy=totalH).

### Constraints (portar idéntico)
`validateAndClampDimensions(tipo, dims, beadRadius)` en `src/core/constraints.ts` — lógica exacta por pieza (gasket: ferruleOD ≥ tubeID+5, beadDistance∈[tubeID+2bR+GAP, ferruleOD−2bR−GAP] con min gap 0.5; endcap: ajustes de rF/rbD con eps 0.2; férula/spool: tubeOD>tubeID+1, ferruleOD>tubeOD+2, beadDistance acotado). Importar constantes CONSTRAINT_EPSILON=0.2, CONSTRAINT_MIN_GAP=0.5.

### Presets (12 filas, ASME BPE)
Columna exacta del CSV: `Preset,DN,ferruleOD,beadDistance,tubeOD,tubeID,tubeHeightCorta,tubeHeightLarga,gasketThickness,Standard`. Filas: 1/2" Mini … 12" TC319. El plugin debe exponerlos como lista + lookup por índice o nombre. (El proyecto web los carga de `src/presets.csv`; el fallback embedded está en `src/data/presets.ts`.)

---

## Estructura del plugin

```
tripta-fittings-freecad/            (repo raíz)
├── package.xml                     # metadata Addon Manager (FreeCAD ≥0.21)
├── Init.py                         # hook startup (sin GUI)
├── InitGui.py                      # hook GUI → registra workbench
├── README.md                       # instalación, uso, estructura
├── tripta_fittings/
│   ├── __init__.py                 # versión, API pública
│   ├── profile_cmds.py             # PORT PURO: dataclasses/dicts + perfil*() + obtener_perfil()
│   ├── constraints.py              # PORT PURO: validate_and_clamp_dimensions()
│   ├── geometry.py                 # PORT PURO: ProfileCommand[] → lista de puntos/segmentos/arcos (sin FreeCAD)
│   ├── presets.py                  # PORT PURO: tabla ASME BPE + lookup
│   ├── feature.py                  # TriptaFittingsFeature (Part::FeaturePython) — capa FreeCAD
│   ├── builder.py                  # wire → revolve → solid (capa FreeCAD, usada por feature y tests cmd)
│   ├── workbench.py                # clase TriptaFittingsWorkbench (menús/toolbar)
│   ├── commands.py                 # comandos FreeCAD: crear pieza, abrir panel
│   └── panel.py                    # TaskPanel/DockablePanel Qt (tipo, preset, sliders, aplicar)
└── tests/
    ├── test_profile_cmds.py        # pytest: coordenadas idénticas al TS (port de aserciones)
    ├── test_constraints.py         # pytest: port de tests TS de constraints
    ├── test_presets.py             # pytest: carga + valores críticos
    ├── test_geometry.py            # pytest: wire points correctos (sin FreeCAD), arcos dirección
    └── test_feature_cmd.py         # smoke freecadcmd: crear feature, recompute, shape válida
```

---

## Tareas (TDD por tarea, 2-5 min c/u)

### Ola 1 — Núcleo puro (3 subagentes paralelos, rama `feat/wave1-core`)
Disjuntos en archivos — sin conflictos.

#### T1: `profile_cmds.py` + tests
**Archivos:** `tripta_fittings/profile_cmds.py`, `tests/test_profile_cmds.py`
**Spec:** Portar 1:1 `ProfileCommand` (como NamedTuple/dataclass o dicts con type/x/y/cx/cy/r/a0/a1/ccw), `perfil_ferula`, `perfil_gasket`, `perfil_endcap`, `perfil_spool`, `obtener_perfil` desde `src/cad/profileDescriptor.ts` del repo fuente. Mismo cálculo, mismas constantes (ENDCAP_STEP_MM=2, ENDCAP_MAX_HEIGHT_MM=5, taper 20°, ángulo férula 20° = tan(rad(20))·(rF−rOD)).
**Tests:** Portar las aserciones de `src/cad/__tests__/profileDescriptor.test.ts` (151 tests approx): contar comandos por pieza (9/9/8/16), primeras/últimas coordenadas exactas, arcs por pieza, dispatch de obtener_perfil con fallback a férula. Verificación: `python -m pytest tests/test_profile_cmds.py -v`.

#### T2: `constraints.py` + tests
**Archivos:** `tripta_fittings/constraints.py`, `tests/test_constraints.py`
**Spec:** Portar `validateAndClampDimensions` (con CONSTANTES EPSILON 0.2 / MIN_GAP 0.5) de `src/core/constraints.ts` + constantes de `src/core/constants.ts`.
**Tests:** Portar `src/core/__tests__/constraints.test.ts` y `constants.test.ts`: clamps por tipo, sin mutar entrada, edge cases (gasket con ferruleOD pequeño, endcap límites, férula beadDistance).

#### T3: `presets.py` + tests
**Archivos:** `tripta_fittings/presets.py`, `tests/test_presets.py`
**Spec:** Tabla de 12 presets ASME BPE (datos de `src/presets.csv`), `PRESETS` lista + `preset_by_index` + normalización de nombres (`1.5" · TC64`). Valores exactos del CSV.
**Tests:** 12 filas, valores críticos (1.5" TC64: ferruleOD=63.90, tubeID=34.80, tubeHeightLarga=28.6, gasketThickness=2.25; 12": 332.00/304.80/44.5/2.75), lookup por nombre.

### Ola 2 — Capa FreeCAD (2 subagentes paralelos, rama `feat/wave2-freecad`)

#### T4: `geometry.py` + `builder.py` + `feature.py` + `test_feature_cmd.py`
**Depende:** T1, T2, T3.
**Archivos:** `tripta_fittings/geometry.py`, `tripta_fittings/builder.py`, `tripta_fittings/feature.py`, `tests/test_feature_cmd.py`
**Spec:**
- `geometry.py`: convertir ProfileCommand[] → representación pura de segmentos (puntos/arcos) validando dirección de arcos — testable sin FreeCAD.
- `builder.py`: construir `Part.Wire` desde la representación (Part.Arc/Part.LineSegment via Part.Vertex points), `revolve` 360° eje Y, `Part.Solid` resultante. Clamp previo a la generación (reusar constraints).
- `feature.py`: `TriptaFittingsFeature` Part::FeaturePython con propiedades: `PieceType` (enumeration), `TubeID`, `TubeOD`, `FerruleOD`, `BeadDistance`, `BeadRadius`, `SpoolLength`, `TubeHeight`, `FerrHeight`, `GasketThickness` (floats, en mm). `execute(fp)` → clamp → perfil → wire → revolve → `fp.Shape`. onChanged/mustExecute sanos.
**Tests (smoke command, headless):** `flatpak run --command=freecadcmd org.freecad.FreeCAD -c "..."` o script python que: crea doc, addObject('Part::FeaturePython') con proxy, setea propiedades, recompute, verifica `Shape.Volume > 0`, `Shape.isValid()`, `Shape.BoundBox` coherente. 4 piezas × preset 1.5" TC64.

#### T5: Estructura addon + README
**Archivos:** `package.xml`, `Init.py`, `InitGui.py`, `workbench.py`, `README.md`
**Spec:** Registro de workbench "Tripta Fittings" (nombre, icono, tools). package.xml con name/version/description/maintainer (Felipe Castellanos) + depends FreeCAD 0.21+. README: qué es, instalación (carpeta Mod/ + Addon Manager), uso básico, estructura, tests.
**Nota:** referencias a FreeCAD API en Init/InitGui/workbench solo evaluadas dentro de FreeCAD — los imports de FreeCAD/PySide deben ser funcionales cuando se ejecutan en FreeCAD, no en pytest (guardar imports). Verificar con freecadcmd: `flatpak run --command=freecadcmd org.freecad.FreeCAD -c "import tripta_fittings"`.

### Ola 3 — UI + integración + verificación (orquestador + 1 subagente, rama `feat/panel-ui`)

#### T6: `panel.py` + `commands.py` + integración
**Depende:** T4, T5.
**Archivos:** `tripta_fittings/panel.py`, `tripta_fittings/commands.py`, `InitGui.py` (toolbar).
**Spec:** Panel Qt acoplable: combo TIPO PIEZA (férula/gasket/spool/endcap), combo PRESET ASME (Custom + 12 presets), sliders/spinboxes para parámetros visibles según pieza, botón "Crear/Actualizar pieza". Espejo de la web: aplicar preset → setea props + recompute; cambiar slider → update prop + recompute. Comando de toolbar "Crear pieza Tripta" + "Panel Tripta".

#### T7 (orquestador): Verificación visual + cierre
**Spec:** Con FreeCAD abierto + MCP (RPC 9875): crear doc, feature con preset 1.5" TC64 férula y gasket, `get_view` → PNG, verificar render (script `verify_render.py` del skill freecad-mcp-linux). Comparar con screenshot de la web (TriptaClamps3D-Web en main). Documentar en README/CHANGELOG. Push + PR de cada rama contra master, cerrar issues con `Closes #N`.

---

## Verificación global (antes de mergear)
1. `python -m pytest tests/ -q` → todo verde (puros, sin FreeCAD).
2. `flatpak run --command=freecadcmd org.freecad.FreeCAD -c "…"` smoke: importa módulo, crea feature 4 piezas, recompute, volúmenes > 0.
3. MCP visual: screenshot render de férula/gasket/spool/endcap — sólidos visibles, geometría plausible.
4. Comparación paramétrica: mismas dimensiones que la web → mismos perfiles (coordenadas idénticas validadas por T1).

## Riesgos y decisiones
- **Verificación FreeCAD en esta máquina:** FreeCAD es Flatpak (`org.freecad.FreeCAD`, UserAppData `~/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/`). freecadcmd vía `flatpak run --command=freecadcmd` requiere acceso al Flatpak; si falla, alternativa: MCP execute_code con GUI abierta (skill freecad-mcp-linux documenta ambos).
- **Dirección de arcos:** única conversión no trivial (Three absarc vs Part.Arc). Mitigado por tests de coordenadas portados (T1) + `test_geometry.py` (T4) que valida wire points.
- **Python version:** usar solo stdlib en el núcleo puro (sin numpy) para máxima compatibilidad con el Python embebido de FreeCAD.
- **Nombres de propiedades FreeCAD:** respetar convención CamelCase para properties visibles + flags de edición correctos (App::PropertyFloat read 0/1 en panel).
- **Sobregeneración:** al cambiar un slider no regenerar todo el documento si el objeto está en construcción — recompute trivial; aceptable.

## Entregables finales
- Repo público `triptamina-labs/tripta-fittings-freecad` con plugin instalable (Addon Manager).
- Issues cerrados por PRs (epic #1 + T1..T7).
- README con instalación y uso + CHANGELOG.
- Ramas por ola: `feat/wave1-core`, `feat/wave2-freecad`, `feat/panel-ui`.