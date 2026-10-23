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
