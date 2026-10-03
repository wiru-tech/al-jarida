---
name: Serene Editorial
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#44474d'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#515f77'
  primary: '#37455c'
  on-primary: '#ffffff'
  primary-container: '#4f5d75'
  on-primary-container: '#c8d6f2'
  inverse-primary: '#b9c7e3'
  secondary: '#496800'
  on-secondary: '#ffffff'
  secondary-container: '#c8f17a'
  on-secondary-container: '#4e6e00'
  tertiary: '#564220'
  on-tertiary: '#ffffff'
  tertiary-container: '#705935'
  on-tertiary-container: '#f1d1a4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#b9c7e3'
  on-primary-fixed: '#0d1c31'
  on-primary-fixed-variant: '#39475e'
  secondary-fixed: '#c8f17a'
  secondary-fixed-dim: '#add461'
  on-secondary-fixed: '#131f00'
  on-secondary-fixed-variant: '#364e00'
  tertiary-fixed: '#fedeb0'
  tertiary-fixed-dim: '#e1c296'
  on-tertiary-fixed: '#281900'
  on-tertiary-fixed-variant: '#584321'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md-mobile:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 30px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-margin: 20px
  gutter: 16px
  stack-sm: 12px
  stack-md: 24px
  stack-lg: 48px
  section-padding: 64px
---

## Brand & Style
This design system centers on high-end digital publishing, prioritizing the reading experience above all else. The brand personality is intellectual, calm, and sophisticated, targeting a literary and professional audience.

The style is **Minimalist** with a strong **Editorial** influence. It utilizes expansive whitespace to reduce cognitive load and focuses on "content-first" layouts. Visual interest is generated through precise typographic hierarchies and a restrained use of color, rather than heavy decorative elements. The emotional response should be one of focus and clarity, reminiscent of a premium physical journal.

## Colors
The palette is rooted in high-contrast readability. 

- **Primary (Muted Indigo):** Used for primary actions, active states, and subtle branding accents. It provides a sophisticated alternative to standard blue.
- **Secondary (Sage Green):** Reserved for success states, category tags, or "Save" actions to provide a natural, organic counterpoint to the indigo.
- **Neutral (Deep Charcoal):** Applied to all primary text and headings. This is preferred over pure black to reduce eye strain while maintaining maximum contrast against the white background.
- **Background (Crisp White):** The canvas for all content, ensuring a clean, distraction-free environment.

Surface colors for cards and containers should use very light grey tints (`#F8F9FA`) to differentiate from the base background without breaking the minimalist aesthetic.

## Typography
Typography is the core of this design system. We use **Playfair Display** for headlines to establish an authoritative, editorial voice. **Inter** is used for body copy and UI elements to ensure legibility and a modern feel.

- **Body Text:** Use `body-lg` for long-form articles to maximize readability. The line height is intentionally generous (1.6x) to prevent line-skipping.
- **Headlines:** Large display sizes use tight letter spacing for a "tight" editorial look.
- **Labels:** Meta-information (dates, categories) uses uppercase `label-md` with slight letter spacing to differentiate it from narrative text.

## Layout & Spacing
The layout follows a **Fluid Grid** model optimized for mobile-first consumption.

- **Mobile:** 4-column grid with 20px outside margins. 
- **Desktop:** 12-column grid with a maximum content width of 1140px. Article pages should be centered with a narrower 8-column reading width to maintain an ideal characters-per-line count (65-75 characters).
- **Rhythm:** We use an 8px base unit. Vertical rhythm is critical; use `stack-lg` between major sections and `stack-md` between article paragraphs or card elements.

## Elevation & Depth
Elevation is handled through **Ambient Shadows** and **Tonal Layers**. We avoid heavy dropshadows in favor of subtle, highly-diffused blurs that suggest a soft lift from the page.

- **Level 1 (Cards/Inputs):** `0px 4px 20px rgba(0, 0, 0, 0.04)`. This creates a soft separation without appearing "heavy."
- **Level 2 (Dropdowns/Modals):** `0px 10px 40px rgba(0, 0, 0, 0.08)`.
- **Interaction:** On hover/tap, cards may transition to a slightly deeper shadow or a subtle 1px border in the primary color to indicate interactivity.

## Shapes
The shape language is **Soft** but disciplined. 

- **Cards & Containers:** Use `0.25rem` (4px) or `0.5rem` (8px) corners. This maintains a professional, structured look while appearing more modern and accessible than sharp 90-degree corners.
- **Buttons:** Small buttons use `rounded-sm`, while larger call-to-action buttons may use `rounded-lg` for a more tactile feel.
- **Images:** All article imagery should share the same corner radius as the cards (8px) to maintain visual consistency.

## Components
- **Buttons:** Primary buttons are solid Indigo with white text. Secondary buttons are ghost-style with a thin charcoal border. Use generous horizontal padding (24px+) to create an "elegant" elongated look.
- **Cards:** White backgrounds, subtle Level 1 shadows, and 8px border-radius. Card content should have at least 24px of internal padding.
- **Chips/Tags:** Used for categories. Small font size, light grey background (`#F1F3F5`), and 4px radius. No shadows.
- **Input Fields:** Bottom-border only or very light grey outlines. Focus states transition the border to the primary Indigo color.
- **Lists:** Clean, borderless lists with 16px vertical spacing between items. Use a thin 1px separator (`#EEE`) only when necessary for high-density data.
- **Progress Indicator:** A thin 2px bar at the top of the viewport in primary Indigo to show reading progress on long-form articles.