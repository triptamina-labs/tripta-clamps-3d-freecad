# Continuar sesión — Port TriptaClamps3D-Web → Plugin FreeCAD

> Estado al cierre de la sesión del **2026-08-18 (madrugada)**. Este documento deja todo listo para que la próxima sesión retome la única tarea pendiente (T7) sin repetir nada.

## Estado actual (TODAS las olas de implementación COMPLETAS y mergeadas)

| PR | Rama | Contenido | Estado |
|----|------|-----------|--------|
| #9 | `feat/wave1-core` | Núcleo puro: `profile_cmds.py`, `constraints.py`, `presets.py` | ✅ Mergeado (`e8985f2`) |
| #10 | `feat/wave2-freecad` | `geometry.py`, `builder.py`, `feature.py`, `smoke_feature_cmd.py`, addon (`package.xml`, `Init.py`, `InitGui.py`, `workbench.py`, README, LICENSE) | ✅ Mergeado (`6672ef1`) |
| #11 | `feat/panel-ui` | `panel.py` (QDockWidget), `commands.py`, integración workbench | ✅ Mergeado (`d0bb0af`) |

**Master actual:** `d0bb0af`. Suite: **88/88 tests pytest** ✅. Smoke freecadcmd: **4/4 sólidos válidos** (volumen>0, Shape.isValid, BoundBox>1mm) ✅.

## Issues

- ✅ Cerrados: #1 (epic NO — ver abajo), #2, #3, #4, #5, #6, #7
- ⏳ **Abiertos para la próxima sesión:**
  - **#8 T7 — Verificación visual MCP + cierre de integración** (con label `wave3-ui, test`)
  - **#1 Epic** (permanece abierto hasta el cierre)

## ✅ LO QUE YA ESTÁ VERIFICADO (no rehacer)

- Núcleo puro portado 1:1 y testado (coordenadas idénticas a la web TS).
- La feature `Part::FeaturePython` genera los 4 sólidos (férula/gasket/spool/endcap) con preset 1.5" TC64 en **freecadcmd headless** — veredicto `PASS` en `/home/tripta/smoke_result.txt`.
- Mapeo preset→props del panel correcto (MAP_OK).
- Imports de `commands`/`panel` sin GUI OK.

## ⏳ LO ÚNICO QUE FALTA — T7 (#8): Verificación visual en GUI + cierre

Motivo de no haberse hecho esta sesión: **FreeCAD GUI no puede arrancar desde la sesión Hermes headless** (sin `DISPLAY`/`WAYLAND_DISPLAY`; error Qt `xcb-cursor` al intentarlo sin entorno gráfico). El GUI solo abre desde la sesión gráfica de Felipe.

### Pasos para la próxima sesión (con GUI disponible)

1. **Instalar el addon en FreeCAD** (para que aparezca el workbench):
   ```bash
   MODDIR="$HOME/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/Mod"
   mkdir -p "$MODDIR"
   # opción A (release estable): copiar el contenido del repo
   cp -r ~/repos/tripta-fittings-freecad "$MODDIR/tripta-fittings"
   # opción B (dev rápido, recomiendo esta): symlink para editar en vivo
   ln -s ~/repos/tripta-fittings-freecad "$MODDIR/tripta-fittings"
   ```
   > Nota: en FreeCAD v1-1, la carpeta Mod ya existe. Verificar ruta real con:
   > `flatpak run --command=freecadcmd org.freecad.FreeCAD -c "import FreeCAD as A; print(A.ConfigGet('UserAppData'))"`
2. **Abrir FreeCAD GUI** desde el escritorio de Felipe: `flatpak run org.freecad.FreeCAD` (debe lanzarse en su sesión gráfica, no en la Hermes headless).
3. **Seleccionar el workbench "Tripta Fittings"** en el selector de workbenches.
4. Usar **TriptaCreatePiece** (toolbar/menú) o el **panel** (TriptaOpenPanel): crear las 4 piezas con preset 1.5" TC64, cambiar parámetros y ver recompute paramétrico en vivo.
5. **Verificar visualmente** (per source-repo convention: render-and-verify como imagen):
   - Screenshot del viewport FreeCAD (MCP `get_view` si el RPC 9875 está vivo, o `computer_use` captura ventana FreeCAD).
   - Si no hay visión auxiliar, usar `verify_render.py` del skill `freecad-mcp-linux` (histograma + bbox) para confirmar sólido renderizado.
   - Comparar formas con la web `TriptaClamps3D-Web` (mismo preset).
6. **Cerrar #8** y **#1 (epic)** con comentario final + verificación adjunta.
7. Actualizar README (estado: "verificado visualmente en GUI") y este doc.

### Resolución del RPC MCP (opcional, para que el MCP de Hermes vea FreeCAD)
- El RPC 9875 solo escucha cuando FreeCAD GUI está abierto (addon `FreeCADMCP` con `auto_start_rpc: true` ya configurado).
- `hermes mcp list` muestra `freecad ✓ enabled`; pero los tools `mcp__freecad_*` solo se cargan en una sesión Hermes que arranca con el server conectado (si no aparecen, abrir una sesión nueva).

## Mapa de archivos del plugin

```
tripta_fittings/
├── profile_cmds.py   # núcleo puro: MoveTo/LineTo/Arc + perfil_ferula/gasket/endcap/spool + obtener_perfil
├── constraints.py    # validate_and_clamp_dimensions (pure)
├── presets.py        # 12 presets ASME BPE + lookups
├── geometry.py       # ProfileCmd → Line|ArcSegment (conversión de arcos según dirección)
├── builder.py        # build_solid: wire→face→revolve 360° eje Y → Part.Solid
├── feature.py        # TriptaFittingsFeature (Part::FeaturePython) + ViewProvider
├── commands.py       # TriptaCreatePiece, TriptaOpenPanel, register_commands()
├── panel.py          # panel QDockWidget (tipo, preset, sliders) + preset_to_props_map()
└── workbench.py      # TriptaFittingsWorkbench
Init.py / InitGui.py / package.xml / README.md / LICENSE
tests/ (test_profile_cmds, test_constraints, test_presets, test_geometry, smoke_feature_cmd.py)
```

## Notas de entorno (no perder)

- **FreeCAD = Flatpak** `org.freecad.FreeCAD` 1.1.3. UserAppData: `~/.var/app/org.freecad.FreeCAD/data/FreeCAD/v1-1/`.
- **freecadcmd headless** funciona SIEMPRE: `flatpak run --env=PYTHONPATH=<repo> --command=freecadcmd org.freecad.FreeCAD -c "..."`.
- **GUI + RPC 9875** SOLO desde la sesión gráfica del usuario (no desde sesión Hermes headless).
- Ver texto de la fecha: plan original en `.hermes/plans/2026-08-18_010000-port-tripta-clamps-freecad.md`.
