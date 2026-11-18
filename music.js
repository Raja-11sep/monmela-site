// Story music: "Play with music" plays our own recording of the Purano Sei Diner Kotha tune.
// Browsers never let a page start sound by itself, so it only plays after a tap, and the file
// is only downloaded then (preload="none"). While it's on, the music fades out when the story
// scrolls away or the tab is hidden, and fades back in when the story is on screen again.
// Without JavaScript the button stays hidden.
(function () {
  var VOLUME = 0.8;

  document.addEventListener('DOMContentLoaded', function () {
    var story = document.querySelector('.story');
    var audio = story && story.querySelector('.story-audio');
    if (!audio || typeof audio.play !== 'function') return;
    var buttons = story.querySelectorAll('.music-btn');      // under the title, and the floating copy
    var headButton = story.querySelector('.story-head .music-btn');
    var tune = story.querySelector('.music-tune');
    var on = false;            // the visitor turned the music on
    var storyOnScreen = false;
    var headOnScreen = true;
    var fading = null;

    // Volume steps toward `target`; `then` runs when it gets there. (iPhones ignore volume
    // changes from a page, so there the music simply starts and stops.)
    function fadeTo(target, then) {
      clearInterval(fading);
      fading = setInterval(function () {
        var step = target > audio.volume ? 0.05 : -0.05;
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

    function play() {
      if (!audio.paused && audio.volume === VOLUME) return;
      if (audio.paused) audio.volume = 0;
      var started = audio.play();
      if (started && started.catch) started.catch(function () { on = false; show(); });
      fadeTo(VOLUME);
    }
    function pause() { fadeTo(0, function () { audio.pause(); }); }

    // Should it be playing right now?
    function update() {
      if (on && storyOnScreen && !document.hidden) play(); else pause();
      story.classList.toggle('float-on', on && storyOnScreen && !headOnScreen);
    }
    function show() {
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(on)); });
      update();
    }

    buttons.forEach(function (b) {
      b.hidden = false;
      b.addEventListener('click', function () { on = !on; show(); });
    });
    if (tune) tune.hidden = false;

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        storyOnScreen = entries[0].isIntersecting;
        update();
      }).observe(story);
      new IntersectionObserver(function (entries) {
        headOnScreen = entries[0].isIntersecting;
        update();
      }).observe(headButton);
    } else {
      storyOnScreen = true;
    }
    document.addEventListener('visibilitychange', update);
  });
})();
