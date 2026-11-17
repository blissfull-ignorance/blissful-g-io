# Blissful Ignorance — WordPress mascot demo

A static GitHub Pages site that mimics a classic WordPress theme and
demonstrates how to embed the interactive bread mascot (the vendor-free
loaf from the bread-stickers project): **four embedding methods** plus an
**overlay technique** that parks the mascot *behind* your content while
its eyes follow the mouse across the whole page.

> Live: https://blissfull-ignorance.github.io/blissful-g-io/

## Pages

| Page | Content |
|---|---|
| [`index.html`](index.html) | overview + live preview |
| [`embedding.html`](embedding.html) | **Embedding, methods 1–4**, each explained + live: 1 iframe · 2 inline (the real fragment, spliced from the actual mascot file at build time) · 3 `[bread_mascot]` shortcode (PHP shown, `do_shortcode()` simulated client-side — Pages has no PHP) · 4 site-wide corner companion (`assets/corner-mascot.js`, active on every page, dismissible) |
| [`overlay.html`](overlay.html) | **Overlay**: the mascot fixed in the lower-right corner *behind* the blog text, gaze tracking the cursor over the entire page, clicks on the text above him still chomp. Method 1 + `pointer-events:none` + a postMessage bridge; includes a z-index toggle to compare behind/in-front |

## Real WordPress, locally (proof of concept)

GitHub Pages can only *imitate* WordPress. For the genuine article:

```
python3 wp_local.py            # Docker required; idempotent
```

Boots a real WordPress with PHP (`wordpress:php8.3-apache` + MariaDB via
`wp/docker-compose.yml`) on **http://127.0.0.1:8765**, installs it with
wp-cli, then **fetches the method-2 inline fragment from this very
site** (`…/blissful-g-io/embedding.html`) and inserts it byte-for-byte
into a `wp_insert_post()` page set as the front page. The mascot then
runs inside genuine WordPress-rendered content — no iframe, no plugin.
Login `admin / breadcrumb`. Flags: `--down` (stop), `--fresh` (wipe DB),
`--fragment-file <html>` (use a local page instead of the live URL).

## Layout

```
mascot/live.html           the mascot: one self-contained file (~104 KB),
                           no vendor runtime, no CDN, no account
mascot/live-overlay.html   overlay variant = live.html + two append-only
                           patches (transparent CSS + postMessage bridge)
assets/wp.css              classic-theme look + overlay frame styles
assets/corner-mascot.js    method 4 (active on every page but the overlay)
assets/shortcode-sim.js    method 3's client-side do_shortcode() stand-in
build_demo.py              regenerates all pages; splices the REAL inline
                           fragment and builds the overlay variant
wp_local.py                local real-WordPress PoC (see above)
wp/docker-compose.yml      the PoC stack
```

## Regenerating

```
python3 build_demo.py
```

Reads `../discord-bread-stickers/mascot/live.html` (regenerate that first
with `python3 scripts/mascot_js.py` after any mascot change), rewrites
all pages, refreshes both `mascot/` files. Commit the output.

## Mapping to a real WordPress site

- `mascot/live.html` / `live-overlay.html` →
  `wp-content/uploads/bread-mascot/` (place via SFTP — the Media Library
  blocks `.html`).
- Methods 1/2 snippets → Gutenberg **Custom HTML** block (or Elementor
  HTML widget / Divi code module).
- Method 3 PHP → `wp-content/mu-plugins/bread-mascot.php` or a WPCode
  snippet.
- Method 4 JS + overlay glue → child-theme `functions.php`
  `wp_enqueue_script()` or a WPCode snippet set to run everywhere.
- WordPress.com: iframes work on every plan; inline scripts, plugins and
  enqueues need the Business/Commerce plan.

The mascot makes **zero third-party requests** and stores nothing —
GDPR-clean by construction.
