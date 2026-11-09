// Home page, "How it works": on wide screens one phone stays in view (CSS sticky) while the
// steps scroll past. Whichever step crosses the middle of the screen becomes active, and the
// phone shows that step's app screen. Without this file, the phone simply shows the first screen.
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var section = document.querySelector('.how');
    if (!section || !('IntersectionObserver' in window)) return;
    var steps = section.querySelectorAll('.how-step');
    var screens = section.querySelectorAll('.phone-sticky img');
    section.classList.add('js-how'); // turns on the dim/bright styling of steps

    function activate(step) {
      steps.forEach(function (s) { s.classList.toggle('is-active', s === step); });
      var key = step.getAttribute('data-screen');
      screens.forEach(function (img) { img.classList.toggle('is-on', img.getAttribute('data-screen') === key); });
    }

    // A thin band across the middle of the viewport: a step is "current" while it overlaps it.
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) activate(e.target); });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(function (s) { observer.observe(s); });
    activate(steps[0]);
  });
})();
