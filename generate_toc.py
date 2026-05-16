#!/usr/bin/env python3
import os
import re
import json

ROOT = os.path.expanduser('~/Desktop/treebune-final')
CHAPTERS_DIR = os.path.join(ROOT, 'chapters')
JS_DIR = os.path.join(ROOT, 'js')

SERIES = {
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

def get_title(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'<h1[^>]*class="chapter-title"[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<title>(.*?)</title>', content)
    if m:
        title = m.group(1).strip()
        title = re.sub(r'\s*[—\-].*$', '', title).strip()
        return title
    return ''

os.makedirs(JS_DIR, exist_ok=True)

for series_key, series_name in SERIES.items():
    series_dir = os.path.join(CHAPTERS_DIR, series_key)
    if not os.path.isdir(series_dir):
        print('跳過（資料夾不存在）：' + series_key)
        continue

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

    if not chapters:
        print('跳過（無章節）：' + series_key)
        continue

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

    print('生成：toc-' + series_key + '.js（' + str(len(chapters)) + ' 篇）')

print('\n完成')
