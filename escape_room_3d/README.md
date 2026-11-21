# Escape Room 3D — 13 rooms, chained keys

Standalone 3D puzzle game. No build step. Just open it in a browser.

## Run
- **Mac:** double-click `Play.command` — it starts localhost:8000 and opens the game in your browser. (First time: right-click → Open, if macOS Gatekeeper complains. Close the Terminal window to stop the server.)
- Manual: `cd escape_room_3d && python3 -m http.server 8000` then open http://localhost:8000
- Or just double-click `index.html` — works offline too. Three.js ships in the folder as `three.min.js`, so there is **no CDN, no internet needed, no build step**. Just keep `three.min.js` next to `index.html`.

## Play
- The progression is: Room 1's Key 1 opens Door 1; Room 2's colour riddle gives code `4154`; Room 3's ball puzzle drops Key 3; Room 4's animal floor reveals its own code; then the chained rooms continue with their keys.
- Controls: `WASD` move (always relative to where you look), mouse look, `E` interact **or throw**, `G` drop selected item, `Q` inventory, `1`-`9` select hotbar slot.
- **Aiming:** interaction is driven by the crosshair, which is always a small **white dot**. When your
  crosshair is on something usable, a prompt below the dot shows what `E` will do. Aiming at nothing
  falls back to the closest item in reach (so you can still grab something at your feet).
- Keys are **consumed** when you use them on a door, so you always carry at most one key.

### Room 1 is the joke room
No labels or signage (Room 1 is the only room with none — Room 2's riddle sign is the puzzle itself), 14 decoy gadgets (buttons, levers, sliders, dials, a keypad with no code),
six do-nothing junk pickups, and one throwable ball. **None of it opens anything.**
Key 1 is tiny (35% scale), dull grey, unlabeled, and lying on the floor in the north-east corner
behind a crate. Looking for it is the puzzle.

### Room 2: the colour riddle
Room 2 has no table and no key. Its north wall carries a painted sign with four clue lines, each in
its own colour (red, yellow, green, blue). Count the capitals in each coloured line and you get one
digit per colour — `4154`, typed on the in-game keypad to open Door 2. The answer is **derived** from
the clue text at startup and compared against the door's password, so the two can never drift apart
silently.

> **Editing the riddle?** The capital count *is* the puzzle, so capitalising an ordinary word silently
> changes the answer and can lock the player out. A capital you did not intend to count — including
> one at the end of a sentence, like `...while others Sleep.` — counts like any other. A mismatch logs
> a `[riddle] sign yields "..." but Door 2 expects "..."` warning in the console, and the smoketest
> fails. Set the capitals deliberately, or change `DOOR_PASSWORDS` to match what the sign now says.

The clue words are marked with `caps: true` (required — it is how a line is recognised as a clue) and
`underline: false`, which hides the underline. So the capitals stand out by being capitalised rather
than by being underlined.

### Room 3: posters and the yellow lamp
Room 3 has three local poster images (`Eggo`, `Dungeons & Dragons`, and `Bicycles`) hung on its walls. They are evenly spaced and clear of the doorways: `Dungeons & Dragons` and `Eggo` sit on the north wall at x = -2.2 and x = +2.2, and `Bicycles` is centred on the south wall, all at the same height. The east and west walls are left empty on purpose — each has a 2.2-wide doorway gap at z = 0, so a poster centred there would hang over a door.

Aiming at a poster shows an `[E] Interact with ... poster` prompt. It is a deliberate no-op: this game has no signage, so the poster itself is the target. Its ceiling lamp and emitted light are warm yellow. Throw the bouncy ball at that lamp to break it; the lamp goes dark, Key 3 drops near Door 3, and the ball is consumed.

> **Note:** open `index.html` over `http://` (e.g. `python3 -m http.server`) rather than `file://`. Browsers block canvas reads of local images under `file://`, so the posters render as empty frames.

**Swapping the artwork.** Drop a replacement image into `assets/posters/` and point its `path` in `POSTER_ASSETS` at it. Each entry's `width`/`height` is only the *first-frame* guess at the source pixel size; once the file really decodes, `hangPoster()` re-fits the plane and its frame to the image's true aspect ratio, so artwork of any shape hangs undistorted even if the declared size is stale. Filenames are matched by `path`, not by extension — the browser sniffs the real format, so a JPEG named `.png` still displays. Keep artwork local rather than linking generated canvas approximations.

### Room 4: the animal floor puzzle
Room 4 is a 5 × 4 floor puzzle with 20 animal pieces. The pieces are hidden until the player enters the room, then shuffled across the floor into separate positions. Pick a piece up with `E`, rearrange or store it in the inventory, and aim at a numbered floor space to place it. Correctly matching all 20 pieces reveals the code that unlocks Door 4. Pieces can be dropped with `G` and moved again.

### The three wall levers
Each lever is mounted on a hinge plate with a metal boss and a shaft that **sticks out from the
wall into the room**, ending in a red knob. `E` throws it down, `E` again throws it back up, and
the arm eases smoothly between the two positions instead of teleporting. The two south-wall levers
are mirrored so they tip *up* in world space, exactly like the north-wall one — no lever points
into its own wall.

### The keypad (in-game, no browser popups)
Pressing `E` on the keypad — or on any future `makeLock` / `makeSafe` — opens a panel **inside the
game window**:
- **4 digit boxes laid out across the top**, starting at `0000`, with the digit you are about to
  type highlighted in gold, so you can always see exactly what you entered.
- Click the on-screen `0`-`9` keys, or just type the numbers on your keyboard.
- The live entry, the last submitted combination, and the recent attempt history stay visible in the panel.
- `Backspace` steps back and clears that digit, `CLR` resets to `0000`, `ENTER` submits, `Esc`/`CLOSE` closes.
- Each physical keypad allows one submitted attempt every 30 seconds; the buttons lock and a countdown is shown while it waits.
- Nothing ever calls the browser's `window.prompt`, so no dialog ever appears outside the game.

### The ball is the only throwable
Pick it up (`E`), make sure it is the selected hotbar slot, aim, then press `E` while nothing else
is in reach. While the ball is selected and your crosshair is on nothing, a small orange
**Press E to throw** hint appears under the crosshair (it disappears the moment you aim at an
object or open the inventory). It flies with gravity, bounces off walls/crates (`ball.hits` counts
bounces), settles, and becomes a pickup again.

## How to expand

### Adding rooms
Rooms are **not** separate files by design — the whole world is generated from data, so most
changes are one line. Everything lives in `index.html`, split into numbered sections with a
FILE MAP comment at the top. Search for `SECTION 8` to jump to room 1.

| I want to... | Edit this |
|---|---|
| More/fewer rooms | `SECTION 1`: `ROOM_COUNT` (rooms, doors, keys, labels, win condition all follow) |
| Change room 1's decoys | `SECTION 8`: copy a `decoyBtn(...)` / `decoyLever(...)` / `decoySlider(...)` / `decoyDial(...)` line |
| Add junk pickups | `SECTION 8`: add a line to the `JUNK` array |
| Move Key 1 | `SECTION 8`: the `kx` / `kz` lines at the bottom of `decorateLobby()` |
| Redecorate an individual room | register a decorator: `ROOM_DECORATORS[4] = lv => { ... }` (see `SECTION 5`) |
| Different room 1 entirely | replace `decorateLobby()` — it is self-contained |
| Real code lock / safe | `SECTION 7`: `makeLock({...})`, `makeSafe({...})` — both open the in-game keypad |
| A lever on a back wall | `SECTION 8`: `decoyLever(x, y, z, name, line, -1)` — pass `-1` for a south wall |
| Keypad on a door | `SECTION 7` lock + `onUnlock: () => { /* remove the door collider */ }` |
| Throwable targets | hook `ball.hits` in `SECTION 6` / the loop in `SECTION 11` |
| Restyle the HUD | the `<style>` block at the top |

### Adding a safe with a hidden code (worked example)
```js
// 1. Put a note somewhere earlier that reveals the code (SECTION 8 or a decorator):
spawnPickup({ id: 'note5', label: 'Torn Note', icon: '📝', mesh: 'book',
  blurb: 'It reads: "the safe is 4123" — the note is kept, drop it with G.' },
  LEVELS[3].cx + 3, 1.5);

// 2. Drop the safe in a later room (SECTION 7 toolkit):
makeSafe({ id: 'safe5', label: 'Safe', x: LEVELS[4].cx + 3.5, y: 0.6, z: -2.5,
  lockCode: '4123', contains: { id: 'key6', label: 'Key 6', icon: '🔑' } });
```
`makeLock` handles the prompt, wrong-code feedback and solved state for you.

### Section map (top of `index.html`)
1. **CONFIG** — room count/size, palette, key list
2. **STATE** — game state, inventory, world registries (declared once)
3. **ENGINE** — three.js renderer/camera/lights + HUD handles
4. **PRIMITIVES** — `mat()`, `box()`, `label()`
5. **WORLD BUILD** — room shells, locked doors, EXIT, `spawnKey()`, default rooms
6. **ITEMS & PICKUPS** — `spawnPickup`, `giveItem`, `dropSelected`, `throwBall`/`stepBall`
7. **PUZZLE TOOLKIT** — in-game keypad (`openKeypad`), `makeLock`, `makeSafe`, decoy gadgets
   (the `decoyLever` `zDir` argument makes a lever mount correctly on either wall)
8. **LEVEL 1: LOBBY** — *edit room 1 here*
9. **HUD & INVENTORY** — objective, messages, hotbar, Q panel, drag & drop
10. **INPUT** — player, WASD, mouse look, pointer lock, hotkeys
11. **MAIN LOOP** — collision, interaction, animation, render

## Notes
- `three.min.js` is three.js **r160 (UMD build)** — the same renderer version the game was written
  with, so the lighting/brightness is identical to the original build (verified by pixel
  comparison). Keep it beside `index.html`.
- The inventory has 36 slots (9 hotbar + 27 backpack). Rearrange by dragging, or click one slot
  then click another to swap.
- Doors need their exact key; using the key consumes it.
- EXIT only opens after all 12 doors, then press `E` at it to win (timer + stats shown).
- If the mouse does not lock (some browsers refuse it), hold the **left button and drag** to look
  around — the game still runs.
- Any script error shows a red **PROBLEM:** banner at the bottom of the window instead of failing
  silently. Almost always it means `three.min.js` is missing from the folder or a JavaScript typo
  was introduced while editing — the banner includes the line number.

