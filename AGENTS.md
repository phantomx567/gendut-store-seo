# Project instructions — Gendut Store

For EVERY new landing page and every landing-page revision, use UI/UX Pro Max before implementation or visual review. Read these physical resources in order:

1. `.agents/skills/ui-ux-pro-max/SKILL.md` (pinned MIT source and provenance in the same directory).
2. `design-system/gendut-store/MASTER.md`.
3. `design-system/gendut-store/PROJECT-DECISIONS.md` and the applicable `design-system/gendut-store/pages/<page>.md`, if present. Page decisions override generated suggestions. Explicit current user instructions take precedence.
4. `references/quick-reference.md` in the skill for relevant web rules; read `references/pro-rules.md` with its native-app scope understood.

Reza's latest explicit direction is DARK PURPLE with restrained neon. Earlier white/lavender UI direction is superseded. Keep the existing new controller mascot; do not regenerate it or reuse the old thumbs-up by default. Preserve original GS logo and verified game icons. No invented promo, metrics, partnership or social proof.

The actual implementation is vanilla HTML/CSS/JS with Python static build. Do not assume React, Tailwind or introduce a framework/WebGL/animation dependency because a search recommends one. The vendor subset supports design-system and product/style/color/landing/typography/ux/web/gsap; absent datasets are unsupported.

For a new page/system-wide direction, run the REQUIRED design-system query with 2–5 meaningful terms and explicit `--output-dir` pointing at this repository root. Invoke `python3 <absolute-repo-path>/.agents/skills/ui-ux-pro-max/scripts/search.py ...`. Read existing MASTER before generating; never use `--force` without explicit authorization. Keep one writer for design-system output. Verify category/source identities and fit; retry once if off-topic/empty and label fallback honestly. Save exact command, result and applied overrides. Read the Python before executing a changed upstream version. No installers or extra paid services are authorized by the skill.

Before delivery, QA the actual built page at 375/390,768,1024 and1440px, including keyboard focus, links/search/filter states,200% zoom, dark contrast (normal text>=4.5:1, large text/meaningful controls>=3:1), no overflow/obscured focus and reduced motion. Prefer44px web hit areas as project usability target; do not confuse native pt/dp rules with web WCAG. Record screenshots/results and limitations. The generated MASTER is guidance, not proof of QA. Implementation and independent QA remain separate; no owner approval or publish claims without actual authorization/evidence.


## Editorial scene covers — current owner direction, 25 October 2026

Use epic landscape art recognizable from actual game characters/world references, not generic castle/island wallpaper, catalog icons, giant logos or blank purple halves. Curated cover metadata is separate from immutable approved Article documents. The assigned scene appears at both hub-card top and Article opening; content-specific instructional diagrams stay inside below the lead, with approved bytes unchanged. Existing GS header supplies brand identity; no social footer/CTA.

Every Article path must have an explicit curated cover assignment matching an approved related game path and exact asset SHA. New Articles require a newly reviewed image/variant by default; reuse must be deliberate and independently checked, never automatic per-game fallback. Missing assignment/qualified cover blocks import/build/release. Multiple variants can belong to one game. Validate local content-addressed path, MIME, hash, dimensions and honest illustration ALT; format-only compression must disclose lossy delivery. Root views actual original/delivery and integrated390px preview before freeze; Sari independently checks all responsive/text200/focus/contrast, source/asset and withdrawal guards. Unreferenced scene files are omitted from output after withdrawal. No new workflow stage, runtime or automation.
