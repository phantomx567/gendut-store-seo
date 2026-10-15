# Local usage

Read SKILL.md unchanged from the pinned source, then the project's MASTER.md and PROJECT-DECISIONS.md. User decisions override generated recommendations.

Use an absolute path to this vendored script, for example:

```bash
python3 /workspace/github/gendut-store-seo/.agents/skills/ui-ux-pro-max/scripts/search.py "gaming ecommerce dark purple" --design-system --persist -p "Gendut Store" --output-dir /workspace/github/gendut-store-seo --json
```

Existing MASTER files are preserved. Read them before considering a new generation; do not use --force without explicit authorization. This project already has a verified Gaming result. The single shared MASTER was created by Niko and checked independently by Nara with the same query; a skipped_exists result is not a newly created file.

This is a minimal copied subset, not an installed cloud plugin. Supported data: product, style, color, landing, typography, ux, web, gsap and design-system reasoning. The repo uses vanilla HTML/CSS/JS with a Python static build. No exact vanilla stack dataset is supplied; do not substitute React or html-tailwind. Charts/icons/google-fonts and framework-specific datasets are absent; get a separately authorized pinned subset if actually needed rather than claiming a match.

No installer, external Python dependency, runtime animation library, service account or paid API is needed. A recommended style is guidance: the user's dark-purple palette, existing controller illustration, performance and accessibility requirements take precedence over generic 3D/parallax or static-asset anti-pattern suggestions.
