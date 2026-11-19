# Personal UI and motion skills

This repository is the versioned source for two independent Codex skills:

- `premium-product-ui/` — research-backed product interface guidance.
- `effects-only-motion/` — accessible React microinteractions with an original geometric-effects component set.

Run `scripts/install-skills.ps1` to copy both into the default user-level directory (`%USERPROFILE%\.codex\skills`) or `$env:CODEX_HOME\skills`. The script refuses to overwrite either existing skill. Codex may need a new session to refresh its skill catalog. Keep `effects-only-motion/assets/react/` synchronized with `frontend/src/motion/`; CI checks that they match.
