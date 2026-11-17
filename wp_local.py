#!/usr/bin/env python3
"""wp_local.py — proof of concept: the demo as REAL WordPress with PHP.

The GitHub Pages site can only imitate WordPress. This script boots a
genuine WordPress (official wordpress:php8.3-apache + MariaDB containers,
so real PHP) on http://127.0.0.1:8765 and puts **method 2 (the inline
embed)** into it for real:

  1. docker compose up  (wp/docker-compose.yml)
  2. install WordPress with wp-cli (fetched inside the container)
  3. FETCH the option-2 inline fragment from the PUBLISHED demo at
     https://blissfull-ignorance.github.io/blissful-g-io/embedding.html
     — the very bytes the Pages site runs — and insert it, untouched,
     into a real wp_insert_post() page set as the static front page
  4. print the URLs

That is the whole proof: one self-contained HTML fragment, no iframe,
no plugin — pasted into post_content by the server, rendered by real
WordPress PHP, mascot alive. (A mu-plugin only removes wpautop so the
editor's auto-paragraphing cannot inject <p> tags into the mascot's
<script>; on a real site you would paste the same fragment into a
Custom HTML block, which has the same effect.)

Requirements: Docker (Desktop/Engine) running. Python 3 only, no pip.

Usage:
  python3 wp_local.py            # start / update (idempotent)
  python3 wp_local.py --fresh    # wipe database, reinstall from scratch
  python3 wp_local.py --down     # stop the stack (data kept)
  python3 wp_local.py --fragment-file embedding.html   # local fragment source
"""
import argparse
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
COMPOSE = ["docker", "compose", "-f", os.path.join(HERE, "wp",
                                                   "docker-compose.yml")]
WP = "blissful-wp"
PORT = 8765
URL = "http://127.0.0.1:%d" % PORT
FRAGMENT_URL = ("https://blissfull-ignorance.github.io/blissful-g-io/"
                "embedding.html")
SLUG = "bread-mascot-inline"


def run(cmd, **kw):
    return subprocess.run(cmd, **kw)


def sh(cmd, **kw):
    """run, inherit stdio, abort on failure"""
    r = run(cmd, **kw)
    if r.returncode != 0:
        sys.exit("command failed (%d): %s" % (r.returncode, " ".join(cmd)))
    return r


def docker_up():
    r = run(["docker", "info", "--format", "ok"], capture_output=True, text=True)
    if r.returncode != 0:
        if sys.platform == "darwin":
            print("Docker daemon not running — starting Docker Desktop …")
            run(["open", "-a", "Docker"])
            for _ in range(60):
                if run(["docker", "info"], capture_output=True).returncode == 0:
                    break
                time.sleep(2)
            else:
                sys.exit("Docker did not come up; start it and rerun.")
        else:
            sys.exit("Docker daemon not reachable — start Docker and rerun.")
    sh(COMPOSE + ["up", "-d"])


def wait_http(timeout=180):
    """any HTTP answer means Apache is up (pre-install WP redirects to
    install.php; that counts)"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            urllib.request.urlopen(URL + "/", timeout=3)
            return True
        except urllib.error.HTTPError:
            return True
        except Exception:
            time.sleep(2)
    return False


def wp(args, **kw):
    return run(["docker", "exec", WP, "wp"] + args + ["--allow-root"], **kw)


def ensure_wp_cli():
    r = run(["docker", "exec", WP, "which", "wp"], capture_output=True)
    if r.returncode == 0:
        return
    print("installing wp-cli inside the container …")
    sh(["docker", "exec", WP, "bash", "-c",
        "curl -sfL https://raw.githubusercontent.com/wp-cli/builds/gh-pages/"
        "phar/wp-cli.phar -o /usr/local/bin/wp && chmod +x /usr/local/bin/wp"])


def install_wordpress():
    # official image docroot is /var/www/html. The mu-plugin is the demo's
    # one honest concession: WP's formatting filters rewrite post_content
    # on display (wpautop injects <p> tags, wptexturize escapes the "&&"
    # inside the mascot's inline <script> — even the template-level call
    # in get_the_block_template_html(), hence run_wptexturize). A Custom
    # HTML block on a real site stores raw HTML and needs no such guard.
    sh(["docker", "exec", "-i", WP, "bash", "-c",
        "mkdir -p /var/www/html/wp-content/mu-plugins && cat > /var/www/html/"
        "wp-content/mu-plugins/bm-inline-guard.php"],
       input=b"""<?php
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
add_filter( 'run_wptexturize', '__return_false' );
""")
    if wp(["core", "is-installed"], capture_output=True).returncode == 0:
        print("WordPress already installed — keeping the database.")
        return
    print("installing WordPress …")
    sh(["docker", "exec", WP, "wp", "core", "install",
        "--url=" + URL,
        "--title=Blissful Ignorance — local WordPress PoC",
        "--admin_user=admin", "--admin_password=breadcrumb",
        "--admin_email=demo@example.invalid", "--skip-email", "--allow-root"])


def fetch_fragment(path=None):
    src = open(path, encoding="utf-8").read() if path else \
        urllib.request.urlopen(FRAGMENT_URL, timeout=30).read().decode("utf-8")
    start = src.index('<div class="bm-inline-host">')
    end = src.index("</script>\n</div>", start) + len("</script>\n</div>")
    frag = src[start:end]
    print("fragment: %d KB, %s" % (
        len(frag.encode()) // 1024,
        "local file " + path if path else "fetched live from " + FRAGMENT_URL))
    return frag


def inject_page(fragment):
    post_html = (
        "<p><em>This page is the proof of concept: the option-2 inline "
        "fragment was fetched from the published GitHub Pages demo and "
        "inserted into this WordPress via </em><code>wp_insert_post()</code>"
        "<em> — no iframe, no plugin. The mascot below is running inside "
        "genuine WordPress-rendered content. Move your mouse over the "
        "page; click the loaf.</em></p>\n"
        + fragment +
        "\n<p><em>…and the article could carry on right here, because the "
        "fragment is just part of the post now.</em></p>\n")
    tmp = os.path.join(HERE, ".fragment-post.html")
    open(tmp, "w", encoding="utf-8").write(post_html)
    sh(["docker", "cp", tmp, WP + ":/tmp/fragment-post.html"])
    os.remove(tmp)
    php = (
        "$c=file_get_contents('/tmp/fragment-post.html');"
        "$p=get_page_by_path('%s');"
        "$id=wp_insert_post(array("
        "'ID'=> $p ? $p->ID : 0,"
        "'post_title'=>'The mascot, inline — real WordPress (method 2)',"
        "'post_name'=>'%s','post_type'=>'page','post_status'=>'publish',"
        "'post_content'=>$c));"
        "if(is_wp_error($id)){echo $id->get_error_message();exit(1);}"
        "update_option('show_on_front','page');"
        "update_option('page_on_front',$id);"
        "echo $id;" % (SLUG, SLUG))
    r = sh(["docker", "exec", WP, "wp", "eval", php, "--allow-root"],
           capture_output=True, text=True)
    print("front page id:", r.stdout.strip())


def down(fresh=False):
    sh(COMPOSE + (["down", "-v"] if fresh else ["stop"]))
    print("stack stopped" + (" (database wiped)" if fresh else "") + ".")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--down", action="store_true", help="stop the stack")
    ap.add_argument("--fresh", action="store_true",
                    help="with --down: also delete the database; "
                         "without: reinstall from scratch")
    ap.add_argument("--fragment-file", metavar="HTML",
                    help="take the inline fragment from a local page "
                         "(default: fetch the published github.io demo)")
    a = ap.parse_args()

    if a.down:
        down(fresh=a.fresh)
        return
    if a.fresh:
        down(fresh=True)

    docker_up()
    print("waiting for Apache …")
    if not wait_http():
        sys.exit("WordPress did not answer on %s (first image pull can "
                 "take a while — rerun)." % URL)
    ensure_wp_cli()
    install_wordpress()
    inject_page(fetch_fragment(a.fragment_file))
    print("""
──────────────────────────────────────────────────────────────
  REAL WordPress with PHP is up:
    front page (mascot inline, method 2):  %s/
    wp-admin:                              %s/wp-admin/
    login:                                 admin / breadcrumb
  The inline fragment came from the published demo:
    %s
  Stop with:  python3 wp_local.py --down
──────────────────────────────────────────────────────────────""" %
          (URL, URL, FRAGMENT_URL))


if __name__ == "__main__":
    main()
