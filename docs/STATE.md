# Current state

A one-page snapshot so any agent (or person) can orient fast without re-reading every doc.
Update it when direction changes or a milestone lands. Longer context lives in `AGENTS.md`,
`docs/decisions.md` and `docs/production-plan.md`.

## Where we are

- Everything through PR #9 (the Supabase plan) is merged into `main`. No feature branch open.
- Latest commit: `73df84b` on `main`.
- Last decisions: 34 Supabase · 35 files-as-seed · 36 static pages for readers · 37 export as a release gate · 38 no foreign keys.

## Real content

- `attention-is-all-you-need` (peer-reviewed): first story, reference for tone and style.
- `size-shapes-life` (arXiv 2408.04070, preprint): front-page lead; fact-check in `docs/fact-checks/size-shapes-life.md`.
- Everything else in `public/data/library.json` is `sample: true`.

## Built

Data-driven React site: front page D, story pages (five tabs, comic strips, family tree, tag shelf),
issue, company and map pages (with list view), swipe feed (`?feed`), search with tag filters.
Path URLs (`/papers/<slug>`). Reduced motion respected; pause switch per section.

## Next

Follow `docs/production-plan.md` (the only maintained launch sequence). Order:

1. **Fix now** (small, from the Codex review): shared claim label on fact cards / feed / evidence; unique React keys; real family-tree links only; reword "Swipe this issue".
2. **Phase 1:** tests (Vitest), Playwright smoke, axe, CI, preview deploys, rendering decision (static / edge / SSR).
3. **Phase 2:** one real company engineering post and 3–5 more papers to replace samples.
4. **Phase 3:** Supabase migrations, import job with orphan checks, media on a CDN with CORS.

## Known gaps kept on purpose (do not "fix")

- **Family tree / explore map** are demo content. The current nodes and links are placeholders
  so the layout can be reviewed. Don't invent, reshuffle or "verify" links to fill the tree.
  The pages carry a "Mockup · links to be fact-checked" badge and `src/components/FamilyTree.tsx`
  carries a DEMO CONTENT banner at the top. We will properly build the screen once there are
  enough verified relations (see decisions 15, 24; production plan section 4).
- Sample stories, companies and placeholders (`[Company name]`, `[Year]`) render on the live
  pages. That is deliberate for design review. Replacing them is Phase 2 work, not a bug.

## Rules that bite most often

- Never commit or push to `main`. Ask before creating a branch. (Full list in `AGENTS.md`.)
- Canvas before code for any new visual or layout.
- Illustration (invented numbers, stamped) vs evidence (real, cited, trust-labelled) are always visibly separate.
- Accessibility is an acceptance criterion per component, not a later pass.

## Model routing (to control cost)

Default to **Haiku** (or the cheapest capable model in whatever family) for mechanical steps:
builds, lints, git ops, data validation, tag inference (`prompts/tag-paper.md`), fact-check
lookups, JSON edits, PR descriptions. Reserve **Opus / Sonnet 5.5** (or equivalent large model)
for writing kid-level explanations, design decisions, and tricky debugging. Each `SKILL.md`
names its own default.
