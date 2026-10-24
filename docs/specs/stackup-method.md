# Stackup and trace geometry method

- **Status:** v1, 2026-10-24. Written by Claude for the T1 main board's stackup v1; generic, for every OpenDAP board.
- **Tool:** `odapkit stackup` ([`bin/odapkit-stackup`](../../bin/odapkit-stackup), [`tools/stackup/`](../../tools/stackup/)).

A board keeps its layer stack and the geometry of each impedance class in one machine-readable file, `hardware/stackup/stackup-<version>.toml`, explained by a spec in its `docs/specs/`. The file is the input to the fab's stack-up request and to the net classes; `odapkit stackup check` recomputes it after every change, so a width in the net classes is never older than the stack it came from.

## 1. Steps

1. **Stack.** Layer count, build (1+N+1, 2+N+2), each layer's role, copper weights and dielectrics from the fab's published materials, with every value that is not published marked as an assumption. `odapkit stackup stack` prints the layer table, the total thickness and the board's `[[distance]]` and `[thickness]` checks.
2. **Design.** For each class, the target impedance, the layer and its reference plane(s), and the dimension held fixed (a pair's gap). `odapkit stackup design` searches the free dimension; the result is rounded to 0.5 µm and recorded in the file with the impedance it gives (`width_um`, `gap_um`, `z_ohm`).
3. **Check.** `odapkit stackup check` recomputes every class: the nominal within the design window (default ±2 % of the target), the recorded `z_ohm` not stale (0.5 Ω), and the fab corners reported.
4. **Fab.** The file goes to the fab with the stack-up request. The fab's answer (its stack, its Dk at frequency, its etch compensation) replaces the assumptions, and the widths are recomputed before the net classes freeze. The fab trims widths to its test coupon; the board's numbers are the design intent, not the fab's final artwork.

## 2. Solver

A 2D quasi-static (quasi-TEM) field solver, the same class of method as commercial PCB impedance calculators. Laplace's equation is solved over the cross-section with linear finite elements ([scikit-fem](https://github.com/kinnala/scikit-fem), BSD-3-Clause) on a graded tensor grid that has a line on every conductor and dielectric edge. The Maxwell capacitance matrix comes from the field energy, with dielectrics and in vacuum; L = C₀⁻¹ / c². A single line gives Z₀ = √(L/C); a symmetric pair gives the odd and even modes, Z_diff = 2 Z_odd and Z_common = Z_even / 2. Effective permittivity and delay per millimetre are reported with each class, for skew budgets across layers.

**Why this solver.** It is a maintained FEM library installed the canonical way: `tools/stackup/pyproject.toml` pins numpy, scipy and scikit-fem, and `uv.lock` pins them with their hashes, so `uv run --locked` installs exactly the verified files. The problem setup is about 150 lines that can be read whole. Alternatives considered: closed-form calculators (IPC-2141A, Wadell, KiCad's calculator) are not field solvers and lose accuracy with thick copper, solder mask, cut-out planes and coupled pairs; atlc is unmaintained; openEMS is a 3D full-wave tool, far heavier than a cross-section needs.

**Model.**

- Planes are the domain's top and bottom boundaries at 0 V. An open (microstrip) problem is enclosed at about 60 × the line's height, which costs under 0.2 %.
- A copper layer between a line and its plane is cut out under the line (`cutout_um`); outside the cut-out it is ground copper. A cut-out layer is filled with the mean Dk of the dielectrics around it.
- An inner trace is embedded in the dielectric named by its layer's `fills` (the prepreg pressed around it). An outer trace carries a conformal solder mask of the mask layer's thickness.
- Etch is trapezoidal; the solve uses the mean width (drawn width minus half the `[etch]` reduction).
- Dielectric thicknesses are pressed thicknesses, copper surface to copper surface.
- Not modelled: frequency dependence of Dk and loss, surface roughness, glass-weave skew, resin-rich areas over cut-outs. These come from the fab's coupon and the board's SI simulation.

**Validation** (`odapkit stackup validate`, also run by the tests):

| Reference | Agreement required | Typical result |
|---|---|---|
| Cohn's exact stripline (zero thickness, conformal mapping) | ±0.5 % | −0.14 to −0.26 % |
| Hammerstad and Jensen microstrip with thickness correction (Wadell §3.5) | ±1.5 % | −0.14 to +0.09 % |
| KiCad's calculator model, microstrip, thin copper (transcribed from its source) | ±1.0 % | −0.3 % |
| A pair 3 mm apart against twice the single line | ±0.5 % | −0.08 % |

IPC-2141A and KiCad's model with thick copper are listed for comparison only. IPC-2141A reads 4–14 % low for the HDI geometries the boards use. KiCad's microstrip model adds a thickness term to the filling factor and reads about 3 % high when the copper is a third of the dielectric height (35 µm on 90 µm); it agrees with the solver for thin copper.

## 3. Tolerances

`check` moves one parameter at a time to each end of its `[tolerance]` range (dielectric thickness, Dk, width, copper thickness) and reports each change, the arithmetic worst case (every parameter at its bad end) and the root sum of squares. The ranges are assumptions unless the fab publishes them. The fab's impedance tolerance (±10 % at PCBWay) is held by the fab compensating the width against its coupon. A worst case outside it is therefore a warning, not a failure, and an RSS outside it means the geometry is too sensitive to rely on.

## 4. File format

```toml
version = 1
name = "…"
design_window_pct = 2.0            # nominal within target ± this

[etch]                              # trapezoid: top width = drawn − reduction
outer_reduction_um = 10.0
inner_reduction_um = 6.0

[tolerance]                         # fab corners for the sensitivity report
dielectric_pct = 10
er_pct = 5
width_um = 10
copper_pct = 15

[thickness]                         # nominal >= min_mm; nominal + tolerance_mm <= max_mm
min_mm = 1.0
max_mm = 1.2
tolerance_mm = 0.1
source = "…"

[[distance]]                        # copper surface to copper surface
from = "L1"
to = "L3"
min_um = 230
max_um = 240
source = "…"

[[layer]]                           # top to bottom
name = "L1"
type = "copper"                     # copper | dielectric | mask
thickness_um = 35
role = "signal"                     # free text
material = "…"                      # free text: source of the values
er = 4.45                           # dielectric and mask
fills = "above"                     # copper: the dielectric pressed around its traces

[[class]]
name = "D90-L1"                     # one geometry; several net classes may share it
netclasses = ["USB2_90D", "USB3_90D"]
type = "diff"                       # se | diff
target_ohm = 90
tolerance_pct = 10                  # the fab's window, for the corner report
layer = "L1"
reference = ["L2"]                  # one plane, or one above and one below
solve = "width"                     # width | gap: what `design` searches
gap_um = 100                        # pair edge-to-edge gap, drawn
width_um = 101.5                    # drawn width (recorded by design)
z_ohm = 89.99                       # recorded impedance (stale check)
cutout_um = 1600                    # optional: copper between line and plane cut out this wide
coplanar_gap_um = 600               # optional: same-layer ground this far from the line
constraints = "…"                   # free text: the constraint IDs it serves
```

A line referenced only from above (a bottom-side line) is solved on the mirrored stack.
