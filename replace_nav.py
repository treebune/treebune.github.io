#!/usr/bin/env python3
import os
import re

ROOT = os.path.expanduser('~/Desktop/treebune-final')

NAV_PATTERN = re.compile(
    r'<header class="site-header">.*?</header>\s*<div class="mobile-menu">.*?</div>',
    re.DOTALL
)

NAV_REPLACEMENT = '<script src="/js/nav.js"></script>'

count = 0
skipped = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    # 跳過 .git 資料夾
    dirnames[:] = [d for d in dirnames if d != '.git']
    for filename in filenames:
        if not filename.endswith('.html'):
            continue
        filepath = os.path.join(dirpath, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if '<script src="/js/nav.js"></script>' in content:
            skipped += 1
            continue
        if not NAV_PATTERN.search(content):
            skipped += 1
            continue
        new_content = NAV_PATTERN.sub(NAV_REPLACEMENT, content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1
        print(f'更新：{os.path.relpath(filepath, ROOT)}')

print(f'\n完成：更新 {count} 個檔案，跳過 {skipped} 個檔案')
