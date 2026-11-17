/* bread-corner-mascot.js — OPTION 4: the site-wide corner companion.
 *
 * On a real WordPress site this exact file is what you enqueue:
 *   - as a WPCode / "Insert HTML Snippet" <script> running on every page, or
 *   - via wp_enqueue_script() in a child theme's functions.php, or
 *   - pasted into the theme footer before </body>.
 * It injects a fixed-position iframe of the mascot into EVERY page, with a
 * dismiss button remembered for the session (mobile etiquette).
 *
 * This demo loads it on all pages — that little loaf bottom-right IS
 * option 4 working. See option-4-corner.html for the full explanation.
 */
(function () {
  'use strict';
  if (sessionStorage.getItem('breadMascotDismissed') === '1') return;
  // the Overlay page owns the lower-right corner itself — stand down
  if (document.body.classList.contains('overlay-page')) return;

  // resolve mascot/live.html relative to this script, so the demo works
  // from any Pages base-path
  var here = document.currentScript
    ? document.currentScript.src.replace(/[^/]*$/, '') : 'assets/';
  var src = here.replace(/assets\/$/, '') + 'mascot/live.html';

  var box = document.createElement('div');
  box.id = 'bread-corner';
  box.innerHTML =
    '<iframe src="' + src + '" title="Bread mascot (site companion)" ' +
    'loading="lazy"></iframe>' +
    '<button type="button" aria-label="hide mascot">&times;</button>' +
    '<div class="tip">option 4 · on every page</div>';
  document.body.appendChild(box);

  box.querySelector('button').addEventListener('click', function () {
    sessionStorage.setItem('breadMascotDismissed', '1');
    box.remove();
  });
})();
