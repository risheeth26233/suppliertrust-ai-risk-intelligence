# Component examples

The code below imports the original implementation shipped in `assets/react/`.

## Button press and impact

```jsx
import {AnimatedButton} from './assets/react/components.jsx';

<AnimatedButton burst onClick={openInvestigation}>
  Open investigation
</AnimatedButton>
```

The effect is decorative and bounded; the same button works with motion disabled.

## State transition and reduced motion

```jsx
const [selected, setSelected] = useState('identity');

<AnimatedTabs
  label="Supplier review sections"
  items={sections}
  selected={selected}
  onSelect={setSelected}
/>
```

The current tab remains selected in static markup; the indicator is an enhancement. `AnimatedToggle` is a labeled native checkbox, while `AnimatedProgress` clamps invalid values to a valid range.

## Completion after a real result

```jsx
const [status, setStatus] = useState('idle');
async function download() {
  setStatus('preparing');
  try {
    const response = await fetch(reportUrl);
    if (!response.ok) throw new Error('Report unavailable');
    const file = await response.blob();
    startDownload(file);
    setStatus('ready');
  } catch {
    setStatus('error');
  }
}
```

Only show a ready state after the response and handoff succeed. Keep a visible error path; a click alone is not success.
