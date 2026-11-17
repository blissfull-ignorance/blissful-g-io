#!/usr/bin/env python3
"""build_demo.py — generate the Blissful Ignorance WordPress-embedding demo.

Reads the vendor-free mascot (discord-bread-stickers/mascot/live.html) and
produces:

  embedding.html   the four embedding methods (iframe / inline / shortcode
                   / corner companion), each explained + live
  overlay.html     the OVERLAY section: mascot BEHIND the page content,
                   eyes following the mouse across the whole page —
                   option 1 (iframe) + pointer-events:none + a
                   postMessage bridge
  index.html       landing page
  mascot/live.html         verbatim mascot (iframe sources)
  mascot/live-overlay.html append-only overlay variant: transparent
                   background + message bridge (the original file stays
                   untouched; the patch is pure <style>/<script> appends)

The option-2 inline fragment and the overlay variant are spliced from the
REAL mascot file, so the demos are the genuine article, not stubs.
"""
import html
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "discord-bread-stickers",
                                   "mascot", "live.html"))

src = open(SRC, encoding="utf-8").read()

# ---- fragments from live.html ----------------------------------------------
def between(s, open_tok, close_tok, start=0):
    a = s.index(open_tok, start) + len(open_tok)
    b = s.index(close_tok, a)
    return s[a:b], b

runtime, end1 = between(src, "<script>", "</script>")
harness, _ = between(src, "<script>", "</script>", end1)
markup = src[src.index('<div id="stage">'):src.index('<p id="foot">')].rstrip()

# ---- option 2: scoped inline fragment ---------------------------------------
SCOPED_CSS = """
.bm-inline-host{display:flex;flex-direction:column;align-items:center;
  gap:12px;background:#0e0f12;color:#e8e6e3;padding:22px 12px;
  border-radius:20px;font:15px/1.5 -apple-system,system-ui,sans-serif}
.bm-inline-host #stage{width:min(78vmin,440px);height:min(78vmin,440px);
  border-radius:20px;background:#18191c;touch-action:none;cursor:pointer;
  overflow:hidden}
.bm-inline-host #stage svg{width:100%;height:100%;display:block}
.bm-inline-host p{margin:0;color:#9a978f;font-size:13px;text-align:center;
  max-width:560px}
.bm-inline-host .tag{display:inline-block;padding:2px 8px;
  border-radius:999px;background:#26221a;color:#e7b24a;font-size:12px;
  margin-right:6px}
.bm-inline-host #rig{display:flex;gap:26px;flex-wrap:wrap;
  justify-content:center;background:#17181c;border:1px solid #26272c;
  border-radius:14px;padding:10px 18px;font-size:12px;color:#9a978f}
.bm-inline-host #rig label{display:flex;flex-direction:column;
  align-items:center;gap:4px}
.bm-inline-host #rig input[type=range]{width:130px;accent-color:#8f7fd4}
"""
INLINE_FRAGMENT = ('<div class="bm-inline-host">\n<style>'
                   + SCOPED_CSS + '</style>\n' + markup
                   + '\n<script>' + runtime + '</script>'
                   + '<script>' + harness + '</script>\n</div>')

# ---- overlay variant: APPEND-ONLY patch of live.html -------------------------
OVERLAY_STYLE = """
  <style>
    /* overlay variant (build_demo.py): transparent everything, the stage
       fills the iframe, page furniture hidden. CSS beats the SVG bg rect's
       presentation attribute. */
    html,body{background:transparent}
    body{padding:0;gap:0}
    #stage{width:100%;height:100%;min-width:0;min-height:0;
      border-radius:0;background:transparent}
    #stage svg > rect{fill:transparent}
    h1,p,#rig,#foot{display:none}
  </style>
"""
OVERLAY_BRIDGE = """
  <script>
  /* overlay bridge: the parent page forwards the pointer via postMessage
     (the iframe itself runs pointer-events:none so the blog stays usable).
     Synthetic events carry clientX/Y, which is all the mascot harness
     reads. Coordinates are clamped to 1.5x the stage so far-away cursor
     positions saturate the gaze instead of spinning it. */
  (function () {
    var stage = document.getElementById('stage');
    addEventListener('message', function (ev) {
      var d = ev.data || {};
      if (d.bread !== 'mascot') return;
      var r = stage.getBoundingClientRect();
      function cl(v, m) { return Math.max(-r.width * m,
                                  Math.min(r.width * (1 + m), v)); }
      if (d.k === 'move' || d.k === 'enter') {
        stage.dispatchEvent(new PointerEvent('pointer' + d.k,
          {clientX: cl(d.x, .5), clientY: cl(d.y, .5)}));
      } else if (d.k === 'leave') {
        stage.dispatchEvent(new PointerEvent('pointerleave'));
      } else if (d.k === 'click') {
        stage.dispatchEvent(new MouseEvent('click',
          {clientX: cl(d.x, .5), clientY: cl(d.y, .5)}));
      }
    });
  })();
  </script>
"""
overlay = src.replace("</head>", OVERLAY_STYLE + "</head>")
overlay = overlay.replace("</body>", OVERLAY_BRIDGE + "</body>")

# ---- page shell ---------------------------------------------------------------
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@ &middot; Blissful Ignorance</title>
<link rel="stylesheet" href="assets/wp.css">
</head>
<body class="@@BODYCLASS@@">
<div class="demo-note">Static demo of <strong>WordPress mascot embedding
&amp; overlay techniques</strong>. These pages mimic a classic WordPress
theme; each section explains what you would do on a real site.</div>
<header class="site-head"><div class="wrap">
  <h1 class="site-title"><a href="index.html">Blissful Ignorance</a></h1>
  <p class="site-tag">don&rsquo;t worry, be bread</p>
</div></header>
<nav class="site-nav"><div class="wrap">@@NAV@@</div></nav>
<div class="wrap cols">
<main>@@BODY@@</main>
<aside>
  <div class="widget"><h2>About this demo</h2>
    <p style="margin:0">A static site imitating a WordPress theme. Where
    real WordPress would run PHP server-side, the demo says so and
    simulates it (GitHub Pages has no PHP).</p></div>
  <div class="widget"><h2>The mascot</h2>
    <ul>
      <li>One self-contained file, ~104&nbsp;KB</li>
      <li>No vendor runtime, no CDN, no account</li>
      <li>Eyes follow the cursor (and get shy)</li>
      <li>Click the loaf &rarr; chomp, the crate &rarr; Gockel</li>
      <li>Leave &rarr; he sleeps, return &rarr; startle-wake</li>
    </ul></div>
  <div class="widget"><h2>GDPR note</h2>
    <p style="margin:0">Zero third-party requests, stores nothing &mdash;
    GDPR-clean by construction.</p></div>
</aside>
</div>
<footer class="site-foot"><div class="wrap">Blissful Ignorance &mdash;
  WordPress embedding &amp; overlay demo &middot; mascot generated by
  <code>scripts/mascot_js.py</code> (bread-stickers project) &middot;
  served by GitHub Pages, not WordPress &#128527;</div></footer>
<script src="assets/corner-mascot.js" defer></script>
@@EXTRA@@</body></html>
"""

NAV = [("index.html", "Home", ""),
       ("embedding.html", "Embedding (1&ndash;4)", "embed"),
       ("overlay.html", "Overlay", "overlay"),
       ("local-wp.html", "Local WordPress", "localwp")]


def page(fname, title, active, body, extra="", bodyclass="",
         shell=SHELL):
    nav = "".join('<a href="%s"%s>%s</a>' % (href,
           ' class="active"' if key == active else "", label)
           for href, label, key in NAV)
    out = (shell.replace("@@TITLE@@", title).replace("@@NAV@@", nav)
                .replace("@@BODY@@", body).replace("@@EXTRA@@", extra)
                .replace("@@BODYCLASS@@", bodyclass))
    open(os.path.join(HERE, fname), "w", encoding="utf-8").write(out)
    print("wrote", fname)


def pre(code):
    return "<pre><code>" + html.escape(code.strip("\n")) + "</code></pre>"


META = ('<p class="meta">Posted in <a href="#">Tutorials</a> &mdash; '
        'bread mascot series</p>')

# ================================ index =======================================
body = """
<article>
<h2>The bread mascot on your WordPress site: embedded, or overlaid</h2>
<p class="kicker">The mascot is one self-contained HTML file: scene data,
art and a ~200-line animation core, no dependencies. This demo covers
both jobs you might want it to do &mdash; <strong>sitting inside a
page</strong> four different ways, and <strong>floating behind the whole
site</strong> while its eyes follow your cursor.</p>

<div class="demo-frame">
  <p class="label">Live preview &mdash; plain iframe</p>
  <iframe class="mascot" src="mascot/live.html" title="bread mascot"
          loading="lazy"></iframe>
</div>

<div class="cards">
  <div class="card"><h3><a href="embedding.html">Embedding &mdash;
     methods 1&ndash;4</a></h3><p>iframe &middot; inline &middot;
     <code>[bread_mascot]</code> shortcode &middot; corner companion.
     From &ldquo;copy-paste one block&rdquo; to &ldquo;20-line
     plugin&rdquo;, each with a live demo and the real-WP
     instructions.</p></div>
  <div class="card"><h3><a href="overlay.html">Overlay &mdash; behind
     the content</a></h3><p>The mascot lives in the lower-right corner
     <em>behind</em> your blog text, follows the mouse across the entire
     page, and still chomps when clicked &mdash; built from method 1
     plus <code>pointer-events:none</code> and a postMessage
     bridge.</p></div>
  <div class="card"><h3><a href="local-wp.html">Local WordPress
     &mdash; the real thing</a></h3><p>Pages can only imitate WordPress.
     <code>wp_local.py</code> boots genuine WordPress with PHP on
     localhost and injects this site&rsquo;s inline fragment into a real
     <code>wp_insert_post()</code> page &mdash; one command, Docker
     required.</p></div>
</div>

<p>Both embedding and overlay use the same asset family:
<a href="mascot/live.html"><code>mascot/live.html</code></a> (the plain
mascot) and <a href="mascot/live-overlay.html"><code>mascot/
live-overlay.html</code></a> (the transparent overlay variant &mdash; an
append-only patch of the first, see the Overlay page). Updating the
mascot after an art change means replacing one file.</p>

<p><strong>Want to see method 2 inside <em>real</em> WordPress?</strong>
The <a href="local-wp.html">Local WordPress</a> section documents
<code>python3 wp_local.py</code>: it boots an actual WordPress with PHP
on <code>http://127.0.0.1:8765</code> and fetches the inline fragment
from this very URL &mdash; so the Pages demo and the WordPress proof run
byte-identical code.</p>
""" + META
page("index.html", "WordPress mascot demo", "", body)

# ============================== embedding =====================================
sec1 = """
<h2 id="m1">Method 1 &mdash; the iframe embed <span class="rec">recommended
  default</span></h2>
<p>Two moving parts: one hosted file, one HTML block. A non-coder can do
it in five minutes and never touch PHP.</p>
<h3>On a real WordPress site</h3>
<ol>
<li><strong>Host the file.</strong> The Media Library refuses
<code>.html</code> uploads (MIME check), so place <code>live.html</code>
via SFTP / hosting file-manager at
<code>wp-content/uploads/bread-mascot/live.html</code> &mdash; static
files in <code>uploads/</code> are served directly. (Alternative: host it
on GitHub Pages and reference that URL &mdash; then updates never touch
the WP install at all. Managed hosts like Kinsta/WordPress.com often
<em>do</em> allow file access or a file-manager plugin; if yours truly
doesn&rsquo;t, the GitHub-Pages URL is your friend.)</li>
<li><strong>Embed.</strong> Add a <em>Custom HTML</em> block (Gutenberg)
or HTML widget (Elementor/Divi) and paste:</li>
</ol>
""" + pre('''
<div style="width:min(460px,100%);margin:0 auto">
  <iframe src="/wp-content/uploads/bread-mascot/live.html"
          title="Bread mascot" loading="lazy"
          style="width:100%;aspect-ratio:1;border:0;border-radius:20px">
  </iframe>
</div>''') + """
<div class="demo-frame">
  <p class="label">Live &mdash; exactly the markup above</p>
  <iframe class="mascot" src="mascot/live.html" title="bread mascot"
          loading="lazy"></iframe>
</div>
<ul>
<li><strong>Sandboxed both ways:</strong> theme CSS can&rsquo;t break the
mascot, the mascot can&rsquo;t leak into the theme.</li>
<li><strong>Works on every plan</strong> including WordPress.com free
&mdash; iframes need no <code>unfiltered_html</code> and no plugins.</li>
<li><strong>Update = re-upload one file;</strong> every embed picks it
up. Cache plugins never touch iframe content.</li>
<li><strong>Limit:</strong> a rectangular island in the flow &mdash; the
page cannot overlap it, and it cannot see the page&rsquo;s mouse. (That
is what the <a href="overlay.html">Overlay</a> section solves.)</li>
</ul>
"""

sec2 = """
<h2 id="m2">Method 2 &mdash; the inline embed (no iframe)</h2>
<p>The mascot lives <em>in</em> the page document: same DOM, same paint.
Blends into layouts an iframe can&rsquo;t.</p>
<h3>On a real WordPress site</h3>
<ol>
<li>Strip <code>live.html</code>&rsquo;s document wrapper
(<code>doctype/html/head/body</code>, the page title, the
<code>html,body</code> CSS rules).</li>
<li>Keep four pieces: <code>&lt;style&gt;</code>, stage + rig markup,
runtime <code>&lt;script&gt;</code>, harness
<code>&lt;script&gt;</code>.</li>
<li>Scope every CSS rule under a host class so nothing leaks into the
theme.</li>
<li>Paste into a <em>Custom HTML</em> block. The instance below is the
real thing &mdash; view this page&rsquo;s source: no iframe here.</li>
</ol>
""" + pre('''
<div class="bm-inline-host">
  <style>/* mascot CSS, every rule scoped under .bm-inline-host */</style>
  <div id="stage"></div>
  <p>&hellip;interaction hints&hellip;</p>
  <div id="rig">&hellip;test-rig sliders&hellip;</div>
  <script>/* runtime: scene JSON + base64 art + sim core (~104 KB) */</script>
  <script>/* harness: pointer listeners + slider wiring */</script>
</div>''') + """
<div class="demo-frame">
  <p class="label">Live &mdash; the actual inline fragment, spliced into
  this page at build time</p>
  <!--INLINE_FRAGMENT-->
</div>
<ul>
<li><strong>Needs <code>unfiltered_html</code>:</strong> admin on
self-hosted WP; on WordPress.com that means Business/Commerce plan
(scripts are stripped below that).</li>
<li><strong>One instance per page</strong> (the fragment uses element
ids); <strong>updates mean re-pasting</strong> &mdash; generate the
fragment from a partial, the way this demo does.</li>
<li><strong>Perk:</strong> page JS can talk to it directly &mdash; no
postMessage needed.</li>
</ul>
"""

sec3 = """
<h2 id="m3">Method 3 &mdash; the <code>[bread_mascot]</code> shortcode</h2>
<p>The WordPress-native answer: editors type a tag, the server renders
the embed. Nothing HTML-shaped ever reaches the editor.</p>
<h3>On a real WordPress site</h3>
<ol>
<li>Drop this into <code>wp-content/mu-plugins/bread-mascot.php</code>
(always-on) or a WPCode PHP snippet:</li>
</ol>
""" + pre('''
<?php
/* Plugin Name: Bread Mascot (shortcode) */
add_shortcode('bread_mascot', function ($atts) {
    $a    = shortcode_atts(['size' => 420, 'align' => 'center'], $atts);
    $url  = esc_url(content_url('uploads/bread-mascot/live.html'));
    $size = max(160, min(640, intval($a['size'])));
    return sprintf(
        '<div class="bread-mascot align%s" style="width:%dpx;max-width:100%%">'
      . '<iframe src="%s" title="Bread mascot" loading="lazy" '
      . 'style="width:100%%;aspect-ratio:1;border:0;border-radius:20px">'
      . '</iframe></div>',
        esc_attr($a['align']), $size, $url);
});''') + """
<li>Host <code>live.html</code> once (method 1).</li>
<li>Anywhere shortcodes run &mdash; posts, pages, Text widgets &mdash;
write <code>[bread_mascot size="380" align="center"]</code>. In PHP
templates: <code>do_shortcode('[bread_mascot]')</code>.</li>
</ol>
<p>GitHub Pages has no PHP, so a ~15-line script performs exactly what
<code>do_shortcode()</code> would, client-side. The &ldquo;post&rdquo;
below contains the raw tag:</p>
""" + pre('''
The bread mascot says hello:

    [bread_mascot size="380" align="center"]

&hellip;carrying on with the article as if nothing happened.
''') + """
<div class="demo-frame">
  <p class="label">Live &mdash; after shortcode expansion (simulated)</p>
  <div data-shortcodes>
  <p>The bread mascot says hello:</p>
  [bread_mascot size="380" align="center"]
  <p>&hellip;carrying on with the article as if nothing happened.</p>
  </div>
</div>
<ul>
<li>Server-side expansion means it also survives feeds and page caches
&mdash; unlike a client-side JS replacer.</li>
<li>The tag outputs method 1&rsquo;s iframe on purpose: one hosted file,
zero JS to manage. A split-<code>mascot.js</code> variant is possible
but needs cache-plugin exclusions.</li>
</ul>
"""

sec4 = """
<h2 id="m4">Method 4 &mdash; the site-wide corner companion</h2>
<p>One script include and every page gets a loaf sitting bottom-right.
It is method 1&rsquo;s iframe, placed by JS instead of by hand &mdash;
and yes, it is running on every page of this demo (look bottom-right;
the Overlay page turns it off to keep the corner free).</p>
<h3>On a real WordPress site</h3>
<ol>
<li>Put <code>bread-corner-mascot.js</code> in the child theme, or paste
it as a WPCode HTML snippet set to <em>run everywhere on the front
end</em>.</li>
<li>Enqueue it:</li>
</ol>
""" + pre('''
<?php
// child-theme functions.php
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_script('bread-corner',
        get_stylesheet_directory_uri() . '/bread-corner-mascot.js',
        array(), '1.0', array('strategy' => 'defer'));
});''') + """
<div class="demo-frame">
  <p class="label">Live &mdash; the companion is on every page. Dismiss
  it, then bring it back:</p>
  <p><button type="button" id="bring-back" style="padding:8px 16px;
     border-radius:8px;border:1px solid var(--line);background:#fff;
     cursor:pointer">re-enable the corner mascot</button>
     <span id="corner-state" style="color:var(--soft);font-size:13px"></span></p>
</div>
<h3>Etiquette</h3>
<ul>
<li>A pet that cannot be shooed is a stain: dismiss &rarr; remembered
for the session via <code>sessionStorage</code>.</li>
<li>Small on mobile, <code>loading="lazy"</code>, modest
<code>z-index</code> so cookie banners and modals stay on top.</li>
<li>Consider front page + blog only &mdash; a checkout page is not a
terrarium.</li>
</ul>
<div class="verdict">
<span class="pill good">method 1: zero code for editors</span>
<span class="pill good">method 2: blends into the page</span>
<span class="pill good">method 3: native WP workflow</span>
<span class="pill good">method 4: site-wide in one include</span>
<span class="pill warn">methods 2&ndash;4 need script access</span>
</div>
""" + META

body = """
<article>
<h2>Embedding &mdash; four methods, one file</h2>
<p class="kicker">All four embed the same <a href="mascot/live.html"><code>
mascot/live.html</code></a>. Pick by access level: <strong>no code at
all</strong> &rarr; method 1 (or 3 once installed); <strong>theme
control</strong> &rarr; methods 2/4. For the mascot <em>behind</em> your
content, see <a href="overlay.html">Overlay</a>.</p>
""" + sec1 + "<hr>" + sec2 + "<hr>" + sec3 + "<hr>" + sec4
page("embedding.html", "Embedding methods 1–4", "embed",
     body.replace("<!--INLINE_FRAGMENT-->", INLINE_FRAGMENT),
     extra='<script src="assets/shortcode-sim.js" defer></script>\n'
           '<script>document.getElementById("bring-back")'
           '.addEventListener("click",function(){'
           'sessionStorage.removeItem("breadMascotDismissed");'
           'location.reload();});'
           'document.getElementById("corner-state").textContent='
           'document.getElementById("bread-corner")'
           '?"currently visible":"currently dismissed (session only)";'
           '</script>\n')

# ================================ overlay =====================================
parent_js = '''
// overlay parent glue (goes in a Custom-HTML block or the same footer
// enqueue as method 4) — the iframe itself is pointer-events:none, so
// the page stays fully usable and WE forward the pointer:
var f = document.getElementById('overlay-mascot'), rect;
function measure() { rect = f.getBoundingClientRect(); }
measure(); addEventListener('resize', measure);
function post(k, x, y) {
  f.contentWindow.postMessage({bread: 'mascot', k: k, x: x, y: y}, '*');
}
f.addEventListener('load', function () { post('enter', 0, 0); }); // wake
addEventListener('pointermove', function (e) {                    // gaze
  post('move', e.clientX - rect.left, e.clientY - rect.top);      // ANYWHERE
}, {passive: true});
addEventListener('click', function (e) {        // chomp/crate hit-test
  if (e.clientX >= rect.left && e.clientX <= rect.right &&
      e.clientY >= rect.top  && e.clientY <= rect.bottom)
    post('click', e.clientX - rect.left, e.clientY - rect.top);   // works
});                                            // even on text above him
document.documentElement.addEventListener('mouseleave',
  function () { post('leave'); });             // out of the window: sleep
document.documentElement.addEventListener('mouseenter',
  function () { post('enter', 0, 0); });       // back: wake with a blink

// optional polish: punch a soft round WINDOW in the content card around
// the corner so the mascot never looks "stuck behind the card". The card
// masks a radial hole at (--hx,--hy); we keep those in card-local coords
// as the page scrolls (133 = frame inset 18 + half of 230px):
var art = document.querySelector('main article');
function placeHole() {
  var r = art.getBoundingClientRect();
  art.style.setProperty('--hx', (innerWidth  - 133 - r.left) + 'px');
  art.style.setProperty('--hy', (innerHeight - 133 - r.top)  + 'px');
}
placeHole();
addEventListener('scroll', placeHole, { passive: true });
addEventListener('resize', placeHole);'''

frame_css = '''
/* the frame: fixed to the corner, BEHIND the content, click-through */
#overlay-mascot{
  position: fixed; right: 18px; bottom: 18px;
  width: 230px; height: 230px;
  border: 0; border-radius: 22px; background: transparent;
  pointer-events: none;   /* the page keeps every mouse event */
  z-index: 0;             /* content sits at z-index:1 => he is behind */
}'''

body = """
<article>
<h2>Overlay &mdash; the mascot <em>behind</em> your content</h2>
<p class="kicker">Wanted: the loaf parked in the lower-right corner,
sitting <em>behind</em> the blog text, eyes following the mouse wherever
it goes on the page. Possible with method 1? Yes &mdash; and this very
page is the demo. Scroll, move your mouse, click a word that happens to
float over him.</p>

<h3>Try it</h3>
<ul>
<li>Move the cursor <strong>anywhere on this page</strong> &mdash; his
gaze tracks it across the whole body, corner-bound like a garden gnome
with a wide neck.</li>
<li>Bring the cursor <strong>close to him</strong> &rarr; he looks away
(shy, as designed).</li>
<li><strong>Click him &mdash; or the text lying on top of him</strong>
&rarr; chomp. Click the crate &rarr; the Gockel cameos. The click lands
on the article (the frame is click-through); the parent hit-tests the
corner and forwards it.</li>
<li>Move the mouse <strong>out of the browser window</strong> &rarr; he
falls asleep. Back in &rarr; wake.</li>
<li><strong>Scroll</strong> &mdash; the article card slides through his
round window in the corner; its edge fades around him instead of
slicing across his face.</li>
</ul>

<label class="z-toggle"><input type="checkbox" id="zflip"> bring the
mascot <strong>in front</strong> instead (flips <code>z-index</code>
&mdash; compare the two looks)</label>

<h3>How it works &mdash; three ingredients</h3>
<p><strong>1. A transparent variant of the mascot.</strong> The plain
<code>live.html</code> paints a dark background (CSS <em>and</em> an SVG
backing rect), which would punch an opaque box into the page. The fix is
an <strong>append-only patch</strong> &mdash; no surgery on the mascot
itself:</p>
""" + pre('''
<!-- live-overlay.html = live.html + these two appends -->
<style>
  html,body{background:transparent}
  #stage{width:100%;height:100%;background:transparent}
  #stage svg > rect{fill:transparent}   /* CSS beats the SVG fill attr */
  h1,p,#rig,#foot{display:none}
</style>''') + """
<p><strong>2. The frame, pinned to the corner behind everything:</strong></p>
""" + pre(frame_css) + """
<p>Your theme&rsquo;s content needs <code>position:relative;
z-index:1</code> &mdash; one CSS line, and he is behind it. To keep that
from reading as &ldquo;stuck behind a wall&rdquo;, this demo punches a
soft <strong>round window</strong> in the card around him: the card
masks a radial hole at <code>(--hx,--hy)</code>, and a few lines of glue
keep those coordinates centred on the corner as the page scrolls. Text
that wanders into the window fades politely around him instead of
slicing across his face.</p>
<p><strong>3. The postMessage bridge.</strong> Here is the catch: an
iframe that sits behind the page must be <code>pointer-events:none</code>
&mdash; otherwise an invisible sheet of glass covers the whole site and
no link, selection or scroll works anymore. But a click-through iframe
also receives <em>no mouse events itself</em>, so the mascot would be
blind. The parent page therefore forwards the pointer:</p>
""" + pre(parent_js) + """
<p>Inside the frame, a ~20-line listener turns those messages back into
synthetic <code>pointermove / pointerenter / pointerleave / click</code>
events on the stage &mdash; the mascot&rsquo;s own harness reads only
<code>clientX/Y</code>, so it cannot tell the difference. Far-away
coordinates are clamped so the gaze saturates at the neck limit instead
of spinning. Full bridge source: <a href="mascot/live-overlay.html"><code>
mascot/live-overlay.html</code></a> (bottom of the file).</p>

<h3>The zero-maintenance route: one external script tag</h3>
<p>Every ingredient above can be pre-packaged. This site serves
<code>mascot-widget.js</code>: it injects the frame, the CSS and the
bridge itself, and loads the transparent mascot build from next to
itself &mdash; the site owner pastes <strong>one line</strong> into a
Custom HTML block, a widget, or the theme&rsquo;s &ldquo;footer
scripts&rdquo; setting and never touches code again:</p>
""" + pre('''
<script src="https://blissfull-ignorance.github.io/blissful-g-io/mascot-widget.js"
        defer></script>''') + """
<ul>
<li><strong>No inline JS enters the page content</strong> &mdash; so
WordPress&rsquo;s display filters (wpautop, wptexturize) have nothing to
mangle: this route needs no mu-plugin guard at all.</li>
<li><strong>Config via data attributes:</strong> <code>data-size</code>,
<code>data-inset</code>, <code>data-corner="br|bl|tr|tl"</code>,
<code>data-front="1"</code> (above instead of behind),
<code>data-raise="article, main"</code> (selectors lifted above him so
&ldquo;behind&rdquo; works even on themes with unpositioned content).</li>
<li><strong>Updates are ours:</strong> replace the mascot on this site
and every embedding site picks it up on next load.</li>
<li>Works on self-hosted WordPress everywhere; on WordPress.com it
needs the Business/Commerce plan (scripts are stripped below that).</li>
</ul>

<h3>On a real WordPress site</h3>
<ul>
<li>Host <code>live-overlay.html</code> like method 1; put the frame
markup + parent glue into a WPCode snippet running on the pages you
want, or the child theme&rsquo;s footer.</li>
<li><strong>Same-origin not required:</strong> postMessage works
across origins (lock <code>'*'</code> down to your site&rsquo;s origin
in production).</li>
<li><strong>z-index etiquette:</strong> stay below modals and cookie
banners; if the theme has its own stacking contexts, raise the
<em>content</em>&rsquo;s z-index rather than fighting with negative
values.</li>
<li><strong>Touch devices:</strong> there is no hover &mdash; the gaze
follows drags and taps land the chomps; consider hiding the overlay
below a breakpoint, or keep him as a sleeping corner ornament.</li>
<li><strong>Performance:</strong> one extra rAF loop; fine on any blog.
<code>loading="lazy"</code> and consider <code>content-visibility</code>
on long pages.</li>
</ul>

<div class="verdict">
<span class="pill good">still method 1: one file + one block</span>
<span class="pill good">page stays 100% interactive</span>
<span class="pill good">gaze spans the whole page</span>
<span class="pill warn">needs the transparent variant + ~35 lines of glue</span>
<span class="pill warn">no hover on touch devices</span>
</div>

<p class="meta">Built with the same asset as <a href="embedding.html">
Embedding 1&ndash;4</a> &mdash; the overlay is a deployment technique,
not a different mascot.</p>
</article>

<iframe id="overlay-mascot" src="mascot/live-overlay.html"
        title="Bread mascot (overlay)" tabindex="-1"
        aria-hidden="true"></iframe>

<script>
(function () {
  var f = document.getElementById('overlay-mascot'), rect;
  function measure() { rect = f.getBoundingClientRect(); }
  measure(); addEventListener('resize', measure);
  function post(k, x, y) {
    f.contentWindow.postMessage({bread: 'mascot', k: k, x: x, y: y}, '*');
  }
  f.addEventListener('load', function () { post('enter', 0, 0); });
  addEventListener('pointermove', function (e) {
    post('move', e.clientX - rect.left, e.clientY - rect.top);
  }, {passive: true});
  addEventListener('click', function (e) {
    if (e.clientX >= rect.left && e.clientX <= rect.right &&
        e.clientY >= rect.top  && e.clientY <= rect.bottom)
      post('click', e.clientX - rect.left, e.clientY - rect.top);
  });
  document.documentElement.addEventListener('mouseleave',
    function () { post('leave'); });
  document.documentElement.addEventListener('mouseenter',
    function () { post('enter', 0, 0); });
  var art = document.querySelector('main article');
  function placeHole() {
    var r = art.getBoundingClientRect();
    art.style.setProperty('--hx', (innerWidth  - 133 - r.left) + 'px');
    art.style.setProperty('--hy', (innerHeight - 133 - r.top)  + 'px');
  }
  placeHole();
  addEventListener('scroll', placeHole, { passive: true });
  addEventListener('resize', placeHole);
  document.getElementById('zflip').addEventListener('change',
    function (e) { f.style.zIndex = e.target.checked ? 60 : 0; });
})();
</script>
"""
# overlay page: full-width, windowed card, no corner companion
page("overlay.html", "Overlay — mascot behind the content", "overlay",
     body, bodyclass="overlay-page")

# ============================= local wordpress ===============================
run_cmd = '''
git clone https://github.com/blissfull-ignorance/blissful-g-io.git
cd blissful-g-io
python3 wp_local.py        # Docker must be running

  ->  front page (mascot inline, method 2):  http://127.0.0.1:8765/
      wp-admin:                              http://127.0.0.1:8765/wp-admin/
      login:                                 admin / breadcrumb'''

steps = '''
1. docker compose up        wordpress:php8.3-apache + MariaDB
                            (wp/docker-compose.yml, port 8765)
2. wp-cli (fetched inside the container)
                            wp core install --url=http://127.0.0.1:8765
3. GET  https://blissfull-ignorance.github.io/blissful-g-io/
                        embedding.html   <-- THIS PUBLISHED PAGE
      extract <div class="bm-inline-host"> ... </div>   (byte-exact)
4. wp_insert_post( page, post_content = fragment )
      + show_on_front = that page       (real PHP, real database)
5. print the URLs. Done. Re-runs are idempotent (page is updated,
   database kept).'''

mu_php = '''<?php
/**
 * Demo guard: the mascot is one self-contained HTML fragment whose inline
 * <script> must reach the browser byte-exact. WordPress's formatting
 * filters rewrite post_content on display (wpautop injects <p> tags,
 * wptexturize escapes "&&" inside scripts), so they are disabled here.
 * On a real site the same protection is what a Custom HTML block gives
 * you - it stores raw HTML.
 */
foreach ( array( 'wpautop', 'convert_chars', 'convert_smilies' ) as $f ) {
\tremove_filter( 'the_content', $f );
}
add_filter( 'run_wptexturize', '__return_false' );'''

body = """
<article>
<h2>Local WordPress &mdash; the demo inside the real thing</h2>
<p class="kicker">Everything on this site imitates WordPress with static
HTML, because GitHub Pages has no PHP. This section is about the other
half: <code>wp_local.py</code>, a ~200-line Python script in the repo
that boots <strong>genuine WordPress with real PHP</strong> on your
machine and puts <a href="embedding.html#m2">method 2 (the inline
embed)</a> into it for real.</p>

<h3>Try it</h3>
""" + pre(run_cmd) + """
<div class="demo-frame">
  <p class="label">What you get</p>
  <p>A stock WordPress install (default theme, real database, working
  wp-admin) whose <strong>static front page</strong> is a real
  <code>wp_insert_post()</code> page containing the mascot&rsquo;s inline
  fragment &mdash; no iframe, no plugin. Move the mouse, click the loaf:
  it is the genuine article, server-rendered by WordPress PHP.</p>
</div>

<h3>The proof-of-concept chain</h3>
<p>The script does not use a local copy of the fragment. It
<strong>fetches this published Pages page</strong>, extracts the
<code>.bm-inline-host</code> div byte-for-byte, and hands those bytes to
WordPress. Same asset, two delivery worlds &mdash; Pages and real
WordPress &mdash; verified equal:</p>
""" + pre(steps) + """
<h3>What building it revealed (the honest caveat)</h3>
<p>Inserted raw, the mascot rendered as an empty frame: WordPress
rewrites <code>post_content</code> <em>on display</em>, and two formatters
mangle inline scripts &mdash; <code>wpautop</code> injects
<code>&lt;p&gt;</code> tags into them, and <code>wptexturize</code>
escapes <code>&amp;&amp;</code> into <code>&amp;#038;&amp;#038;</code>
(a minimal <code>&lt;script&gt;if (a &lt; 1 &amp;&amp; b)&lt;/script&gt;</code>
reproduces it). The sneaky part: block themes run
<code>wptexturize()</code> <strong>directly on the assembled
template</strong> (<code>get_the_block_template_html()</code>), so
unhooking it from <code>the_content</code> is not enough &mdash; the
demo&rsquo;s mu-plugin uses the documented <code>run_wptexturize</code>
kill-switch as well:</p>
""" + pre(mu_php) + """
<p>On a real site you meet the same issue in miniature: a
<strong>Custom HTML block</strong> stores raw HTML and is the right
place for the fragment, but the template-level pass still applies on
block themes &mdash; so keep the two-line guard (mu-plugin or theme
<code>functions.php</code>) whenever content carries inline JS. Or skip
the whole class of problems with <a href="overlay.html">the iframe
overlay</a>: scripts inside an iframe are nobody&rsquo;s content but
their own.</p>

<h3>Script reference</h3>
<ul>
<li><code>python3 wp_local.py</code> &mdash; start / update (idempotent;
reuses the running stack and the database).</li>
<li><code>--down</code> &mdash; stop the stack, data kept;
<code>--down --fresh</code> &mdash; also delete the database volume.</li>
<li><code>--fresh</code> &mdash; wipe and reinstall in one go.</li>
<li><code>--fragment-file embedding.html</code> &mdash; take the
fragment from a local file instead of the live URL (useful offline or
before a push).</li>
<li>Requirements: Docker (Desktop or Engine) running, Python&nbsp;3 with
nothing extra to install, port&nbsp;8765 free. First run pulls ~700&nbsp;MB
of official images.</li>
</ul>

<div class="verdict">
<span class="pill good">real WordPress, real PHP, one command</span>
<span class="pill good">fragment fetched from the live Pages URL</span>
<span class="pill good">byte-exact render, verified</span>
<span class="pill warn">Docker required</span>
<span class="pill warn">localhost only &mdash; it is a PoC, not hosting</span>
</div>
""" + META
page("local-wp.html", "Local WordPress — real PHP proof of concept",
     "localwp", body)

# ---- assets -----------------------------------------------------------------
os.makedirs(os.path.join(HERE, "mascot"), exist_ok=True)
shutil.copyfile(SRC, os.path.join(HERE, "mascot", "live.html"))
open(os.path.join(HERE, "mascot", "live-overlay.html"), "w",
     encoding="utf-8").write(overlay)
open(os.path.join(HERE, ".nojekyll"), "w").write("")
print("mascot/live.html %d KB, live-overlay.html %d KB"
      % (os.path.getsize(os.path.join(HERE, "mascot", "live.html")) // 1024,
         len(overlay.encode()) // 1024))
