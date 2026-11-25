function copyWalletText(id, btn) {
  var el = document.getElementById(id);
  if (!el) return;
  var copiedLabel = btn.getAttribute('data-copied') || 'Copied!';
  navigator.clipboard.writeText(el.innerText).then(function() {
    var old = btn.innerText;
    btn.innerText = copiedLabel;
    setTimeout(function() { btn.innerText = old; }, 2000);
  });
}

function filterScreenshots(mode, btn) {
  document.querySelectorAll('.filter-btn').forEach(function(b) {
    b.classList.remove('active');
  });
  btn.classList.add('active');
  document.querySelectorAll('.shot-card').forEach(function(card) {
    var theme = card.getAttribute('data-theme-shot');
    if (mode === 'all' || theme === mode) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.lang-pill').forEach(function(el) {
    el.addEventListener('click', function() {
      try { sessionStorage.setItem('jw_lang_selected', '1'); } catch(e) {}
    });
  });
});
