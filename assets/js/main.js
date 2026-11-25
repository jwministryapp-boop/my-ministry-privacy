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

function toggleWalletQR(qrId) {
  var el = document.getElementById(qrId);
  if (el) el.classList.toggle('open');
}

function filterScreenshots(mode, btn) {
  document.querySelectorAll('.filter-btn').forEach(function(b) {
    b.classList.remove('active');
  });
  btn.classList.add('active');

  document.querySelectorAll('.shot-card').forEach(function(card) {
    var theme = card.getAttribute('data-theme-shot');
    if (mode === 'ipad') {
      card.style.display = (theme === 'ipad') ? 'flex' : 'none';
    } else if (mode === 'all') {
      card.style.display = (theme === 'ipad') ? 'none' : 'flex';
    } else {
      card.style.display = (theme === mode) ? 'flex' : 'none';
    }
  });
}

function switchScreenshotLanguage(folderName, displayLangName, badgeEl) {
  var prefix = document.body.getAttribute('data-prefix') || '.';
  var encodedFolder = encodeURIComponent(folderName);

  // Обновляем 8 карточек iPhone
  document.querySelectorAll('img[data-shot-file]').forEach(function(img) {
    var file = img.getAttribute('data-shot-file');
    img.src = prefix + '/screenshots/' + encodedFolder + '/' + file;
  });

  // Обновляем индикатор выбранного языка скриншотов
  var ind = document.getElementById('active-shot-lang-name');
  if (ind) ind.innerText = displayLangName;

  // Подсвечиваем активный бейдж
  document.querySelectorAll('.loc-badge').forEach(function(b) {
    b.classList.remove('active-shot-lang');
  });
  if (badgeEl) badgeEl.classList.add('active-shot-lang');

  // Плавно прокручиваем к галерее скриншотов, если кликнули снизу
  var screensSec = document.getElementById('screens');
  if (screensSec && badgeEl) {
    screensSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.lang-pill').forEach(function(el) {
    el.addEventListener('click', function() {
      try { sessionStorage.setItem('jw_lang_selected', '1'); } catch(e) {}
    });
  });
});
