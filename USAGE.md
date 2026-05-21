# PDF Arranger — User Guide

PDF Arranger is a free, offline desktop app for Linux that lets you rearrange, merge, split,
rotate, crop, and sign PDF files — all without uploading your documents anywhere.

---

## Download and Install

### Ubuntu / Linux Mint / Debian

Open a terminal and run:

```bash
sudo apt-get install -y python3-pip python3-gi python3-gi-cairo \
    gir1.2-gtk-3.0 gir1.2-poppler-0.18 python3-setuptools \
    python3-dateutil python3-pil git

git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
pip install --user --break-system-packages -e ".[pikepdf]"
python3 -m pdfarranger
```

### Arch Linux

```bash
sudo pacman -S poppler-glib python-pip python-gobject gtk3 python-cairo libhandy python-pillow git
git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
pip install --user -e ".[pikepdf]"
python3 -m pdfarranger
```

### Fedora

```bash
sudo dnf install -y poppler-glib python3-pip python3-gobject gtk3 python3-cairo \
    python3-pikepdf python3-dateutil libhandy python3-pillow git
git clone https://github.com/RincolTech-Solutions-ltd/pdfarranger.git
cd pdfarranger
pip install --user -e .
python3 -m pdfarranger
```

### Launch from anywhere (optional)

After installing, create a shortcut so you can type `pdfarranger` in any terminal:

```bash
echo '#!/bin/bash
cd "$HOME/pdfarranger" && python3 -m pdfarranger "$@"' | sudo tee /usr/local/bin/pdfarranger
sudo chmod +x /usr/local/bin/pdfarranger
```

---

## Opening and Saving PDFs

| Action | How |
|---|---|
| Open a PDF | File > Open, or drag a PDF file into the window |
| Add more pages | File > Add, or drag another PDF on top |
| Save (same file) | File > Save (Ctrl+S) |
| Save as new file | File > Save As (Ctrl+Shift+S) |

---

## Rearranging Pages

- **Drag and drop** thumbnails left or right to reorder pages.
- **Select multiple pages** by holding Ctrl or Shift while clicking.
- **Delete pages** — select them, then press Delete or use Edit > Delete.

---

## Rotating Pages

Select one or more pages, then:
- Click the **Rotate Left** or **Rotate Right** buttons in the header bar.
- Or use Edit > Rotate 90 / 270.

---

## Merging PDFs

1. Open the first PDF.
2. Use File > Add to bring in additional PDFs.
3. Drag pages into the order you want.
4. Save As a new file.

---

## Splitting a PDF

1. Open the PDF.
2. Select the pages you want in the first output file.
3. File > Save As to save only the selected pages, OR
4. Use Edit > Split to split at a specific page.

---

## Cropping Pages

1. Select the pages to crop.
2. Edit > Crop.
3. Drag the crop handles in the preview, then click Apply.

---

## Inserting a Signature

This fork adds a built-in signature tool. Access it two ways:
- Right-click any page thumbnail > **Insert Signature...**
- Edit menu > **Insert Signature...**

### Step 1 — Create your signature

The dialog has three tabs:

**Type tab**
- Type your name in the box.
- Choose a colour from the palette (blue, black, grey).
- Click any style in the font grid to pick a font.

**Draw tab**
- Draw your signature freehand using your mouse or touchpad.
- Click Clear to start over.

**Upload Image tab**
- Click "Select image" to choose a PNG or JPEG file (e.g. a photo of your handwritten signature).
- Three versions are shown:
  - **Original** — unmodified
  - **Transparent A** — background removed (best for clean white paper scans)
  - **Transparent B** — higher contrast, better for yellowish or grey paper
- Select the version that looks cleanest.

### Step 2 — Position the signature

After clicking Insert, a placement dialog opens showing your page with the signature overlaid.
- **Drag the signature** to move it anywhere on the page.
- Use the **Horizontal offset** and **Vertical offset** spinboxes for precise positioning.
- Click **OK** to place, or **Cancel** to abort.

### Tips

- The signature is placed as a transparent overlay — no white box, even over coloured backgrounds.
- For a photo signature, "Transparent A" works well for most clean scans.
  Use "Transparent B" if the paper has a colour tint.
- After placing, save your PDF normally with Ctrl+S.

---

## Switching Between Thumbnail Grid and Full-Page View

- **Double-click** any thumbnail to open it in full-page view.
- Click the **toggle button** in the header bar (top-right area) to switch back to the thumbnail grid.
  - When in full-page view the button shows a grid icon.
  - When in thumbnail view the button shows a single-page icon.
- You can also use View > Fit One Page and View > Zoom In/Out.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+O | Open |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+A | Select all pages |
| Delete | Delete selected pages |
| Ctrl++ / Ctrl+= | Zoom in |
| Ctrl+- | Zoom out |

---

## Getting Updates

```bash
cd pdfarranger
git pull
```

The install is live — updates take effect immediately without reinstalling.

---

## Reporting Issues

Open an issue at: https://github.com/RincolTech-Solutions-ltd/pdfarranger/issues

---

## License

GPL-3.0. Free to use, share, and modify. If you distribute a modified version, it must also be
open source under GPL-3.0.
