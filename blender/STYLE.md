# Night Shift at STACKHOUSE — Blender style and dimension contract

Every generator script in `blender/<batch>/` follows this file. The Studio map, the
KitchenRenderer and the gameplay services rely on the dimensions below, so treat them as
an interface, not a suggestion. Library: `blender/lib/nslib.py` (read its docstrings).

## 1. Look
* **Stylized, chunky, readable.** Soft bevels on every hard edge (0.03–0.12 studs depending on
  size), simple bold silhouettes, no noisy detail. Clean low-poly with smooth shading where it
  helps (fruit, bread, creatures) and crisp facets where it helps (crates, appliances).
* **Food is the most saturated thing in any frame.** Environment colours are a step greyer.
* Environment palette: kitchen warm cream `#EFE6D2` and stainless `#B9C0C6`; dining room deep
  navy `#1E2A44` with neon pink `#FF4FA3` / cyan `#38E1FF`; freezer icy blue `#9FD3E8`;
  basement charcoal `#3A3D42`; brand accents STACKHOUSE red-orange `#E8502A` and mustard
  `#F2B33D`.
* Night ingredients are clearly "wrong": black bread, glowing sauce (Neon), purple mystery meat.
* Creatures are uncanny but cartoon-readable (DOORS-level stylization), never gory.
* Everything must read on a phone screen at a glance. If a preview at 256 px is mush, simplify.
* Never ship something that looks like default primitives (a bare cylinder "can", a cube
  "box"). Add the one or two features that make the object recognisable.

## 2. Technical rules
* 1 Blender unit = 1 stud. Z up. **Front faces Blender −Y.** Pivot = bottom-centre unless the
  object hinges (doors, lids: pass `pivot=` at the hinge line, bottom).
* Solid colours only, one part per colour/material (`ns.tag`). Part names are unique inside an
  asset, PascalCase, no spaces. Parts that change at runtime get a `recolor=` role
  (`"toast"` for bread, `"crate_body"`, `"crate_trim"`, `"tell_<name>"` for Regular tells...).
* Roblox materials allowed: SmoothPlastic (default), Plastic, Metal, DiamondPlate, Wood,
  WoodPlanks, Fabric, Glass, Neon, Concrete, Brick, Ice, Foil, Marble, Granite, Pebble, Slate.
* Triangle budgets: food 100–800, props 200–2,000, creatures/characters 2,000–8,000, building
  modules 500–5,000. `run_main` prints the count; stay inside the budget.
* Gameplay points are exported as **sockets** (`export_asset(..., sockets={...})`, see nslib).
  The map and the renderer find them as `Socket_<Name>` CFrame attributes on the Model.
* Asset names: `Category_Name` (Food_, Kitchen_, Shop_, Lobby_, Char_, Creature_, Cosmetic_).
* Collision: everything exports `can_collide=False` except building modules and big furniture
  that players should bump into (walls, counter, booths, tables, desk, shelves, stairs):
  those pass `can_collide=True`.
* Each generator script runs standalone: `bpyenv/bin/python blender/<batch>/<Asset>.py`
  renders the two-angle preview to `/home/claude/previews/<batch>/`; `NS_EXPORT=1` also
  exports; `NS_ICON=1` also renders the icon (where the asset has one).

## 3. Character scale (Roblox R15 avatar ≈ 5 studs tall, eye line ≈ 4.5)
| Thing | Size (studs) |
|---|---|
| Floor to ceiling (shop interior) | 12 |
| Door opening | 5 wide × 8 tall |
| Counter / prep worktop height | 3.0 |
| Booth seat height / table height | 1.6 / 2.8 |
| Wall module | 8 wide × 12 tall × 1 thick (window module: 8 wide, sill 3.5, head 9) |
| Walkway minimum | 5 wide |

## 4. Sandwich assembly contract (KitchenRenderer)
* A sandwich lies along the **asset's X axis** (Blender X), centred, bottom at Z = 0.
* Sub roll: **length 2.2, width 0.85**. Bottom half ≈ 0.30 tall, top half ≈ 0.42 tall (dome).
* Every filling/sauce asset is modelled to sit on that roll and carries meta:
  `ingredient` (config id), `layer_height` (thickness it adds to the stack),
  `layer_count` and `layer_spacing` (if the visual is N copies along X, like tomato slices;
  else 1 / 0). Fillings may overhang the roll by ≤ 0.08.
* Bread assets come in pairs: `Food_<Bread>_Bottom` and `Food_<Bread>_Top`, crust and crumb as
  separate parts, crust part `recolor="toast"` (the client darkens it with doneness).
* Cheese also exports a melted variant `Food_<Cheese>_Melted` (drapes over the filling below).
* Sauces export a ribbon `Food_<Sauce>_Ribbon` (thick glossy zig-zag along X).
* Stack order on the tray: Bottom bread → meats → cheeses → veggies → sauces → Top bread.

## 5. Kitchen contract
| Asset | Key dimensions | Sockets |
|---|---|---|
| Kitchen_PrepStation | 7 wide × 3 deep, worktop at 3.0; two trays (2.8 × 1.3) side by side | `Slot1`, `Slot2` (tray top centres, yaw 0 = sandwich along X), `CookCamera` (camera point ≈ 2.2 above and 2.6 in front of the trays, looking at them), `Prompt` |
| Kitchen_BinRail | 7.2 long frame holding 6 insert pans (1.1 × 0.9 × 0.45 deep), top at 3.0 | `Bin1`…`Bin6` (pan bottom centres) |
| Kitchen_SauceRail | 4 bottle holders, ≈ 3.2 long | `Bottle1`…`Bottle4` |
| Kitchen_Toaster | conveyor oven, 2 lanes side by side, ≈ 4 wide × 3 deep × 2.2 tall on the worktop | `Lane1In`, `Lane1Out`, `Lane2In`, `Lane2Out`, `Prompt` |
| Kitchen_WrapStation | 3 wide worktop with a paper roll | `Wrap`, `Prompt` |
| Kitchen_TicketPrinter / Kitchen_TicketRail | printer ≈ 1 cube; rail 4.5 long holding 4 tickets + 1 pinned slot | rail: `Ticket1`…`Ticket4`, `Pinned` |
| Kitchen_FreezerDoor | 5 × 8 door leaf, pivot at the hinge (left edge, bottom) | `Handle` |
| Kitchen_BreakerBox | wall-mounted, front −Y | `Lever`, `Prompt` |

Crates (`Kitchen_Crate`, gate asset) are one mesh for all five crate types, recoloured at
runtime; do not duplicate it.

## 6. Review loop (every asset)
1. Run the script → look at the preview PNG (two angles + 1-stud reference cube).
2. Ask: is it recognisable at phone size, chunky, soft-bevelled, on-palette, inside budget,
   front facing −Y, pivot right? Fix and re-render until yes.
3. Export (`NS_EXPORT=1`). Icons (`NS_ICON=1`) use the shared icon rig, never a custom one.
