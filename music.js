// Site music: our own recording of the Purano Sei Diner Kotha tune, on every page.
// It's on by default, but browsers never let a page start sound by itself: it starts with the
// visitor's first tap, click or key press anywhere on the page. On the next pages of the site it
// can usually start straight away (Chrome allows that once you've interacted with the site), and
// it carries on from where it was. "Pause music" turns it off, and that choice is remembered on
// every page until they turn it on again. The track only downloads when it first plays.
// Without JavaScript there's no music and no buttons.
(function () {
  var VOLUME = 0.6;
  var OFF = 'mm-music-off';      // localStorage: the visitor turned the music off
  var AT = 'mm-music-at';        // sessionStorage: where the tune was when they left the last page

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
    var audible = false;         // playing (or fading in), as far as the buttons are concerned
    var hiddenWhilePlaying = false;
    var fading = null;

    // Volume steps toward `target`, then `then` runs. (iPhones ignore volume changes from a
    // page, so there it simply starts and stops.)
    function fadeTo(target, then) {
      clearInterval(fading);
      fading = setInterval(function () {
        var step = target > audio.volume ? 0.04 : -0.04;
        var next = audio.volume + step;
        if ((step > 0 && next >= target) || (step < 0 && next <= target)) {
          audio.volume = target;
          clearInterval(fading);
          if (then) then();
        } else {
          audio.volume = next;
        }
      }, 40);
    }

    function show() {
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(audible)); });
    }

    function play() {
      if (audible) return;
      audible = true;
      show();
      if (audio.paused) audio.volume = 0;
      var started = audio.play();
      if (started && started.then) {
        started.then(function () { fadeTo(VOLUME); }, function () { audible = false; show(); });   // not allowed yet: wait for a tap
      } else {
        fadeTo(VOLUME);
      }
    }
    function pause() {
      audible = false;
      show();
      fadeTo(0, function () { if (!audible) audio.pause(); });
    }

    // Carry on from where the last page left off.
    var saved = read('sessionStorage', AT);
    var carryOn = saved !== null;
    var at = parseFloat(saved) || 0;
    if (at > 0) {
      audio.addEventListener('loadedmetadata', function () {
        if (at < audio.duration) audio.currentTime = at;
      }, { once: true });
    }

    buttons.forEach(function (b) {
      b.hidden = false;
      b.addEventListener('click', function () {
        if (audible) { write('localStorage', OFF, '1'); pause(); }
        else { write('localStorage', OFF, null); play(); }
      });
    });
    if (tune) tune.hidden = false;

    // On by default: start with the first tap, click or key anywhere (the buttons handle their own).
    function firstTouch(e) {
      if (e.target.closest && e.target.closest('.music-btn')) return;
      document.removeEventListener('click', firstTouch, true);
      document.removeEventListener('keydown', firstTouch, true);
      if (read('localStorage', OFF) !== '1') play();
    }
    if (read('localStorage', OFF) !== '1') {
      document.addEventListener('click', firstTouch, true);
      document.addEventListener('keydown', firstTouch, true);
      if (carryOn) play();       // it was playing on the last page: try to carry straight on
    }

    // Quiet while the tab is in the background; back when it returns.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden && audible) { hiddenWhilePlaying = true; pause(); }
      else if (!document.hidden && hiddenWhilePlaying) { hiddenWhilePlaying = false; play(); }
    });
    // Leaving the page: remember where the tune was, if it was playing.
    addEventListener('pagehide', function () {
      write('sessionStorage', AT, audible || hiddenWhilePlaying ? String(audio.currentTime) : null);
    });

    // The floating button steps aside while the story's own button is on screen.
    if (storyButton && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        document.documentElement.classList.toggle('head-music-on-screen', entries[0].isIntersecting);
      }).observe(storyButton);
    }
  });
})();
