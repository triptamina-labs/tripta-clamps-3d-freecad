# Tripta Fittings — Workbench para FreeCAD

**Port del proyecto [TriptaClamps3D-Web](https://github.com/triptalabs/TriptaClamps3D-Web) a FreeCAD.**

Workbench paramétrico que genera piezas tri-clamp industriales con precisión dimensional certificada según ASME BPE.

---

## Características

- **4 piezas paramétricas**: férula (ferrule), gasket, spool y endcap.
- **Presets ASME BPE**: tablas con dimensiones certificadas para tamaños desde ½" Mini hasta 4".
- **Exportación nativa de FreeCAD**: STEP y BREP desde el propio workbench.
- **Cálculo puro**: el núcleo de dimensiones no depende de FreeCAD (testing sin GUI).
- **Validación de constraints**: previene dimensiones incompatibles con límites y tolerancias.

---

## Instalación

### Modo 1 — Addon Manager (recomado)

1. Abre FreeCAD → *Edit → Preferences → Addon Manager*.
2. Busca **tripta-fittings** (o instala desde URL del repositorio).
3. Reinicia FreeCAD.

### Modo 2 — Instalación manual

Copia la carpeta del repositorio dentro del directorio de addons de FreeCAD:

```bash
# Linux
cp -r tripta-fittings-freecad ~/.local/share/FreeCAD/Mod/tripta-fittings

# macOS
cp -r tripta-fittings-freecad ~/Library/Application\ Support/FreeCAD/Mod/tripta-fittings

# Windows
xcopy /E /I tripta-fittings-freecad "%APPDATA%\FreeCAD\Mod\tripta-fittings"
```

Reinicia FreeCAD. El workbench aparecerá en el selector de workbenches como **Tripta Fittings**.

---

## Uso básico

1. Selecciona el workbench **Tripta Fittings** desde el selector de workbenches.
2. Usa el menú *Tripta Fittings → Create Piece* para abrir el panel de creación (ola 3).
3. Selecciona una pieza (férula, gasket, spool o endcap).
4. Elige un preset ASME BPE o ajusta los parámetros manualmente.
5. Haz clic en **Create** para generar la geometría en FreeCAD.
6. Modifica parámetros y ejecuta **Recompute** (Ctrl+Shift+R) para actualizar.

---

## Estructura del proyecto

```
tripta-fittings-freecad/
├── package.xml              # Metadatos del Addon Manager
├── Init.py                  # Hook de inicialización FreeCAD
├── InitGui.py               # Hook GUI — registra el workbench
├── README.md                # Este archivo
├── LICENSE                  # MIT
├── tripta_fittings/         # Paquete principal
│   ├── __init__.py
│   ├── constraints.py       # Dimensiones y tolerancias
│   ├── presets.py           # Tablas ASME BPE
│   ├── profile_cmds.py      # Comandos de creación de perfiles
│   └── workbench.py         # Clase TriptaFittingsWorkbench
├── tests/                   # Suite de pruebas
│   ├── test_constraints.py
│   ├── test_presets.py
│   └── test_profile_cmds.py
└── .venv/                   # Entorno virtual (desarrollo)
```

---

## Ejecución de tests

### Pruebas del núcleo puro (sin FreeCAD)

```bash
cd tripta-fittings-freecad
.venv/bin/python -m pytest tests/ -v
```

### Smoke test con FreeCAD (headless)

```bash
flatpak run --env=PYTHONPATH=/home/tripta/repos/tripta-fittings-freecad \
  --command=freecadcmd org.freecad.FreeCAD -c "
import tripta_fittings
print('IMPORT_OK')
"
```

---

## Estado actual

| Ola | Descripción | Estado |
|-----|-------------|--------|
| 1 | Núcleo puro (constraints, presets, constants) | ✅ Completada |
| 2 | FreeCAD adapters (profile_cmds, workbench stub) | ✅ Completada |
| 3 | UI — TaskPanel y comandos interactivos | 🔲 Pendiente |
| 4 | Exportación STEP/BREP nativa | 🔲 Pendiente |
| 5 | Tests de integración con FreeCAD headless | 🔲 Pendiente |

---

## Roadmap

- [x] Paquete Python puro con datos ASME BPE
- [x] Restricciones dimensionales y validación
- [x] Comandos de perfiles básicos
- [ ] Workbench con menú y TaskPanel
- [ ] Panel paramétrico interactivo
- [ ] Exportación a STEP y BREP
- [ ] Integración con FreeCAD Assembly
- [ ] Documentación y ejemplos

---

## Licencia

MIT — Ver [LICENSE](LICENSE).

---

**Autor:** Felipe Castellanos Cárdenas — [TriptaLabs](https://triptalabs.co)
