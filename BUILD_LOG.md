# BUILD LOG — Night Shift at STACKHOUSE (Build Prompt 01)

Mirror of `ServerStorage.Documentation.BUILD_LOG` in the place. Newest first within each section.

## Status
| Phase | State | Verified how |
|---|---|---|
| 0 Recon & setup | ✅ done | Verified: bpy 5.2.3 cube→FBX→Cycles PNG in workspace; repo attached with push; Studio place 105460251185388 reachable; HttpService GET of raw.githubusercontent.com works; DataStore read/write works in a real playtest |
| 1 Pipeline gate | ⏳ blocked on Studio restart | Assets modelled, rendered, exported and pushed (tomato, crate, Nibbler + Idle/Scurry). Studio refuses `CreateAssetAsync` from the assistant tool, so a local plugin (NightShiftImporter.lua) was installed in Landon's Plugins folder — waits for Studio to be reopened |
| 2 Architecture & config | 🔶 in progress | Config + validator + logic modules: Verified (playtest) — 54/54 unit tests pass on the Play server; ConfigValidator passes. ARCHITECTURE doc + map contract written (ServerStorage.Documentation.ARCHITECTURE) |
| 3 Blender assets | 🔶 in progress | Batches A_food, A_kitchen, B_shop being modelled (scripts in `blender/<batch>/`); not yet imported (needs the gate) |
| 5 Core systems (server) | 🔶 server written | Verified (playtest): full run loop N1 cleared → Break Room → N2 quota miss → fired; rewards; receipts/gifts; 36 services boot in both modes |
| 6 Entities / Director (server) | 🔶 server written | Verified (playtest): Director scripted events fire on time. Client visuals pending |
| 7 UI | 🔶 in progress | UIKit (+Motion, Icons), UIAudit, UIBuilder: 29 screens built, Verified (edit-mode harness): UIAudit 0 problems; screenshots reviewed in Studio. Controllers next |
| 4, 8–11 | not started / server parts done | — |

## Next step
1. When Studio has been reopened (ServerStorage.NS_Pipeline has ImporterVersion): run the gate — `AssetImport.importAsset("gate/Food_Tomato")`, `("gate/Kitchen_Crate")`, `("gate/Test_TomatoVertexColor")`, `("gate/Creature_Nibbler", {rigName="Nibbler"})`; screenshot next to a 1-stud part; Nibbler Scurry playtest with MoveTo; tomato icon upload.
2. Continue Phase 2/5 code meanwhile.

## Decisions
- **Icons travel as NSZ** (base64 of "NSZ1" + u16 w/h + zlib RGBA). Studio's `upload_image` refuses raw.githubusercontent URLs ("Image Url is not trusted"), so the importer plugin (v1.1) inflates NSZ payloads into an EditableImage and publishes them with CreateAssetAsync; IDs land in the generated module `Shared/Generated/Icons`.
- **Sockets:** Blender assets export named gameplay points (`Socket_<Name>` CFrame attributes on the Model) so the map and renderer line up with the models; dimensions are an interface in `blender/STYLE.md`.
- **UIKit lives in `ReplicatedStorage.Client.UIKit`** (Bible says `Client/UIKit`): the edit-time UIBuilder (server context) and client controllers both require it.
- **Touch minimums switch on at runtime:** `TouchMin` UISizeConstraints are stored with MinSize 0 and attribute Min (44 / 72); UIController enables them on touch devices only, so mouse/gamepad layouts are exactly as designed.
- **TV safe area:** on the 10-foot interface UIController maps each interactive screen's top-level clusters into the central 90% (Position 0.05 + 0.9·p, Size 0.9·s) instead of a 16:9-letterboxed root container (a root container with an aspect constraint would stop HUD clusters hugging phone edges).
- **Full-screen layers** (backdrop, FX vignettes, CCTV static, jumpscare, loading/teleport art) are direct children of ScreenInsets.None screens marked `FullScreen = true` and are exempt from the per-child aspect constraint (an aspect constraint would letterbox them).
- **Templates are stored invisible** (GuiObjects under a Folder still render); `UIKit.clone` shows clones.
- **Studio require cache:** edited modules are swapped for fresh clones with `BuildTools.Reload` before re-requiring at edit time.
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
