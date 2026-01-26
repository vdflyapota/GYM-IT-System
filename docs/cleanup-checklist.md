# Cleanup Checklist

- Remove tracked HTML/CSS/JS outside `templates/` and `static/` unless referenced by templates
- Consolidate UI into ≤2-click flows: registration, tournament setup, result entry
- Delete orphan assets (images, fonts) not referenced by templates or CSS
- Delete old prototypes, mockups, and unused scripts
- Move sensitive code or secrets out of repo (use `.env`)
- Verify imports are one-directional and remove cross-module or cyclic dependencies
- Run `make lint` and fix formatting/security warnings
- Run `make test` and ensure green test suite
