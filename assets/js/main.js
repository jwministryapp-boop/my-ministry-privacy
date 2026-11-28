function copyWalletText(id, btn) {
  var el = document.getElementById(id);
  if (!el) return;
  var copiedLabel = btn.getAttribute('data-copied') || 'Copied!';
  navigator.clipboard.writeText((el.textContent || el.innerText).trim()).then(function() {
    var old = btn.innerText;
    btn.innerText = copiedLabel;
    setTimeout(function() { btn.innerText = old; }, 2000);
  });
}

function toggleWalletQR(qrId) {
  var el = document.getElementById(qrId);
  if (el) el.classList.toggle('open');
}

function toggleLangDropdown(e) {
  e.stopPropagation();
  var dd = document.getElementById('lang-dropdown');
  if (dd) dd.classList.toggle('open');
}

function toggleMobileMenu() {
  var drawer = document.getElementById('mobile-drawer');
  var iconOpen = document.getElementById('burger-icon-open');
  var iconClose = document.getElementById('burger-icon-close');
  if (!drawer) return;
  var isOpen = drawer.classList.toggle('open');
  if (iconOpen && iconClose) {
    iconOpen.style.display = isOpen ? 'none' : 'block';
    iconClose.style.display = isOpen ? 'block' : 'none';
  }
}

function closeMobileMenu() {
  var drawer = document.getElementById('mobile-drawer');
  var iconOpen = document.getElementById('burger-icon-open');
  var iconClose = document.getElementById('burger-icon-close');
  if (drawer) drawer.classList.remove('open');
  if (iconOpen && iconClose) {
    iconOpen.style.display = 'block';
    iconClose.style.display = 'none';
  }
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
    } else if (mode === 'duo') {
      card.style.display = (theme === 'duo') ? 'flex' : 'none';
    } else if (mode === 'all') {
      card.style.display = (theme === 'ipad' || theme === 'duo') ? 'none' : 'flex';
    } else {
      card.style.display = (theme === mode) ? 'flex' : 'none';
    }
  });
}

function switchScreenshotLanguage(folderName, displayLangName, badgeEl) {
  var prefix = document.body.getAttribute('data-prefix') || '.';
  var encodedFolder = encodeURIComponent(folderName);

  document.querySelectorAll('img[data-shot-file]').forEach(function(img) {
    var file = img.getAttribute('data-shot-file');
    img.src = prefix + '/screenshots/' + encodedFolder + '/' + file;
  });

  var ind = document.getElementById('active-shot-lang-name');
  if (ind) ind.innerText = displayLangName;

  document.querySelectorAll('.loc-badge').forEach(function(b) {
    b.classList.remove('active-shot-lang');
  });
  if (badgeEl) badgeEl.classList.add('active-shot-lang');

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

  document.addEventListener('click', function() {
    var dd = document.getElementById('lang-dropdown');
    if (dd) dd.classList.remove('open');
  });

  // Показываем нижнюю мобильную плашку только после прокрутки первого экрана (360px)
  var stickyBar = document.querySelector('.sticky-mobile-bar');
  if (stickyBar) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 360) {
        stickyBar.classList.add('visible');
      } else {
        stickyBar.classList.remove('visible');
      }
    }, { passive: true });
  }
});

function switchChangelogTab(ver, btn) {
  document.querySelectorAll('.cl-tab').forEach(function(b) {
    b.classList.remove('active');
  });
  if (btn) btn.classList.add('active');
  var p201 = document.getElementById('cl-panel-201');
  var p18 = document.getElementById('cl-panel-18');
  if (p201) p201.style.display = (ver === '201') ? 'grid' : 'none';
  if (p18) p18.style.display = (ver === '18') ? 'grid' : 'none';
}
