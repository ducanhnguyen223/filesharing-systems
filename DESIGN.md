# Design System: FileSharing 2026 — Calm Dark UI
**Project ID:** 16480794170637879747

## 1. Visual Theme & Atmosphere
The design embodies **"Calm Neo-Minimalism"** — a 2026 trend that moves away from high-contrast neon toward a mature, physically grounded aesthetic. The atmosphere is **quiet, deep, and tactile**, evoking the feeling of a premium leather-bound notebook in a dimly lit studio. Every surface has weight. Every interaction has friction. The UI breathes through generous whitespace and whisper-soft elevation layers.

A barely-perceptible **film grain texture** (2% opacity fractal noise) is layered across the entire viewport, lending a cinematic, analog quality to the digital canvas.

## 2. Color Palette & Roles
* **Void Charcoal** (#0B0B0C): The foundational canvas. Not pure black — a hair of warmth to reduce eye strain. Used for the page background.
* **Elevated Charcoal** (#141414): The primary surface color for cards, containers, and bento cells. One step above the void.
* **Sidebar Slate** (#161617): A marginally distinct shade for the persistent sidebar, creating subtle spatial separation without a harsh divide.
* **Lifted Surface** (#1C1C1E): For elevated UI elements that need to "float" above their containers (modal backgrounds, dropdowns).
* **Deep Well** (#080808): Input field backgrounds — recessed below the surface to create a tactile "input well" effect.
* **Soft Indigo** (#6366F1): The primary action color. Used for buttons, active states, and progress fills. Calm yet confident.
* **Light Periwinkle** (#818CF8): A lighter accent for hover states, focus rings, and highlighted text. The "glow" variant of the primary.
* **Cool Cyan** (#06B6D4): A secondary accent for badges, tags, and informational highlights. Provides visual variety without clashing.
* **Calm Emerald** (#10B981): Success states and positive indicators.
* **Soft Coral** (#EF4444): Danger states, delete actions, and error messages. Used sparingly.
* **Cloud White** (#EAEAEA): Primary text color. Soft off-white that avoids harsh contrast against the dark canvas.
* **Stone Gray** (#888888): Secondary text for labels, metadata, timestamps, and supporting copy.
* **Ash Gray** (#555555): Muted text for tertiary information and disabled states.
* **Pure White** (#FFFFFF): Reserved exclusively for text on primary-colored backgrounds.

## 3. Typography Rules
* **Font Family:** Inter (with system-ui, -apple-system as fallbacks). A highly legible, modern sans-serif chosen for its clean geometry and excellent screen rendering.
* **Headings:** Weight 700, tight letter-spacing (-0.02em) for a dense, editorial quality. H1 at 2rem.
* **Body:** Weight 400, generous line-height (1.6) for breathing room. Antialiased rendering enforced.
* **Labels & Metadata:** Weight 500-600, 0.85-0.9rem, in Stone Gray (#888888).
* **Interactive Text (Links):** Weight 600, Light Periwinkle (#818CF8), no underline by default, underline on hover.

## 4. Component Stylings
* **Buttons (Primary):** Soft Indigo (#6366F1) background, Pure White text, gently rounded corners (12px). Transitions to Light Periwinkle on hover with a fast snap (200ms). Padding 10px 20px, weight 600.
* **Buttons (Ghost):** Transparent background with a ghost border (5% white). Text in Stone Gray, transitioning to Cloud White on hover. Background lifts to 3% white on hover.
* **Cards / Bento Cells:** Elevated Charcoal (#141414) background, ghost border (1px at 5% white opacity), generously rounded (24px). A whisper-soft **inner glow** (inset 0 1px 0 0 at 5% white) gives a subtle top-edge highlight. On hover: border brightens to 10% white, shadow deepens, card lifts 2px.
* **Inputs:** Deep Well (#080808) background — visually "sunken" below the surface. Ghost border, gently rounded (12px). On focus: border glows with Indigo at 30% opacity, surrounded by a soft 4px focus ring at 10% Indigo.
* **Progress Bars:** 6px tall, pill-shaped (full radius). Track at 5% white on dark. Fill in Soft Indigo with a smooth 1s width transition.
* **Modals:** Glass-card styling with Elevated Charcoal background, centered with a dark overlay. Smooth fade-in transition.

## 5. Layout Principles
* **Macro Layout:** A fixed sidebar (280px) + fluid main content area. Sidebar is sticky, full-height, with a ghost border on the right edge.
* **Content Grid:** Bento Grid pattern — `auto-fill` columns with 300px minimum, 24px gap. Items self-organize into a masonry-like flow.
* **Whitespace:** Generous padding throughout. Main content area: 48px. Cards: 24px internal padding. Sidebar: 32px top/bottom, 24px horizontal.
* **Responsive:** Sidebar collapses on ≤1024px. Grid falls to single-column on ≤768px. Content padding reduces to 24px.
* **Depth Strategy:** Elevation is communicated through subtle shadow layering and inner glow, NOT through color brightness. All surfaces share a similar dark tone; depth comes from shadow, not lightness.
