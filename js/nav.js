(function() {
  var nav = `
  <header class="site-header">
    <div class="container">
      <p class="site-eyebrow">Sami 純人工</p>
      <h1 class="site-name"><a href="/index.html">寫在掌心的領悟</a></h1>
      <p class="site-tagline"><a href="/about.html" class="tagline-link">我正孤獨通過自己行星的曠野</a></p>
      <nav class="site-nav">
        <div class="nav-item">
          故事 <span class="nav-arrow">▾</span>
          <div class="dropdown">
            <div class="dropdown-inner">
              <a class="dropdown-item" href="/chapters/lakecity/01.html">湖城記事</a>
              <a class="dropdown-item" href="/chapters/name/01.html">名字</a>
              <a class="dropdown-item" href="/chapters/story/01.html">故事之城</a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="/chapters/yanran/01.html">炎涼記</a>
              <a class="dropdown-item" href="/chapters/baitai/01.html">百態記</a>
              <a class="dropdown-item" href="/chapters/limu/01.html">黎小木上學記</a>
              <a class="dropdown-item" href="/chapters/hudi/01.html">惠帝列傳</a>
              <a class="dropdown-item" href="/chapters/traveler/01.html">旅行者回憶錄</a>
              <a class="dropdown-item" href="/chapters/animals/01.html">動物食堂</a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="/chapters/suosui/01.html" style="font-style:italic;color:#9a9890;">瑣碎集</a>
            </div>
          </div>
        </div>
        <a class="nav-item" href="/about.html">關於</a>
        <a class="nav-item" href="/letter.html">寫信</a>
      </nav>
      <div class="hamburger">
        <span></span><span></span><span></span>
      </div>
    </div>
  </header>

  <div class="mobile-menu">
    <span class="mobile-menu-close">關閉</span>
    <a href="/index.html">首頁</a>
    <a href="/chapters/lakecity/01.html">湖城記事</a>
    <a href="/chapters/name/01.html">名字</a>
    <a href="/chapters/story/01.html">故事之城</a>
    <a href="/chapters/yanran/01.html">炎涼記</a>
    <a href="/chapters/baitai/01.html">百態記</a>
    <a href="/chapters/limu/01.html">黎小木上學記</a>
    <a href="/chapters/hudi/01.html">惠帝列傳</a>
    <a href="/chapters/traveler/01.html">旅行者回憶錄</a>
    <a href="/chapters/animals/01.html">動物食堂</a>
    <a href="/chapters/suosui/01.html">瑣碎集</a>
    <a href="/about.html">關於</a>
    <a href="/letter.html">寫信</a>
  </div>`;

  document.addEventListener('DOMContentLoaded', function() {
    var existing = document.querySelector('.site-header');
    var existingMenu = document.querySelector('.mobile-menu');
    var temp = document.createElement('div');
    temp.innerHTML = nav.trim();

    var newHeader = temp.querySelector('.site-header');
    var newMenu = temp.querySelector('.mobile-menu');

    if (existing) {
      existing.replaceWith(newHeader);
    } else {
      document.body.insertBefore(newHeader, document.body.firstChild);
    }

    if (existingMenu) {
      existingMenu.replaceWith(newMenu);
    } else {
      newHeader.after(newMenu);
    }

    var hamburger = document.querySelector('.hamburger');
    var closeBtn = document.querySelector('.mobile-menu-close');
    var menu = document.querySelector('.mobile-menu');

    if (hamburger) hamburger.addEventListener('click', function() {
      if (menu) menu.classList.add('open');
    });

    if (closeBtn) closeBtn.addEventListener('click', function() {
      if (menu) menu.classList.remove('open');
    });
  });
})();
