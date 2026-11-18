// Home page motion, in three places (styles: the "motion" part of style.css):
//  1. How it works: a kantha thread sews from step to step; each number lights up like a mela bulb
//     and its phone wakes up.
//  2. Adda Tables: the two cards are dealt onto the table, then the front card acts out asking for
//     a seat (tap, "request sent", "you're in") over and over while it's on screen.
//  3. Inside the app: on wide screens the five phones start as a fanned hand of cards and are laid
//     out in a row as you scroll; on narrower screens they rise in one after another.
// Plus: phones tilt toward the mouse pointer.
// With reduced motion, or without this file, everything simply shows in its final state.
(function () {
  if (!window.matchMedia || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!('IntersectionObserver' in window)) return;

  // A start state is only set while the element is still below the fold, so nobody already
  // looking at it sees it vanish and come back.
  function belowFold(el) { return el.getBoundingClientRect().top > innerHeight * 0.8; }

  // Calls fn once, when el is `share` (0 to 1) visible.
  function whenSeen(el, share, fn) {
    var seen = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { seen.disconnect(); fn(); }
    }, { threshold: share });
    seen.observe(el);
  }

  function clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function easeInOut(x) { return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }

  // 1. How it works: light the steps in order, one at a time, up to the furthest step on screen;
  //    CSS sews the thread on after each. On wide screens all four are on screen together, so
  //    they light one after another; in the phone's swipeable row each lights as it's swiped in.
  function howItWorks() {
    var row = document.querySelector('.how-row');
    if (!row || !belowFold(row)) return;
    var steps = [].slice.call(row.querySelectorAll('.how-item'));
    var furthest = -1, next = 0, busy = false;
    row.classList.add('armed');

    function lightNext() {
      if (next > furthest) { busy = false; return; }
      busy = true;
      steps[next++].classList.add('lit');
      setTimeout(lightNext, 780);
    }
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        furthest = Math.max(furthest, steps.indexOf(e.target));
        seen.unobserve(e.target);
      });
      if (!busy) { busy = true; setTimeout(lightNext, 150); }
      if (next >= steps.length) seen.disconnect();
    }, { threshold: 0.35 });
    steps.forEach(function (step) { seen.observe(step); });
  }

  // 2. Adda Tables: deal the cards, then loop the little story while the cards are on screen.
  function addaTables() {
    var section = document.querySelector('.adda');
    var art = section && section.querySelector('.adda-art');
    if (!art) return;
    // [state, how long it lasts in ms]. "" is the card as it is: "Ask for a seat".
    var STORY = [['', 2200], ['aim', 550], ['press', 220], ['wait', 1900], ['in', 3800]];
    var step = 0, timer = null;

    function next() {
      var s = STORY[step];
      if (s[0]) section.setAttribute('data-state', s[0]); else section.removeAttribute('data-state');
      step = (step + 1) % STORY.length;
      timer = setTimeout(next, s[1]);
    }
    function stop() { clearTimeout(timer); timer = null; step = 0; section.removeAttribute('data-state'); }

    function startStory() {
      new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { if (!timer) next(); } else stop();
      }, { threshold: 0.4 }).observe(art);
    }

    if (belowFold(art)) {
      art.classList.add('armed');
      whenSeen(art, 0.35, function () {
        art.classList.add('dealt');
        setTimeout(startStory, 1300);         // let the cards land first
      });
    } else {
      startStory();
    }
  }

  // 3. Inside the app.
  function insideTheApp() {
    var row = document.querySelector('.tour-row');
    if (!row) return;
    var items = [].slice.call(row.querySelectorAll('.tour-item'));
    var wide = matchMedia('(min-width: 1101px)');
    var offsets = [], near = false, queued = false;

    items.forEach(function (item, i) { item.style.setProperty('--i', i); });

    // How far each phone is from the middle of the row, laid out (offsetLeft ignores transforms).
    function measure() {
      var middle = row.offsetWidth / 2;
      offsets = items.map(function (item) { return middle - (item.offsetLeft - row.offsetLeft + item.offsetWidth / 2); });
    }

    // Scroll position -> how fanned the hand is: fully fanned with the row's top near the bottom
    // of the screen, laid out flat by the time it's a fifth of the way down.
    function draw() {
      queued = false;
      var top = row.getBoundingClientRect().top;
      var laid = easeInOut(clamp((innerHeight * 0.95 - top) / (innerHeight * 0.75)));
      var fan = 1 - laid, middle = (items.length - 1) / 2;
      items.forEach(function (item, i) {
        var c = i - middle;                    // -2 .. 2, from the leftmost card to the rightmost
        item.style.transform = fan < 0.001 ? '' :
          'translate(' + (offsets[i] * 0.9 * fan).toFixed(1) + 'px,' + (40 * fan).toFixed(1) + 'px) ' +
          'rotate(' + (c * 10 * fan).toFixed(2) + 'deg) scale(' + (1 - 0.08 * fan).toFixed(3) + ')';
        item.style.setProperty('--cap', clamp((laid - 0.78) / 0.22).toFixed(3));
      });
    }
    function queue() { if (near && !queued) { queued = true; requestAnimationFrame(draw); } }

    // Only follow the scroll while the row is near the screen.
    new IntersectionObserver(function (entries) {
      near = entries[0].isIntersecting;
      queue();
    }, { rootMargin: '300px 0px' }).observe(row);
    addEventListener('scroll', queue, { passive: true });

    var risen = false;
    function setup() {
      if (wide.matches) {
        row.classList.remove('armed', 'in');
        row.classList.add('fan');
        measure();
        draw();
      } else {
        row.classList.remove('fan');
        items.forEach(function (item) { item.style.transform = ''; item.style.removeProperty('--cap'); });
        if (!risen && belowFold(row)) {
          row.classList.add('armed');
          whenSeen(row, 0.25, function () { row.classList.add('in'); });
        }
        risen = true;
      }
    }
    setup();
    addEventListener('resize', function () { if (wide.matches) { measure(); queue(); } });
    if (wide.addEventListener) wide.addEventListener('change', setup); else wide.addListener(setup);
    // Fonts and images can shift the layout a little after load.
    addEventListener('load', function () { if (wide.matches) { measure(); draw(); } });
  }

  // Phones lean toward the pointer, with a glint that follows it (mouse and trackpad only).
  function tilt() {
    if (!matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    document.querySelectorAll('.how-item .phone, .tour-item .phone').forEach(function (phone) {
      phone.addEventListener('pointerenter', function () {
        phone.style.transition = 'transform .15s linear';
        phone.classList.add('tilting');
      });
      phone.addEventListener('pointermove', function (e) {
        var r = phone.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        phone.style.transform = 'perspective(900px) translateY(-8px) rotateY(' + (x * 14).toFixed(2) +
          'deg) rotateX(' + (-y * 10).toFixed(2) + 'deg)';
        phone.style.setProperty('--gx', ((x + 0.5) * 100).toFixed(1) + '%');
        phone.style.setProperty('--gy', ((y + 0.5) * 100).toFixed(1) + '%');
      });
      phone.addEventListener('pointerleave', function () {
        phone.style.transition = 'transform .6s cubic-bezier(.2, .9, .25, 1)';
        phone.style.transform = '';
        phone.classList.remove('tilting');
        setTimeout(function () { phone.style.transition = ''; }, 650);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    howItWorks();
    addaTables();
    insideTheApp();
    tilt();
  });
})();
