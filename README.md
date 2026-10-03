# AL-JARIDA — Modern Editorial News Portal

A full-stack Django news & blogging platform built to the **Global Editorial
Standard** design (navy/black + crimson accent, `Newsreader` serif headlines,
`Inter` body, `Noto Nastaliq Urdu` / `Amiri` for RTL scripts).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data          # loads demo content + admin user
python manage.py runserver
```

Open http://127.0.0.1:8000/ — the admin is at `/admin/`.

**Demo admin login:** `editor` / `aljarida123`

> The demo uses remote placeholder images (picsum.photos) and Google Fonts,
> so run it with an internet connection to see images and Urdu/Arabic fonts.

## Translations (English / Urdu / Arabic)

Two separate mechanisms, both required for a fully translated page:

| Layer | What it covers | Where it lives |
|---|---|---|
| `gettext` | Static UI strings — nav labels, buttons, headings, legal copy | `locale/<lang>/LC_MESSAGES/django.po` |
| `django-modeltranslation` | Editorial content — article titles/bodies, category names, widget copy | Per-language DB columns |

### Editorial content

`news/translation.py` registers the translated fields. Each becomes one
column per language (`title_en`, `title_ur`, `title_ar`, ...) and the plain
attribute turns into a descriptor returning the **active language**, so
templates need no changes — `{{ article.title }}` returns Urdu under Urdu.

Blank translations fall back to English (`MODELTRANSLATION_FALLBACK_LANGUAGES`),
so a partly translated article still renders.

Editors fill all three languages from tabs on the normal admin form
(`TabbedTranslationAdmin`). After adding a translated field:

```bash
python manage.py makemigrations news && python manage.py migrate
python manage.py update_translation_fields   # backfill *_en from existing rows
python manage.py seed_translations           # Urdu/Arabic section names
```

### Static strings

```bash
python manage.py makemessages -l ur -l ar --ignore=venv --ignore=myenv
python manage.py compilemessages --ignore=venv --ignore=myenv
```

> Pass `--ignore` for the bundled `venv/` and `myenv/` folders, or the commands
> walk thousands of vendored Django `.po` files and take minutes.

### RTL and the fallback problem

`<html dir>` flips from the active language, and most mirroring is automatic
via CSS logical properties. The subtle part: when an Urdu page shows an
article that has **no** Urdu translation, that English prose must stay LTR in
a Latin face — but genuinely translated Urdu must not.

Templates therefore stamp each content block with the language it actually
resolved to:

```django
<article class="card" lang="{{ a|content_lang }}">
```

and `rtl.css` keys off it with one inherited rule:

```css
[dir="rtl"] [lang="en"]{ direction:ltr; text-align:right;
  --serif:var(--serif-ltr); --sans:var(--sans-ltr); }
```

The `content_lang` filter lives in `news/templatetags/i18n_extras.py`.

## What's included

**Models** (`news/models.py`): `Category`, `Tag`, `Author`, `Article`
(scheduling, multilingual, view counter, featured/breaking flags),
`GalleryImage`, `Comment` (threaded + moderation), `MarketRate`, `WidgetData`
(live-TV / quote / horoscope / transport), `ContactInquiry`.

**Frontend**
- Homepage: breaking-news ticker, hero, trending column, Live-TV / Markets /
  Daily Perspective / Most-Read sidebar, Latest Dispatch grid, Islamic Life &
  Culture section, section grids.
- Article page: hero image, byline, share rail, secondary-language pull-quote
  (RTL), video embed, photo gallery, threaded comments.
- Category, tag, full-text search (with filters + sort), contact, directory,
  and legal pages (privacy / terms / copyright).

**Interactivity** (`static/js/main.js`, vanilla ES6 `fetch`)
- Live search dropdown → `/api/search/`
- Currency converter → `/api/markets/`
- Language switcher (EN / UR / AR) with automatic RTL
- One-click social sharing, comment reply threading.

**Backend**
- Customised admin "newsroom" (`news/admin.py`) with inline gallery/comments,
  bulk publish/approve actions, colour swatches.
- Context processor injecting nav, ticker, sidebar widgets site-wide.
- RSS syndication feed at `/rss/`.
- i18n via `LocaleMiddleware` + `gettext`; `select_related` / `prefetch_related`
  throughout for query efficiency.
- Security: CSRF on all forms, ORM (no raw SQL), template auto-escaping,
  honeypot on the contact form, and production HTTPS/HSTS settings gated on
  `DEBUG=False`.

## Switching to PostgreSQL

Uncomment the Postgres block in `aljarida/settings.py`, set the `DB_*`
environment variables, install `psycopg`, then re-run `migrate`.

## Scheduling

Articles have a `status` (draft / scheduled / published) and a `publish_at`
datetime. The published queryset only returns items whose `publish_at` is in
the past, so future-dated articles appear automatically when their time comes.
