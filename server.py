#!/usr/bin/env python3
"""
treebune 上稿伺服器
跑起來後在瀏覽器開 upload-tool.html 使用
"""

import os
import re
import json
import subprocess
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64

ROOT = os.path.expanduser('~/Desktop/treebune-final')
CHAPTERS_DIR = os.path.join(ROOT, 'chapters')
IMAGES_DIR = os.path.join(ROOT, 'images')
JS_DIR = os.path.join(ROOT, 'js')
PORT = 5500

SERIES_NAMES = {
    'lakecity': '湖城記事',
    'name': '名字',
    'story': '故事之城',
    'yanran': '炎涼記',
    'baitai': '百態記',
    'limu': '黎小木上學記',
    'hudi': '惠帝列傳',
    'traveler': '旅行者回憶錄',
    'animals': '動物食堂',
    'suosui': '瑣碎集',
}

# 各系列的特殊條目（num:0），會插在目錄最前面
SERIES_SPECIAL = {
    'name': {'num': 0, 'title': '名字・全', 'file': 'all.html'},
}

def get_title(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'<h1[^>]*class="chapter-title"[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return ''

def regenerate_toc(series_key):
    series_name = SERIES_NAMES.get(series_key, series_key)
    series_dir = os.path.join(CHAPTERS_DIR, series_key)
    if not os.path.isdir(series_dir):
        return

    chapters = []
    files = sorted(
        [f for f in os.listdir(series_dir) if re.match(r'^\d+\.html$', f)],
        key=lambda x: int(x.replace('.html', ''))
    )
    for filename in files:
        num = int(filename.replace('.html', ''))
        filepath = os.path.join(series_dir, filename)
        title = get_title(filepath)
        chapters.append({'num': num, 'title': title, 'file': filename})

    # 如果這個系列有特殊條目（如全卷），且對應檔案存在，插在最前面
    special = SERIES_SPECIAL.get(series_key)
    if special:
        special_path = os.path.join(series_dir, special['file'])
        if os.path.isfile(special_path):
            chapters.insert(0, special)

    data = {
        'key': series_key,
        'name': series_name,
        'total': len(chapters),
        'chapters': chapters
    }
    var_name = 'SERIES_' + series_key.upper()
    js_content = 'var ' + var_name + ' = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n'
    js_path = os.path.join(JS_DIR, 'toc-' + series_key + '.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    return len(chapters)

def regenerate_sitemap():
    urls = [
        ('https://www.treebune.cc/', 'weekly', '1.0'),
        ('https://www.treebune.cc/about.html', 'monthly', '0.8'),
        ('https://www.treebune.cc/letter.html', 'monthly', '0.6'),
        ('https://www.treebune.cc/series.html', 'monthly', '0.7'),
    ]
    for series_key in SERIES_NAMES:
        series_dir = os.path.join(CHAPTERS_DIR, series_key)
        if not os.path.isdir(series_dir):
            continue
        files = sorted(
            [f for f in os.listdir(series_dir) if re.match(r'^\d+\.html$', f)],
            key=lambda x: int(x.replace('.html', ''))
        )
        for filename in files:
            num = int(filename.replace('.html', ''))
            numstr = str(num).zfill(2)
            url = 'https://www.treebune.cc/chapters/' + series_key + '/' + numstr + '.html'
            priority = '0.7' if series_key != 'suosui' else '0.6'
            urls.append((url, 'monthly', priority))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, freq, pri in urls:
        lines.append('  <url><loc>' + url + '</loc><changefreq>' + freq + '</changefreq><priority>' + pri + '</priority></url>')
    lines.append('</urlset>')

    sitemap_path = os.path.join(ROOT, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def update_index(series_key, chap_num, title, desc, note):
    index_path = os.path.join(ROOT, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新近況
    if note:
        content = re.sub(
            r'(<p class="shelf-note-text">).*?(</p>)',
            r'\g<1>' + note + r'\g<2>',
            content
        )

    # 更新主推文章（stories-main）
    series_name = SERIES_NAMES.get(series_key, series_key)
    numstr = str(chap_num).zfill(2)
    href = '/chapters/' + series_key + '/' + numstr + '.html'

    # 把現在的主推存成第一個副推，第一個副推存成第二個，最新的成為主推
    # 先抓現在的主推資訊
    main_match = re.search(
        r'<a href="([^"]+)" class="stories-main-link">.*?<p class="stories-main-series">([^<]+)</p>\s*<p class="stories-main-title">([^<]+)</p>\s*<p class="stories-main-desc">([^<]*)</p>',
        content, re.DOTALL
    )

    if main_match:
        old_main_href = main_match.group(1)
        old_main_series = main_match.group(2)
        old_main_title = main_match.group(3)

        # 抓現在的第一個副推
        sides = re.findall(
            r'<a href="([^"]+)" class="story-side">.*?<p class="story-side-series">([^<]+)</p>\s*<p class="story-side-title">([^<]+)</p>\s*<p class="story-side-desc">([^<]*)</p>',
            content, re.DOTALL
        )

        # 更新主推
        content = re.sub(
            r'(<a href=")[^"]+(" class="stories-main-link">)',
            r'\g<1>' + href + r'\g<2>',
            content, count=1
        )
        content = re.sub(
            r'(<p class="stories-main-series">)[^<]*(</p>)',
            r'\g<1>' + series_name + r'\g<2>',
            content, count=1
        )
        content = re.sub(
            r'(<p class="stories-main-title">)[^<]*(</p>)',
            r'\g<1>' + title + r'\g<2>',
            content, count=1
        )
        if desc:
            content = re.sub(
                r'(<p class="stories-main-desc">)[^<]*(</p>)',
                r'\g<1>' + desc + r'\g<2>',
                content, count=1
            )

        # 更新第一個副推為舊主推
        if sides:
            new_sides = re.sub(
                r'(<a href=")[^"]+(" class="story-side">)',
                r'\g<1>' + old_main_href + r'\g<2>',
                content, count=1
            )
            new_sides = re.sub(
                r'(<p class="story-side-series">)[^<]*(</p>)',
                r'\g<1>' + old_main_series + r'\g<2>',
                new_sides, count=1
            )
            new_sides = re.sub(
                r'(<p class="story-side-title">)[^<]*(</p>)',
                r'\g<1>' + old_main_title + r'\g<2>',
                new_sides, count=1
            )
            content = new_sides

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

def git_push(message):
    try:
        subprocess.run(['git', '-C', ROOT, 'add', '.'], check=True)
        subprocess.run(['git', '-C', ROOT, 'commit', '-m', message], check=True)
        subprocess.run(['git', '-C', ROOT, 'push', 'origin', 'main'], check=True)
        return True, '推送成功'
    except subprocess.CalledProcessError as e:
        return False, str(e)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 靜音 log

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode('utf-8'))
        except Exception:
            self.respond(400, {'ok': False, 'error': '無法解析請求'})
            return

        action = data.get('action')

        if action == 'publish':
            self.handle_publish(data)
        elif action == 'update_note':
            self.handle_note(data)
        else:
            self.respond(400, {'ok': False, 'error': '未知動作'})

    def handle_publish(self, data):
        series = data.get('series')
        chap_num = int(data.get('chap_num', 0))
        title = data.get('title', '')
        html = data.get('html', '')
        note = data.get('note', '')
        desc = data.get('desc', '')
        images = data.get('images', {})

        if not series or not chap_num or not title or not html:
            self.respond(400, {'ok': False, 'error': '缺少必要欄位'})
            return

        numstr = str(chap_num).zfill(2)

        # 寫入 HTML
        series_dir = os.path.join(CHAPTERS_DIR, series)
        os.makedirs(series_dir, exist_ok=True)
        html_path = os.path.join(series_dir, numstr + '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # 寫入圖片
        if images:
            img_dir = os.path.join(IMAGES_DIR, series, numstr)
            os.makedirs(img_dir, exist_ok=True)
            for filename, b64data in images.items():
                img_path = os.path.join(img_dir, filename)
                with open(img_path, 'wb') as f:
                    f.write(base64.b64decode(b64data.split(',')[-1]))

        # 更新 toc JS
        total = regenerate_toc(series)

        # 更新 sitemap
        regenerate_sitemap()

        # 更新首頁
        update_index(series, chap_num, title, desc, note)

        # git push
        commit_msg = series + ' 第' + str(chap_num) + '篇：' + title
        ok, msg = git_push(commit_msg)

        self.respond(200, {'ok': ok, 'message': msg, 'total': total})

    def handle_note(self, data):
        note = data.get('note', '')
        if not note:
            self.respond(400, {'ok': False, 'error': '近況不能空白'})
            return

        index_path = os.path.join(ROOT, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(
            r'(<p class="shelf-note-text">).*?(</p>)',
            r'\g<1>' + note + r'\g<2>',
            content
        )

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

        ok, msg = git_push('更新近況')
        self.respond(200, {'ok': ok, 'message': msg})

    def respond(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), Handler)
    print('伺服器啟動：http://localhost:' + str(PORT))
    print('請在上稿機按發布，按 Ctrl+C 停止')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n停止')
