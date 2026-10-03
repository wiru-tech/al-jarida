---
name: Global Editorial Standard
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#b41d11'
  on-secondary: '#ffffff'
  secondary-container: '#d83828'
  on-secondary-container: '#fffbff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#111c2d'
  on-tertiary-container: '#79849a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#ffdad4'
  secondary-fixed-dim: '#ffb4a8'
  on-secondary-fixed: '#410000'
  on-secondary-fixed-variant: '#930000'
  tertiary-fixed: '#d8e3fb'
  tertiary-fixed-dim: '#bcc7de'
  on-tertiary-fixed: '#111c2d'
  on-tertiary-fixed-variant: '#3c475a'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Newsreader
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Newsreader
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  urdu-body:
    fontFamily: Noto Nastaliq Urdu
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 40px
  arabic-body:
    fontFamily: Amiri
    fontSize: 20px
    fontWeight: '400'
    lineHeight: 36px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-max: 1280px
  gutter: 1.5rem
  margin-mobile: 1rem
  section-gap: 4rem
  stack-sm: 0.5rem
  stack-md: 1rem
---

## Brand & Style

The design system is built for a high-density, authoritative news portal that balances global journalistic standards with regional cultural nuances. The personality is intellectual, urgent, and trustworthy, evoking the feel of a legacy broadsheet translated into a high-performance digital experience.

The aesthetic follows a **Modern Editorial** style:
- **High-Density Information:** Layouts prioritize content volume without sacrificing legibility, utilizing tight grids and clear visual anchors.
- **Architectural Structure:** Uses "Heavy-Top" layouts where navigation and breaking news establish a firm foundation.
- **Cultural Synthesis:** Integrates traditional calligraphic scripts (Urdu/Arabic) with systematic Western grotesques, ensuring neither feels like an afterthought.
- **Subtle Interaction:** Motion is reserved for functional feedback, such as slight vertical lifts on article cards, maintaining a serious tone.

## Colors

The palette is rooted in traditional journalistic colors to convey authority and urgency.

- **Primary (Deep Editorial Navy):** Used for primary navigation, headers, and key branding elements. It provides a more sophisticated alternative to pure black.
- **Secondary (Crimson Red):** Reserved strictly for "Live" indicators, breaking news, and urgent calls to action. Use sparingly to maintain its impact.
- **Background (Warm Light Crisp):** A slightly off-white base that reduces eye strain during long-form reading compared to stark white.
- **Text (Dark Charcoal):** Used for body copy to ensure high contrast while maintaining a softer, more professional look than #000.
- **Borders:** Subtle grey tones are used to define the "grid" without creating visual noise.

## Typography

This design system utilizes a tiered typographic scale to manage high-density information across multiple languages.

- **English Serif (Newsreader):** Used for headlines to establish a literary, authoritative tone. It provides the "Editorial" feel necessary for news.
- **English Sans (Inter):** Used for body text, UI labels, and metadata. Its high x-height ensures clarity at small sizes.
- **Urdu (Noto Nastaliq Urdu):** Must always maintain a line-height of at least 2.0 to 2.2 to accommodate descending strokes. 
- **Arabic (Amiri):** Used for literary or Islamic content sections, providing a classical contrast to the modern UI.

**Hierarchy Rules:**
- Use `label-caps` for category tags (e.g., POLITICS, WORLD NEWS) in Crimson Red or Navy.
- News summaries should use `body-md` with slightly tighter line-height than long-form articles.

## Layout & Spacing

The layout utilizes a **12-column asymmetric fluid grid** that mimics the rhythm of a physical newspaper.

- **Desktop (1280px+):** Use 12 columns. Implement a "Main Content / Sidebar" split (8 cols / 4 cols) for standard articles. Use asymmetric spans (e.g., 7 columns for lead story, 5 columns for a stack of secondary stories) on the homepage.
- **Tablet (768px - 1024px):** Shift to an 8-column grid. Sidebars typically drop below the main content or condense into a single column.
- **Mobile (<768px):** Single column with 16px margins. Headlines scale down via the `headline-lg-mobile` token.

**Sticky Mechanics:** 
The primary navigation and "Trending" ticker should remain sticky. On scroll, the navigation should condense to maximize vertical reading space.

## Elevation & Depth

To maintain a professional and "flat" editorial feel, this design system avoids heavy drop shadows and dramatic 3D effects.

- **Tonal Layering:** Depth is communicated through background color shifts. The main body sits on `neutral` (#F8FAFC), while sidebar widgets or "Breaking News" sections may use a subtle grey or white fill to distinguish themselves.
- **Interactive Elevation:** Article cards use a `transform: translateY(-4px)` on hover accompanied by a very soft, diffused shadow (10% opacity) to indicate interactivity.
- **Borders as Dividers:** Use 1px borders (#E2E8F0) for vertical and horizontal rules. This reinforces the "grid" feel common in high-end news publications.
- **Islamic Content Depth:** For geometric or religious sections, use layered background patterns or thin gold/navy borders rather than shadows to imply importance.

## Shapes

The design system uses a **Soft (0.25rem)** roundedness profile. This keeps the UI looking precise and modern without the "consumer app" friendliness of heavily rounded corners.

- **Buttons & Inputs:** Use the standard `rounded` (0.25rem) for a sharp, professional finish.
- **Article Cards:** Use `0px` (Sharp) or `rounded` (0.25rem). If using images, ensure the corner radius matches the container.
- **Geometric Borders:** In Islamic sections, use 8-point star patterns or repetitive geometric motifs within borders to add cultural texture while maintaining the 1px stroke weight used elsewhere.

## Components

### News Ticker
A full-width, sticky component at the top of the viewport. Background: `primary_color_hex` (Navy). Text: `neutral_color_hex`. Use a scrolling or fading transition for "Breaking News" headlines.

### Article Cards
- **Lead Card:** Large image, `display-lg` headline, and a 3-line excerpt.
- **Standard Card:** Horizontal layout on desktop, image on left (4 cols), text on right (8 cols).
- **Hover State:** Apply `translateY(-4px)` and darken the headline color slightly.

### Multi-level Navigation
The primary menu should use a mega-menu style for categories like "World," "Politics," and "Economy." Use `label-caps` for top-level links.

### Input Fields & Buttons
- **Primary Button:** Solid Navy background, white text, 0.25rem radius.
- **Secondary Button:** Crimson Red border and text, used for "Subscribe" or "Live" alerts.
- **Search:** A minimal line-based input with a search icon; avoid heavy boxes.

### Islamic Content Section
Specifically styled with `geometric-borders`. Use `noto-serif` or `amiri` for titles in this section. Backgrounds can use a very subtle "Paper" texture or a geometric watermark at 5% opacity.

### Sidebar Widgets
Structured lists with 1px horizontal dividers. Use "Most Read" numbered lists where numbers are large, low-opacity Deep Navy (`#0F172A` at 10%) behind the headline text.