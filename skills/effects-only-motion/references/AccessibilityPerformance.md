# Accessibility and performance review

## Accessible interaction

- Keep actual `<button>`, `<input>`, `<progress>`, `<details>`, and tab semantics. Do not use `div` plus click for controls.
- Give icon-only controls a name. Ensure all hit targets are comfortable on touch, and visible focus is not removed.
- Use roving focus and arrow keys for a true tablist; otherwise use navigation semantics. Keep the destination or effect clear in text.
- Mark decorative SVG `aria-hidden="true"` and `focusable="false"`. Never rely on motion or color as the sole status cue.
- Give live status to asynchronous completion only after the operation returns successfully. Keep errors and failure states available as text.
- Keep tooltip wording supplementary, Escape-dismissible, and available on focus; do not make required help hover-only.

## Motion and cleanup

- Honor `prefers-reduced-motion` and a product-level off setting. Do not animate a status change in a way that blocks the control.
- Prefer finite WAAPI/CSS transitions over a permanent animation loop. Do not add document-wide pointer listeners or canvas layers for a local effect.
- Cancel the prior animation when replaying; cancel and clear animations, observers, timers, and listeners on unmount or page hiding.
- Use transform/opacity rather than layout properties for brief feedback. Keep particle counts bounded and effects inside their component's stacking context.
- Skip animation while the document is hidden; settle to the final state if motion is disabled mid-flight.

## Verification

- Check build output, no console errors, correct action result, and no extra network or runtime dependency.
- Exercise pointer, keyboard, repeated clicks, interrupted animation, unmount, disabled, failure, and system reduced motion.
- Inspect screenshots at intermediate frames and at desktop/mobile widths. Look for clipping, unwanted SVG paths/images/text, focus loss, and overlays blocking clicks.
- Confirm there are no unbounded `requestAnimationFrame` loops and no animation continues after its component unmounts.
