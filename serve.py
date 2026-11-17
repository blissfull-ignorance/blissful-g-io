#!/usr/bin/env python3
"""serve.py — localhost stand-in for GitHub Pages (dev loop, no pushes).

Rebuilds the demo (build_demo.py), then serves the repo root at
http://127.0.0.1:8080 with no-store headers, so every reload shows the
fresh page. This is the daily driver; git push to Pages happens only at
milestones.

  python3 serve.py                     # build + serve on :8080
  python3 serve.py --port 9000 --no-build

Pair with the local WordPress PoC reading the LOCAL demo instead of the
published one (keeps github.io pushes down to zero while iterating):

  python3 wp_local.py --origin http://127.0.0.1:8080

The mascot-widget.js resolves the transparent mascot build relative to
its own URL, so the one-line widget works from localhost too.
"""
import argparse
import functools
import http.server
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


class NoStore(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):  # quieter than the default
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--no-build", action="store_true",
                    help="skip running build_demo.py first")
    a = ap.parse_args()

    if not a.no_build:
        subprocess.run([sys.executable, os.path.join(HERE, "build_demo.py")],
                       check=True, stdout=subprocess.DEVNULL)
        print("built.")

    handler = functools.partial(NoStore, directory=HERE)
    with http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler) as srv:
        print("demo  : http://127.0.0.1:%d/" % a.port)
        print("wp poc: python3 wp_local.py --origin http://127.0.0.1:%d"
              % a.port)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
