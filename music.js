// Site music: our own recording of the Purano Sei Diner Kotha tune, on every page.
//
// On by default. Browsers only allow sound once the visitor has touched the site (a tap, click
// or key press; scrolling doesn't count), so:
//   - every page tries to start it straight away: that works once they've touched any page of
//     the site (Chrome), or, on desktop, when they often play sound on this site;
//   - otherwise it starts with their first tap, click or key press anywhere on the page;
//   - it carries on across pages from where it was.
// When a page opens silent, the floating button says "Tap for music" for a few seconds.
// "Pause music" (or pausing from the phone's lock screen) turns it off, and that's remembered
// on every page until they turn it on again.
// It stops at once when the page is hidden (another tab or app, screen locked) and comes back
// when the page is shown again. The track only downloads when it first plays.
// Without JavaScript there's no music and no buttons.
(function () {
  var VOLUME = 0.6;
  var OFF = 'mm-music-off';      // localStorage: the visitor turned the music off
  var AT = 'mm-music-at';        // sessionStorage: where the tune was when they left the last page
  var NUDGED = 'mm-music-nudged';  // sessionStorage: the "Tap for music" nudge has been shown this visit
  var TOUCHES = ['click', 'keydown', 'touchend', 'pointerup'];

  // Storage can be blocked (private modes, strict settings); then nothing is remembered.
  function read(store, key) { try { return window[store].getItem(key); } catch (e) { return null; } }
  function write(store, key, value) {
    try { if (value === null) window[store].removeItem(key); else window[store].setItem(key, value); } catch (e) { /* not remembered */ }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var audio = document.querySelector('.site-audio');
    if (!audio || typeof audio.play !== 'function') return;
    var buttons = [].slice.call(document.querySelectorAll('.music-btn'));
    var storyButton = document.querySelector('.story-head .music-btn');
    var tune = document.querySelector('.music-tune');

    var wanted = read('localStorage', OFF) !== '1';  // the visitor's choice: on unless they turned it off
    var playing = false;        // we started it and haven't stopped it (what the buttons show)
    var starting = false;       // a play() is in progress
    var backAfterHidden = false;
    var fading = null;

    // Pages can't change the volume on iPhones; there it simply starts and stops, without fades.
    var canFade = (function () {
      try { audio.volume = 0.5; var ok = Math.abs(audio.volume - 0.5) < 0.01; audio.volume = 1; return ok; }
      catch (e) { return false; }
    })();

    // Volume glides to `target` over `ms`, timed by the clock so a slow timer can't stretch it.
    function fadeTo(target, ms, then) {
      clearInterval(fading);
      if (!canFade) { if (then) then(); return; }
      var from = audio.volume, began = Date.now();
      fading = setInterval(function () {
        var k = Math.min(1, (Date.now() - began) / ms);
        audio.volume = from + (target - from) * k;
        if (k >= 1) { clearInterval(fading); if (then) then(); }
      }, 30);
    }

    function show() {
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(playing)); });
      if (playing) endNudge();
    }

    // The nudge: if a page opens and sound isn't allowed yet, the floating button says "Tap for
    // music" for a few seconds (once per visit, so it doesn't nag on every page).
    var floatButton = document.querySelector('.music-float');
    var nudgeTimer = null;
    function endNudge() { clearTimeout(nudgeTimer); if (floatButton) floatButton.classList.remove('nudge'); }
    function nudge() {
      if (!floatButton || playing || !wanted || read('sessionStorage', NUDGED)) return;
      write('sessionStorage', NUDGED, '1');
      floatButton.classList.add('nudge');
      nudgeTimer = setTimeout(endNudge, 7000);
    }

    // Try to play. If the browser says "not yet", nothing changes and we wait for a touch.
    function start() {
      if (!wanted || playing || starting || document.hidden) return;
      starting = true;
      if (audio.paused && canFade) audio.volume = 0;
      var result = audio.play();
      function ok() {
        starting = false;
        if (!wanted || document.hidden) { audio.pause(); return; }   // changed their mind meanwhile
        playing = true;
        show();
        stopListening();
        fadeTo(VOLUME, 700);
      }
      function blocked() { starting = false; }
      if (result && result.then) result.then(ok, blocked); else ok();
    }

    // Stop: with a short fade when the visitor presses Pause, at once in every other case.
    function stop(fadeMs) {
      playing = false;
      show();
      if (fadeMs && canFade && !document.hidden) {
        fadeTo(0, fadeMs, function () { if (!playing) audio.pause(); });
      } else {
        clearInterval(fading);
        audio.pause();
      }
    }

    function turnOn() { wanted = true; write('localStorage', OFF, null); start(); }
    function turnOff(fadeMs) { wanted = false; write('localStorage', OFF, '1'); stop(fadeMs); }

    // Carry on from where the last page left off.
    var at = parseFloat(read('sessionStorage', AT)) || 0;
    if (at > 0) {
      audio.addEventListener('loadedmetadata', function () {
        if (at < audio.duration) audio.currentTime = at;
      }, { once: true });
    }

    buttons.forEach(function (b) {
      b.hidden = false;
      b.addEventListener('click', function () { if (playing) turnOff(400); else turnOn(); });
    });
    if (tune) tune.hidden = false;

    // The first touch anywhere starts it (the music buttons handle their own clicks).
    function touched(e) {
      if (e.target && e.target.closest && e.target.closest('.music-btn')) return;
      start();
    }
    function stopListening() {
      TOUCHES.forEach(function (type) { document.removeEventListener(type, touched, true); });
    }
    TOUCHES.forEach(function (type) { document.addEventListener(type, touched, true); });

    // Something else paused it (headphones unplugged, a phone call): show it as stopped.
    audio.addEventListener('pause', function () { if (playing && !document.hidden) { playing = false; show(); } });

    // Hidden (another tab or app, screen locked): stop now; shown again: carry on.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        if (playing || starting) { backAfterHidden = true; stop(0); }
      } else if (backAfterHidden) {
        backAfterHidden = false;
        start();
      }
    });
    // Leaving the page: remember where the tune was if it was playing, then stop.
    addEventListener('pagehide', function () {
      write('sessionStorage', AT, playing || backAfterHidden ? String(audio.currentTime) : null);
      if (playing) stop(0);
    });
    // Back to this page from the browser's back button (restored from memory).
    addEventListener('pageshow', function (e) { if (e.persisted) start(); });

    // Lock screen / notification controls on phones.
    if ('mediaSession' in navigator) {
      try {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: 'Purano Sei Diner Kotha', artist: 'Mon Mela',
          artwork: [{ src: 'icon-512.png', sizes: '512x512', type: 'image/png' }]
        });
        navigator.mediaSession.setActionHandler('play', turnOn);
        navigator.mediaSession.setActionHandler('pause', function () { turnOff(0); });
      } catch (e) { /* older browsers: no lock-screen controls */ }
    }

    // The floating button steps aside while the story's own button is on screen.
    if (storyButton && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        document.documentElement.classList.toggle('head-music-on-screen', entries[0].isIntersecting);
      }).observe(storyButton);
    }

    start();   // works if the browser already allows sound here
    setTimeout(nudge, 1200);   // still silent a moment later: invite the first tap
  });
})();
