#!/usr/bin/env bash
# PDF Arranger — Rincol Tech Fork
# One-command installer for Linux (Ubuntu / Mint / Debian / Arch / Fedora)
#
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/RincolTech-Solutions-ltd/pdfarranger/main/install.sh)
#   bash <(wget -qO- https://raw.githubusercontent.com/RincolTech-Solutions-ltd/pdfarranger/main/install.sh)

set -e

REPO="https://github.com/RincolTech-Solutions-ltd/pdfarranger.git"
INSTALL_DIR="$HOME/pdfarranger"
LAUNCHER="/usr/local/bin/pdfarranger"
LOCAL_LAUNCHER="$HOME/.local/bin/pdfarranger"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor"

echo ""
echo "======================================================"
echo "  PDF Arranger — Rincol Tech Fork — Installer"
echo "======================================================"
echo ""

# ── Detect distro ─────────────────────────────────────────────────────────────
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)

# ── Install system dependencies ────────────────────────────────────────────────
echo "[1/5] Installing system dependencies for: $DISTRO"

case "$DISTRO" in
    ubuntu|linuxmint|debian|pop|elementary|zorin)
        sudo apt-get update -qq
        sudo apt-get install -y \
            python3-pip python3-wheel python3-gi python3-gi-cairo \
            gir1.2-gtk-3.0 gir1.2-poppler-0.18 python3-setuptools \
            gettext python3-dateutil python3-venv python3-pil git
        ;;
    arch|manjaro|endeavouros)
        sudo pacman -Sy --noconfirm \
            poppler-glib python-pip python-gobject gtk3 python-cairo \
            libhandy python-pillow git
        ;;
    fedora|rhel|centos|rocky|almalinux)
        sudo dnf install -y \
            poppler-glib python3-pip python3-gobject gtk3 python3-cairo \
            python3-wheel python3-pikepdf python3-img2pdf python3-dateutil \
            libhandy python3-pillow git
        ;;
    opensuse*|sles)
        sudo zypper install -y \
            python3-pip python3-gobject python3-gobject-Gdk gtk3 \
            python3-cairo typelib-1_0-Gtk-3_0 typelib-1_0-Poppler-0_18 \
            python3-Pillow git
        ;;
    *)
        echo "WARNING: Distro '$DISTRO' not recognised."
        echo "Attempting to continue — install GTK3 + python3-gi manually if this fails."
        ;;
esac

echo ""

# ── Clone or update repo ───────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "[2/5] Updating existing installation at $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "[2/5] Cloning repository to $INSTALL_DIR"
    git clone "$REPO" "$INSTALL_DIR"
fi

echo ""

# ── Install Python package ─────────────────────────────────────────────────────
echo "[3/5] Installing Python package"
cd "$INSTALL_DIR"

if pip install --user --break-system-packages -e ".[pikepdf]" 2>/dev/null; then
    true
elif pip install --user -e ".[pikepdf]" 2>/dev/null; then
    true
else
    python3 -m venv --system-site-packages "$INSTALL_DIR/venv"
    "$INSTALL_DIR/venv/bin/pip" install -e ".[pikepdf]"
    VENV_INSTALL=true
fi

echo ""

# ── Create launchers ───────────────────────────────────────────────────────────
echo "[4/5] Creating launchers"

if [ "$VENV_INSTALL" = true ]; then
    LAUNCH_CMD="\"$INSTALL_DIR/venv/bin/python3\" -m pdfarranger \"\$@\""
else
    LAUNCH_CMD="python3 -m pdfarranger \"\$@\""
fi

# /usr/local/bin launcher (system-wide)
sudo tee "$LAUNCHER" > /dev/null <<LAUNCHEOF
#!/bin/bash
cd "$INSTALL_DIR" && $LAUNCH_CMD
LAUNCHEOF
sudo chmod +x "$LAUNCHER"

# ~/.local/bin launcher (pip may have created one — fix it to cd first)
mkdir -p "$HOME/.local/bin"
cat > "$LOCAL_LAUNCHER" <<LAUNCHEOF
#!/bin/bash
cd "$INSTALL_DIR" && $LAUNCH_CMD
LAUNCHEOF
chmod +x "$LOCAL_LAUNCHER"

echo ""

# ── Install desktop entry and icons ───────────────────────────────────────────
echo "[5/5] Installing desktop entry and icons"

# Icons
for size in 16x16 32x32 48x48 256x256; do
    mkdir -p "$ICONS/$size/apps"
    cp "$INSTALL_DIR/data/icons/hicolor/$size/apps/com.github.jeromerobert.pdfarranger.png" \
       "$ICONS/$size/apps/" 2>/dev/null || true
done
mkdir -p "$ICONS/scalable/apps"
cp "$INSTALL_DIR/data/icons/hicolor/scalable/apps/com.github.jeromerobert.pdfarranger.svg" \
   "$ICONS/scalable/apps/" 2>/dev/null || true

# Desktop entry
mkdir -p "$APPS"
cat > "$APPS/pdfarranger.desktop" <<DESKTOPEOF
[Desktop Entry]
Version=1.0
Name=PDF Arranger
Comment=Merge, split, rearrange and sign PDF pages
Type=Application
Exec=pdfarranger %U
Icon=com.github.jeromerobert.pdfarranger
MimeType=application/pdf;
Categories=Office;
Terminal=false
StartupNotify=true
Keywords=pdf;sign;merge;split;arrange;

[Desktop Action new-window]
Name=New Window
Exec=pdfarranger
DESKTOPEOF

# Refresh caches
gtk-update-icon-cache -f -t "$ICONS" 2>/dev/null || true
update-desktop-database "$APPS" 2>/dev/null || true

echo ""
echo "======================================================"
echo "  Installation complete!"
echo ""
echo "  Launch from terminal:  pdfarranger"
echo "  Find in app menu:      search 'PDF Arranger'"
echo "  Pin to panel:          right-click app in menu -> Add to Panel"
echo "  Update anytime:        cd ~/pdfarranger && git pull"
echo "  Source:                https://github.com/RincolTech-Solutions-ltd/pdfarranger"
echo "======================================================"
echo ""
