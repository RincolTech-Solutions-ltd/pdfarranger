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
echo "[1/4] Installing system dependencies for: $DISTRO"

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
        echo ""
        echo "WARNING: Distro '$DISTRO' not recognised."
        echo "Attempting to continue — install GTK3 + python3-gi manually if this fails."
        echo ""
        ;;
esac

echo ""

# ── Clone or update repo ───────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "[2/4] Updating existing installation at $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "[2/4] Cloning repository to $INSTALL_DIR"
    git clone "$REPO" "$INSTALL_DIR"
fi

echo ""

# ── Install Python package ─────────────────────────────────────────────────────
echo "[3/4] Installing Python package"
cd "$INSTALL_DIR"

# Try editable install; fall back if pip complains about system-managed env
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

# ── Create launcher ────────────────────────────────────────────────────────────
echo "[4/4] Creating launcher at $LAUNCHER"

if [ "$VENV_INSTALL" = true ]; then
    LAUNCH_CMD="\"$INSTALL_DIR/venv/bin/python3\" -m pdfarranger \"\$@\""
else
    LAUNCH_CMD="python3 -m pdfarranger \"\$@\""
fi

sudo tee "$LAUNCHER" > /dev/null <<LAUNCHEOF
#!/bin/bash
cd "$INSTALL_DIR" && $LAUNCH_CMD
LAUNCHEOF

sudo chmod +x "$LAUNCHER"

echo ""
echo "======================================================"
echo "  Installation complete!"
echo ""
echo "  Run the app:     pdfarranger"
echo "  Update anytime:  cd $INSTALL_DIR && git pull"
echo "  Source:          https://github.com/RincolTech-Solutions-ltd/pdfarranger"
echo "======================================================"
echo ""
