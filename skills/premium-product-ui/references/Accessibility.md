# Accessibility and UI quality checklist

## Semantics and keyboard

- Use native buttons, links, inputs, selects, checkboxes, progress, and details/summary where possible.
- Every control has a visible or programmatic name. Do not make a noninteractive card focusable or replace a native control with a visual-only imitation.
- Tab order follows visual/task order. Focus is visible, not clipped, and restored after dialogs close. Escape dismisses transient layers when appropriate.
- Tabs follow the tab pattern and support arrow keys, Home, and End if implemented as a tablist. Otherwise use ordinary navigation links/buttons.

## Content and state

- Use a real heading hierarchy and meaningful labels; avoid relying on color, icons, or tooltip-only copy.
- Associate validation text with its field and mark invalid fields. Announce async status and errors without moving focus unexpectedly.
- Show loading, empty, filtered-empty, error, selected, disabled, and success states. Success follows verified completion.
- Provide text for warnings and risk limits. Do not overstate what a score or source proves.

## Visual and motion

- Check contrast for body text, metadata, focus rings, borders, and disabled states. Keep status distinguishable without color alone.
- Preserve content reflow at 320–390 px and 200% zoom; avoid clipped menus and page-level horizontal scroll.
- Check `prefers-reduced-motion: reduce` and any in-product motion-off setting. Do not start an animation loop while idle.
- Ensure decorative SVG/canvas layers are `aria-hidden`, pointer-transparent, bounded, and cannot cover controls.

## Verification

- Build production and exercise the relevant flow in a real browser.
- Test keyboard operation and focus return; inspect reduced motion; capture narrow and wide screenshots.
- Check console/page errors and any network failures. For changes to secure demos, confirm public write/upload/refresh controls remain unavailable.
