// Adda page helper (/adda?id=…). The "Get the app" button works without this file; this adds:
//  - Android: an "Open in the app" button for the shared table. It's an intent:// link, so
//    Chrome opens the app if it's installed, and Google Play (data-fallback) if not.
//  - iPhone/iPad: explain it's Android-only for now.
(function () {
  var ua = navigator.userAgent || '';
  var isIOS = /iPhone|iPad|iPod/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var isAndroid = /Android/i.test(ua);

  function show(id, visible) {
    var el = document.getElementById(id);
    if (el) el.hidden = !visible;
  }

  // The id comes from the link, so accept only a real table id (a uuid) before using it.
  var id = (new URLSearchParams(location.search).get('id') || '').toLowerCase();
  var validId = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id);

  document.addEventListener('DOMContentLoaded', function () {
    show('ios', isIOS);
    if (!isAndroid || !validId) return;

    var btn = document.getElementById('open-btn');
    var host = btn.getAttribute('data-host');
    var fallback = encodeURIComponent(btn.getAttribute('data-fallback'));
    // intent://<host>/adda?id=…#Intent;scheme=https;package=<app>;S.browser_fallback_url=…;end
    btn.href = 'intent://' + host + '/adda?id=' + id +
      '#Intent;scheme=https;package=com.monmela.app;S.browser_fallback_url=' + fallback + ';end';
    show('open', true);
    show('open-hint', true);
    show('get', false); // the big button already covers "no app yet"
  });
})();
