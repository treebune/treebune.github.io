(function() {
  var path = window.location.pathname;
  var m = path.match(/\/chapters\/([^/]+)\/(\d+)\.html/);
  if (!m) return;

  var key = m[1];
  var currentNum = parseInt(m[2]);
  var varName = 'SERIES_' + key.toUpperCase();

  function initToc() {
    var data = window[varName];
    if (!data) return;

    var sidebar = document.querySelector('.reading-sidebar');
    if (!sidebar) return;

    var total = data.total;
    var pct = Math.round((currentNum / total) * 100);

    var html = '<p class="section-label">' + data.name + '</p>';
    html += '<div class="progress-bar"><div class="progress-fill" style="width:' + pct + '%"></div></div>';
    html += '<p class="progress-label">第 ' + currentNum + ' 篇，共 ' + total + ' 篇</p>';
    html += '<ul class="toc-list">';

    var chapters = key === 'suosui' ? data.chapters.slice().reverse() : data.chapters;

    chapters.forEach(function(ch) {
      var numStr = String(ch.num).padStart(2, '0');
      var isActive = ch.num === currentNum;
      html += '<li class="toc-item">';
      html += '<div class="toc-num">' + numStr + '</div>';
      html += '<div class="toc-name' + (isActive ? ' active' : '') + '">';
      if (!isActive) {
        html += '<a href="/chapters/' + key + '/' + numStr + '.html">' + (ch.title || '第' + ch.num + '篇') + '</a>';
      } else {
        html += ch.title || '第' + ch.num + '篇';
      }
      html += '</div></li>';
    });

    html += '</ul>';
    html += '<a href="/series.html?s=' + key + '" style="display:block;margin-top:1.5rem;font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--text-faint);text-decoration:none;transition:color .15s;" onmouseover="this.style.color=\'var(--text-primary)\'" onmouseout="this.style.color=\'var(--text-faint)\'">系列總覽</a>';

    sidebar.innerHTML = html;
  }

  if (window[varName]) {
    initToc();
  } else {
    var script = document.createElement('script');
    script.src = '/js/toc-' + key + '.js';
    script.onload = initToc;
    document.head.appendChild(script);
  }
})();
