# Earth Defense - Bullet Frenzy

A Python/PyOpenGL space-defense game originally built by two teammates for CSE423: Computer Graphics. Fly a spaceship, destroy incoming asteroids, and protect Earth.

This is a repaired portfolio revision. The original submission is preserved unchanged in `original/Lab-03(Final).py`. The original starter template and permitted-function list are unavailable, so compliance of this revision with those restrictions has not been verified. Add both contributors' names and actual contributions before publishing.

## Run on this Windows computer

1. Open this folder in File Explorer.
2. Double-click **setup_and_run.bat**.
3. Click the game window to give it keyboard focus.

The project environment has already been prepared in this local folder. The launcher will use it. On first setup elsewhere, the launcher creates `.venv` and downloads PyOpenGL; internet access is needed for that step only. It uses installed Python, or the Codex bundled Python if available.

If using the ZIP, choose **Extract All** first. Do not run the launcher from inside the ZIP.

## Run on another Windows computer

Install Python 3.10 or newer from https://www.python.org/downloads/windows/ and double-click **setup_and_run.bat**. Python 3.12 (64-bit) was used for verification. Setup errors stay visible in the terminal on failure.

For manual setup, open a terminal in this folder and run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

No environment activation is needed. If `py` is unavailable but `python --version` works, use `python` instead of `py -3` for the first command.

## How to play

- Asteroids start arriving after two seconds, then every five seconds initially. Every five kills raises the threat level; spawn intervals gradually shorten to a minimum of 2.5 seconds and asteroid speed has a cap.
- Each asteroid destroyed earns one point.
- Five asteroid impacts on Earth end the round.
- Your spaceship has three shields. Collisions remove one shield and grant 1.8 seconds of protection from additional damage. Losing all shields ends the round.
- **Aim assist is ON by default.** Turn toward an asteroid until gold LOCK brackets appear, then fire. The shot aims vertically and leads the asteroid automatically. It works within a 22-degree forward cone and does not target through Earth. Bullets fly straight after firing; they do not home.
- Low asteroids can now be shot from above. They remain above the ship's minimum altitude throughout their approach; the previous difficulty came from horizontal-only firing.
- For manual aim, toggle assistance OFF with T. Hold I/K to raise/lower the firing angle; J returns to level. Q/E still changes your ship's altitude.
- Use the radar to locate threats around Earth. Cyan is your ship, orange points are asteroids, and the blue disc is Earth. Targets on the far side may require flying around Earth.
- The status panel shows whether an acquired target is ABOVE, BELOW, or LEVEL with the ship. The dashed line ahead of the ship shows the firing direction.
- Earth blocks your ship and absorbs shots. Shots absorbed by Earth count as misses but do not damage it.
- The moon is decorative. High score and ships lost are tracked for the current application session, not saved to disk.

| Key | Action |
| --- | --- |
| W / S | Hold to fly forward / backward |
| A / D | Hold to turn left / right |
| Q / E | Hold to ascend / descend |
| Space | Hold to fire |
| Left mouse click | Fire once |
| V | Toggle cockpit / external camera |
| C | Toggle chase / overview camera; exits cockpit |
| T | Toggle aim assist |
| G | Toggle navigation grid (hidden initially) |
| I / K | Raise / lower manual firing angle |
| J | Reset manual firing angle to level |
| Arrow left / right | Orbit overview camera |
| Arrow up / down | Change overview camera height |
| Page Up / Page Down | Zoom overview camera in / out |
| P | Pause / resume |
| R | Restart after game over |
| Esc | Quit |

If the game pauses after minimizing, press P to resume. Pause before switching applications to avoid held-key input persisting if the operating system does not deliver a key release. A window of at least 900 x 600 is recommended for the HUD.

## Gameplay and visual improvements

- Three-dimensional aiming, motion prediction, and optional assistance for lower and higher targets.
- Gold target brackets, target elevation hints, and a firing guide.
- Radar with player heading and asteroid positions.
- Three-hit shields with temporary protection after damage.
- Gradual, capped difficulty progression.
- Chase camera with protection against entering Earth, alongside overview and cockpit views.
- Redesigned HUD with Earth integrity, shield bars, score, and threat level.
- NASA surface maps give Earth real continents/oceans and the Moon crater and dark-plain detail. Both use directional day/night lighting; Earth has a thin blue atmosphere rim.
- Stars are distributed over a distant sphere, with varied brightness and subtle color. Camera translation does not move them through the arena.
- The Moon is approximately 27% of Earth's radius; the orbit is separated visually but deliberately compressed for gameplay.
- The navigation grid is hidden by default; G toggles it.
- Map sources and processing are documented in `ASSET_CREDITS.md`. All texture assets are bundled; no additional dependencies are required.

## What was fixed

- Restart no longer crashes; it resets round state, bullets, explosions, spawn timing, and ship position.
- Ships lost are counted once per ship collision; the hit flag persists through game over.
- Simulation uses elapsed time with fixed small steps. Long stalls are capped to avoid large catch-up jumps.
- Movement responds to held keys and supports simultaneous turning and movement.
- Both firing controls share the same muzzle calculation and cooldown.
- Bullet removal no longer uses duplicate list indices. Segment collision checks prevent fast bullets skipping asteroids and choose the nearest hit.
- Asteroid movement uses a correct three-axis direction vector.
- Explosions expire independently of asteroid count.
- Stars are generated once; drawing no longer reseeds gameplay randomness.
- Earth surface patches are visible; bullet colors reset for each projectile.
- HUD and game-over text render without depth or lighting interference.
- Projection and viewport update on resize; overview camera controls avoid invalid positions.
- First-person camera looks along the firing direction and includes an aiming mark.
- Added pause, controlled frame scheduling, and clean exit.

## Project files

- `main.py`: OpenGL rendering and input, retaining the original spaceship model.
- `celestial.py` / `assets/`: Textured Earth and Moon, atmosphere, and distant starfield.
- `ASSET_CREDITS.md`: NASA surface-map credits and source links.
- `game_state.py`: Game rules and collision calculations, independent of OpenGL.
- `test_game.py`: Regression tests for movement, firing, collision, pause, game over, and restart.
- `run.py` / `setup_and_run.bat`: Local environment setup and launch.
- `requirements.txt`: Pinned dependency.
- `original/`: Unmodified original submission; run the repaired `main.py` instead.

## Verification

Verified on Windows using Python 3.12.14 and PyOpenGL 3.1.10:

- All 19 automated gameplay regression tests passed, including hitting low and high asteroids, Earth obstruction, manual vertical aim, shields, and restart.
- OpenGL frames rendered for overview, chase, first person, pause, game over, and resize; overview, chase, and resized HUD images were inspected.
- Input callbacks for view switching, pause, and restart ran successfully.
- The actual main event loop started and exited successfully.
- Launcher setup used an isolated environment and loaded FreeGLUT successfully.

These checks do not replace a complete manual playthrough or verify every graphics driver. Run tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_game
```

## Troubleshooting

**Python not found:** Install Python from the official site, reopen the terminal, and retry. The ZIP does not bundle Python or the local virtual environment.

**No module named OpenGL:** Use `setup_and_run.bat`, or install requirements with the exact environment commands above. Installing into a different Python environment will not fix the game environment.

**FreeGLUT could not load / glutInit is undefined:** The pinned Windows PyOpenGL package includes FreeGLUT DLLs. Verify that the requirements installation completed. If loading still fails, check the Microsoft Visual C++ runtime for your Python architecture. Official runtime downloads: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist .

**Blank window or OpenGL context failure:** Update the graphics driver from your device/GPU manufacturer and try a local desktop session. This game uses legacy desktop OpenGL; it is not a browser game.

**Dependency download fails:** Check internet access and retry; keep the exact error message if it still fails.

## GitHub preparation

Add both teammates' names and contribution details, then record a gameplay demo. Keep `.venv` out of Git (already covered by `.gitignore`). Document course template attribution. Choose any license with both contributors and with the starter-code terms in mind; this package does not assign a license automatically.
