# monmela.in source

The website is plain HTML/CSS/JS built by a small Python script. This `_src` folder is **not published**:
GitHub Pages skips folders whose name starts with `_`.

## Rebuild

```
pip install qrcode pillow
python3 _src/build.py
```

This rewrites `index.html`, `download.html` and the four legal pages in the site folder.

| File | What it holds |
|---|---|
| `_src/build.py` | Page layouts, all home/download text (English + Bengali), header/footer, settings |
| `_src/art.py` | The illustrations (arched Howrah Bridge window with kites, alpana border, stitched rings), drawn as SVG |
| `_src/pages/*.html` | Legal page bodies (privacy, terms, delete account, child safety) |
| `_src/tools/prep_screens.py` | Turns app screenshots into `img/app-*.webp` (cleans the status bar, blurs photos) |
| `style.css`, `site.js`, `home.js`, `download.js` | Styles and the small scripts (edited directly) |

Settings at the top of `build.py`:

- `PLAY_URL`: set at the public launch. Every Download button then goes to Google Play, and `/download` redirects there.
- `APK_FILE`: where the website APK lives (`app/mon-mela.apk`).
- `UPDATED_EN` / `UPDATED_BN`: the "Last updated" date on the legal pages.

Links to `style.css` and the scripts carry `?v=<hash>`, so browsers fetch the new file as soon as it changes.

## New app screenshots

Take them on an emulator with a debug build (release builds block screenshots). Use test accounts only.
Put them in a folder as `welcome.jpg`, `looking-for.jpg`, `quiz.jpg` and `picks.jpg`, then:

```
python3 _src/tools/prep_screens.py <that folder>
python3 _src/build.py
```

Raw screenshots are not stored here.
