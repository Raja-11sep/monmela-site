// Language switch: shows the English or Bengali copy of the page and remembers the choice.
(function () {
  var KEY = 'monmela-lang';
  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  // ?lang=bn in the link wins (handy for sharing), then the saved choice, then the phone's language.
  var fromUrl = new URLSearchParams(location.search).get('lang');
  var lang = fromUrl || saved() || ((navigator.language || '').toLowerCase().indexOf('bn') === 0 ? 'bn' : 'en');
  if (lang !== 'bn') lang = 'en';

  function apply(l) {
    document.documentElement.setAttribute('data-lang', l);
    document.documentElement.lang = l;
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.lang === l));
    });
    var t = document.querySelector('meta[name="title-' + l + '"]');
    if (t) document.title = t.content;
  }
  apply(lang);
  document.addEventListener('DOMContentLoaded', function () {
    apply(lang);
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.addEventListener('click', function () { lang = b.dataset.lang; save(lang); apply(lang); });
    });
  });
})();

// Top bar: .scrolled once the page has moved (the capsule then floats over the content), the link
// of the section being read lit (.on), and --read (0 to 1) for the line along its bottom edge.
// Section links only point within the page on the home page, so elsewhere nothing is lit.
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var bar = document.querySelector('.top');
    if (!bar) return;
    var inner = bar.querySelector('.top-inner');
    var links = [].slice.call(bar.querySelectorAll('.top-nav a[href^="#"]'));
    var sections = links.map(function (a) {
      var heading = document.getElementById(a.getAttribute('href').slice(1));
      return heading && (heading.closest('section') || heading);
    });
    var queued = false;

    function update() {
      queued = false;
      var y = window.scrollY, room = document.documentElement.scrollHeight - innerHeight;
      bar.classList.toggle('scrolled', y > 8);
      inner.style.setProperty('--read', room > 0 ? Math.min(1, y / room).toFixed(4) : '0');
      // The section crossing a line a third of the way down the screen is the one being read.
      var line = innerHeight * 0.35, current = -1;
      sections.forEach(function (sec, i) {
        if (!sec) return;
        var r = sec.getBoundingClientRect();
        if (r.top <= line && r.bottom > line) current = i;
      });
      links.forEach(function (a, i) {
        a.classList.toggle('on', i === current);
        if (i === current) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
      });
    }
    function queue() { if (!queued) { queued = true; requestAnimationFrame(update); } }
    addEventListener('scroll', queue, { passive: true });
    addEventListener('resize', queue);
    update();
  });
})();
