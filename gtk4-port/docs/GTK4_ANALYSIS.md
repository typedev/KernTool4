# KernTool4 → GTK4 Port: Глубокий анализ

**Дата:** 2025-11-20
**Версия:** 1.0
**Статус:** Proposal

---

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Анализ текущей кодовой базы](#анализ-текущей-кодовой-базы)
3. [Технический стек GTK4](#технический-стек-gtk4)
4. [Архитектура портирования](#архитектура-портирования)
5. [Компоненты и их сложность](#компоненты-и-их-сложность)
6. [Преимущества и недостатки](#преимущества-и-недостатки)
7. [Подводные камни](#подводные-камни)
8. [Детальный план разработки](#детальный-план-разработки)
9. [Оценка ресурсов](#оценка-ресурсов)

---

## Обзор проекта

### Текущее состояние

**KernTool4** - это расширение для RoboFont (macOS) для работы с кернингом шрифтов.

**Ключевые характеристики:**
- ~14,143 строк Python кода
- 20 модулей
- 25+ классов
- Зрелый production-ready проект

### Цель портирования

Создать **standalone desktop приложение** для Linux на базе GTK4 с сохранением всей функциональности.

---

## Анализ текущей кодовой базы

### Статистика зависимостей

| Компонент | Файлов | Использование | Критичность |
|-----------|--------|---------------|-------------|
| **Vanilla** | 15 | UI Framework | ⚠️ КРИТИЧНО |
| **Merz** | 6 | Canvas Rendering | ⚠️ КРИТИЧНО |
| **AppKit** | 4 | macOS Integration | ⚠️ СРЕДНЕ |
| **Mojo** | 10 | RoboFont API | ⚠️ КРИТИЧНО |
| **FontParts** | 10 | Font Handling | ✅ ПОРТИРУЕМО |

### Ключевые метрики

```python
# Rendering complexity
Merz drawing calls: 59
  - appendLineSublayer: 28
  - appendSymbolSublayer: 15
  - appendTextLineSublayer: 12
  - appendRectangleSublayer: 4

# Animation usage
Files with animations: 2
  - tdGlyphsMerzView.py
  - tdMerzMatrix.py

# UI complexity
Window widgets: 1 main + multiple dialogs
Custom views: 2 (glyphs + groups)
Toolbar items: 13
Keyboard shortcuts: 30+
```

### Портируемость компонентов

**✅ ЛЕГКО (30% кода):**
- Бизнес-логика кернинга
- Алгоритмы расчета пар, групп, margins
- Обработка UFO файлов
- Проверка языковой совместимости

**⚠️ СРЕДНЕ (20% кода):**
- Event handling
- Keyboard shortcuts
- Простые диалоги
- File I/O

**🔴 СЛОЖНО (50% кода):**
- Canvas rendering (Merz → Cairo)
- Виртуальный scrolling
- Анимации
- Drag & Drop
- Главное окно с toolbar

---

## Технический стек GTK4

### Core Technologies

```yaml
Platform: Linux (primary), с возможностью BSD
Language: Python 3.10+

UI Framework:
  - GTK4 (4.12+)
  - libadwaita (1.4+)
  - PyGObject (3.46+)

Rendering:
  - Cairo (vector graphics)
  - Pango (text rendering)
  - fontTools.pens.cairoPen (glyph rendering)

Font Handling:
  - fontParts (UFO manipulation)
  - fontTools (font parsing)
  - ufoLib2 (UFO I/O)
  - defcon (UFO data model)

Build System:
  - Meson + Ninja
  - Flatpak (packaging)
  - AppStream (metadata)
```

### Почему GTK4?

**Преимущества над GTK3:**
1. **Современный API** - cleaner, более pythonic
2. **GPU acceleration** - через GskRenderer
3. **Better animations** - Adwaita animation API
4. **ListView/GridView** - эффективная виртуализация
5. **Wayland native** - лучше для современного Linux

**Преимущества над Qt:**
1. **Python-friendly** - лучшие биндинги
2. **Меньший footprint** - ~30MB vs ~100MB
3. **GNOME ecosystem** - стандарт для Linux desktop
4. **License** - LGPL vs commercial Qt

---

## Архитектура портирования

### Высокоуровневая архитектура

```
┌──────────────────────────────────────────────┐
│         GTK4 Application Layer               │
│  ┌────────────────────────────────────────┐  │
│  │  KernToolApp (Gtk.Application)         │  │
│  │  ├─ MainWindow (Adw.ApplicationWindow) │  │
│  │  ├─ PreferencesWindow                  │  │
│  │  └─ DialogManager                      │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│           View Layer (GTK4 Widgets)          │
│  ┌────────────────────────────────────────┐  │
│  │  GlyphsViewport (Gtk.ScrolledWindow)   │  │
│  │    └─ GlyphsCanvas (Gtk.DrawingArea)   │  │
│  │  GroupsViewport (Gtk.ScrolledWindow)   │  │
│  │    └─ GroupsCanvas (Gtk.DrawingArea)   │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│        Rendering Layer (Cairo)               │
│  ┌────────────────────────────────────────┐  │
│  │  CairoGlyphRenderer                    │  │
│  │  ├─ draw_glyph_outline()               │  │
│  │  ├─ draw_margins()                     │  │
│  │  ├─ draw_ray_beam()                    │  │
│  │  ├─ draw_metrics()                     │  │
│  │  └─ draw_annotations()                 │  │
│  │                                         │  │
│  │  GlyphCache (LRU caching)              │  │
│  │  AnimationController (optional)         │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│        Business Logic Layer                  │
│  ┌────────────────────────────────────────┐  │
│  │  KerningEngine (портировано)           │  │
│  │  ├─ FontManager                        │  │
│  │  ├─ GroupsManager                      │  │
│  │  ├─ PairsBuilder                       │  │
│  │  ├─ LanguageChecker                    │  │
│  │  └─ HistoryController                  │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│          Font Data Layer                     │
│  ┌────────────────────────────────────────┐  │
│  │  fontParts / fontTools / defcon        │  │
│  │  ├─ UFO reading/writing                │  │
│  │  ├─ Glyph data access                  │  │
│  │  └─ Kerning manipulation               │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Модульная структура

```
kerntool-gtk4/
├── src/
│   ├── main.py                 # Application entry point
│   ├── application.py          # Gtk.Application
│   ├── window.py               # Main window
│   │
│   ├── views/                  # GTK4 UI components
│   │   ├── glyphs_view.py      # Main glyphs viewport
│   │   ├── groups_view.py      # Groups viewport
│   │   ├── toolbar.py          # Toolbar implementation
│   │   └── dialogs/
│   │       ├── font_selector.py
│   │       ├── pairs_builder.py
│   │       └── preferences.py
│   │
│   ├── rendering/              # Cairo rendering
│   │   ├── glyph_renderer.py   # Main renderer
│   │   ├── cache.py            # Glyph cache
│   │   ├── layers.py           # Layer system
│   │   └── animations.py       # Animation helpers
│   │
│   ├── engine/                 # Business logic (портировано)
│   │   ├── kerning.py          # Kerning operations
│   │   ├── groups.py           # Groups management
│   │   ├── pairs.py            # Pairs generation
│   │   ├── margins.py          # Margins calculation
│   │   ├── language.py         # Language checking
│   │   └── history.py          # Undo/redo
│   │
│   ├── models/                 # Data models
│   │   ├── font_model.py
│   │   ├── glyph_model.py
│   │   └── pair_model.py
│   │
│   ├── controllers/            # Event handling
│   │   ├── keyboard.py
│   │   ├── mouse.py
│   │   └── scroll.py
│   │
│   └── utils/                  # Utilities
│       ├── constants.py
│       ├── helpers.py
│       └── config.py
│
├── data/                       # Resources
│   ├── ui/                     # GTK UI definitions
│   │   ├── window.ui
│   │   ├── preferences.ui
│   │   └── dialogs.ui
│   ├── icons/                  # Application icons
│   ├── langset/                # Language data (портировано)
│   └── com.typedev.KernTool.gschema.xml
│
├── tests/
│   ├── test_rendering.py
│   ├── test_kerning.py
│   └── test_ui.py
│
├── meson.build                 # Build configuration
├── meson_options.txt
├── com.typedev.KernTool.json   # Flatpak manifest
└── README.md
```

---

## Компоненты и их сложность

### 1. Cairo Glyph Renderer

**Сложность:** ⭐⭐⭐⭐ (4/5)

**Что нужно реализовать:**
- Рендеринг контуров глифов через fontTools.pens.cairoPen
- Система слоев (замена Merz layers)
- Margins, metrics, annotations
- Ray beam для точных измерений
- Kerning visualization

**Основные вызовы:**
1. **Performance** - Cairo может быть медленным при большом масштабе
   - Решение: Aggressive caching, рендеринг в ImageSurface
2. **Text rendering** - Pango для всех текстовых элементов
   - Решение: Layout caching, переиспользование объектов
3. **Coordinate system** - конвертация между font units и screen pixels
   - Решение: Четкая система трансформаций

**Оценка времени:** 6-8 недель

### 2. Виртуальный Scrolling

**Сложность:** ⭐⭐⭐ (3/5)

**Варианты реализации:**

**Вариант A: GTK4 ListView (рекомендуется)**
```python
# Преимущества:
- Встроенная виртуализация
- Оптимизирован из коробки
- Меньше кода

# Недостатки:
- Менее гибкий
- Может не подойти для сложных случаев
```

**Вариант B: Custom scrolling**
```python
# Преимущества:
- Полный контроль
- Можно оптимизировать под специфику

# Недостатки:
- Больше кода
- Нужно управлять всем вручную
```

**Оценка времени:** 1.5-2 недели

### 3. Keyboard & Event Handling

**Сложность:** ⭐⭐ (2/5)

**Что нужно:**
- Keyboard shortcuts (30+ комбинаций)
- Mouse events (click, drag, scroll)
- Focus management
- Event propagation

**GTK4 решение:**
```python
# Используем EventController API (новый в GTK4)
key_controller = Gtk.EventControllerKey()
motion_controller = Gtk.EventControllerMotion()
scroll_controller = Gtk.EventControllerScroll()
```

**Оценка времени:** 1 неделя

### 4. Drag & Drop

**Сложность:** ⭐⭐⭐ (3/5)

**Функциональность:**
- Перетаскивание глифов между view
- Изменение порядка глифов
- Visual feedback во время drag

**GTK4 решение:**
```python
# DragSource & DropTarget API (новый в GTK4)
drag_source = Gtk.DragSource()
drop_target = Gtk.DropTarget()
```

**Оценка времени:** 1 неделя

### 5. Animations

**Сложность:** ⭐⭐⭐⭐ (4/5)

**Текущее использование:**
- Cursor animations (loop)
- Smooth scroll
- Появление элементов (fade in)
- Position transitions

**GTK4 решение:**
```python
# Используем Adwaita animations
animation = Adw.TimedAnimation.new(...)
animation.set_easing(Adw.Easing.EASE_IN_OUT_CUBIC)
animation.play()
```

**Вопрос:** Нужны ли все анимации?
- **Критичные:** Smooth scroll
- **Nice-to-have:** Cursor loop, fade in
- **Можно убрать:** Большинство остальных

**Оценка времени:** 1 неделя (если упростить)

### 6. UI Dialogs

**Сложность:** ⭐⭐ (2/5)

**Список диалогов:**
1. Font Selector
2. Pairs Builder (Make Pairs)
3. Language Set Checker
4. Preferences
5. File open/save dialogs

**GTK4 преимущества:**
- Можно использовать Glade/Cambalache для UI design
- Декларативный подход через .ui файлы

**Оценка времени:** 1.5 недели

---

## Преимущества и недостатки

### ✅ Преимущества GTK4

#### 1. Native Performance
- **Direct GPU access** через GskRenderer
- **Hardware acceleration** для Cairo
- **Low memory footprint** (~50-100MB)
- **Instant startup** - нет браузера/JS

#### 2. Linux Integration
```python
# Примеры:
- Native file dialogs
- System theme support (dark/light mode)
- D-Bus integration
- FreeDesktop.org standards compliance
- Wayland/X11 support
```

#### 3. Development Experience
- **Python-native** - полная поддержка Python экосистемы
- **Mature ecosystem** - GTK существует 25+ лет
- **Excellent documentation** - docs.gtk.org
- **Active community** - GNOME, Python communities
- **Easy debugging** - standard Python tools

#### 4. Deployment
```yaml
Packaging:
  - Flatpak (рекомендуется) - sandboxed, portable
  - AppImage - single binary
  - Snap - Ubuntu ecosystem
  - Native packages - deb, rpm, arch

Distribution:
  - Flathub (60M+ users)
  - Snapcraft
  - Distro repositories
```

#### 5. Accessibility
- **Built-in a11y** - screen readers, keyboard navigation
- **GNOME standards** - accessibility из коробки
- **AT-SPI2** - assistive technologies support

### ⚠️ Недостатки GTK4

#### 1. Кривая обучения
**Проблема:** GTK4 API verbose и отличается от Vanilla

```python
# Vanilla (простой):
w = vanilla.Window((800, 600))
w.btn = vanilla.Button((10, 10, 100, 30), "Click")
w.open()

# GTK4 (verbose):
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(800, 600)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        btn = Gtk.Button(label="Click")
        btn.set_margin_start(10)
        btn.set_margin_top(10)
        box.append(btn)

        self.set_child(box)
```

**Решение:** Создать wrapper library для упрощения

#### 2. Cairo rendering сложность
**Проблема:** Нужно вручную управлять всем

```python
# В Merz:
layer.appendLineSublayer(
    startPoint=(0, 0),
    endPoint=(100, 100),
    strokeColor=(1, 0, 0, 1)
)

# В Cairo:
cr.save()
cr.set_source_rgba(1, 0, 0, 1)
cr.set_line_width(1.0)
cr.move_to(0, 0)
cr.line_to(100, 100)
cr.stroke()
cr.restore()
```

**Решение:** Создать layer abstraction поверх Cairo

#### 3. Platform limitation
**Проблема:** Только Linux (основная платформа)

- macOS: Возможно через homebrew, но не native
- Windows: Теоретически возможно, но сложно

**Решение:** Это приемлемо для Linux-first проекта

#### 4. Animation capabilities
**Проблема:** Анимации сложнее чем в Merz

**Merz:** Декларативные анимации из коробки
**GTK4:** Нужно использовать Adwaita или писать вручную

**Решение:** Упростить UX, минимизировать анимации

---

## Подводные камни

### 1. Cairo Performance Issues

**Проблема:**
Cairo может быть медленным при рендеринге большого количества глифов с высоким zoom level.

**Симптомы:**
- Laggy scrolling при >100 глифов на экране
- Медленный zoom
- High CPU usage

**Решения:**

```python
# 1. Aggressive caching
class GlyphCache:
    def __init__(self, max_size=1000):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get_or_create(self, key, render_func):
        if key in self.cache:
            # Move to end (LRU)
            self.cache.move_to_end(key)
            return self.cache[key]

        # Render to ImageSurface
        surface = render_func()
        self.cache[key] = surface

        # Evict if needed
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

        return surface

# 2. Level-of-detail rendering
def draw_glyph(self, cr, glyph, scale):
    if scale < 0.05:
        # Low detail - just bounding box
        self.draw_bbox(cr, glyph)
    elif scale < 0.1:
        # Medium detail - outline only
        self.draw_outline(cr, glyph)
    else:
        # Full detail
        self.draw_full(cr, glyph)

# 3. Dirty region tracking
def invalidate_region(self, x, y, width, height):
    # Only redraw changed area
    self.queue_draw_area(x, y, width, height)
```

### 2. Memory Leaks

**Проблема:**
Cairo objects должны быть правильно cleaned up, иначе memory leak.

**Опасные места:**
```python
# BAD - leak:
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
# ... use surface ...
# forgot to call surface.finish()!

# GOOD - proper cleanup:
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
try:
    # ... use surface ...
finally:
    surface.finish()  # Always cleanup!

# BEST - context manager:
@contextmanager
def create_surface(width, height):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    try:
        yield surface
    finally:
        surface.finish()

with create_surface(100, 100) as surface:
    # ... use surface ...
    pass  # Auto cleanup!
```

**Тестирование:**
```bash
# Используем valgrind для детекции leaks
valgrind --leak-check=full python kerntool.py
```

### 3. Threading Issues

**Проблема:**
GTK НЕ потокобезопасный! Все GTK calls должны быть в main thread.

**Правильный подход:**
```python
import threading
from gi.repository import GLib

def load_font_slow(path):
    """Long operation - runs in thread"""
    font = defcon.Font(path)
    return font

def load_font_async(self, path):
    """Async wrapper"""
    def worker():
        try:
            font = load_font_slow(path)
            # Switch to main thread for GTK calls
            GLib.idle_add(self._on_font_loaded, font)
        except Exception as e:
            GLib.idle_add(self._on_font_error, e)

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()

def _on_font_loaded(self, font):
    """Main thread - safe to call GTK"""
    self.add_font_to_ui(font)
    return False  # Remove from idle
```

### 4. Pango Text Rendering Performance

**Проблема:**
Создание PangoLayout на каждый frame дорого.

**Решение:**
```python
class TextCache:
    def __init__(self):
        self.layouts = {}
        self.pango_context = None

    def get_layout(self, text, font_desc):
        # Reuse layouts
        key = (text, font_desc.to_string())

        if key not in self.layouts:
            layout = Pango.Layout(self.pango_context)
            layout.set_text(text, -1)
            layout.set_font_description(font_desc)
            self.layouts[key] = layout

        return self.layouts[key]

    def clear(self):
        # Clear when font changes
        self.layouts.clear()
```

### 5. Coordinate System Confusion

**Проблема:**
Нужно работать с 3 coordinate systems:
1. **Font units** (glyph coordinates)
2. **View coordinates** (scaled font units)
3. **Window coordinates** (screen pixels)

**Решение:**
```python
class CoordinateTransform:
    def __init__(self):
        self.scale = 0.096  # pt to font units
        self.offset_x = 0
        self.offset_y = 0

    def font_to_view(self, x, y):
        """Font units → view coordinates"""
        return (x * self.scale, y * self.scale)

    def view_to_font(self, x, y):
        """View coordinates → font units"""
        return (x / self.scale, y / self.scale)

    def view_to_window(self, x, y):
        """View → window (add offset)"""
        return (x + self.offset_x, y + self.offset_y)

    def window_to_view(self, x, y):
        """Window → view (remove offset)"""
        return (x - self.offset_x, y - self.offset_y)

    def apply_to_context(self, cr):
        """Apply transform to Cairo context"""
        cr.translate(self.offset_x, self.offset_y)
        cr.scale(self.scale, self.scale)
```

---

## Детальный план разработки

### Фаза 1: Инфраструктура (3-4 недели)

**Неделя 1: Настройка проекта**
- [x] Создать структуру каталогов
- [x] Настроить Meson build system
- [x] Создать базовый meson.build
- [x] Настроить Flatpak manifest
- [x] Создать .desktop файл
- [x] Настроить pre-commit hooks

**Неделя 2: GTK4 скелет**
- [ ] Создать Gtk.Application
- [ ] Создать главное окно (ApplicationWindow)
- [ ] Добавить меню и базовый toolbar
- [ ] Настроить GSettings (preferences)
- [ ] Создать About dialog

**Неделя 3: Портирование бизнес-логики**
- [ ] Портировать tdKernToolEssentials4.py
- [ ] Портировать groups management
- [ ] Портировать pairs generation
- [ ] Портировать language checking
- [ ] Создать unit tests

**Неделя 4: Font handling integration**
- [ ] Интегрировать fontParts
- [ ] Создать FontManager
- [ ] Реализовать font loading/saving
- [ ] Создать font selector UI
- [ ] Тестирование с реальными шрифтами

### Фаза 2: Cairo Renderer (6-8 недель)

**Недели 1-2: Базовый rendering**
- [ ] Создать CairoGlyphRenderer class
- [ ] Реализовать draw_glyph_outline() через CairoPen
- [ ] Реализовать coordinate transforms
- [ ] Добавить basic zoom/pan
- [ ] Тестирование с разными шрифтами

**Недели 3-4: Margins & Metrics**
- [ ] Реализовать draw_margins()
- [ ] Реализовать draw_metrics()
- [ ] Добавить Pango text rendering
- [ ] Создать text cache
- [ ] Реализовать show/hide toggles

**Недели 5-6: Ray Beam System**
- [ ] Портировать ray beam calculations
- [ ] Реализовать draw_ray_beam()
- [ ] Добавить stem width measurements
- [ ] Реализовать ray beam controls (Up/Down)
- [ ] Тестирование с italic fonts

**Недели 7-8: Optimization & Caching**
- [ ] Реализовать GlyphCache (LRU)
- [ ] Добавить ImageSurface caching
- [ ] Реализовать dirty region tracking
- [ ] Level-of-detail rendering
- [ ] Performance profiling и tuning

### Фаза 3: Виртуальный Scrolling (1.5 недели)

**Option A: GTK4 ListView**
- [ ] Создать GlyphLineModel (Gio.ListStore)
- [ ] Создать ListItemFactory
- [ ] Реализовать setup/bind callbacks
- [ ] Интегрировать с renderer
- [ ] Тестирование с большими списками (1000+ строк)

**Option B: Custom scrolling**
- [ ] Создать GlyphsCanvas (Gtk.DrawingArea)
- [ ] Реализовать виртуализацию вручную
- [ ] Добавить scrollbars
- [ ] Оптимизация видимых элементов

### Фаза 4: UI Components (4-5 недель)

**Неделя 1: Split View & Panels**
- [ ] Реализовать Gtk.Paned для split
- [ ] Создать GlyphsViewport (main)
- [ ] Создать GroupsViewport (bottom)
- [ ] Синхронизация между panels
- [ ] Resize handling

**Неделя 2: Keyboard Handling**
- [ ] Создать KeyboardController
- [ ] Реализовать все shortcuts (30+)
- [ ] Добавить shortcut hints
- [ ] Создать keyboard help dialog

**Неделя 3: Drag & Drop**
- [ ] Реализовать DragSource
- [ ] Реализовать DropTarget
- [ ] Добавить visual feedback
- [ ] Тестирование различных сценариев

**Недели 4-5: Dialogs**
- [ ] Font Selector dialog
- [ ] Pairs Builder dialog (Make Pairs)
- [ ] Preferences window
- [ ] Language Set checker dialog
- [ ] All dialogs с .ui файлами

### Фаза 5: Polish & Testing (2-3 недели)

**Неделя 1: Animations (optional)**
- [ ] Smooth scroll animations
- [ ] Cursor animations
- [ ] Fade in/out effects
- [ ] Или: упростить UX без анимаций

**Неделя 2: Bug Fixing & Testing**
- [ ] Тестирование на разных дистрибутивах
- [ ] Wayland vs X11 testing
- [ ] Memory leak detection (valgrind)
- [ ] Performance profiling
- [ ] Edge cases testing

**Неделя 3: Documentation & Packaging**
- [ ] User documentation
- [ ] Developer docs (API)
- [ ] Flatpak packaging
- [ ] AppImage creation (optional)
- [ ] Submit to Flathub

---

## Оценка ресурсов

### Временные затраты

```
Общая оценка: 15-20 недель (4-5 месяцев)

По фазам:
├─ Фаза 1: Инфраструктура        3-4 недели
├─ Фаза 2: Cairo Renderer        6-8 недель
├─ Фаза 3: Virtual Scrolling     1.5 недели
├─ Фаза 4: UI Components         4-5 недель
└─ Фаза 5: Polish & Testing      2-3 недели

Сложность по компонентам:
├─ Cairo rendering               ⭐⭐⭐⭐ (40% времени)
├─ Виртуальный scrolling         ⭐⭐⭐  (10% времени)
├─ UI components                 ⭐⭐   (30% времени)
├─ Портирование логики           ⭐⭐   (10% времени)
└─ Testing & polish              ⭐⭐   (10% времени)
```

### Команда

**Минимальный состав:**
- 1x Senior Python/GTK Developer (full-time, 4-5 месяцев)

**Оптимальный состав:**
- 1x Lead Developer (GTK4 expert)
- 1x Python Developer (business logic)
- 1x QA Engineer (part-time)
- 1x UX Designer (консультант)

### Риски & Буфер

| Риск | Вероятность | Влияние | Буфер |
|------|-------------|---------|-------|
| Cairo performance issues | Средняя | Высокое | +2 недели |
| Сложность виртуализации | Средняя | Среднее | +1 неделя |
| Memory leaks | Низкая | Высокое | +1 неделя |
| Анимации слишком сложны | Высокая | Низкое | 0 (можно убрать) |
| Проблемы совместимости | Низкая | Среднее | +1 неделя |

**Рекомендованный буфер:** +5 недель (25%)

**Итого с буфером:** 20-25 недель (5-6 месяцев)

---

## Выводы и рекомендации

### Итоговая оценка портирования на GTK4

**Сложность:** 7/10
**Время:** 5-6 месяцев (с буфером)
**Feasibility:** ✅ Реалистично

### Почему GTK4 - хороший выбор

1. **Зрелая платформа** - 25+ лет развития
2. **Отличная Python поддержка** - PyGObject стабильный и полный
3. **Native Linux experience** - интеграция с системой из коробки
4. **Cairo performance** - при правильной оптимизации очень быстрый
5. **Большая community** - поддержка и примеры

### Ключевые вызовы

1. **Cairo rendering** - самая сложная часть (40% времени)
2. **Virtual scrolling** - критично для UX
3. **Performance optimization** - нужен профилинг

### Следующие шаги

1. **Proof of Concept** (1-2 недели):
   - Базовый GTK4 window
   - Simple Cairo glyph rendering
   - Test performance с реальными шрифтами

2. **Prototype** (1 месяц):
   - Core rendering functionality
   - Basic UI
   - Validate architecture

3. **Full Development** (3-4 месяца):
   - По плану выше

### Альтернативы

Если GTK4 окажется слишком сложным:
- **Web-based version** - рассмотреть отдельно
- **Qt/PySide6** - более тяжелый, но проще rendering
- **Dear ImGui** - для быстрого прототипа

---

## Приложения

См. также:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Детальная архитектура
- [RENDERING.md](./RENDERING.md) - Cairo rendering guide
- [EXAMPLES.md](./EXAMPLES.md) - Примеры кода
- [ROADMAP.md](./ROADMAP.md) - Развернутый roadmap

---

**Документ подготовлен:** Claude (Anthropic)
**Для проекта:** KernTool4 GTK4 Port
**Лицензия:** Следует лицензии основного проекта
