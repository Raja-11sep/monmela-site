# Draws og.png: the picture WhatsApp, Facebook, Instagram and X show when someone shares a
# monmela.in link (1200 x 630, the size they all expect). Same look as the home page hero:
# dusk, the string of lights, the headline in Bengali, the Ganga ghat picture in its arch.
#   python3 _src/tools/make_og.py      (then build.py, so pages point at the new image)
# It renders a temporary page with the site's own CSS, fonts and art, then deletes it.
import functools
import http.server
import pathlib
import socketserver
import sys
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_src"))
from art import LOGO, festoon, hero_art  # noqa: E402  (the same logo, lights and picture as the home page)

PAGE = ROOT / "_og.html"            # temporary: served so style.css, fonts/ and img/ load as on the site

HTML = f"""<!doctype html><html lang="bn"><head><meta charset="utf-8">
<link rel="stylesheet" href="style.css">
<style>
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; }}
  .og {{ position: relative; width: 1200px; height: 630px; overflow: hidden; color: var(--on-dusk);
        background: radial-gradient(50% 70% at 82% 60%, rgba(245, 176, 35, .18), transparent 70%),
                    linear-gradient(180deg, var(--dusk-deep) 0%, var(--dusk) 60%, #0D4440 100%); }}
  .og .festoon {{ height: 96px; }}
  .og .festoon .bulb {{ animation: none; }}            /* all lights on in a still picture */
  .og-text {{ position: absolute; left: 72px; top: 150px; width: 640px; }}
  .og-brand {{ display: flex; align-items: center; gap: 14px; font: 700 34px/1 var(--display); }}
  .og-brand svg {{ width: 58px; height: 58px; }}
  .og h1 {{ margin: 38px 0 18px; font: 800 64px/1.2 var(--display); white-space: nowrap; color: var(--on-dusk); }}
  .og p {{ margin: 0; font: 400 31px/1.4 var(--sans); color: var(--on-dusk-muted); }}
  .og-tags {{ display: flex; gap: 12px; margin-top: 30px; }}
  .og-tags span {{ padding: 8px 20px; border-radius: 999px; font: 600 23px/1.3 var(--sans);
                  background: rgba(255, 246, 229, .1); box-shadow: inset 0 0 0 1.5px rgba(255, 246, 229, .3); }}
  .og-tags span:first-child {{ background: var(--marigold); color: var(--ink); box-shadow: none; }}
  .og-art {{ position: absolute; right: 64px; top: 104px; width: 370px; }}
  .og-art .kite {{ animation: none; }}
</style></head><body>
<div class="og">
  {festoon()}
  <div class="og-text">
    <div class="og-brand">{LOGO}<span>Mon Mela</span></div>
    <h1>মন মিললে, বন্ধু মেলে।</h1>
    <p lang="en">Friends nearby who love what you love.</p>
    <div class="og-tags" lang="en"><span>Free</span><span>Kolkata &amp; West Bengal</span><span>Not dating</span></div>
  </div>
  <div class="og-art">{hero_art("img/hero-ghat.webp")}</div>
</div>
</body></html>"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


if __name__ == "__main__":
    PAGE.write_text(HTML, encoding="utf-8")
    server = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1200, "height": 630})
            page.goto(f"http://127.0.0.1:{server.server_address[1]}/_og.html", wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(400)
            page.screenshot(path=str(ROOT / "og.png"))
            browser.close()
    finally:
        server.shutdown()
        PAGE.unlink()
    # Keep it small: WhatsApp skips large preview images. A 256-colour PNG is plenty for this art.
    img = Image.open(ROOT / "og.png").convert("RGB")
    img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(ROOT / "og.png", optimize=True)
    print("wrote og.png", (ROOT / "og.png").stat().st_size // 1024, "KB")
