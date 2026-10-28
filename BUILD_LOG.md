# BUILD LOG — Night Shift at STACKHOUSE (Build Prompt 01)

Mirror of `ServerStorage.Documentation.BUILD_LOG` in the place. Newest first within each section.

## Status
| Phase | State | Verified how |
|---|---|---|
| 0 Recon & setup | ✅ done | Verified: bpy 5.2.3 cube→FBX→Cycles PNG in workspace; repo attached with push; Studio place 105460251185388 reachable; HttpService GET of raw.githubusercontent.com works; DataStore read/write works in a real playtest |
| 1 Pipeline gate | ⏳ blocked on Studio restart | Assets modelled, rendered, exported and pushed (tomato, crate, Nibbler + Idle/Scurry). Studio refuses `CreateAssetAsync` from the assistant tool, so a local plugin (NightShiftImporter.lua) was installed in Landon's Plugins folder — waits for Studio to be reopened |
| 2 Architecture & config | 🔶 in progress | Config + validator + logic modules: Verified (playtest) — 54/54 unit tests pass on the Play server; ConfigValidator passes |
| 3–11 | not started | — |

## Next step
1. When Studio has been reopened (ServerStorage.NS_Pipeline has ImporterVersion): run the gate — `AssetImport.importAsset("gate/Food_Tomato")`, `("gate/Kitchen_Crate")`, `("gate/Test_TomatoVertexColor")`, `("gate/Creature_Nibbler", {rigName="Nibbler"})`; screenshot next to a 1-stud part; Nibbler Scurry playtest with MoveTo; tomato icon upload.
2. Continue Phase 2/5 code meanwhile.

## Decisions
- **UI standard = AutoScale Lite** (Landon, 2026-10-28). Bible updated to v2.1 (§13.11 + hard rule 11). Supersedes Prompt Phase 7 "created once by its controller … IgnoreGuiInset = true": screens are Studio-authored ScreenGuis in StarterGui, Scale-only, UIAspectRatioConstraint on each top-level child, ScreenInsets = CoreUISafeInsets.
- **Path A uses a local plugin.** `AssetService:CreateAssetAsync` returns "not available yet" from the Studio assistant's execute_luau; Roblox documents it for locally loaded plugins. `studio-plugin/NightShiftImporter.lua` (in this repo, installed to `%LOCALAPPDATA%\Roblox\Plugins`) publishes meshes only from this repo's raw URLs; everything else (MeshParts, colours, rigs) is done by `ServerStorage.BuildTools.AssetImport`.
- **Game source code is NOT in this public repo** (anti-cloning); the place file is the source of truth for code.
- Config modules added beyond the bible tree: `Config.Player` (movement/stamina/flashlight/life timing) and `Config.Hazards` (power/noise/hiding/CCTV/doors) so numbers stay findable.
- Profile schema additions: `titles`, `title` (level-reward titles need storage).
- Riddle constraints authored per Secret (Config.Riddles); `toast = nil` accepts any state except Burnt.
- Order modifications (Night 3+): 35% chance per human order, one "no X"/"extra X" (bible gives no rate).
- Daily quests drawn deterministically from the UTC day number (same three for everyone).
- `HttpService.HttpEnabled` set true for development (asset/anim fetches). Runtime game code does not use HTTP; turn it off before launch.
- Studio-only `ServerStorage.DevProbe` BindableFunction (created by Bootstrap only in Studio) lets the build session inspect live service state.

## Open bugs
- none yet

## Asset IDs
- none yet (see ASSET_MANIFEST after the gate)

## Bible Questions
- none yet
