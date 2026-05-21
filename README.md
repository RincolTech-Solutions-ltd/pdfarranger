## PDF Arranger — Rincol Tech Fork

This is a fork of [pdfarranger/pdfarranger](https://github.com/pdfarranger/pdfarranger) maintained by
[Rincol Tech Solutions](https://github.com/RincolTech-Solutions-ltd). It adds:

- **Signature insertion** — Type, draw freehand, or upload a photo of your signature. True PDF
  transparency via pikepdf SMask — no white box, smooth anti-aliased edges, works on any
  background colour.
- **View toggle button** — switch between full-page view and thumbnail grid with one click in the
  header bar.

Everything else is identical to the upstream project.
Licensed under **GPL-3.0** — free to use, copy, and modify. Modifications must remain open source.

---

*PDF Arranger* is a small Python-GTK application that helps you merge or split PDF documents and
rotate, crop and rearrange their pages using an interactive graphical interface.
It is a front end for [pikepdf](https://github.com/pikepdf/pikepdf).

![screenshot of PDF Arranger](https://github.com/pdfarranger/pdfarranger/raw/main/data/screenshot.png)

---

## Install on Linux (this fork)

### Option 1 — Clone and install (Ubuntu / Debian / Linux Mint)

```bash
# 1. Install system dependencies
sudo apt-get install -y python3-pip python3-wheel python3-gi python3-gi-cairo \
    gir1.2-gtk-3.0 gir1.2-poppler-0.18 python3-setuptools gettext \
    python3-dateutil python3-venv python3-pil git

# 2. Clone this fork
git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger

# 3. Install (editable — so updates are instant with git pull)
pip install --user --break-system-packages -e ".[pikepdf]"

# 4. Run
python3 -m pdfarranger
```

### Option 2 — Clone and install (Arch Linux)

```bash
sudo pacman -S poppler-glib python-pip python-gobject gtk3 python-cairo \
    libhandy python-pillow git

git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
pip install --user -e ".[pikepdf]"
python3 -m pdfarranger
```

### Option 3 — Clone and install (Fedora)

```bash
sudo dnf install -y poppler-glib python3-pip python3-gobject gtk3 python3-cairo \
    python3-wheel python3-pikepdf python3-img2pdf python3-dateutil libhandy \
    python3-pillow git

git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
pip install --user -e .
python3 -m pdfarranger
```

### Option 4 — Virtual environment (any Linux distro, no system pip changes)

```bash
# Install GTK system dependencies first (Ubuntu/Mint example):
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-poppler-0.18 python3-venv git

# Clone and set up venv:
git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
python3 -m venv --system-site-packages venv
venv/bin/pip install -e ".[pikepdf]"
venv/bin/python3 -m pdfarranger
```

### Getting updates

```bash
cd pdfarranger
git pull
# That's it — the editable install picks up changes immediately.
```

### Optional: launch from anywhere in the terminal

```bash
echo '#!/bin/bash
cd "$HOME/pdfarranger" && python3 -m pdfarranger "$@"' | sudo tee /usr/local/bin/pdfarranger
sudo chmod +x /usr/local/bin/pdfarranger
```

---

## Original upstream install options

| [Windows](https://github.com/pdfarranger/pdfarranger/releases) | [Flathub](https://flathub.org/apps/details/com.github.jeromerobert.pdfarranger) | [Snap Store](https://snapcraft.io/pdfarranger) | [More packages](https://github.com/pdfarranger/pdfarranger/wiki/Binary-packages) |
|---|---|---|---|

> Note: packages above are the upstream pdfarranger and do not include the signature or view-toggle features from this fork.

---

## User Guide

For a full guide on how to use the app (open files, rearrange, crop, insert signatures, keyboard shortcuts), see **[USAGE.md](USAGE.md)**.

---

## For developers

```bash
git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
pip install --user --break-system-packages -e ".[pikepdf]"
python3 -m pdfarranger
```

For testing see [TESTING.md](TESTING.md).

For Windows see [Win32.md](Win32.md).

For macOS see [macOS.md](macOS.md).


## For translators

Translations are located in the following files:

*   [`po`](po)`/LANG.po` for interface translation strings
*   [data/com.github.jeromerobert.pdfarranger.metainfo.xml](data/com.github.jeromerobert.pdfarranger.metainfo.xml) for repository integration
*   [data/com.github.jeromerobert.pdfarranger.desktop](data/com.github.jeromerobert.pdfarranger.desktop) for desktop integration
*   [config.py](pdfarranger/config.py) `LANGUAGE_NAMES` for native language name in preferences drop-down list

If you are not comfortable working with git, **you may edit translations directly from Github's web interface**. However, in the normal case
you would contribute translations by following these steps:

*   Download the main branch (see [For developers](#for-developers))
*   Checkout a new branch to save your changes: `git checkout -b update-translation-LANG`
*   Run `po/updatepo.sh LANG`, where `LANG` is the locale you would like to update
*   Update your translations in `po/LANG.po` file, and commit them; do not commit changes to `po/pdfarranger.pot` which may have been automatically regenerated
*   If possible, test your translation to see it in context (see [For developers](#for-developers))
*   Create a new pull request with your changes to the main branch

If you are editing mnemonics accelerators (letters preceded by an underscore), here are some additional guidelines. However, if you have no idea what this means, don't worry about it.
Try to follow these rules by priority order:

*   be consistent with other GTK/GNOME software
*   pick a unique letter **within that given menu** if possible
*   pick the same letter as the original string if available
*   pick a strong letter (e.g. in "Search and replace" rather pick `s`, `r` or `p` than `a`)
