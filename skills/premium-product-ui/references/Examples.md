# React examples

Use the project's existing components and test setup first. These patterns are intentionally small.

## Search with a visible result count and reset

```jsx
<label className="search-field">
  <span className="sr-only">Search suppliers by name, country, or category</span>
  <input value={query} onChange={event => setQuery(event.target.value)} />
  {query && <button type="button" onClick={() => setQuery('')}>Clear search</button>}
</label>
<p role="status">{visibleRows.length} of {allRows.length} suppliers</p>
```

## Destination navigation with explanation

```jsx
<nav aria-label="Supplier investigation sections">
  <button type="button" aria-current={page === 'evidence' ? 'page' : undefined}
    title="Inspect recorded sources and their limitations"
    onClick={() => onNavigate('evidence')}>Evidence</button>
</nav>
```

For an accessible description, prefer nearby page copy; reserve `title` for a short supplementary hint, not essential instructions.

## Progressive disclosure

```jsx
<details>
  <summary>What contributes to this indicator?</summary>
  <p>Read the recorded basis and its limits before taking action.</p>
</details>
```

Keep meaningful explanation in the DOM and usable without animation.
