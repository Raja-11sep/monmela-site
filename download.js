// Download page helpers. The Download button works without this file; this only adds hints:
//  - iPhone/iPad: explain it's Android-only for now (an APK can't install there).
//  - In-app browsers (Instagram, Facebook...): they often block downloads, so offer "Open in browser".
//  - Checks the APK is really on the site: shows its size, or "coming soon" instead of a broken button.
(function () {
  var ua = navigator.userAgent || '';
  // iPadOS reports itself as a Mac, so also check for a touch screen.
  var isIOS = /iPhone|iPad|iPod/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  // "; wv)" marks any Android WebView (Telegram, many others).
  var inApp = /FBAN|FBAV|FB_IAB|Instagram|LinkedInApp|Snapchat|Line\/|; wv\)/i.test(ua);

  function show(id, visible) {
    var el = document.getElementById(id);
    if (el) el.hidden = !visible;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var apk = document.getElementById('apk');
    if (!apk) return; // after launch the page redirects to Google Play instead

    if (isIOS) {
      show('get', false);
      show('ios', true);
      return;
    }
    if (inApp) show('inapp', true);

    // HEAD = ask for the file's details without downloading it.
    if (window.fetch) {
      fetch(apk.href, { method: 'HEAD', cache: 'no-store' }).then(function (res) {
        if (res.status === 404) {
          show('get', false);
          show('soon', true);
          return;
        }
        var bytes = Number(res.headers.get('content-length'));
        if (res.ok && bytes > 0) {
          document.getElementById('apk-size').textContent = ' · ' + Math.round(bytes / 1048576) + ' MB';
        }
      }).catch(function () { /* offline or blocked: leave the button as it is */ });
    }

    // Copy link: clipboard API where allowed, otherwise select the visible link for a manual copy.
    var copy = document.getElementById('copy');
    var link = document.getElementById('page-link');
    if (copy && link) {
      copy.addEventListener('click', function () {
        function done() {
          copy.innerHTML = '<span class="l" lang="en">Link copied</span><span class="l" lang="bn">লিংক কপি হয়েছে</span>';
        }
        function manual() {
          link.focus();
          link.select();
          try { if (document.execCommand('copy')) done(); } catch (e) { /* user can long-press to copy */ }
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(link.value).then(done, manual);
        } else {
          manual();
        }
      });
    }
  });
})();
