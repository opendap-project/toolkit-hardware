# Component export contract

Every OpenDAP component (board, case core, faceplates, HATs, the HAT Case Standard, …) keeps its own internal sources: KiCad, FreeCAD, Blender, simulations, code. Towards everyone else it publishes itself **as a single unit**, through its `export/` folder.

Composition is hierarchical, and not only at the top: any component may consume another component's export wherever that makes sense (a HAT consumes the device-side piece from `hat-standard`; a faceplate consumes the faceplate interface from `case`), and the product integration (`t1`) consumes them all. At every level, an imported component behaves as one part, not as its internal pieces.

## Rules

1. Consumers read only `export/`, never the sources of another repository.
2. Each export is pinned to a tagged version of the producing repository.
3. An export declares the interfaces it implements and their versions.
4. Exports are generated locally from the sources and committed with their tag.

## `export/` contents

`component.yaml` describes the export: name, version, implemented interfaces with their versions, and the list of exported files. The exported files depend on the component:

| Domain | Internal sources | Exported as one unit | Consumed for |
|---|---|---|---|
| Mechanics | FreeCAD | STEP of the whole component as a single body, plus a simplified envelope; mass and center of gravity in `component.yaml` | Fit, interference, drop and thermal studies of the assembly |
| Renders | Blender | A Blender collection (linked, not appended), plus glTF as a neutral format | Renders of the assembly |
| Electronics | KiCad | STEP of the assembled PCB, connector netlist, interface definition | System-level connectivity checks across connectors |
| Signal paths | Simulations | Touchstone (`.sNp`) model of the component's segment of each high-speed channel | Cascading segments into a full channel model |
| Power and thermal | Simulations | Dissipated power and simplified thermal geometry | Thermal simulation of the assembly |
| Firmware | Rust | Versioned binaries | OpenDAP OS image |
| Software and OS | Rust, overlays | Crates, OpenDAP OS packages, device tree overlays | OpenDAP OS image composition |

The exact `component.yaml` schema is not defined yet.
