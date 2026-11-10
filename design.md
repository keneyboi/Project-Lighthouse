Here is the complete, self-contained `design.md` file ready to be saved directly in your project root or docs folder:

```markdown
# DESIGN.md — Project Lighthouse UI/UX System & Design Architecture

## 1. Vision & Core Philosophy

**Project Lighthouse** is a trauma-informed emergency sanctuary locator and discreet safety-dispatch web application. It connects people in immediate domestic vulnerability with verified safe havens, emergency desks, and shelters.

### Core Aesthetic Pillars
* **Trauma-Informed & Non-Triggering:** Replaces panic-inducing red alert banners, aggressive borders, and jarring warning dialogs with calm, grounding, monochromatic typography and plain-text error handling.
* **Editorial Noir & Film Minimalist:** Merges high-fashion editorial serif typography (`Serif-regular`) with clean monospace system cues (`Doto`) and modern sans-serif operational text (`SF Pro Display`).
* **Deep Monochrome Architecture:** Pure void black base (`#000000`) paired with layered obsidian cards (`#080808` to `#141414`), hairline slate borders (`#1c1c1c` to `#242424`), and high-contrast stark bone-white CTA buttons (`#ffffff`).
* **Lantern Beacon Accent (Used Selectively):** A single warm lantern glow (`#ff9d42`) reserved strictly for active map pins, interactive tags, and confidential secret verification passphrases.
* **Discreet & Zero-Trace First:** Features secret passphrase verification, discreet check-in dispatch pings, zero tracking traces, and a persistent `Quick Exit (Esc)` safety mechanism.

---

## 2. Color Tokens & Surface Hierarchy

| Token Name | Hex / RGBA | Role / Usage Context |
| :--- | :--- | :--- |
| **`--canvas-void`** | `#000000` | Full page backdrop across all landing, auth, and subpage templates |
| **`--surface-card`** | `#0b0b0b` / `#0a0a0a` | Container frames, auth cards, section modules |
| **`--surface-input`** | `#141414` | Form inputs, unselected list items |
| **`--surface-input-focus`**| `#181818` | Active input field background |
| **`--surface-elevated`** | `#212121` | Floating interactive cards, modal background surfaces |
| **`--surface-floating-card`**| `#ffffff` | Floating interactive cards on Leaflet map canvas |
| **`--border-subdued`** | `#1c1c1c` / `#1f1f1f` | Subtle card borders, horizontal dividers, footer lines |
| **`--border-active`** | `rgba(255, 255, 255, 0.35)` | Input focus rings, card hover highlights |
| **`--text-primary`** | `#ffffff` / `#f5f5f5` | Editorial titles, prominent headings, CTA buttons |
| **`--text-secondary`** | `#888888` / `#999999` | Subtitles, helper text, physical addresses |
| **`--text-muted`** | `#4a4a4a` / `#555555` | Placeholders, inactive arrow controls |
| **`--accent-beacon`** | `#ff9d42` | Active pins, distance badges, secret phrase box borders |
| **`--accent-beacon-soft`**| `rgba(255, 157, 66, 0.12)`| Backgrounds for badges and confidential indicators |
| **`--status-safe`** | `#15803d` / `#4ade80` | "Open 24/7" badge, trace-free green session indicator |
| **`--surface-contrast`**| `#d8d8d8` | "How It Works" accordion panels (studio light grey) |

---

## 3. Typography Hierarchy

### Font Families
* **Editorial Serif:** `'Serif-regular', serif`
  * Used for: Section titles (`h1`, `h2`), auth card headers, lowercase input labels, and secret verification phrases.
* **Modern System Sans:** `'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif`
  * Used for: Body copy, input values, button labels, operational descriptions, and footer links.
* **Monospace Data:** `'Doto', monospace`
  * Used for: Step indices (`1`, `2`, `3`), map pin numbering, technical metrics, and status badges.

### Typographic Rules & Scales
* **Hero Headline:** `5.8rem`, `line-height: 0.95`, `letter-spacing: -0.02em`, `font-weight: 400`, color `#ffffff`.
* **Section Header H2:** `3.5rem`, `line-height: 1.0`, `letter-spacing: -0.01em`, color `#ffffff`.
* **Auth Card Title:** `3.6rem` - `3.8rem`, `line-height: 0.95`, lowercase or title case, color `#f5f5f5`.
* **Auth Form Input Labels:** `1.45rem` - `1.5rem`, `'Serif-regular'`, strictly lowercase, color `#e2e2e2`.
* **Body / Subtitle Copy:** `0.95rem` - `1.05rem`, `line-height: 1.5`, color `#888888`.
* **Primary Button Text:** `13.5px` - `14px`, `font-weight: 700`, `'SF Pro Display'`, color `#000000`.

---

## 4. Layout Architecture & Component Rules

### 4.1 Fixed Navigation Header
* Glassmorphic header (`backdrop-filter: blur(12px); background: rgba(0, 0, 0, 0.6)`).
* Displays branding ("project lighthouse"), internal anchor links, and an orange emergency button labeled `Quick Exit (Esc)`.
* **Global Rule:** All subpages and authentication containers must apply at least `padding-top: 130px` to `140px` to ensure zero overlap.

### 4.2 "How It Works" Selective Horizontal Accordion
* Flex container (`height: 420px; gap: 16px`).
* **Panels (`.hiw-panel`):**
  * Studio grey surfaces (`background-color: #d8d8d8`, color `#000000`, `border-radius: 8px`).
  * Default state: Panel 1 is expanded (`flex: 3.2`), Panels 2, 3, 4 are collapsed (`flex: 1`).
  * Selective Hover: Panel 1 stays open when directly hovered. Hovering over panels 2, 3, or 4 collapses panel 1 to `flex: 1` via `.hiw-accordion-group:has(.hiw-panel:not(.active):hover) .hiw-panel.active`.
* **Vertical Label Geometry:**
  * Number at top (`font-size: 2.4rem`).
  * Vertical text (`writing-mode: vertical-rl; transform: rotate(180deg)`), anchored with `bottom: 50px` to prevent bottom-edge clipping.

### 4.3 Safe Havens Interactive Map & Overlay Carousel
* **Map Canvas:** Grayscale-inverted OpenStreetMap tiles:
  ```css
  .sh-map-canvas .leaflet-tile {
    filter: grayscale(100%) invert(90%) contrast(120%) brightness(95%);
  }

```

* **Map Pins:** Circular monochrome badges with numeric counters. Active state shifts to lantern orange (`#ff9d42`) with halo bloom (`box-shadow: 0 0 16px rgba(255, 157, 66, 0.9)`).
* **Floating Bottom Carousel:**
* Overlay positioned at `bottom: 24px`, leaving room for left/right navigation arrows.
* Headroom padding (`padding: 20px 8px 10px 8px`) prevents hover scale/shadow cuts.
* Cards use percentage widths (`calc((100% - (16px * 2)) / 3)`) to ensure exactly 3 cards fit cleanly without partial slicing.
* Card hover effect: `transform: translateY(-4px) scale(1.02)` with white halo glow.


* **Verification Phrase Modal:**
* Backdrop blur (`rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px)`).
* Prominent dashed container (`#1c1c1c`, border `1px dashed rgba(255, 157, 66, 0.5)`) presenting the confidential passphrase in serif italics.



### 4.4 Authentication Layouts (Login & Register)

* **File Architecture:**
* `static/css/common/auth_layout.css`: Shared full-bleed vignette, postcard stacks, shuffling animations, form primitives, and buttons.
* `static/css/login/login.css`: Login-specific card sizing (`max-width: 580px`, padding `56px 52px`).
* `static/css/register/register.css`: Register-specific card sizing (`max-width: 620px`) and two-column grid rows (`auth-grid-row`).


* **Postcard Shuffling Animation:**
* Two stacks flanking the card with matte white photo borders and monochrome filters.
* Default angles: Left stack rotated `-6deg` / `3deg`; Right stack rotated `5deg` / `-3deg`.
* Hover interaction: Top card shifts outward (`translate(±50px, -20px)`), mimics hands shuffling through polaroids.


* **Full-Bleed Viewport Vignette:**
* Uses `position: fixed; width: 100vw; height: 100vh; z-index: 3`.
* Deep black center (`rgba(0, 0, 0, 0.96)`) feathering out to transparent edges so shifting cards are never clipped by fixed-width boundaries.


* **Form Inputs & Validation Styling:**
* Low-glare dark inputs (`#141414`, border `#242424`, `border-radius: 10px` to `12px`).
* Focus state uses soft white glow (`box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05)`).
* Errors are plain white text (`color: #ffffff; opacity: 0.85; font-size: 12px; margin-top: 6px;`). No red boxes, no red backgrounds.
* Default Django helper lists and bullet points are suppressed via `.auth-field-group ul, .auth-field-group .helptext { display: none !important; }`.



### 4.5 Monochromatic Global Footer

* Pure `#080808` canvas with hairline `#1f1f1f` dividers.
* 4-column structured grid:
1. *Safe Havens*
2. *24/7 Lifelines* (National Emergency 911, VAWC 1343, PNP Desks)
3. *Partners*
4. *About Lighthouse*


* Bottom metadata bar with legal privacy links and emergency notice: *"For urgent danger, call 911 immediately."*

---

## 5. Responsive Breakpoint Rules

| Breakpoint | Target Screen | Behavioral Adaptation |
| --- | --- | --- |
| **`> 1280px`** | Large Screens | Postcards fully expanded with generous gap (`60px`). Exactly 3 map cards visible. |
| **`1040px – 1280px`** | Medium Laptops | Postcards scale down proportionally (`width: 260px`). |
| **`768px – 1040px`** | Tablets | Postcard stacks and vignette hidden (`display: none`). Map carousel shifts to 2 cards per view. Accordion becomes vertical stack. |
| **`< 640px`** | Mobile Phones | Single-column forms (`auth-grid-row` drops to 1fr). Card padding reduced (`32px 22px`). Navigation arrows hide in favor of touch swipe. |

---

## 6. Implementation Guide for New Pages

When adding new views or dashboards to Project Lighthouse:

1. **Extend `base.html`:** Ensures global glass header, escape-key listener, and monochrome footer are automatically inherited.
2. **Include CSS stylesheets in proper cascade order:**
```html
{% block extra_css %}
  <link rel="stylesheet" href="{% static 'css/common/auth_layout.css' %}">
  <link rel="stylesheet" href="{% static 'css/your_feature/feature.css' %}">
{% endblock %}

```


3. **Preserve Form Layout Hierarchy:**
* Container canvas: `#000000`
* Main cards: `#0b0b0b` with border `#1c1c1c` and radius `20px`
* Inputs: `#141414` with border `#242424` and white focus outline
* Submit button: `#ffffff` background with `#000000` text
* Field labels: `'Serif-regular'`, lowercase


4. **Preserve Safety Guardrails:** Never introduce aggressive alert reds or remove the instant quick-exit pathway.

```

<FollowUp> Would you like to create a companion `components.html` template showcasing working examples of all these inputs, badges, and buttons in one place? </FollowUp>

```