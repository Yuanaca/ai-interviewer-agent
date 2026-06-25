---
name: Synthetic Intelligence Interface
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c7c4d8'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#918fa1'
  outline-variant: '#464555'
  surface-tint: '#c3c0ff'
  primary: '#c3c0ff'
  on-primary: '#1d00a5'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#4d44e3'
  secondary: '#b3c5ff'
  on-secondary: '#002b75'
  secondary-container: '#0266ff'
  on-secondary-container: '#f9f7ff'
  tertiary: '#4edea3'
  on-tertiary: '#003824'
  tertiary-container: '#006e4b'
  on-tertiary-container: '#67f4b7'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#dae1ff'
  secondary-fixed-dim: '#b3c5ff'
  on-secondary-fixed: '#001849'
  on-secondary-fixed-variant: '#003fa4'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1440px
  gutter: 24px
---

## Brand & Style

The design system is engineered for a high-stakes, professional AI environment. The brand personality is **intelligent, reliable, and analytical**, projecting an aura of cutting-edge precision. It avoids the playfulness of consumer AI in favor of a **Modern Enterprise AI** aesthetic—a fusion of corporate reliability and futuristic technical sophistication.

The visual style utilizes **Dark-Mode Minimalism** with **Glassmorphic** accents. High-contrast data visualization and subtle glowing states signify active AI cognition. The interface should feel like a high-performance command center: spacious, focused, and operationally dense without being cluttered.

## Colors

The palette is anchored in a deep, nocturnal foundation to minimize eye strain during long technical interviews.

*   **Primary (Deep Indigo):** Used for core actions, branding, and primary interactive states. It conveys depth and institutional trust.
*   **Secondary (AI Blue):** Reserved for "Active AI" states, processing indicators, and highlights. 
*   **Surface & Background:** The background is a solid `#0F172A`. Component surfaces use `#1E293B` with varying opacities to create depth.
*   **Accents:** Cyber Green (`#10B981`) is strictly for success states and high-confidence AI scores. Neon Blue (`#38BDF8`) is used for the "Processing Glow" to indicate real-time RAG (Retrieval-Augmented Generation) analysis.

## Typography

This design system utilizes **Inter** for all UI elements to ensure maximum legibility and a neutral, systematic feel. To lean into the "Tech" aspect of the product, **JetBrains Mono** is introduced as a secondary label font for metadata, confidence scores, and code-like data snippets.

Headlines should use tighter letter-spacing to appear more authoritative. Body text maintains standard spacing for readability. All typography is rendered in high-contrast whites or silver-greys against the dark background.

## Layout & Spacing

The layout follows a **12-column fluid grid** for desktop, transitioning to a **4-column grid** for mobile. 

*   **Rhythm:** A strict 8px grid system governs all margins and paddings. 
*   **Density:** The "Interview Intelligence" views utilize a high-density layout to maximize data visibility (transcripts, sentiment graphs, and resume matching).
*   **Structure:** Content is housed in "Modules." Modules should have a consistent `24px` (md) gap between them.
*   **Safe Areas:** Large side-margins (`40px+`) are used on landing and dashboard views to maintain a premium, cinematic feel.

## Elevation & Depth

Depth is communicated through **Tonal Layering** and **Glassmorphism**, rather than traditional heavy shadows.

1.  **Base Layer:** `#0F172A` (Background).
2.  **Surface Layer:** `#1E293B` (Cards/Panels).
3.  **Glass Layer:** Semi-transparent overlays (`rgba(30, 41, 59, 0.7)`) with a `12px` backdrop blur for floating modals or sticky navigation.
4.  **The "Active Glow":** Active AI nodes or buttons use a `0px 0px 15px` outer glow using the Secondary Blue color at 30% opacity to simulate light emitting from the interface.
5.  **Borders:** Use low-contrast 1px strokes (`#334155`) to define boundaries without adding visual weight.

## Shapes

The design system uses a **Soft** shape language. While the brand is professional, the `0.25rem` (4px) corner radius prevents the UI from feeling "sharp" or "hostile," striking a balance between precision and modern software aesthetics.

*   **Small Elements (Checkboxes, Tags):** 4px (Soft).
*   **Medium Elements (Buttons, Inputs, Cards):** 8px (Large).
*   **Large Elements (Dialogs, Feature Panels):** 12px (Extra Large).

## Components

*   **Buttons:** Primary buttons are solid Indigo. "AI Action" buttons use a gradient from Deep Indigo to AI Blue with a subtle pulse animation during processing.
*   **Inputs:** Dark filled backgrounds with a 1px border. On focus, the border transitions to AI Blue with a subtle `2px` glow.
*   **AI Flow Diagrams:** Connecting nodes use thin, animated "marching ants" lines in Neon Blue to indicate data flow.
*   **Confidence Chips:** Small badges using Cyber Green for high confidence (80%+) and Amber for low confidence, utilizing a mono-font for the numerical value.
*   **Data Tables:** Borderless design with alternating row highlights (Zebra striping) using a slightly lighter navy.
*   **Glass Cards:** Used for real-time interview transcripts. The background blur allows the underlying dashboard gradients to peek through, creating a sense of sophisticated layering.