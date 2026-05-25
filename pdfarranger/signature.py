"""
signature.py — Signature dialog for pdfarranger.
Tabs: Type (font grid + colour palette) | Draw | Upload Image
"""

import io
import subprocess
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango

from PIL import Image, ImageDraw, ImageFont
from pdfarranger.image_utils import (
    remove_bg as _remove_bg,
    boost_contrast as _boost_contrast,
    autocrop_alpha as _autocrop_alpha,
    rgba_pil_to_pdf,
)

# ── Persistence ───────────────────────────────────────────────────────────────
_CONFIG_DIR = Path.home() / ".config" / "pdfarranger"
_SAVED_SIG   = _CONFIG_DIR / "signature.png"

# ── Ink colours: (r,g,b 0-1, hex string) ─────────────────────────────────────
COLORS = [
    ((0.40, 0.55, 1.00), "#6699FF"),
    ((0.20, 0.40, 0.85), "#3366D9"),
    ((0.10, 0.25, 0.70), "#1940B2"),
    ((0.05, 0.15, 0.55), "#0D268C"),
    ((0.27, 0.27, 0.27), "#454545"),
    ((0.50, 0.50, 0.50), "#808080"),
    ((0.00, 0.00, 0.00), "#000000"),
]

# ── Font specs: (fc-pattern, pango-description, display-label) ────────────────
FONTS = [
    ("URW Chancery L:style=Italic",        "URW Chancery L Italic 28",       ),
    ("URW Chancery L:style=Bold Italic",   "URW Chancery L Bold Italic 26",  ),
    ("Noto Serif:style=Italic",            "Noto Serif Italic 22",           ),
    ("Noto Serif:style=Bold Italic",       "Noto Serif Bold Italic 22",      ),
    ("DejaVu Serif:style=Italic",          "DejaVu Serif Italic 20",         ),
    ("DejaVu Serif:style=Bold Italic",     "DejaVu Serif Bold Italic 20",    ),
    ("Liberation Serif:style=Italic",      "Liberation Serif Italic 22",     ),
    ("FreeSerif:style=Italic",             "FreeSerif Italic 22",            ),
    ("Bitstream Charter:style=Italic",     "Bitstream Charter Italic 20",    ),
    ("FreeMono:style=Italic",              "FreeMono Italic 18",             ),
    ("DejaVu Sans:style=Oblique",          "DejaVu Sans Oblique 20",         ),
]

# ── Position grid: (off_x, off_y) for paste_as_layer ─────────────────────────
POSITIONS = [
    (0.0, 0.0), (0.5, 0.0), (1.0, 0.0),
    (0.0, 0.5), (0.5, 0.5), (1.0, 0.5),
    (0.0, 1.0), (0.5, 1.0), (1.0, 1.0),
]
_DEFAULT_POS = 8   # bottom-right


class SignatureDialog(Gtk.Dialog):

    def __init__(self, parent):
        super().__init__(
            title="Insert Signature",
            transient_for=parent,
            modal=True,
            use_header_bar=1,
        )
        self.set_default_size(720, 540)
        self.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        ok = self.add_button("_Insert", Gtk.ResponseType.OK)
        ok.get_style_context().add_class("suggested-action")

        # internal state
        self._color_idx        = 6          # black by default
        self._font_idx         = 0
        self._upload_variants  = [None, None, None]
        self._selected_variant = 1          # Transparent A
        self._draw_strokes     = []
        self._draw_current     = None
        self._pos_idx          = _DEFAULT_POS

        self._build_ui()
        self._load_saved()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        content = self.get_content_area()
        content.set_spacing(0)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.pack_start(root, True, True, 0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_margin_start(12)
        self.notebook.set_margin_end(12)
        self.notebook.set_margin_top(12)
        self.notebook.set_margin_bottom(8)
        root.pack_start(self.notebook, True, True, 0)

        self.notebook.append_page(self._build_type_tab(),   Gtk.Label(label="⌨  Type"))
        self.notebook.append_page(self._build_draw_tab(),   Gtk.Label(label="✍  Draw"))
        self.notebook.append_page(self._build_upload_tab(), Gtk.Label(label="📄  Upload Image"))

        root.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        bar.set_margin_start(16)
        bar.set_margin_end(16)
        bar.set_margin_top(8)
        bar.set_margin_bottom(8)
        root.pack_start(bar, False, False, 0)

        hint = Gtk.Label(label="Position set interactively after clicking Insert")
        hint.set_sensitive(False)
        bar.pack_start(hint, False, False, 0)

        self.save_check = Gtk.CheckButton(label="Save signature")
        self.save_check.set_active(True)
        bar.pack_end(self.save_check, False, False, 0)

        content.show_all()

    # ── Type tab ──────────────────────────────────────────────────────────────
    def _build_type_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(14)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_bottom(8)

        # Name entry
        self.type_entry = Gtk.Entry()
        self.type_entry.set_placeholder_text("Your full name")
        self.type_entry.connect("changed", self._on_type_changed)
        vbox.pack_start(self.type_entry, False, False, 0)

        # Colour palette
        palette_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        palette_row.set_halign(Gtk.Align.CENTER)
        self._color_btns = []
        first = None
        for i, ((r, g, b), _) in enumerate(COLORS):
            btn = Gtk.RadioButton.new_from_widget(first)
            if first is None:
                first = btn
            btn.set_mode(False)
            btn.set_relief(Gtk.ReliefStyle.NONE)
            da = Gtk.DrawingArea()
            da.set_size_request(26, 26)
            da.connect("draw", self._draw_circle, r, g, b)
            btn.add(da)
            btn.set_active(i == self._color_idx)
            btn.connect("toggled", self._on_color_toggled, i)
            palette_row.pack_start(btn, False, False, 0)
            self._color_btns.append(btn)
        vbox.pack_start(palette_row, False, False, 0)

        # Font grid label
        style_lbl = Gtk.Label(label="Choose a style:")
        style_lbl.set_halign(Gtk.Align.START)
        vbox.pack_start(style_lbl, False, False, 0)

        # Scrollable FlowBox
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(230)
        scroll.set_vexpand(True)

        self.font_flow = Gtk.FlowBox()
        self.font_flow.set_max_children_per_line(3)
        self.font_flow.set_min_children_per_line(3)
        self.font_flow.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.font_flow.set_homogeneous(True)
        self.font_flow.set_row_spacing(4)
        self.font_flow.set_column_spacing(4)
        self.font_flow.connect("child-activated", self._on_font_activated)

        self._font_labels = []
        for i, (_, pango_desc) in enumerate(FONTS):
            child = Gtk.FlowBoxChild()
            child.set_size_request(218, 64)
            lbl = Gtk.Label()
            lbl.set_ellipsize(Pango.EllipsizeMode.END)
            lbl.set_xalign(0.5)
            lbl.set_yalign(0.5)
            self._font_labels.append((lbl, pango_desc))
            child.add(lbl)
            self.font_flow.add(child)

        self._refresh_font_labels()
        scroll.add(self.font_flow)
        vbox.pack_start(scroll, True, True, 0)

        # Select first child
        GLib.idle_add(lambda: self.font_flow.select_child(
            self.font_flow.get_child_at_index(0)) or False)

        return vbox

    def _draw_circle(self, widget, cr, r, g, b):
        alloc = widget.get_allocation()
        cx, cy, rad = alloc.width / 2, alloc.height / 2, min(alloc.width, alloc.height) / 2 - 1
        cr.set_source_rgb(r, g, b)
        cr.arc(cx, cy, rad, 0, 6.28318)
        cr.fill()

    def _on_color_toggled(self, btn, idx):
        if btn.get_active():
            self._color_idx = idx
            self._refresh_font_labels()
            self.draw_area.queue_draw()

    def _on_type_changed(self, _entry):
        self._refresh_font_labels()

    def _refresh_font_labels(self):
        text = self.type_entry.get_text().strip() if hasattr(self, "type_entry") else ""
        display = text or "Your Signature"
        _, hexcol = COLORS[self._color_idx]
        for lbl, pango_desc in self._font_labels:
            # Build Pango markup: font from pango_desc, colour from palette
            lbl.set_markup(f'<span font="{pango_desc}" color="{hexcol}">{display}</span>')

    def _on_font_activated(self, _fb, child):
        self._font_idx = child.get_index()

    def _get_type_image(self):
        """Render typed text in selected font+colour → PIL RGBA Image."""
        text = self.type_entry.get_text().strip()
        if not text:
            return None
        fc_pattern, pango_desc = FONTS[self._font_idx]
        (r_f, g_f, b_f), _ = COLORS[self._color_idx]
        ink = (int(r_f * 255), int(g_f * 255), int(b_f * 255), 255)

        # Resolve font file via fc-match
        try:
            font_path = subprocess.run(
                ["fc-match", "--format=%{file}", fc_pattern],
                capture_output=True, text=True, timeout=3
            ).stdout.strip()
            font = ImageFont.truetype(font_path, 60)
        except Exception:
            font = ImageFont.load_default()

        # Measure and render
        tmp = Image.new("RGBA", (1, 1))
        bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font)
        pad = 20
        w = bbox[2] - bbox[0] + pad * 2
        h = bbox[3] - bbox[1] + pad * 2
        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        ImageDraw.Draw(img).text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=ink)
        return img

    # ── Draw tab ──────────────────────────────────────────────────────────────
    def _build_draw_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_top(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_bottom(8)

        vbox.pack_start(Gtk.Label(label="Draw your signature below:"), False, False, 0)

        frame = Gtk.Frame()
        self.draw_area = Gtk.DrawingArea()
        self.draw_area.set_size_request(660, 210)
        self.draw_area.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.draw_area.connect("draw",                 self._on_canvas_draw)
        self.draw_area.connect("button-press-event",   self._on_canvas_press)
        self.draw_area.connect("button-release-event", self._on_canvas_release)
        self.draw_area.connect("motion-notify-event",  self._on_canvas_motion)
        frame.add(self.draw_area)
        vbox.pack_start(frame, True, True, 0)

        clear = Gtk.Button(label="Clear")
        clear.set_halign(Gtk.Align.END)
        clear.connect("clicked", lambda _: self._canvas_clear())
        vbox.pack_start(clear, False, False, 0)
        return vbox

    def _on_canvas_draw(self, widget, cr):
        alloc = widget.get_allocation()
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, alloc.width, alloc.height)
        cr.fill()
        r, g, b = COLORS[self._color_idx][0]
        cr.set_source_rgb(r, g, b)
        cr.set_line_width(2.5)
        cr.set_line_cap(1)   # ROUND
        cr.set_line_join(1)  # ROUND
        for stroke in self._draw_strokes:
            if len(stroke) < 2:
                continue
            cr.move_to(*stroke[0])
            for pt in stroke[1:]:
                cr.line_to(*pt)
            cr.stroke()
        if self._draw_current and len(self._draw_current) >= 2:
            cr.move_to(*self._draw_current[0])
            for pt in self._draw_current[1:]:
                cr.line_to(*pt)
            cr.stroke()

    def _on_canvas_press(self, _w, event):
        if event.button == 1:
            self._draw_current = [(event.x, event.y)]

    def _on_canvas_motion(self, widget, event):
        if self._draw_current is not None:
            self._draw_current.append((event.x, event.y))
            widget.queue_draw()

    def _on_canvas_release(self, _w, _event):
        if self._draw_current:
            self._draw_strokes.append(self._draw_current)
            self._draw_current = None
            self.draw_area.queue_draw()

    def _canvas_clear(self):
        self._draw_strokes = []
        self._draw_current = None
        self.draw_area.queue_draw()

    def _get_draw_image(self):
        if not self._draw_strokes:
            return None
        alloc = self.draw_area.get_allocation()
        w, h = alloc.width, alloc.height
        img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        r_f, g_f, b_f = COLORS[self._color_idx][0]
        ink = (int(r_f * 255), int(g_f * 255), int(b_f * 255), 255)
        for stroke in self._draw_strokes:
            for i in range(len(stroke) - 1):
                x0, y0 = int(stroke[i][0]),   int(stroke[i][1])
                x1, y1 = int(stroke[i+1][0]), int(stroke[i+1][1])
                draw.line([(x0, y0), (x1, y1)], fill=ink, width=3)
        return img

    # ── Upload tab ────────────────────────────────────────────────────────────
    def _build_upload_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(16)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_bottom(8)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.pack_start(Gtk.Label(label="Select image:"), False, False, 0)
        self.file_chooser = Gtk.FileChooserButton(
            title="Select Signature Image",
            action=Gtk.FileChooserAction.OPEN
        )
        filt = Gtk.FileFilter()
        filt.set_name("Images (PNG, JPEG)")
        filt.add_mime_type("image/png")
        filt.add_mime_type("image/jpeg")
        self.file_chooser.add_filter(filt)
        self.file_chooser.connect("file-set", self._on_file_set)
        row.pack_start(self.file_chooser, True, True, 0)
        vbox.pack_start(row, False, False, 0)

        choose_lbl = Gtk.Label(label="Choose an image version:")
        choose_lbl.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(choose_lbl, False, False, 0)

        # CSS: blue border on selected variant frame
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .variant-frame { border: 3px solid transparent; border-radius: 8px; padding: 2px; }
            .variant-frame.selected { border: 3px solid #1A73E8; border-radius: 8px; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        thumbs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        thumbs.set_halign(Gtk.Align.CENTER)
        thumbs.set_vexpand(True)

        self._var_btns   = []
        self._var_imgs   = []
        self._var_frames = []
        self._var_labels = []
        first = None
        for i, caption in enumerate(["Original", "Transparent A", "Transparent B"]):
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

            btn = Gtk.RadioButton.new_from_widget(first)
            if first is None:
                first = btn
            btn.set_mode(False)
            btn.set_relief(Gtk.ReliefStyle.NONE)
            img_w = Gtk.Image()
            img_w.set_size_request(190, 130)
            btn.add(img_w)
            btn.connect("toggled", self._on_variant_toggled, i)

            # Wrap button in a frame that gets a blue border when selected
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.NONE)
            frame.get_style_context().add_class("variant-frame")
            frame.add(btn)

            lbl_cap = Gtk.Label()
            lbl_cap.set_markup(caption)

            col.pack_start(frame, False, False, 0)
            col.pack_start(lbl_cap, False, False, 0)
            thumbs.pack_start(col, False, False, 0)

            self._var_btns.append(btn)
            self._var_imgs.append(img_w)
            self._var_frames.append(frame)
            self._var_labels.append((lbl_cap, caption))

        self._var_btns[self._selected_variant].set_active(True)
        self._refresh_variant_selection()
        vbox.pack_start(thumbs, True, True, 0)
        return vbox

    def _refresh_variant_selection(self):
        for i, (frame, (lbl, caption)) in enumerate(
                zip(self._var_frames, self._var_labels)):
            if i == self._selected_variant:
                frame.get_style_context().add_class("selected")
                lbl.set_markup(
                    f'<b><span foreground="#1A73E8">✓  {caption}</span></b>')
            else:
                frame.get_style_context().remove_class("selected")
                lbl.set_markup(caption)

    def _on_variant_toggled(self, btn, idx):
        if btn.get_active():
            self._selected_variant = idx
            self._refresh_variant_selection()

    def _on_file_set(self, chooser):
        path = chooser.get_filename()
        if not path:
            return
        try:
            orig = Image.open(path).convert("RGBA")
        except Exception:
            return
        trans_a = _autocrop_alpha(_remove_bg(orig, threshold=200))
        trans_b = _autocrop_alpha(_remove_bg(_boost_contrast(orig), threshold=160))
        self._upload_variants = [orig, trans_a, trans_b]
        for i, img in enumerate(self._upload_variants):
            self._var_imgs[i].set_from_pixbuf(_pil_to_pixbuf(img, 190, 130))
        self._var_btns[1].set_active(True)
        self._selected_variant = 1
        self._refresh_variant_selection()

    def _get_upload_image(self):
        return self._upload_variants[self._selected_variant]

    # ── Saved signature ───────────────────────────────────────────────────────
    def _load_saved(self):
        if _SAVED_SIG.exists():
            try:
                img = Image.open(_SAVED_SIG).convert("RGBA")
                self._upload_variants[1] = img
                self._var_imgs[1].set_from_pixbuf(_pil_to_pixbuf(img, 190, 130))
                self._var_btns[1].set_active(True)
                self.notebook.set_current_page(2)
            except Exception:
                pass

    def _save_signature(self, img):
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        img.save(_SAVED_SIG)

    # ── Public result ─────────────────────────────────────────────────────────
    def get_result(self):
        """Return (PIL_RGBA_Image, None) — position chosen interactively after."""
        tab = self.notebook.get_current_page()
        img = None
        if tab == 0:
            img = self._get_type_image()
        elif tab == 1:
            img = self._get_draw_image()
        elif tab == 2:
            img = self._get_upload_image()

        if img is not None and self.save_check.get_active():
            self._save_signature(img.convert("RGBA"))

        return img, None


# ── GTK-specific image helper ─────────────────────────────────────────────────

def _pil_to_pixbuf(img: Image.Image, max_w: int, max_h: int) -> GdkPixbuf.Pixbuf:
    from gi.repository import GdkPixbuf as GPB
    img = img.convert("RGBA")
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    w, h = img.size
    return GPB.Pixbuf.new_from_bytes(
        GLib.Bytes.new(img.tobytes()),
        GPB.Colorspace.RGB, True, 8, w, h, w * 4
    )


# rgba_pil_to_pdf is imported from pdfarranger.image_utils above.
