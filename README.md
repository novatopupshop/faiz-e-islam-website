# Faiz e Islam — Website (coded, multi-page, static)

A complete multi-page static website in plain HTML + CSS + JavaScript — **not WordPress, not a single-page demo**. Every section is its own page, and every one of the 114 Surahs has its own page under `al-quran/`.

## Structure

- `index.html` — Home (hero, Quran, Durood, Most Read Surahs, Kalimas, Salaat, Duas, Istikhara, Blogs, tools)
- `al-quran.html` — searchable list of all 114 Surahs
- `al-quran/surah-<slug>.html` — one page per Surah (114 pages, Template A: facts, audio, Arabic + Urdu + English verse by verse, virtues, FAQs)
- `durood.html`, `kalimas.html`, `salaat.html`, `duas.html`, `istikhara.html`, `blogs.html`, `naat.html`, `wazaif.html`, `names.html` (99 Names), `zakat.html`, `tasbih.html`, `about.html`, `contact.html`, `donate.html`, `privacy-policy.html`, `quran-classes.html`
- `blogs/*.html` — 6 blog articles
- `assets/css/style.css`, `assets/js/main.js` — shared theme and tools (nav, search, Tasbih, Zakat calculator)
- `vercel.json` — clean URLs (no `.html` needed)

## Data sources

Quran Arabic text and Urdu (Junagarhi) / English (Sahih International) translations: **AlQuran.cloud** API. Audio: Mishary Rashid Alafasy via the **Islamic Network CDN**. Introductions, guides, virtues and FAQs are written freshly for this site — the Quran text and translations are kept as-is with source credit, as in the structure document.

## Run locally

```bash
cd faiz-e-islam-site
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy on Vercel (complete testing)

1. Push this folder to a GitHub repository, or run `vercel` in this folder.
2. In Vercel, choose **Import Project** and select the repository.
3. Framework preset: **Other** (static site). **Build command: leave empty. Output directory: leave as the project root (`.`).**
4. Click **Deploy**. Vercel serves the static files; `vercel.json` gives clean URLs, so `/al-quran` works without `.html`.
5. Test the live site, then add your own domain in Vercel under **Settings → Domains** when you buy one.

No build step, no database, no server code is needed.
