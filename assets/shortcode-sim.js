/* shortcode-sim.js — OPTION 3 demo helper.
 *
 * WordPress expands [bread_mascot ...] SERVER-SIDE with do_shortcode().
 * GitHub Pages has no PHP, so this tiny script simulates the expansion
 * client-side: it scans every element marked data-shortcodes and swaps
 * [bread_mascot size="…" align="…"] for the same iframe markup the PHP
 * shortcode on this page would output. Same contract, different engine.
 */
(function () {
  'use strict';
  var here = document.currentScript
    ? document.currentScript.src.replace(/[^/]*$/, '') : 'assets/';
  var src = here.replace(/assets\/$/, '') + 'mascot/live.html';

  document.querySelectorAll('[data-shortcodes]').forEach(function (el) {
    el.innerHTML = el.innerHTML.replace(
      /\[bread_mascot([^\]]*)\]/g,
      function (m, attrs) {
        var size = (/size="(\d+)"/.exec(attrs) || [])[1] || 420;
        var align = (/align="(\w+)"/.exec(attrs) || [])[1] || 'center';
        return '<div class="bread-mascot align' + align +
          '" style="width:' + size + 'px;max-width:100%">' +
          '<iframe class="mascot" src="' + src +
          '" title="Bread mascot (shortcode)" loading="lazy"></iframe></div>';
      });
  });
})();
