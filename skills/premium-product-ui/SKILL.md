---
name: premium-product-ui
description: Design or refine professional web product interfaces, dashboards, workflows, search, onboarding, typography, responsive layouts, or accessibility. Use when building or improving UI/UX in React or another web stack.
---

# Premium product UI

Start with the user's task, the existing design system, routes, data contracts, and trust boundaries. Keep working flows and security rules intact. Before editing, list the affected screens, shared components, tests, and breakage risks.

## Workflow

1. Inspect the actual application at desktop and mobile widths. Separate observed reference behavior from inferred recommendations; never claim an interaction was tested when it was not.
2. State the user's next action and the destination or outcome before adding visual polish. Reuse existing components, icons, tokens, and text. Prefer clear descriptions and native navigation over decorative info buttons.
3. Use hierarchy, spacing, typography, and restrained color to make dense information scannable. Adapt the graphite/emerald examples only when they fit the product.
4. Preserve native semantics, keyboard behavior, focus visibility, loading/error/empty states, and reduced-motion support.
5. Make the smallest complete change. Verify the production build and the relevant real browser paths at narrow and wide widths; include keyboard and reduced-motion checks for interactive work.

## References

- `references/DesignReferences.md` records what was accessible on the research sites and separates observation from application guidance.
- `references/DesignSystem.md` covers hierarchy, layout, typography, navigation, onboarding, and search/filter patterns.
- `references/Accessibility.md` is the implementation and review checklist.
- `references/Examples.md` contains concise React patterns.

Do not copy any brand identity, assets, or exact compositions. Use the references as design reasoning, not as a request to imitate a particular brand.
