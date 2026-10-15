# Nara — UI/UX Pro Max design handoff

Source pin:56ea9cf174ed86786187daa9de0e6247cb0747e4, MIT Next Level Builder. Vendor `.agents/skills/ui-ux-pro-max/`, unchanged original files plus LICENSE/ATTRIBUTION/PROVENANCE. No installer, network script or added service. Local source clone reused, not downloaded again.

Search command actually run by Nara after Python inspection:
`python <repo>/.agents/skills/ui-ux-pro-max/scripts/search.py "gaming ecommerce dark purple" --design-system --persist -p "Gendut Store" --output-dir /workspace/github/gendut-store-seo --json`
Log: `/workspace/scratch/seo-redesign/nara-uiux-design-system-search.json`. Gaming product/reasoning/color, Gaming Bold typography,3d-and-hyperrealism style and Feature-Rich Showcase landing are verified nonempty identities; reasoning_default=false. Persistence honestly returned skipped_exists: Niko had already generated the same MASTER at15:31:04 from the same pin/query. Nara read it and PROJECT-DECISIONS, did not overwrite or force. This is ONE shared design system, not two generated files.

## Applied decisions for Niko and Sari

Latest user palette is DARK PURPLE, modest neon; white page backgrounds are rejected. MASTER's white modal, rose CTA, Three.js/parallax and anti-static suggestions are not adopted. PROJECT-DECISIONS overrides them; keep the existing static controller mascot, no new runtime. This supersedes the white/lavender palette in Nara's earlier asset handoff while preserving its pose/layout/asset identity.

Concrete shared palette follows Niko's current dark candidate: canvas `#110B1C`, surface `#20152F`, raised `#2B1D3D`, foreground `#F7F3FF`, secondary text `#C0B5D0`, primary `#7C3AED` with white label, hover `#6D28D9`, neon focus `#64E4D4` and lavender accent `#C2A4FF`. This applies the Gaming match plus the user's dark-purple override; it is not claimed verbatim generator output. Use solid surfaces for text; restrained violet/cyan glow behind art only. Do not use neon for every border. The earlier alternative token proposal in the search scratch log is not a second implementation palette.

Nara calculated solid sRGB WCAG contrast: foreground/canvas 17.657:1; secondary/surface 8.896:1 and secondary/raised 7.996:1; accent/surface 8.306:1; white/default primary 5.699:1 and white/hover 7.105:1; focus/raised 10.098:1; search border/surface 4.161:1. Decorative border `#443451` against surface is only 1.534:1: it must not be the sole functional control boundary or focus cue. These are token-pair calculations, not proof for rendered gradients, opacity, geometry or all states. Calculation and exact CSS snapshot hash: `/workspace/scratch/seo-redesign/nara-uiux-contrast.json`. Sari independently checks the actual rendered candidate.

Typography: Gaming Bold returns Russo One/Chakra Petch. On this static site keep existing system sans for speed/offline robustness unless Niko deliberately supplies licensed font files; a search URL alone is not installed typography. H1 clamp36–64px/1.08, H2 28–36/1.2, body16–18/1.6, card title18/1.3, secondary label14/1.5; max2 families, body400 and headings650–750 with available font weights. No clipped labels, essential text<14px or all-caps paragraphs.

Spacing:4,8,12,16,24,32,48,64,96px. Max content1200px; desktop gutters32px, mobile20px. Section gaps64–96 desktop/48–64 mobile. Radius16px cards,12px inputs/buttons. Card borders subdued, focus indicators distinct. Preserve HTML heading order and visible search label.

Hero: desktop copy left48–52%, one controller mascot right44–48%,460–560px contain, original logo separate. Mobile375/390: copy+primary action first, mascot below at280–340px, no fixed hero height or image overlay. No horizontal scroll and no blank tall strip; concise copy leads to game grid. Keep mascot hands/controller/shoes visible, reserved image dimensions and no duplicated mascot. Reuse existing transparent PNG; no new imagegen. Game colors come from Marco's seven verified original icons, not generated logos or unapproved staff banners.

Product cards: real anchor links; one clear name/platform/region where known. Entire card operable by keyboard, no nested competing links. Default raised dark surface; hover border/brightness and subtle shadow without reflow; focus-visible2–3px cyan outline+3px offset; pressed darker surface; disabled only if actually unavailable with text and semantic state. Search empty result gives a readable reset action. Never invent stock/promo/sales counts. Minimum44px project target for controls with8px gaps.

Motion:150ms color/opacity feedback, no automatic float/parallax/loop, no carousel requirement. `prefers-reduced-motion: reduce` removes transform/entrance/smooth scrolling; all content remains visible and usable with JS absent where possible. No GSAP dependency despite dataset support.

QA acceptance: rendered desktop1440,1024/tablet768 and375/390 mobile plus landscape;200% zoom, keyboard navigation, focus not obscured by header, search/filter no-results/recovery, actual destinations. Measure text>=4.5:1, large text and meaningful control boundaries>=3:1 in default/hover/focus states; focus cyan is functional, not decorative-only. Check original logo ratio, mascot fit, game icons and real firstfold. Capture screenshots and actual measurements. This brief/vendoring is not a declaration that implementation or QA has passed.

## Verification and source scope

All 16 original skill/reference/script/CSV files and the MIT LICENSE were compared byte-for-byte against `git show 56ea9cf174ed86786187daa9de0e6247cb0747e4:<path>`; all match. Four Python scripts parse; inspected imports are standard library plus the three local modules, with no dynamic eval/exec calls, network client or subprocess import. Search only reads local CSV and persists to the explicit repository output directory without `--force`. Verification evidence: `/workspace/scratch/seo-redesign/nara-uiux-verification.json`.

Supplemental query `dark mode contrast --domain ux --json` returned three verified UX matches: Contrast Readability, Color Contrast and Focus Appearance (the last is explicitly AAA guidance, not an invented AA requirement). Log: `/workspace/scratch/seo-redesign/nara-uiux-contrast-search.json`. The vanilla web stack has no exact stack dataset in this subset, so no React/Tailwind stack search or fabricated stack match is presented. Use stack-agnostic web/reference guidance and existing vanilla implementation.

