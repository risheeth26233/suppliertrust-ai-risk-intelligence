# Product interface design system

## Hierarchy and type

- Give each screen one clear heading, a one-sentence purpose, and a primary action with a predictable outcome.
- Use a compact scale: display/title, section title, body, supporting label. Reserve uppercase and wide tracking for short metadata labels, never long prose.
- Keep body text comfortable to scan, lines moderate in width, and dense records aligned in columns. Prefer existing project fonts and tokens; do not add a typeface dependency for polish alone.
- Pair a restrained display style with a plain, readable body style. Make risk, warning, and status language explicit in text as well as color.

## Layout, color, and density

- Start from the current application shell and token system. Use a spacing rhythm and consistent card edges before adding decoration.
- Use whitespace to group related information; do not create empty cards or oversized hero blocks inside task-oriented dashboards.
- Keep graphite surfaces distinct by luminance and border. Use emerald as an action/positive accent, amber for caution, and red only for destructive/error states. Check text contrast and non-color cues.
- At narrow widths, preserve content order, reachable actions, and readable tables (reflow or intentional horizontal scroll). Prevent page-level horizontal overflow.

## Navigation and contextual actions

- Keep the active destination visible. Use labels that describe the destination, a selected state beyond color, and native links/buttons with normal focus behavior.
- Put an action beside the record it changes. State destructive scope before confirmation and report success only after the operation succeeds.
- Prefer inline descriptions, labels, Help, and useful hover/focus names over circular information controls.
- For keyboard-efficient products, keep tab order predictable and shortcuts discoverable; shortcuts must not replace a usable pointer path.

## Search, filters, and results

- Label search by the values it covers and retain the current query while results update.
- Show active filters and the resulting count. Keep clear/reset available when a filter is active.
- Use native selects where they fit; custom menus need arrow-key movement, Escape, focus restoration, and announced state.
- Preserve empty, loading, no-results, and error states. Do not imply a query matched a supplier or risk indicator unless the data says so.

## Onboarding and progressive disclosure

- Teach one concept per step, show progress, explain the next destination, and give a useful skip/exit path.
- Make the first useful action visible before optional detail. Reveal deeper evidence or caveats near the relevant decision.
- A completion signal must follow completed work; never use celebration to imply trust, verification, or a regulatory outcome.

## Motion

- Treat motion as feedback or orientation. Animate only meaningful state changes; avoid parallax or looping decoration in work surfaces.
- Keep transitions short and consistent, animate transform/opacity where practical, and preserve a static final state.
- Respect `prefers-reduced-motion`, user settings, hidden tabs, and component unmount. See the companion `effects-only-motion` skill for implementation details.
