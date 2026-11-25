// Home page, "A story of friendship".
//  - Wide screens: the pictures sit in one sticky frame, and the picture changes as each
//    chapter reaches the middle of the screen.
//  - Phones: the chapters are a row of cards to swipe through (CSS); this adds the dots under the
//    row, which follow the swipe and jump to a chapter when tapped.
// Without this file every chapter simply shows its own picture card.
(function () {
  var WIDE = '(min-width: 900px)';

  document.addEventListener('DOMContentLoaded', function () {
    var story = document.querySelector('.story');
    if (!story || !('IntersectionObserver' in window) || !window.matchMedia) return;
    var row = story.querySelector('.story-chapters');
    var chapters = story.querySelectorAll('.chapter');
    var pics = story.querySelectorAll('.sf-pic');
    var dots = story.querySelectorAll('.sf-dots span');
    var current = -1;

    function show(i) {
      if (i === current) return;
      current = i;
      for (var n = 0; n < chapters.length; n++) {
        var on = n === i;
        chapters[n].classList.toggle('is-current', on);
        if (pics[n]) pics[n].classList.toggle('on', on);
        if (dots[n]) dots[n].classList.toggle('on', on);
      }
    }

    // Wide: a chapter counts as "current" while it crosses a thin band in the middle of the screen.
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) show(Number(e.target.getAttribute('data-i')));
      });
    }, { rootMargin: '-45% 0px -45% 0px' });

    // Phones: one dot per chapter under the swipe row.
    var bar = document.createElement('div');
    bar.className = 'story-dots';
    var swipeDots = [].map.call(chapters, function (chapter, i) {
      var dot = document.createElement('button');
      dot.type = 'button';
      dot.setAttribute('aria-label', 'Chapter ' + (i + 1));
      dot.addEventListener('click', function () {
        row.scrollTo({ left: chapter.offsetLeft - row.offsetLeft - parseFloat(getComputedStyle(row).paddingLeft), behavior: 'smooth' });
      });
      bar.appendChild(dot);
      return dot;
    });
    row.after(bar);
    var shownCard = -1, queued = false;
    function followSwipe() {
      queued = false;
      var step = chapters.length > 1 ? chapters[1].offsetLeft - chapters[0].offsetLeft : 1;
      var i = Math.max(0, Math.min(chapters.length - 1, Math.round(row.scrollLeft / step)));
      if (i === shownCard) return;
      shownCard = i;
      swipeDots.forEach(function (d, n) {
        d.classList.toggle('on', n === i);
        if (n === i) d.setAttribute('aria-current', 'step'); else d.removeAttribute('aria-current');
      });
    }
    row.addEventListener('scroll', function () {
      if (!queued) { queued = true; requestAnimationFrame(followSwipe); }
    }, { passive: true });

    // Nov 2026: wide screens show the three chapters side by side (CSS), so the sticky frame
    // (is-live) is no longer switched on; only the phone's swipe dots are kept.
    followSwipe();
  });
})();
