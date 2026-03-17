# CLI Puzzle Game - Design Spec

## Overview

CLI hacker-themed narrative puzzle game. Split-pane terminal UI: ASCII art scene on top, interactive command area on bottom. Player traces a missing programmer through a series of puzzles using progressive terminal commands.

## Core Decisions

- **Genre:** Narrative puzzle + hacker simulation (CLI Watch Dogs)
- **Command style:** Progressive - simplified early, realistic later
- **Story structure:** Linear chapters
- **Chapter 1 length:** 15-20 minutes
- **Tech stack:** Python + Textual
- **Art style:** Pixel-block ASCII art (█▓░▒)
- **AI usage:** Dynamic content generation (file names, logs, passwords vary per playthrough) + AI-assisted development
- **Save system:** Auto-save per puzzle checkpoint

## UI Layout

```
┌─────────────────────────────────────────┐
│           Scene Panel (40-50%)           │
│   Pixel-block ASCII art of location     │
├─────────────────────────────────────────┤
│           Terminal Panel (50-60%)        │
│   Narrative text + command input        │
│   > player commands here                │
└─────────────────────────────────────────┘
```

## Command System

### Basic (Act 1)
- `ls` - list items in scene
- `cat <item>` - read/examine item
- `use <item> [target]` - use item
- `look` - re-examine scene
- `take <item>` - pick up item
- `inventory` / `bag` - view inventory
- `help` - show available commands

### Advanced (Act 2-3)
- `ssh <address>` - connect to machine
- `scan` - discover network nodes
- `grep <keyword> <file>` - search in files
- `decrypt <file>` - decrypt with found key
- `history` - view command history (may contain clues)

## Chapter 1: "Offline Signal"

### Act 1 - Locked Room (5 min)
Player wakes in underground server room. Learn basic commands. Find key, escape room.

### Act 2 - Server Room (7 min)
Explore server room. SSH into missing programmer's machine. Piece together clues from logs, chat records, code comments. Discover: he found something hidden in user data.

### Act 3 - The Trace (5 min)
Scan internal network. Find encrypted machine. Decrypt using collected clues. Find farewell message + lead to next chapter. Cliffhanger: "You shouldn't have opened this."

## Architecture

```
cli-puzzle/
├── main.py              # Entry point
├── app.py               # Textual App, split-pane layout
├── engine/
│   ├── scene.py          # Scene management
│   ├── command.py        # Command parser
│   ├── inventory.py      # Inventory system
│   └── save.py           # Auto-save (JSON)
├── content/
│   ├── chapter1.json     # Chapter 1 scene definitions
│   └── ascii_art/        # ASCII art files per scene
└── saves/
    └── save.json          # Player save data
```
