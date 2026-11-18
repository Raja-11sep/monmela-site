# Makes the website's font files in fonts/ (already done; run again only to change fonts).
#   npm pack @fontsource-variable/anek-bangla @fontsource/hind-siliguri   (then untar both)
#   pip install fonttools brotli
#   python3 _src/tools/make_fonts.py <folder with the two unpacked packages>
# Anek Bangla is trimmed: width fixed at 112 (the wide look the site uses) and weights 500-800
# only, which takes the Bengali file from ~450 KB to ~110 KB. Hind Siliguri is copied as is (400, 600).
import pathlib
import shutil
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(__file__).resolve().parents[2] / "fonts"
out.mkdir(exist_ok=True)

anek = next(src.glob("*anek-bangla*")) / "files"
for script in ("latin", "bengali"):
    font = TTFont(anek / f"anek-bangla-{script}-standard-normal.woff2")
    font = instancer.instantiateVariableFont(font, {"wdth": 112, "wght": (500, 800)})
    font.flavor = "woff2"
    font.save(out / f"anek-bangla-{script}.woff2")

hind = next(src.glob("*hind-siliguri*")) / "files"
for script in ("latin", "bengali"):
    for weight in (400, 600):
        shutil.copy(hind / f"hind-siliguri-{script}-{weight}-normal.woff2", out / f"hind-siliguri-{script}-{weight}.woff2")
print("fonts written to", out)
