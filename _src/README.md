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
| `_src/art.py` | The SVG illustrations: the home picture's kites and stitched arch frame, the strings of mela lights (`festoon`), alpana border |
| `_src/tools/make_story.py` | Paints the six pictures of the home page story ("A story of friendship") into `img/story-1.webp` … `story-6.webp`, with the same four friends and style as the hero. Run it, then `build.py`. `python3 _src/tools/make_story.py 4` repaints only picture 4 |
| `story.js` | The story section on wide screens: one sticky picture frame that cross-fades as each chapter scrolls past. Without it (and on phones) each chapter shows its own picture card |
| `motion.js` | Home page motion: How it works (a thread sews from step to step, each number lights up, its phone wakes), Adda Tables (the cards are dealt, then the front card acts out asking for a seat), Inside the app (a fanned hand of phones laid out as you scroll), and phones tilting toward the mouse. Off for visitors who ask for reduced motion |
| `music.js`, `audio/story-theme.mp3` | The site's music, on every page: our own recording of the Purano Sei Diner Kotha tune, made by `_src/tools/make_theme.py` (public-domain tune, so no licence needed). On by default: every page tries to start it, which browsers allow once the visitor has tapped anywhere on the site; otherwise their first tap starts it. It carries on across pages, stops at once when the page is hidden (another app or tab, screen locked) and comes back after, has lock-screen controls, and "Pause music" is remembered. No fades on iPhones (pages can't change the volume there) |
| `match.js` | "Matched by what you share": the two circles drift together, shared answers fly into the overlap, the match % counts up; "Try someone else" matches you with the next person (`VENN_PEOPLE` in `build.py`) |
| `_src/tools/make_hero.py` | Paints the home page picture (friends on a Ganga ghat at sunset) into `img/hero-ghat.webp`. Run it, then `build.py`. Other looks: `dusk`, `morning` |
| `_src/pages/*.html` | Legal page bodies (privacy, terms, delete account, child safety) |
| `_src/tools/prep_screens.py` | Turns app screenshots into `img/app-*.webp` (cleans the status bar, blurs photos) |
| `style.css`, `site.js`, `story.js`, `motion.js`, `music.js`, `match.js`, `download.js` | Styles and the small scripts (edited directly) |
| `fonts/` | Anek Bangla (headings) and Hind Siliguri (text), served from the site itself. `_src/tools/make_fonts.py` remakes them |

Settings at the top of `build.py`:

- `PLAY_URL`: set at the public launch. Every Download button then goes to Google Play, and `/download` redirects there.
- `APK_FILE`: where the website APK lives (`app/mon-mela.apk`).
- `UPDATED_EN` / `UPDATED_BN`: the "Last updated" date on the legal pages.

Links to `style.css` and the scripts carry `?v=<hash>`, so browsers fetch the new file as soon as it changes.

## Look

"A mela at dusk": deep-teal evening sections (hero, download page, closing panel, footer) with strings of
lights that switch on once when the page opens, and warm sections in between: paper, haldi yellow
(Adda Tables), terracotta clay like Bishnupur's temples (How it works), and mela night (Inside the app). Marigold is kept for
the "get the app" buttons. Colours, fonts and every section are described at the top of `style.css`.

## New app screenshots

Take them on an emulator with a debug build (release builds block screenshots). Use test accounts only.
Put them in a folder as `welcome.jpg`, `looking-for.jpg`, `quiz.jpg` and `picks.jpg`, then:

```
python3 _src/tools/prep_screens.py <that folder>
python3 _src/build.py
```

Raw screenshots are not stored here.
