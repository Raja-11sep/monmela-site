// Download page helpers. The Download button works without this file; this only adds hints:
//  - iPhone/iPad: explain it's Android-only for now (an APK can't install there).
//  - In-app browsers (Instagram, Facebook...): they often block downloads, so offer "Open in browser".
//  - Checks the APK is really on the site: shows its size, or "coming soon" instead of a broken button.
//  - Google Play test: turns the two tester steps into one guided button.
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

  // Google Play test: one big button that walks through the two steps. The links open in a new
  // tab, so this page stays open and moves on to the next step; the step is remembered (on this
  // phone only) for when someone comes back later.
  function setupFlow() {
    var flow = document.getElementById('flow');
    var btn = document.getElementById('flow-btn');
    if (!flow || !btn) return;
    var KEY = 'mm_tester_step';
    function load() { try { return Number(localStorage.getItem(KEY)) || 1; } catch (e) { return 1; } }
    function save(n) { try { localStorage.setItem(KEY, String(n)); } catch (e) { /* private mode: fine */ } }

    // 1 = join the group, 2 = become a tester, 3 = both done (button reopens the tester page).
    function render(n) {
      flow.classList.add('js-flow'); // CSS hides the two small buttons
      btn.hidden = false;
      btn.href = n === 1 ? btn.getAttribute('data-group') : btn.getAttribute('data-join');
      var en = btn.querySelector('[lang="en"]');
      var bn = btn.querySelector('[lang="bn"]');
      en.textContent = en.getAttribute('data-en' + n);
      bn.textContent = bn.getAttribute('data-bn' + n);
      document.getElementById('step1').className = n > 1 ? 'done' : 'current';
      document.getElementById('step2').className = n > 2 ? 'done' : (n === 2 ? 'current' : '');
      show('flow-hint', n < 3);
      show('flow-done', n === 3);
    }

    var step = load();
    render(step);
    btn.addEventListener('click', function () {
      step = Math.min(step + 1, 3);
      save(step);
      // After the browser has followed the link (it uses the address at click time).
      setTimeout(function () { render(step); }, 300);
    });
    var restart = document.getElementById('flow-restart');
    if (restart) {
      restart.addEventListener('click', function () {
        step = 1;
        save(1);
        render(1);
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var apk = document.getElementById('apk');
    if (!apk) return; // after launch the page redirects to Google Play instead

    if (isIOS) {
      show('get', false);
      show('flow', false); // Google Play is Android-only too
      show('ios', true);
      return;
    }
    if (inApp) show('inapp', true);
    setupFlow();

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
