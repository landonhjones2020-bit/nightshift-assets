# BUILD LOG — Night Shift at STACKHOUSE (Build Prompt 01)

Mirror of `ServerStorage.Documentation.BUILD_LOG` in the place. Newest first within each section.

## Status
| Phase | State | Verified how |
|---|---|---|
| 0 Recon & setup | ✅ done | Verified: bpy 5.2.3 cube→FBX→Cycles PNG in workspace; repo attached with push; Studio reachable; HttpService GET of raw.githubusercontent.com works; DataStore read/write works in a real playtest |
| 1 Pipeline gate | ✅ done | Verified (edit-mode harness + playtest): local plugin NightShiftImporter v1.1 publishes meshes/icons with CreateAssetAsync (Studio beta "CreateAssetAsync Luau API" on); tomato/crate/Nibbler imported at correct scale, orientation, pivot and vertex colours; Nibbler Scurry plays in a playtest; NSZ icon decodes and displays |
| 2 Architecture & config | ✅ done | Config + validator + logic modules: Verified (playtest) — unit tests pass; ConfigValidator passes on every boot. ARCHITECTURE doc + map contract (ServerStorage.Documentation.ARCHITECTURE) |
| 3 Blender assets | 🔶 in progress | A_kitchen (17 props) done, pushed (a7b57bc) and imported (17/17). A_food, B_shop, C_lobby, D_characters, E_creatures being modelled; F cosmetics, G icons, H player poses not started |
| 4 Maps | 🔶 built with placeholders | `BuildTools.ShopMap` / `BuildTools.LobbyMap` (MapKit) generate both maps; every contract part present. Verified (playtest, Shift): all prompts created (22 restock, 5 crates, 5 hides, 2 cook, CCTV, bell, breaker, 5 slam), customers walk lot → front door (chime) → serve spots over NavNodes; nav graph fully connected (builder check). Verified (playtest, Lobby): map cloned by ModeService, 4 test-kitchen stations, 4 van pads, 5 screen/jukebox prompts, 16 world screens. Real meshes so far only for the kitchen props; the rest are pink placeholders until B/C import |
| 5 Core systems (server) | 🔶 server written | Verified (playtest): full run loop N1 cleared → Break Room → N2 quota miss → fired; rewards; receipts/gifts |
| 6 Entities / Director (server) | 🔶 server written | Verified (playtest): Director scripted events fire on time. Client visuals pending creature imports |
| 7 UI | 🔶 in progress | 30 screens; UIAudit 0 problems (edit-mode harness); Lobby/Shop/Shift HUD screenshots reviewed in playtests. Device-simulator pass Not tested |
| 8–11 | not started / partial | — |

## Next step
1. Import B_shop / A_food / C_lobby / D / E as each batch reports (`AssetImport.importBatch`), rebuild both maps, review screenshots in play mode, tune light values.
2. **Landon:** set `Lighting.Technology = Future` in the Lighting properties (scripts are not allowed to set it).
3. Phase 5–6 playtests on the real map: cook → toast → wrap → serve; creature visits; blackout + breaker; Shiver door.

## Decisions
- **Maps are generated, not hand-built** (`ServerStorage.BuildTools.ShopMap`, `LobbyMap`, shared `MapKit`): assets placed at exact coordinates or at other assets' sockets, translucent placeholders until an asset is imported, invisible collision + wall segments that also stop nav links crossing walls, and a reachability check of the whole NavNodes graph on every build. Re-run after each import; never hand-edit the map.
- **Shop layout** (80 × 56 + basement): prep line 12 studs from the counter, Break Room door → prep 15, prep → pantry ≈ 20, prep → freezer door ≈ 30, prep → office ≈ 27 (hallway door had to move to the west end because the bin rails line the back wall; Bible says 35), prep → breaker ≈ 70. 6 booths (Bible §4). The counter is a 16-stud pass-through under a header.
- **Doors (Bible §9.6):** `DoorService` + client `Controllers.Doors`. Touch doors (office, restroom, basement, back door) open within 6.5 studs and can be slammed (prompt, noise 30, shut 1.5 s); the front door opens for visitors only and chimes; the Break Room door is one-way during nights (only someone leaving opens it, outsiders get a note). The server only flips attributes; clients swing the leaf with a spring, so it is smooth on every device. The freezer door stays owned by the Shiver module.
- **Collision groups** (`Services.CollisionGroups`): Walls, Ghosts (pass Walls/StaffBarrier), NPCs (pass each other and StaffBarrier), StaffBarrier (front doorway). NPC models are assigned on spawn, including parts added later (looks).
- **Lighting is client-owned** (`Config.Lighting`, `Controllers.Lighting`): mode base (Shift night / Lobby dusk) → room look when the camera is inside `Rooms.Freezer`/`Basement`/`Dining` → dawn from 5:00 AM → blackout grade; the restroom lamp flickers (attribute Flicker). The basement has no light sources (flashlight only, Bible §6.6). Freezer cold mist uses the engine's built-in smoke texture (no external asset).
- **Lobby world** (`LobbyService`, client `LobbyWorld`): `Interact.<Name>` parts get prompts; Kind "Screen" prompts open UI screens client-side (no remote needed). World screens (leaderboards, Employee of the Month, van signs/numbers, daily board, kiosk) are SurfaceGuis built on `Boards.<Name>` parts, Scale-only with TextScaled + size constraints. VIP Lounge barrier is passable for VIP clients; the server returns non-VIPs found inside.
- **StreamingEnabled = false.** Measurement (Studio playtest, client, Lobby with placeholders): content tags Instances 112.5 MB, BaseParts 19.3, GraphicsMeshParts 5.3, GraphicsTexture 55.1, Gui 95.6; Studio's total (3,036 MB) includes the editor, so it is not representative. Each map is ≈ 1,000 parts. Re-measure on a phone (Developer Console) in a live test before launch.
- Default Baseplate and SpawnLocation removed from Workspace (they sat inside the kitchen); spawning is handled by LifeService.
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
- **Employee of the Month = "weekly top players"** (§3.2) but the leaderboards are all-time. The wall currently shows the top 3 of Nights Survived (all-time). A weekly board needs a per-week counter in the profile and a weekly OrderedDataStore — confirm you want that.
- Prep → manager's office is ≈ 27 studs walking, not 35 (§4), because the hallway door had to move clear of the bin rails. Tell me if the office should be farther.
