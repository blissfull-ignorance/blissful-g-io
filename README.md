# Blissful Ignorance — WordPress mascot-embedding demo

A static GitHub Pages site that mimics a classic WordPress theme and
demonstrates **four ways to embed the interactive bread mascot** (the
vendor-free loaf from the bread-stickers project). Every option page
contains a live, working instance *and* explains what you would do on a
real WordPress install.

> The little mascot in the bottom-right corner of **every page** is
> option 4 running live.

## Pages

| Page | Method | Live demo |
|---|---|---|
| [`index.html`](index.html) | overview + preview | iframe |
| [`option-1-iframe.html`](option-1-iframe.html) | host `live.html`, embed via Custom-HTML `<iframe>` | iframe |
| [`option-2-inline.html`](option-2-inline.html) | paste the mascot's scoped style+markup+scripts inline (no iframe) | real inline fragment |
| [`option-3-shortcode.html`](option-3-shortcode.html) | `[bread_mascot]` shortcode (PHP shown; expansion simulated client-side — Pages has no PHP) | simulated |
| [`option-4-corner.html`](option-4-corner.html) | site-wide corner companion via one enqueued JS file | `assets/corner-mascot.js` |

## Layout

```
mascot/live.html          the mascot: one self-contained file (~104 KB),
                          no vendor runtime, no CDN, no account
assets/wp.css             classic-theme look for the demo
assets/corner-mascot.js   option 4 (active on every page)
assets/shortcode-sim.js   option 3's client-side do_shortcode() stand-in
build_demo.py             regenerates the pages; splices the REAL inline
                          fragment (option 2) out of the mascot file
```

## Regenerating

```
python3 build_demo.py
```

Reads `../discord-bread-stickers/mascot/live.html` (regenerate that first
with `python3 scripts/mascot_js.py` after any mascot change), rewrites
all five pages, refreshes `mascot/live.html`. Commit the output.

## Mapping to a real WordPress site

- `mascot/live.html` → `wp-content/uploads/bread-mascot/live.html`
  (place via SFTP — the Media Library blocks `.html`).
- Option 1/2 snippets → Gutenberg **Custom HTML** block (or Elementor
  HTML widget / Divi code module).
- Option 3 PHP → `wp-content/mu-plugins/bread-mascot.php` or a WPCode
  snippet.
- Option 4 JS → child-theme `functions.php` `wp_enqueue_script()` or a
  WPCode snippet set to run everywhere.
- WordPress.com: iframes work on every plan; inline scripts, plugins and
  enqueues need the Business/Commerce plan.

The mascot makes **zero third-party requests** and stores nothing —
GDPR-clean by construction.
