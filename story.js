// Home page, "A story of friendship": on wide screens the six pictures sit in one sticky frame,
// and the picture changes as each chapter reaches the middle of the screen.
// Without this file (or on phones) every chapter simply shows its own picture card.
(function () {
  var WIDE = '(min-width: 900px)';

  document.addEventListener('DOMContentLoaded', function () {
    var story = document.querySelector('.story');
    if (!story || !('IntersectionObserver' in window) || !window.matchMedia) return;
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

    // A chapter counts as "current" while it crosses a thin band in the middle of the screen.
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) show(Number(e.target.getAttribute('data-i')));
      });
    }, { rootMargin: '-45% 0px -45% 0px' });

    var wide = window.matchMedia(WIDE);
    function setup() {
      observer.disconnect();
      story.classList.toggle('is-live', wide.matches); // CSS: sticky frame on, inline cards off
      if (!wide.matches) return;
      chapters.forEach(function (c) { observer.observe(c); });
      if (current < 0) show(0);
    }
    setup();
    if (wide.addEventListener) wide.addEventListener('change', setup); else wide.addListener(setup);
  });
})();
