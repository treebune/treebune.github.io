#!/usr/bin/env python3
import os
import re

ROOT = os.path.expanduser('~/Desktop/treebune-final')
CHAPTERS_DIR = os.path.join(ROOT, 'chapters')

count = 0
skipped = 0

for dirpath, dirnames, filenames in os.walk(CHAPTERS_DIR):
    dirnames[:] = [d for d in dirnames if d != '.git']
    for filename in filenames:
        if not filename.endswith('.html'):
            continue
        filepath = os.path.join(dirpath, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'data-pagefind-body' in content:
            skipped += 1
            continue
        new_content = content.replace(
            '<div class="chapter-body">',
            '<div class="chapter-body" data-pagefind-body>'
        )
        if new_content == content:
            skipped += 1
            continue
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1

print('更新：' + str(count) + ' 個檔案')
print('跳過：' + str(skipped) + ' 個檔案')
print('完成')
