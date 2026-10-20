# Pocket Toolbox

Twelve free everyday tools in one fast, private website: word counter, password generator, bill splitter, discount, percentage, unit, loan and BMI calculators, date and age calculator, timer and stopwatch, to-do list and QR code maker.

There are no ads, accounts or trackers. Everything runs in the visitor's browser and nothing they type is sent to a server. It is a plain static site (HTML, CSS and JavaScript), so there is nothing to install to run it and no framework to learn.

## The tools

| Tool | What it does |
|---|---|
| Word counter | Counts words, characters and sentences as you type, and estimates reading time (220 words a minute). |
| Passwords | Makes random passwords of 8 to 48 characters from the character types you choose, using the browser's secure random generator. One click copies it. |
| Split a bill | Adds a tip to a bill and divides the total between any number of people. Choose Rs., $, €, £ or no currency symbol. |
| Discount | Takes a price, a discount percentage and optional tax, and shows the sale price, how much you save and the final price. |
| Percentages | Three calculators: X% of Y, X is what percent of Y, and percent change from one number to another. |
| Units | Converts length, weight, volume, speed and temperature, with a copy button for the result. |
| Loan payment | Estimates the monthly payment, total repaid and total interest for a fixed-rate loan with equal payments. |
| BMI | Works out body mass index in metric or imperial units and shows the standard category. A rough screening number, not a diagnosis. |
| Dates and age | Finds the time between two dates in years, months, days, total days and weeks. A birth date gives an age. |
| Timer | Countdown with 1, 5, 10 and 25 minute presets, a sound and vibration at the end, the countdown in the browser tab, and an optional "keep the screen on". Also a stopwatch with laps. Both survive a page reload. |
| To-do | Add, edit, tick off, delete and clear completed tasks. Saved on the device. |
| QR code | Turns a link or any text into a QR code and downloads it as a PNG. |

Also: a search box (press `/` to jump to it), four accent colours, light, dark and automatic themes, and a separate page and address for every tool so each can be shared, bookmarked and found by search engines. It can be installed on a phone and works offline.

## Run it locally

    cd site
    python3 -m http.server 8000

Then open http://localhost:8000. Any static file server works. Use a server rather than double-clicking `index.html`: installing as an app and offline use need a web address (they also work on `localhost`).

## What is in this folder

    README.md          this file
    site/              the website: upload this folder to your host
    build.py           regenerates the generated files in site/ (see below)
    set-domain.py      puts your real web address into the site
    tools/             template for the service worker
    icon-source/       editable SVG artwork for the app icon

Inside `site/`:

- `index.html` is the one source file for the whole app (the markup, styles and scripts).
- The other `.html` pages (`loan-payment-calculator.html` and so on) are generated copies of it with their own title, description and address. Do not edit them.
- `sw.js`, `sitemap.xml` and `robots.txt` are also generated.
- `fonts/`, `qrcode.min.js`, `icon-*.png`, `favicon.*`, `apple-touch-icon.png`, `og-image.png` and `manifest.webmanifest` are static assets.

## Making changes

1. Edit `site/index.html` (or any asset).
2. Run `python3 build.py`.

That regenerates the tool pages, the sitemap and the service worker. Do not skip step 2 after an edit, or the tool pages will be out of date.

To add a tool, add its section and menu entry in `index.html`, add its page name to `SLUG` in `index.html` and to `SEO` in `build.py`, then run the build.

## Publishing

1. Run `python3 set-domain.py yourdomain.com` once. It replaces the placeholder `YOUR-DOMAIN.com` in every page, the sitemap and robots.txt.
2. Upload the `site/` folder to any static host. Netlify Drop (app.netlify.com/drop) is the easiest: drag the folder onto the page. Cloudflare Pages and GitHub Pages also work and are free.
3. Optional: add the site to Google Search Console and submit `https://yourdomain.com/sitemap.xml`.

Installing on a phone and offline use only work on https, which all of the hosts above provide.

## How updates reach visitors

`build.py` stamps `sw.js` with a new version (a hash of every file) on each run. The service worker works like this:

- Pages and the manifest are fetched network first and bypass the browser's cache, so visitors get a new release on their next page load even if the host tells browsers to cache files. If the network is down, or takes longer than 4 seconds, the saved copy is used.
- Fonts, images and scripts are served from the cache instantly and refreshed in the background.
- Only successful responses are cached, and old caches are deleted when a new version activates.

Tested against a host that redirects `/page.html` to `/page`, caches everything for an hour, and responds slowly.

## Privacy

The site makes no requests to other websites: the fonts and the QR library are bundled. The to-do list, timer, stopwatch, colour and theme choices are stored in the visitor's own browser (localStorage) and never leave it. Your host may keep ordinary server logs, as any host does.

## Browser support

Current Chrome, Edge, Firefox and Safari. The soft background glow needs Chrome 111 or Safari 16.2 or newer; older browsers show a plain background and everything else still works.

## Third-party files

- DM Sans and Fraunces fonts: SIL Open Font License (`site/fonts/`)
- qrcode.js by davidshimjs: MIT License (`site/licenses/`)
