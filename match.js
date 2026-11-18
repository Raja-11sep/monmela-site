// "Matched by what you share": the Venn diagram acts out a match. Two circles, you and someone
// else, each holding six answers, trace themselves in and drift together. Where they overlap
// the lens fills with marigold, the answers you both gave fly in from both sides and merge, and
// the match % counts up. "Try someone else" plays it backwards, swaps in the next person and
// plays it again. With reduced motion each result simply appears. Without this file the figure
// stays as built (the first person).
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var END = 4.0;                    // seconds in the whole match
  var MEET = 0.9;                   // the moment the circles start moving (also where "Try someone else" rewinds to)
  var BN_DIGITS = '০১২৩৪৫৬৭৮৯';

  function clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function lerp(a, b, k) { return a + (b - a) * k; }
  function ease(x) { return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  function easeOut(x) { return 1 - Math.pow(1 - x, 3); }
  function backOut(x) { var c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }
  function bengali(n) { return String(n).replace(/[0-9]/g, function (d) { return BN_DIGITS[d]; }); }

  function el(name, attrs, parent) {
    var node = document.createElementNS(NS, name);
    for (var k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }

  // One piece of text in both languages; the page's CSS shows the one being read.
  function Words(parent, en, bn, cls) {
    this.en = el('text', { 'class': 'l ' + cls, lang: 'en' }, parent);
    this.bn = el('text', { 'class': 'l ' + cls, lang: 'bn' }, parent);
    this.en.textContent = en;
    this.bn.textContent = bn;
  }
  Words.prototype.at = function (x, y, opacity) {
    [this.en, this.bn].forEach(function (t) {
      t.setAttribute('x', x.toFixed(1));
      t.setAttribute('y', y.toFixed(1));
      t.setAttribute('opacity', opacity.toFixed(3));
    });
  };
  Words.prototype.mark = function (cls, on) {
    this.en.classList.toggle(cls, on);
    this.bn.classList.toggle(cls, on);
  };
  Words.prototype.say = function (en, bn) { this.en.textContent = en; this.bn.textContent = bn; };

  document.addEventListener('DOMContentLoaded', function () {
    var fig = document.querySelector('.venn[data-venn]');
    if (!fig || !window.requestAnimationFrame) return;
    var data = JSON.parse(fig.getAttribute('data-venn'));
    var svg = fig.querySelector('svg');
    var caption = fig.querySelector('figcaption');
    var next = fig.querySelector('.venn-next');
    var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var person = 0;

    // ---- the scene, drawn fresh (the static copy is only for when this file doesn't run)
    svg.textContent = '';
    var clip = el('circle', { cy: 170 }, el('clipPath', { id: 'venn-left' }, el('defs', {}, svg)));
    var you = new Words(svg, 'You', 'আপনি', 'who-t');
    var ringL = el('circle', { 'class': 'ring', cy: 170 }, svg);
    var ringR = el('circle', { 'class': 'ring', cy: 170 }, svg);
    var lens = el('circle', { cy: 170, 'clip-path': 'url(#venn-left)', fill: '#F5B023' }, svg);
    var mineLayer = el('g', {}, svg);
    var them = el('g', { 'class': 'them' }, svg);
    var sparkLayer = el('g', {}, svg);
    var scoreText = new Words(el('g', { 'class': 'score' }, svg), '', '', '');
    var scoreBox = scoreText.en.parentNode;

    var mine = data.you.map(function (w) { return { words: new Words(mineLayer, w[0], w[1], 't'), en: w[0] }; });
    var theirs = [], who = null, sparks = [];
    for (var k = 0; k < 3; k++) sparks.push(el('circle', { 'class': 'spark', r: 0, opacity: 0 }, sparkLayer));

    // Who is in which place for the current person: shared answers get an overlap slot (0-2),
    // the rest a side slot (0-2), in the order they sit in the circle.
    function cast() {
      var p = data.people[person];
      them.textContent = '';
      who = new Words(them, p.who[0], p.who[1], 'who-t');
      theirs = p.items.map(function (w) { return { words: new Words(them, w[0], w[1], 't'), en: w[0] }; });
      [mine, theirs].forEach(function (list) {
        var side = 0;
        list.forEach(function (item, i) {
          item.row = i;
          item.slot = p.shared.indexOf(item.en);
          if (item.slot < 0) item.side = side++;
        });
      });
      caption.querySelector('[lang="en"]').textContent = p.caption[0];
      caption.querySelector('[lang="bn"]').textContent = p.caption[1];
    }
    // the "who" labels use the same look as the static figure
    function styleWho(w) { [w.en, w.bn].forEach(function (t) { t.style.fill = '#fff'; t.style.fontWeight = 600; t.style.fontSize = '15px'; }); }

    // ---- the picture at moment t (seconds)
    function draw(t) {
      var p = data.people[person];
      var meet = ease(clamp((t - MEET) / 1.2));
      var cxL = lerp(110, 170, meet), cxR = lerp(330, 270, meet), r = lerp(98, 120, meet);
      var traced = easeOut(clamp(t / 0.9)), round = 2 * Math.PI * r;

      [[ringL, cxL], [ringR, cxR]].forEach(function (ring) {
        ring[0].setAttribute('cx', ring[1].toFixed(1));
        ring[0].setAttribute('r', r.toFixed(1));
        ring[0].setAttribute('stroke-dasharray', round.toFixed(1));
        ring[0].setAttribute('stroke-dashoffset', (round * (1 - traced)).toFixed(1));
        ring[0].setAttribute('fill-opacity', traced.toFixed(3));
      });
      clip.setAttribute('cx', cxL.toFixed(1)); clip.setAttribute('r', r.toFixed(1));
      lens.setAttribute('cx', cxR.toFixed(1)); lens.setAttribute('r', r.toFixed(1));
      lens.setAttribute('opacity', clamp((2 * r - (cxR - cxL)) / 140).toFixed(3));

      var named = clamp((t - 0.2) / 0.5);
      you.at(lerp(cxL, cxL - 68, meet), 30, named);
      who.at(lerp(cxR, cxR + 68, meet), 30, named);

      var spread = ease(clamp((t - 1.5) / 0.9));
      function place(item, cx, outward, isMine) {
        var shown = clamp((t - 0.35 - item.row * 0.05) / 0.4);
        var homeY = 104 + item.row * 24;
        if (item.slot < 0) {                          // only theirs: settle to the side
          item.words.at(cx + outward * spread, lerp(homeY, 150 + item.side * 26, spread), shown);
          item.words.mark('landed', false);
          return;
        }
        var fly = ease(clamp((t - (1.7 + item.slot * 0.32)) / 0.85));
        var x = lerp(cx, 220, fly), y = lerp(homeY, 128 + item.slot * 26, fly) - Math.sin(Math.PI * fly) * 16;
        // the two copies meet in the overlap; theirs fades into yours
        item.words.at(x, y, isMine ? shown : shown * (1 - clamp((fly - 0.75) / 0.25)));
        item.words.mark('landed', fly >= 1);
      }
      mine.forEach(function (item) { place(item, cxL, -68, true); });
      theirs.forEach(function (item) { place(item, cxR, 68, false); });

      sparks.forEach(function (spark, k) {         // a little ring of light where each pair lands
        var s = clamp((t - (1.7 + k * 0.32 + 0.85)) / 0.5);
        spark.setAttribute('cx', 220);
        spark.setAttribute('cy', 123 + k * 26);
        spark.setAttribute('r', (4 + 22 * s).toFixed(1));
        spark.setAttribute('opacity', s > 0 && s < 1 ? (0.9 * (1 - s)).toFixed(3) : 0);
      });

      var counted = Math.round(easeOut(clamp((t - 2.9) / 1.0)) * p.score);
      scoreText.say(counted + '% match', bengali(counted) + '% মিল');
      var pop = 0.6 + 0.4 * backOut(clamp((t - 2.85) / 0.45));
      scoreBox.setAttribute('transform', 'translate(220 225) scale(' + pop.toFixed(3) + ') translate(-220 -225)');
      scoreText.at(220, 230, clamp((t - 2.85) / 0.2));

      fig.classList.toggle('told', t >= 3.5);
    }

    // ---- playing it: t runs toward `target` at `speed`, then `then` runs
    var t = 0, target = 0, speed = 1, frame = 0, last = 0, then = null;
    function step(now) {
      var dir = target >= t ? 1 : -1;
      t += dir * speed * Math.min(0.05, (now - last) / 1000);
      last = now;
      if ((dir > 0 && t >= target) || (dir < 0 && t <= target)) {
        t = target; draw(t); frame = 0;
        var done = then; then = null;
        if (done) done();
        return;
      }
      draw(t);
      frame = requestAnimationFrame(step);
    }
    function playTo(to, rate, done) {
      target = to; speed = rate; then = done || null;
      if (!frame) { last = performance.now(); frame = requestAnimationFrame(step); }
    }

    cast();
    styleWho(you);
    styleWho(who);
    fig.classList.add('live');

    next.hidden = false;
    next.addEventListener('click', function () {
      if (still) {
        person = (person + 1) % data.people.length;
        cast(); styleWho(who); draw(END);
        return;
      }
      next.disabled = true;
      playTo(MEET, 3, function () {                   // unmatch, quickly
        them.style.opacity = 0;
        setTimeout(function () {
          person = (person + 1) % data.people.length;
          cast(); styleWho(who); draw(t);
          them.style.opacity = 1;
          playTo(END, 1, function () { next.disabled = false; });
        }, 300);
      });
    });

    if (still || fig.getBoundingClientRect().top < innerHeight * 0.8) {
      t = END; draw(END);                           // already on screen, or no motion wanted
      return;
    }
    draw(0);
    var seen = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { seen.disconnect(); playTo(END, 1); }
    }, { threshold: 0.45 });
    seen.observe(fig);
  });
})();
