# GTK4 Port: Code Examples

Practical examples of implementing key KernTool4 components in GTK4.

---

## 1. Cairo Glyph Renderer

### Basic Glyph Renderer

```python
# src/rendering/glyph_renderer.py

import cairo
import math
from gi.repository import Pango, PangoCairo
from fontTools.pens.cairoPen import CairoPen

class CairoGlyphRenderer:
    """
    Central glyph renderer - replaces Merz
    """

    def __init__(self):
        self.scale = 0.096  # Font units to view units
        self.offset_x = 0
        self.offset_y = 0

        # Display settings
        self.show_margins = False
        self.show_metrics = False
        self.show_ray_beam = False
        self.ray_beam_position = 300

        # Colors (from original)
        self.color_glyph = (0, 0, 0, 1)
        self.color_margins = (0.5, 0.5, 0.5, 1)
        self.color_ray_beam = (1, 0, 0, 0.8)
        self.color_metrics = (0.2, 0.5, 0.2, 1)

        # Fonts for UI text
        self.display_font = "Menlo 9"
        self.pango_context = None

    def draw_scene(self, cr, width, height, glyph_lines):
        """
        Main method - called from do_snapshot()

        Args:
            cr: Cairo context
            width, height: Canvas dimensions
            glyph_lines: List of glyph line data
        """
        cr.save()

        # Setup coordinate system
        self._setup_transform(cr)

        # Draw each visible line
        visible_lines = self._get_visible_lines(glyph_lines, height)

        y_pos = 0
        for line_data in visible_lines:
            self.draw_glyph_line(cr, line_data, y_pos)
            y_pos += self._get_line_height(line_data)

        cr.restore()

    def draw_glyph_line(self, cr, line_data, y_pos):
        """
        Draw one line of glyphs

        Args:
            cr: Cairo context
            line_data: Dict with 'glyphs', 'info', 'link', etc.
            y_pos: Y position for this line
        """
        glyphs = line_data['glyphs']
        x_pos = 0

        cr.save()
        cr.translate(0, y_pos)

        for glyph in glyphs:
            self._draw_single_glyph(cr, glyph, x_pos)
            x_pos += glyph.width

        cr.restore()

    def _draw_single_glyph(self, cr, glyph, x_pos):
        """Draw one glyph with all annotations"""
        cr.save()
        cr.translate(x_pos, 0)

        font = glyph.font
        italic_angle = font.info.italicAngle or 0

        # 1. Draw glyph outline
        self.draw_glyph_outline(cr, glyph, font)

        # 2. Draw margins (if enabled)
        if self.show_margins:
            self.draw_margins(cr, glyph, italic_angle)

        # 3. Draw metrics (if enabled)
        if self.show_metrics:
            self.draw_metrics(cr, font, glyph.width)

        # 4. Draw ray beam (if enabled)
        if self.show_ray_beam:
            self.draw_ray_beam(cr, glyph, self.ray_beam_position)

        cr.restore()

    def draw_glyph_outline(self, cr, glyph, font):
        """
        Draw glyph outline via fontTools CairoPen

        This replaces: container.appendPathSublayer()
        """
        cr.save()

        # Flip coordinate system (font coords are bottom-up)
        cr.translate(0, 600)  # Baseline position
        cr.scale(1, -1)

        # Use fontTools CairoPen - direct support!
        glyph_set = font.getGlyphSet()
        pen = CairoPen(glyph_set, cr)

        # Draw glyph
        glyph.draw(pen)

        # Style
        cr.set_source_rgba(*self.color_glyph)
        cr.set_line_width(1.0 / self.scale)
        cr.stroke()

        cr.restore()

    def draw_margins(self, cr, glyph, italic_angle=0):
        """
        Display margins

        Replaces: container.appendTextLineSublayer() for margin labels
        """
        left_margin, right_margin = self._get_margins(glyph)

        cr.save()

        # Italic shift for margins
        def italic_shift(y_pos):
            if italic_angle:
                return y_pos * math.tan(-italic_angle * 0.0175)
            return 0

        # Setup Pango for text
        if not self.pango_context:
            self.pango_context = cr.create_context()

        layout = Pango.Layout(self.pango_context)
        font_desc = Pango.FontDescription(self.display_font)
        layout.set_font_description(font_desc)

        # Left margin
        left_symbol = chr(int('25C2', 16))  # ◂
        layout.set_text(f"{left_symbol}{left_margin}", -1)

        cr.move_to(-10 + italic_shift(200), 200)
        cr.set_source_rgba(*self.color_margins)
        PangoCairo.show_layout(cr, layout)

        # Right margin
        right_symbol = chr(int('25B8', 16))  # ▸
        layout.set_text(f"{right_margin}{right_symbol}", -1)

        cr.move_to(glyph.width + 10 + italic_shift(200), 200)
        PangoCairo.show_layout(cr, layout)

        cr.restore()

    def draw_ray_beam(self, cr, glyph, beam_position):
        """
        Ray beam for precise margin measurements

        Replaces: container.appendLineSublayer() for beam line
        """
        cr.save()

        # Calculate beam intersections with outline
        intersections = self._get_ray_intersections(glyph, beam_position)

        # Draw horizontal line
        cr.set_source_rgba(*self.color_ray_beam)
        cr.set_line_width(1.0)
        cr.set_dash([3.0, 3.0])

        cr.move_to(0, beam_position + 600)
        cr.line_to(glyph.width, beam_position + 600)
        cr.stroke()

        # Draw intersection markers
        for x, y in intersections:
            cr.arc(x, y + 600, 2.5, 0, 2 * math.pi)
            cr.fill()

        # Draw position label
        layout = Pango.Layout(self.pango_context)
        font_desc = Pango.FontDescription(self.display_font)
        layout.set_font_description(font_desc)
        layout.set_text(str(beam_position), -1)

        cr.move_to(0, beam_position + 600 - 15)
        PangoCairo.show_layout(cr, layout)

        cr.restore()

    def draw_metrics(self, cr, font, glyph_width):
        """
        Draw font metrics (baseline, x-height, cap-height, etc.)

        Replaces: container.appendLineSublayer() for metric lines
        """
        cr.save()

        metrics = {
            'descender': font.info.descender,
            'baseline': 0,
            'x-height': font.info.xHeight,
            'cap-height': font.info.capHeight,
            'ascender': font.info.ascender,
        }

        cr.set_source_rgba(*self.color_metrics)
        cr.set_line_width(0.5)

        for name, position in metrics.items():
            y = position + 600

            # Draw line
            cr.move_to(0, y)
            cr.line_to(glyph_width, y)
            cr.stroke()

            # Draw label
            layout = Pango.Layout(self.pango_context)
            font_desc = Pango.FontDescription("Menlo 7")
            layout.set_font_description(font_desc)
            layout.set_text(name[0], -1)  # First letter

            cr.move_to(-15, y - 5)
            PangoCairo.show_layout(cr, layout)

        cr.restore()

    def _get_margins(self, glyph):
        """Calculate margins (with ray beam support)"""
        if self.show_ray_beam:
            # Use ray margins
            left = glyph.getRayLeftMargin(self.ray_beam_position)
            right = glyph.getRayRightMargin(self.ray_beam_position)
        else:
            # Use regular margins
            font = glyph.font
            if font.info.italicAngle:
                left = glyph.angledLeftMargin
                right = glyph.angledRightMargin
            else:
                left = glyph.leftMargin
                right = glyph.rightMargin

        return (int(round(left or 0)), int(round(right or 0)))

    def _get_ray_intersections(self, glyph, beam_position):
        """
        Calculate ray beam intersections with glyph outline

        Ported from: tdSpaceControl.getIntersectGlyphWithHorizontalBeam()
        """
        from mojo.tools import IntersectGlyphWithLine

        try:
            x_min, y_min, x_max, y_max = glyph.bounds
        except:
            return []

        # Get intersections
        intersections = sorted(
            IntersectGlyphWithLine(
                glyph,
                ((x_min, beam_position), (x_max, beam_position)),
                canHaveComponent=True,
                addSideBearings=False
            )
        )

        # Return as list of (x, y) tuples
        return [(x, beam_position) for x, y in intersections]

    def _setup_transform(self, cr):
        """Setup Cairo transform for font coordinate system"""
        cr.translate(self.offset_x, self.offset_y)
        cr.scale(self.scale, self.scale)

    def _get_visible_lines(self, all_lines, viewport_height):
        """Virtualization - return only visible lines"""
        # TODO: Implement proper virtualization
        return all_lines

    def _get_line_height(self, line_data):
        """Calculate line height"""
        return 2000  # Default from original
```

---

## 2. Glyph Canvas Widget

### Custom GTK4 DrawingArea for rendering

```python
# src/views/glyphs_view.py

from gi.repository import Gtk, Gdk, Graphene
from .rendering.glyph_renderer import CairoGlyphRenderer

class GlyphsCanvas(Gtk.DrawingArea):
    """
    Canvas for rendering glyphs

    Replaces: TDGlyphsMerzView
    """

    def __init__(self, renderer=None):
        super().__init__()

        # Renderer
        self.renderer = renderer or CairoGlyphRenderer()

        # Data
        self.glyph_lines = []
        self.selected_indices = []

        # Scrolling
        self.scroll_offset_x = 0
        self.scroll_offset_y = 0

        # Setup drawing
        self.set_draw_func(self._on_draw)
        self.set_can_focus(True)

        # Event controllers
        self._setup_event_controllers()

        # Request size
        self.set_size_request(400, 400)

    def _on_draw(self, area, cr, width, height):
        """GTK4 draw callback"""
        # Clear background
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        # Apply scroll offset
        self.renderer.offset_x = self.scroll_offset_x
        self.renderer.offset_y = self.scroll_offset_y

        # Draw scene
        self.renderer.draw_scene(cr, width, height, self.glyph_lines)

    def _setup_event_controllers(self):
        """Setup GTK4 event controllers"""
        # Keyboard
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)

        # Mouse click
        click_controller = Gtk.GestureClick()
        click_controller.connect("pressed", self._on_mouse_pressed)
        self.add_controller(click_controller)

        # Scroll
        scroll_controller = Gtk.EventControllerScroll()
        scroll_controller.set_flags(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        scroll_controller.connect("scroll", self._on_scroll)
        self.add_controller(scroll_controller)

        # Drag (for pan)
        drag_controller = Gtk.GestureDrag()
        drag_controller.connect("drag-update", self._on_drag_update)
        self.add_controller(drag_controller)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle keyboard shortcuts"""
        # Example: zoom with +/-
        if keyval == Gdk.KEY_plus:
            self.zoom_in()
            return True
        elif keyval == Gdk.KEY_minus:
            self.zoom_out()
            return True

        return False

    def _on_mouse_pressed(self, gesture, n_press, x, y):
        """Handle mouse click"""
        # Convert to glyph coordinates
        glyph_x = (x - self.scroll_offset_x) / self.renderer.scale
        glyph_y = (y - self.scroll_offset_y) / self.renderer.scale

        # Find clicked glyph
        # TODO: Implement hit testing

    def _on_scroll(self, controller, dx, dy):
        """Handle scroll for panning"""
        self.scroll_offset_y += dy * 10
        self.queue_draw()
        return True

    def _on_drag_update(self, gesture, offset_x, offset_y):
        """Handle drag for panning"""
        self.scroll_offset_x += offset_x
        self.scroll_offset_y += offset_y
        self.queue_draw()

    def set_glyph_lines(self, lines):
        """Update glyph lines data"""
        self.glyph_lines = lines
        self.queue_draw()

    def zoom_in(self):
        """Zoom in"""
        self.renderer.scale *= 1.2
        self.queue_draw()

    def zoom_out(self):
        """Zoom out"""
        self.renderer.scale /= 1.2
        self.queue_draw()

    def toggle_margins(self):
        """Toggle margins display"""
        self.renderer.show_margins = not self.renderer.show_margins
        self.queue_draw()

    def toggle_ray_beam(self):
        """Toggle ray beam"""
        self.renderer.show_ray_beam = not self.renderer.show_ray_beam
        self.queue_draw()
```

---

## 3. Virtual Scrolling with ListView

### Alternative approach - GTK4 ListView

```python
# src/views/glyphs_listview.py

from gi.repository import Gtk, Gio, GObject

class GlyphLineModel(GObject.Object):
    """Model for one line of glyphs"""

    def __init__(self, glyphs, info, link):
        super().__init__()
        self.glyphs = glyphs
        self.info = info
        self.link = link


class GlyphsListView(Gtk.ScrolledWindow):
    """
    Virtualized glyph list via GTK4 ListView

    Automatic virtual scrolling!
    """

    def __init__(self):
        super().__init__()

        # Data store
        self.store = Gio.ListStore.new(GlyphLineModel)

        # Selection model
        self.selection = Gtk.NoSelection.new(self.store)

        # Create ListView
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_setup)
        factory.connect("bind", self._on_bind)

        self.list_view = Gtk.ListView.new(self.selection, factory)
        self.list_view.set_show_separators(False)

        self.set_child(self.list_view)

        # Renderer
        self.renderer = CairoGlyphRenderer()

    def _on_setup(self, factory, list_item):
        """Setup - create widget for item"""
        # Create drawing area for this item
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(-1, 200)
        drawing_area.set_draw_func(self._draw_line)

        list_item.set_child(drawing_area)

    def _on_bind(self, factory, list_item):
        """Bind - attach data to widget"""
        # Get data model
        model = list_item.get_item()

        # Get drawing area
        drawing_area = list_item.get_child()

        # Store model in drawing area
        drawing_area.glyph_line_model = model

        # Trigger redraw
        drawing_area.queue_draw()

    def _draw_line(self, area, cr, width, height):
        """Draw one glyph line"""
        if not hasattr(area, 'glyph_line_model'):
            return

        model = area.glyph_line_model

        # Clear background
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        # Draw this line
        line_data = {
            'glyphs': model.glyphs,
            'info': model.info,
            'link': model.link,
        }

        self.renderer.draw_glyph_line(cr, line_data, 0)

    def set_glyph_lines(self, lines):
        """Update data - only call this!"""
        self.store.remove_all()

        for line_data in lines:
            model = GlyphLineModel(
                glyphs=line_data['glyphs'],
                info=line_data.get('info', ''),
                link=line_data.get('link', None)
            )
            self.store.append(model)
```

---

## 4. Keyboard Controller

### Hotkey management

```python
# src/controllers/keyboard.py

from gi.repository import Gtk, Gdk

class KeyboardController:
    """
    Hotkey management

    Replaces: tdKeyCommander
    """

    def __init__(self, widget):
        self.widget = widget
        self.handlers = {}

        # Setup event controller
        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect("key-pressed", self._on_key_pressed)
        widget.add_controller(self.key_controller)

    def register(self, keyval, modifiers, callback, value=None):
        """
        Register hotkey

        Args:
            keyval: Gdk.KEY_* constant
            modifiers: Tuple of (shift, ctrl, alt, cmd)
            callback: Function to call
            value: Optional value to pass to callback
        """
        key = (keyval, modifiers)
        self.handlers[key] = (callback, value)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press"""
        # Extract modifiers
        shift = bool(state & Gdk.ModifierType.SHIFT_MASK)
        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
        alt = bool(state & Gdk.ModifierType.ALT_MASK)
        cmd = bool(state & Gdk.ModifierType.META_MASK)

        modifiers = (shift, ctrl, alt, cmd)
        key = (keyval, modifiers)

        # Find handler
        if key in self.handlers:
            callback, value = self.handlers[key]

            if value is not None:
                callback(self.widget, value)
            else:
                callback(self.widget)

            return True  # Event handled

        return False


# Usage example:
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        # Create glyphs view
        self.glyphs_view = GlyphsCanvas()

        # Setup keyboard
        self.keyboard = KeyboardController(self.glyphs_view)

        # Register shortcuts (from original):

        # TAB - next pair
        self.keyboard.register(
            Gdk.KEY_Tab,
            (False, False, False, False),
            self.select_next_pair
        )

        # Alt+TAB - previous pair
        self.keyboard.register(
            Gdk.KEY_Tab,
            (False, False, True, False),
            self.select_previous_pair
        )

        # LEFT - decrease kerning by 10
        self.keyboard.register(
            Gdk.KEY_Left,
            (False, False, False, False),
            self.adjust_kerning,
            value=-10
        )

        # Shift+LEFT - decrease by 5
        self.keyboard.register(
            Gdk.KEY_Left,
            (True, False, False, False),
            self.adjust_kerning,
            value=-5
        )

        # B - toggle ray beam
        self.keyboard.register(
            Gdk.KEY_b,
            (False, False, False, False),
            self.toggle_ray_beam
        )

        # +/- for zoom
        self.keyboard.register(
            Gdk.KEY_plus,
            (False, False, False, False),
            lambda w: w.zoom_in()
        )

        self.keyboard.register(
            Gdk.KEY_minus,
            (False, False, False, False),
            lambda w: w.zoom_out()
        )

    def select_next_pair(self, widget):
        """Select next glyph pair"""
        # Implementation...
        pass

    def adjust_kerning(self, widget, value):
        """Adjust kerning by value"""
        # Implementation...
        pass
```

---

## 5. Glyph Cache for Performance

### LRU cache for rendered glyphs

```python
# src/rendering/cache.py

import cairo
from collections import OrderedDict
from contextlib import contextmanager

class GlyphCache:
    """
    LRU cache for rendered glyphs

    Store glyphs as ImageSurface for fast blitting
    """

    def __init__(self, max_size=1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get_key(self, glyph, scale, show_margins=False):
        """Generate cache key"""
        return (
            glyph.name,
            id(glyph.font),
            round(scale, 3),
            show_margins
        )

    def get(self, glyph, scale, show_margins=False):
        """Get cached surface or None"""
        key = self.get_key(glyph, scale, show_margins)

        if key in self.cache:
            # Move to end (most recent)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def put(self, glyph, scale, surface, show_margins=False):
        """Store surface in cache"""
        key = self.get_key(glyph, scale, show_margins)

        # Add to cache
        self.cache[key] = surface

        # Evict if needed (LRU)
        if len(self.cache) > self.max_size:
            # Remove oldest (first) item
            self.cache.popitem(last=False)

    def clear(self):
        """Clear all cache"""
        # Finish all surfaces
        for surface in self.cache.values():
            surface.finish()

        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


# Usage with renderer:
class CachedGlyphRenderer(CairoGlyphRenderer):
    """Renderer with caching"""

    def __init__(self):
        super().__init__()
        self.cache = GlyphCache(max_size=1000)

    def draw_glyph_outline(self, cr, glyph, font):
        """Draw with caching"""
        # Try cache first
        cached = self.cache.get(glyph, self.scale, self.show_margins)

        if cached:
            # Use cached surface
            cr.set_source_surface(cached, 0, 0)
            cr.paint()
            return

        # Not in cache - render to ImageSurface
        with self._create_glyph_surface(glyph) as surface:
            # Render glyph to surface
            ctx = cairo.Context(surface)
            super().draw_glyph_outline(ctx, glyph, font)

            # Store in cache
            self.cache.put(glyph, self.scale, surface, self.show_margins)

            # Draw to main context
            cr.set_source_surface(surface, 0, 0)
            cr.paint()

    @contextmanager
    def _create_glyph_surface(self, glyph):
        """Create temporary surface for rendering"""
        # Calculate size
        width = int(glyph.width * self.scale) + 100
        height = int(2000 * self.scale)

        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            width,
            height
        )

        try:
            yield surface
        finally:
            pass  # Don't finish here - cache owns it
```

---

## 6. Application Structure

### Main application

```python
# src/application.py

from gi.repository import Gtk, Adw, Gio
import sys

class KernToolApplication(Adw.Application):
    """
    Main GTK application

    Replaces: TDKernMultiTool
    """

    def __init__(self):
        super().__init__(
            application_id="com.typedev.KernTool",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.window = None
        self.fonts = []

    def do_activate(self):
        """Called when app is activated"""
        if not self.window:
            self.window = MainWindow(application=self)

        self.window.present()

    def do_startup(self):
        """Called once at startup"""
        Adw.Application.do_startup(self)

        # Setup actions
        self._create_actions()

        # Load settings
        self._load_settings()

    def _create_actions(self):
        """Create application actions"""
        # File actions
        action = Gio.SimpleAction.new("open", None)
        action.connect("activate", self._on_open)
        self.add_action(action)

        action = Gio.SimpleAction.new("save", None)
        action.connect("activate", self._on_save)
        self.add_action(action)

        # View actions
        action = Gio.SimpleAction.new("toggle-margins", None)
        action.connect("activate", self._on_toggle_margins)
        self.add_action(action)

        # Quit
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", lambda *_: self.quit())
        self.add_action(action)
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])

    def _on_open(self, action, param):
        """Open font dialog"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Open Font")

        # Filter for UFO files
        filter_ufo = Gtk.FileFilter()
        filter_ufo.set_name("UFO Fonts")
        filter_ufo.add_pattern("*.ufo")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_ufo)
        dialog.set_filters(filters)

        # Open async
        dialog.open(self.window, None, self._on_file_opened)

    def _on_file_opened(self, dialog, result):
        """Callback when file is opened"""
        try:
            file = dialog.open_finish(result)
            path = file.get_path()

            # Load font
            self._load_font(path)

        except Exception as e:
            print(f"Error opening file: {e}")

    def _load_font(self, path):
        """Load font from path"""
        import defcon

        # Load in background thread
        def worker():
            font = defcon.Font(path)
            return font

        def callback(font):
            self.fonts.append(font)
            self.window.add_font(font)

        # Use GLib.idle_add for thread safety
        import threading

        def run():
            font = worker()
            from gi.repository import GLib
            GLib.idle_add(callback, font)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()


class MainWindow(Adw.ApplicationWindow):
    """Main window"""

    def __init__(self, application):
        super().__init__(application=application)

        self.set_title("KernTool 4 GTK")
        self.set_default_size(1000, 800)

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build UI"""
        # Header bar
        header = Adw.HeaderBar()

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        header.pack_end(menu_button)

        self.set_titlebar(header)

        # Main content
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)

        # Top: glyphs view
        self.glyphs_view = GlyphsCanvas()
        paned.set_start_child(self.glyphs_view)

        # Bottom: groups view
        self.groups_view = GlyphsCanvas()
        paned.set_end_child(self.groups_view)

        self.set_content(paned)


def main():
    """Entry point"""
    app = KernToolApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
```

---

## Next Steps

1. **Create project:**
   ```bash
   mkdir kerntool-gtk4
   cd kerntool-gtk4
   meson init
   ```

2. **Setup dependencies:**
   ```toml
   # pyproject.toml
   [dependencies]
   pygobject = "^3.46"
   fonttools = "^4.40"
   fontparts = "^0.12"
   defcon = "^0.10"
   ufolib2 = "^0.16"
   ```

3. **Run prototype:**
   ```python
   python src/main.py
   ```

See also:
- [GTK4_ANALYSIS.md](./GTK4_ANALYSIS.md) - Complete analysis
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture
