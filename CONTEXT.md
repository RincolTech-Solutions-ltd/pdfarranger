# CONTEXT.md

> **Cross-machine continuity bridge.** Read this first when resuming work on this project from any machine — it travels with the repo via git. Detailed conversation memory (feedback, decisions, deeper history) is mirrored at `Obsidian/myKnowledge/project-memory/pdfarranger/` in the shared Obsidian vault.

## What This Is
Fork of upstream [pdfarranger/pdfarranger](https://github.com/pdfarranger/pdfarranger) maintained by Rincol Tech Solutions, adding:
- **Signature insertion** — type, draw, or upload a signature; true PDF transparency via pikepdf SMask.
- **View toggle** — switch between full-page view and thumbnail grid.

## Stack
- Python-GTK application, front end for `pikepdf`. GPL-3.0 (modifications must remain open source).

## Status (as of 2026-06-11)
- Branch: `main`
- Recent work: extracted shared image utils and slimmed `signature.py`, fixed thumbnail selection-highlight clearing, removed startup limitations dialog, added `install.sh` one-command installer for all Linux distros.

## Active Work / Next Steps
- Editable pip install skips `data_files` — fixed by symlinking `~/.local/share/pdfarranger/` (see memory mirror for the exact fix).
- Everything outside the signature/view-toggle features tracks upstream — be mindful when merging upstream changes.

## Notes
- Fork of: `pdfarranger/pdfarranger` (upstream, GPL-3.0)
- Rincol fork remote: `RincolTech-Solutions-ltd`
