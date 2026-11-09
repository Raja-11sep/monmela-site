// Home page, "What do you love?": the interest chips can be tapped on and off, like in the app,
// and the line under them counts how many are picked (in English and Bengali digits).
// Without this file the chips simply show the starting picks.
(function () {
  var BN_DIGITS = '০১২৩৪৫৬৭৮৯';
  function bengali(n) {
    return String(n).replace(/[0-9]/g, function (d) { return BN_DIGITS[d]; });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var board = document.querySelector('.chip-board');
    if (!board) return;
    var chips = board.querySelectorAll('.chip');
    var en = document.querySelector('.chip-count [lang="en"] .n');
    var bn = document.querySelector('.chip-count [lang="bn"] .n');

    function updateCount() {
      var picked = board.querySelectorAll('.chip[aria-pressed="true"]').length;
      if (en) en.textContent = picked;
      if (bn) bn.textContent = bengali(picked);
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var on = chip.getAttribute('aria-pressed') === 'true';
        chip.setAttribute('aria-pressed', String(!on));
        updateCount();
      });
    });
  });
})();
