# CLI Arkanoid

A terminal Arkanoid / brick-breaker game built with `curses`.

## What This Project Does

- Lets you move a paddle in the terminal to bounce the ball and clear every brick.
- Tracks score, waves, local high scores, and simple falling power-ups.
- Includes a title screen, round countdown, game over flow, and high-score entry.

## Refactor Highlights

- Reorganized the code around clear data objects and smaller update/render helpers.
- Replaced fragile non-ASCII UI glyphs with plain ASCII so the game renders more reliably across terminals.
- Added a real `3` lives system, so the `+` power-up now gives an extra life.
- Kept the other power-ups intact: `E` expands the paddle and `S` slows the ball.

## Run

```bash
python arkanoid.py
```

On this machine, the compatible Windows launcher is:

```powershell
.\run_game.ps1
```

## Controls

- `Left` / `A`: move left
- `Right` / `D`: move right
- `Space` / `Enter`: start or confirm
- `Q` / `Esc`: quit

## Requirements

- Terminal size of at least `60x24`
- A Python environment with `curses`
- On Windows, you will usually need `windows-curses`
