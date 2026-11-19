# Effects-only motion implementation

## Sakuga source audit

Reference: [finktheartist/sakuga-vfx at c3dabb173928a3ad2372183103caf2e6f50953d0](https://github.com/finktheartist/sakuga-vfx/tree/c3dabb173928a3ad2372183103caf2e6f50953d0). The repository's README, MIT license, shared `core.js`, bundled agent skill, and button/toggle/tabs/progress/toast/input/tooltip components were inspected as text. The gallery at [sakuga-vfx.vercel.app/gallery](https://sakuga-vfx.vercel.app/gallery/) was unavailable to this research pass, so no live gallery interactions or timing were claimed.

- License: upstream source identifies the MIT License, copyright Fink The Artist, 2026. This project does not copy upstream code, assets, or the agent skill; it implements a separate geometric system. Retain that license only with any future copied upstream material.
- Architecture: the reference uses vanilla custom elements and Shadow DOM with a shared first-window core; component source includes the core rather than importing it as a package.
- Rendering: the shared engine creates a viewport-fixed, pointer-transparent canvas at a very high stacking order, caps device pixel ratio, tracks frame callbacks with `requestAnimationFrame`, and stops when callbacks/layers/timers drain. Mounted components register frame callbacks, so idle mounted controls can keep work scheduled. Global layers can also compete with dialogs and stacking contexts.
- Springs: the inspected core uses semi-implicit Euler integration with mass 1, stiffness 300, damping 20, and substeps up to roughly 8 ms. Those values describe the inspected source, not universal design settings.
- Reduced motion: the core listens to the system preference and drops/simplifies effects in its calm mode. This source behavior was inspected, not accessibility-audited in a running browser.
- Embedded artwork: `core.js` maps sound-effect words to SVG path data, turns paths into cached canvas graphics, and draws them. Deleting the source strings alone would leave the glyph paths. The toggle source also embeds a large WebP sprite. Both are excluded here; the original components use only circles, transforms, color, and text already present in the product UI.
- Existing agent skill: it prescribes upstream-specific setup, art direction, and sound-effect usage. It is a reference for understanding that project, not installed or reused because those requirements conflict with this effects-only brief.

No upstream source or image was executed or imported. The local research copy is ignored under `output/reference/sakuga/` and is not part of the deliverable.

## Original React components

`assets/react/` is the reusable source copy. The SupplierTrust app has a synchronized copy in `frontend/src/motion/`; `scripts/check-motion-sync.mjs` asserts the files remain identical.

```jsx
<AnimatedButton burst onClick={openInvestigation}>
  Open investigation
</AnimatedButton>

<AnimatedTabs
  label="Investigation sections"
  items={tabs}
  selected={section}
  onSelect={setSection}
/>

<AnimatedProgress label="Review preparation" value={80} />
<AnimatedToast open={saved} onClose={dismiss}>Changes saved.</AnimatedToast>
```

The button uses a brief squash, spring recovery, and six-circle burst. Tabs move one indicator. Toggle state stays in a labeled native checkbox. Progress stays a native `<progress>`. Toast uses `role="status"`; tooltip text is supplemental and appears on hover or focus. Input errors are associated with the input. Nothing runs continuously.

## Build a new effect

1. Name the state transition and its useful purpose.
2. Keep a static, correct final state in CSS/HTML.
3. Add one finite transform/opacity animation at the interaction point.
4. Suppress it when `prefers-reduced-motion` or `[data-motion="off"]` applies.
5. Keep the visual in the component stacking context, pointer-transparent if decorative, and under the control label.
6. Cancel or detach all work on interruption/unmount; test rapid repeat input.
7. Inspect actual frames for overlaps, stray letter-like forms, and mobile clipping.
