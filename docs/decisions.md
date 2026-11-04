# Decisions

A running log of product and technical decisions, newest last. Don't rewrite old entries; add a new one that
supersedes them. Format: **what**, then **why**. Dates are when the decision was made.

## 2026-11-04

1. **Newspaper look with hand-drawn animated illustrations.** Cream newsprint, serif masthead, Courier labels,
   halftone dots, muted ink colours. Cartoon "word buddy" characters. Inline SVG + CSS keyframes; no video files.
   *Why:* the owner loved the first prototype; it feels trustworthy and playful at once.

2. **Illustration vs evidence are always visibly separate.** Invented numbers are stamped "Illustration · numbers
   invented". Real numbers sit in "Evidence from the paper" cards with links to the exact section.
   *Why:* explaining with simplified numbers must never be mistaken for real results.

3. **"How it works" is told as comic strips.** Six three-panel strips (number codes, ask around, blend it in, many
   lookers, six floors, no peeking). Each ends with "Grown-up words: …". This replaced an earlier step-through
   slideshow.
   *Why:* the owner wanted every technical idea shown with pictures a school kid can read, not text.

4. **The UI renders data.** Content is JSON (a database later); graphics are standalone files referenced by URL
   (a CDN/S3 later). Components stay generic and render typed blocks.
   *Why:* many papers are coming, and layouts will change without rewriting content.

5. **React + TypeScript + Vite.** *Why:* the owner's choice, for a maintainable, typed, fast frontend.

6. **Never push to `main`; always use feature branches and PRs.** *Why:* the owner's rule.

7. **Graphics are self-contained animated SVG files.** They are inlined into a shadow root at runtime (so the page can
   pause them), with an `<img>` fallback. GIF/WebP/MP4 are supported as media types too.
   *Why:* they can live on a CDN, stay sharp, are small, and work with reduced motion.

8. **Many tags per paper from a shared vocabulary.**
   - 13 facets: field, area, concept, technique, task, dataset, metric, use, impact, organization, author, venue,
     everyday.
   - Each tag has relevance 0–1 and a basis (paper with evidence link / background / editorial).
   - AI-suggested tags stay hidden until approved.

   *Why:* readers search by curiosity, and the AI converter infers tags.

9. **Site name: The Geeky Times.**
   - Alternatives considered: Paper Cuts, Big If True, ELI5 Times, Nerd Alert!, Mind Blown Daily, The Curious Times.
   - Paper Cuts was rejected: the "Academic Paper-Cuts" podcast already uses nearly the same concept and name, and
     papercuts.com has been taken since 1997.
   - A USPTO search found no "GEEKY TIMES" mark, and geekytimes.com looked unregistered on 2026-11-04 (not yet
     bought).
   - Neighbours to know about: thegeekytimes.com (an inactive Shopify page) and Geektime (an Israeli tech-news
     site).
   - Get legal clearance before spending on the brand.

10. **The front page is a landing page, separate from story pages.** Desktop is designed first, mobile next. Layout **D**
    was chosen:
    - Above the fold: a broadsheet (full masthead, lead story across 2/3, a column of stories with thin rules).
    - Below the fold: a soft bento of "Keep exploring" tiles (light border, rounded corners, gentle shadow, no hard
      ink offset).

    Rejected: magazine cover (C). Kept as references: pure broadsheet (A) and pure bento (B).

11. **Snack mode.** A full-screen, swipeable feed of bite-size "moments" (comic strips, chapters, facts), each
    deep-linking into the story. *Why:* the "TikTok for intellectuals" goal.

12. **Volumes and issues are the publishing rhythm, not the main navigation.**
    - A volume is a year.
    - An issue is a curated package of several stories (one lead, features, briefs, a "From the vault" classic), with
      a theme and an editor's note.
    - Discovery runs through topics, storylines, the graph and search.

    *Why:* issues create habit and shareable moments, but nobody searches by issue number.

13. **Publish continuously; curate in issues.** A story goes live as soon as it passes review (library, feed, graph,
    search). The weekly issue packages what went live plus vault picks.
    *Why:* the owner wants to publish fast, and the graph improves with volume.

14. **The old-paper backlog.**
    - Keep two dates: the source's original year, and our publish date.
    - Launch with "Volume 0" themed special editions.
    - After that, every issue gets 1–2 "From the vault" classics, plus occasional new special editions.

15. **A knowledge graph of related work.**
    - Nodes are sources, including important ones not explained yet (greyed out, "not explained yet").
    - Typed edges: builds on, improves on, uses the method of, puts into practice, disagrees with, same problem.
    - Each edge has strength, basis and evidence.
    - Edges come from citation APIs (OpenAlex, Semantic Scholar), AI classification and editors.
    - Reader views: a timeline-style family tree on each story, guided storylines ("How X evolved"), and an explore
      map.
    - Unexplained nodes with many links decide what to explain next.

16. **Sources are more than papers.** Company engineering blogs (Netflix, LinkedIn, Meta, Uber, …) are sources too:
    `source.type` = paper | blog | (later) talk, rfc, patent.
    - Trust levels: peer-reviewed / preprint / company-reported.
    - Blogs are followed through RSS and archived when published (Wayback) so evidence links survive edits.
    - Company pages use plain names, never logos.
    - Copyright: write our own explanations and drawings; short quotes only; respect robots.txt and terms; consider
      asking companies for permission; get legal advice before launch.

17. **Project knowledge lives in tool-neutral files.** `AGENTS.md`, `docs/`, `skills/` and `prompts/` are all plain
    markdown, so any model or person can resume the project. Nothing essential lives only in a vendor-specific folder.
