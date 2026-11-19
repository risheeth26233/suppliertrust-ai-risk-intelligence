---
name: effects-only-motion
description: Design, implement, or review accessible React microinteractions, spring motion, animated controls, reduced-motion behavior, or motion performance. Use when adding interaction feedback without decorative lettering.
---

# Effects-only motion

Use the smallest motion that helps a person understand a press, selection, reveal, progress change, or result. Inspect the existing component and state first; preserve native behavior, the product theme, data flow, and security restrictions.

## Hard constraints

- No Japanese characters, manga sound-effect graphics, comic lettering, anime branding, or decorative replacement text.
- Inspect SVG paths, sprites, raster images, and generated graphics; removing text strings is not enough to remove baked glyphs.
- No global canvas/effects layer, uncontrolled particle system, idle animation loop, or motion that blocks input or hides content.
- A visual success state may follow only a confirmed successful operation.
- Keep controls usable without animation and honor system/product reduced-motion settings.

## Workflow

1. Read `references/Implementation.md` and inspect the target flow, callers, existing tests, and package dependencies.
2. Prefer existing platform/library features. The original reference implementation is in `assets/react/`; its synchronized application copy is `frontend/src/motion/` in this repository.
3. Use finite, local Web Animations API/CSS/SVG effects; cancel on replacement, reduced motion, hidden tab, and unmount.
4. Keep native semantics and stable final styles. Animate only transform/opacity when practical; never animate text into glyph-like shapes.
5. Run the small spring self-check, browser interaction test, production build, keyboard check, mobile width check, and reduced-motion check. Inspect rendered frames.

## References

- `references/Implementation.md` records the source audit and component examples.
- `references/AccessibilityPerformance.md` covers semantics, cleanup, and review.
- `assets/react/` contains the original, dependency-free component implementation. It uses React as the host project already does; do not install another animation dependency to reuse it.
