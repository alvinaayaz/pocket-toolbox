#!/usr/bin/env python3
"""Put your real web address into every page, the sitemap and robots.txt.

  python3 set-domain.py yourdomain.com

Run it once, after you know your address and before you upload the site/ folder.
It also refreshes the service worker version, so you do not need to run build.py afterwards.
"""
import glob, os, re, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) != 2: sys.exit('Usage: python3 set-domain.py yourdomain.com')
domain = re.sub(r'^https?://', '', sys.argv[1].strip()).strip('/')
if not domain or ' ' in domain: sys.exit('That does not look like a domain name.')
site = os.path.join(ROOT, 'site')
changed = 0
for path in glob.glob(os.path.join(site, '*.html')) + [os.path.join(site, 'sitemap.xml'), os.path.join(site, 'robots.txt')]:
    with open(path, encoding='utf-8') as f: text = f.read()
    if 'YOUR-DOMAIN.com' in text:
        with open(path, 'w', encoding='utf-8') as f: f.write(text.replace('YOUR-DOMAIN.com', domain))
        changed += 1
sys.path.insert(0, ROOT)
import build
version, _ = build.stamp_sw()
print(f'Updated {changed} files to use https://{domain}/ (service worker version {version})')
