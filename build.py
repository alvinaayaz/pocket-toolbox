#!/usr/bin/env python3
"""Rebuild the generated files in site/ after you edit site/index.html.

  python3 build.py

What it does
  1. Makes one page per tool (word-counter.html, loan-payment-calculator.html, ...) as copies
     of index.html with their own title, description and address.
  2. Writes sitemap.xml and robots.txt.
  3. Writes site/sw.js from tools/sw.template.js and stamps a new cache version (a hash of
     every site file), so returning visitors always receive your update.

index.html is the one source file. The other tool pages are generated copies: do not edit them.
The web address is read from the canonical link in index.html (see set-domain.py).
"""
import hashlib, html, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')

# tool id: (page name, page title, description). Page names must match SLUG in index.html.
SEO = {
 'words': ('word-counter', 'Free Word Counter: words, characters, reading time', 'Count words, characters and sentences as you type, and see the reading time. Free and private, runs in your browser.'),
 'pass':  ('password-generator', 'Free Password Generator: strong random passwords', 'Create strong random passwords with the length and characters you choose. Made in your browser and never sent anywhere.'),
 'tip':   ('bill-splitter', 'Bill Splitter and Tip Calculator', 'Add a tip and split the bill between friends in seconds. Works with any currency and needs no sign-up.'),
 'sale':  ('discount-calculator', 'Discount Calculator: sale price and savings', 'Enter a price and discount to see the sale price, how much you save, and the final price with tax.'),
 'perc':  ('percentage-calculator', 'Percentage Calculator: percent of, percent change', 'Find X% of a number, work out what percent one number is of another, and calculate percent change.'),
 'units': ('unit-converter', 'Unit Converter: length, weight, volume, speed, temperature', 'Convert between common units of length, weight, volume, speed and temperature instantly.'),
 'loan':  ('loan-payment-calculator', 'Loan Payment Calculator: monthly payment estimate', 'Estimate your monthly loan payment, total repayment and total interest from the amount, rate and term.'),
 'bmi':   ('bmi-calculator', 'BMI Calculator: metric and imperial', 'Calculate your body mass index from kilograms and centimetres or pounds and inches. A rough screening number, not a diagnosis.'),
 'dates': ('age-and-date-calculator', 'Age and Date Calculator: days between two dates', 'Find your exact age or the time between two dates in years, months, days and weeks.'),
 'timer': ('timer-and-stopwatch', 'Online Timer and Stopwatch', 'A simple countdown timer with presets and a stopwatch with laps. Keeps running if you reload the page.'),
 'todo':  ('to-do-list', 'Simple To-Do List', 'A private to-do list that saves on your device. Add, edit, tick off and clear tasks. No account needed.'),
 'qr':    ('qr-code-maker', 'QR Code Maker: free, download as PNG', 'Turn any link or text into a QR code and download it as a PNG. Free and private, made in your browser.'),
}

def read(rel):
    with open(os.path.join(SITE, rel), encoding='utf-8') as f: return f.read()

def write(rel, text):
    with open(os.path.join(SITE, rel), 'w', encoding='utf-8') as f: f.write(text)

def build_pages():
    home = read('index.html')
    m = re.search(r'<link rel="canonical" href="([^"]+)">', home)
    if not m: sys.exit('index.html has no canonical link.')
    base = m.group(1).rstrip('/')
    urls = [base + '/']
    for slug, title, desc in SEO.values():
        if "'" + slug + "'" not in home:
            sys.exit(f"index.html does not know the page name '{slug}'. Keep SEO in build.py and SLUG in index.html in step.")
        url = f'{base}/{slug}.html'
        urls.append(url)
        page = home
        for pattern, new in [
            (r'<title>.*?</title>', f'<title>{html.escape(title)} | Pocket Toolbox</title>'),
            (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc, quote=True)}">'),
            (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">'),
            (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title, quote=True)}">'),
            (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(desc, quote=True)}">'),
            (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
            (r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">'),
            (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{html.escape(desc, quote=True)}">'),
        ]:
            page, n = re.subn(pattern, lambda _m, new=new: new, page, count=1)
            if n != 1: sys.exit(f'Could not find this tag in index.html: {pattern}')
        write(slug + '.html', page)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n')
    return len(SEO)

def stamp_sw():
    with open(os.path.join(ROOT, 'tools', 'sw.template.js'), encoding='utf-8') as f: template = f.read()
    files = []
    for folder, _, names in os.walk(SITE):
        for name in names:
            rel = os.path.relpath(os.path.join(folder, name), SITE).replace(os.sep, '/')
            if rel != 'sw.js': files.append(rel)
    files.sort()
    h = hashlib.sha256()
    for rel in files:
        h.update(rel.encode())
        with open(os.path.join(SITE, rel), 'rb') as f: h.update(f.read())
    h.update(template.encode())
    version = h.hexdigest()[:10]
    precache = ['./', 'index.html'] + [f for f in files if re.search(r'\.(woff2|ico|webmanifest)$', f)
                                       or (f.endswith('.png') and f != 'og-image.png') or f == 'qrcode.min.js']
    write('sw.js', template.replace('__VERSION__', version).replace('__PRECACHE__', json.dumps(precache, indent=2)))
    return version, len(precache)

if __name__ == '__main__':
    pages = build_pages()
    version, cached = stamp_sw()
    print(f'Built {pages} tool pages, sitemap.xml, robots.txt')
    print(f'Service worker version {version} ({cached} files cached for offline use)')
