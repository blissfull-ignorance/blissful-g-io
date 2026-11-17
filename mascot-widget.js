/* mascot-widget.js — zero-maintenance overlay companion (external resource).
 *
 * The site owner pastes ONE line wherever HTML is accepted — a Custom
 * HTML block, a text widget, or the theme's "footer scripts" setting:
 *
 *   <script src="https://blissfull-ignorance.github.io/blissful-g-io/mascot-widget.js"
 *           defer></script>
 *
 * Everything else — the mascot file, the frame CSS, the postMessage
 * bridge — loads from OUR server, resolved relative to this script's
 * own URL (the transparent mascot build lives in mascot/ beside it).
 * Updates never touch the WordPress site again.
 *
 * Because no inline JavaScript ever enters the page content, WordPress's
 * display filters (wpautop, wptexturize) have nothing to mangle — this
 * route needs no mu-plugin guard.
 *
 * Failure mode: the frame stays invisible until the mascot inside
 * reports ready; if the asset is missing or blocked, the widget removes
 * itself and logs a console error — visitors never see anything broken.
 *
 * Config via data attributes on the script tag:
 *   data-size="230"          frame edge length in px
 *   data-inset="18"          distance from the corner, px
 *   data-corner="br"         br | bl | tr | tl
 *
 * The mascot: https://blissfull-ignorance.github.io/blissful-g-io/
 * (bread-stickers project, vendor-free single-file build).
 */
(function () {
  'use strict';
  if (document.getElementById('bread-overlay-frame')) return; // one per page

  var s = document.currentScript;
  if (!s) {
    var all = document.getElementsByTagName('script');
    for (var k = all.length - 1; k >= 0; k--)
      if (/mascot-widget\.js/.test(all[k].src)) { s = all[k]; break; }
  }
  if (!s) return;

  function attr(n, d) { var v = s.getAttribute('data-' + n); return v === null ? d : v; }
  var size  = Math.max(120, Math.min(420, +attr('size', 230)));
  var inset = Math.max(0, +attr('inset', 18));
  var corner = (/^(br|bl|tr|tl)$/).test(attr('corner', 'br')) ? attr('corner', 'br') : 'br';
  var front  = attr('front', '1') !== '0';
  var raise  = attr('raise', 'article, main');

  // the transparent mascot build lives in mascot/ next to this script
  var src = s.src.replace(/[^/]*$/, '') + 'mascot/live-overlay.html';

  var css =
    '#bread-overlay-frame{position:fixed;width:' + size + 'px;height:' + size + 'px;' +
      'border:0;border-radius:22px;background:transparent;' +
      'pointer-events:none;z-index:' + (front ? 9990 : 0) + ';' +
      (corner[1] === 'r' ? 'right:' : 'left:') + inset + 'px;' +
      (corner[0] === 't' ? 'top:' : 'bottom:') + inset + 'px}' +
    (front ? '' : raise + '{position:relative;z-index:1}');
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var f = document.createElement('iframe');
  f.id = 'bread-overlay-frame';
  f.src = src;
  f.title = 'Bread mascot';
  f.setAttribute('aria-hidden', 'true');
  f.setAttribute('tabindex', '-1');
  f.setAttribute('loading', 'lazy');
  f.style.visibility = 'hidden';   // until the mascot inside says ready
  document.body.appendChild(f);

  // professional failure mode: if the mascot asset is missing or
  // blocked, its script never runs, no ready message arrives, and the
  // widget removes itself after a grace period - visitors never see a
  // broken frame, developers find a console error.
  var live = false;
  var boom = setTimeout(function () {
    if (live) return;
    console.error('[bread-mascot] mascot asset did not load: ' + src +
                  ' - widget removed.');
    f.remove();
  }, 5000);
  addEventListener('message', function (ev) {
    var d = ev.data || {};
    if (d.bread === 'mascot' && d.k === 'ready' && ev.source === f.contentWindow) {
      live = true;
      clearTimeout(boom);
      f.style.visibility = 'visible';
      post('enter', 0, 0);
    }
  });

  // the bridge: the frame is click-through, so WE forward the pointer
  var rect;
  function measure() { rect = f.getBoundingClientRect(); }
  measure();
  addEventListener('resize', measure);
  function post(k, x, y) {
    if (!live) return;
    try { f.contentWindow.postMessage({bread: 'mascot', k: k, x: x, y: y}, '*'); }
    catch (e) {}
  }
  f.addEventListener('load', function () { if (!live) post('ping', 0, 0); });
  addEventListener('pointermove', function (e) {
    post('move', e.clientX - rect.left, e.clientY - rect.top);
  }, {passive: true});
  addEventListener('click', function (e) {
    if (e.clientX >= rect.left && e.clientX <= rect.right &&
        e.clientY >= rect.top  && e.clientY <= rect.bottom)
      post('click', e.clientX - rect.left, e.clientY - rect.top);
  });
  document.documentElement.addEventListener('mouseleave', function () { post('leave'); });
  document.documentElement.addEventListener('mouseenter', function () { post('enter', 0, 0); });
})();
