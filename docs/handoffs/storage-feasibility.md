# Supabase Storage feasibility for media migration

Audit date: 2026-11-12. Branch `v1`. Read-only investigation. No code, config, migrations, or `package.json` were changed. No accounts were created and no assets were moved.

## Verdict

- **Blocker: NO** against documented limits. Nothing in the official docs prevents Supabase Storage from serving the 174 SVGs.
- **Two items are not documented and must be verified empirically before cutover:** (a) CORS `Access-Control-Allow-Origin` on public-object responses, and (b) `Content-Type: image/svg+xml` on served SVGs. These are gaps in the docs, not confirmed blockers.
- **Recommendation:** Proceed with Supabase Storage as the media host, gated on a one-time CORS and Content-Type check against a throwaway public bucket in an existing project. Fallbacks (R2 or S3) are not needed unless that check fails.

## 1. Inventory: `public/media/` (excluding `samples/`)

Command: `find public/media -path public/media/samples -prune -o -type f -print`

| Metric | Value |
|---|---|
| Files | 174 |
| Extensions | 174 x `.svg` (no other types) |
| Total bytes | 1,424,060 (about 1.36 MiB / 1.42 MB) |
| Largest file | 46,110 bytes: `public/media/h3-hexagons/lead/honeycomb-map.svg` |
| Next largest | 39,209 bytes: `public/media/google-search/lead/pile.svg`; 26,550 bytes: `google-search/story/01-too-many.svg` |

Note on the 180 count in the brief: `public/media/samples/` contains 6 SVGs (`dna`, `mold`, `particle`, `protein`, `stairs`, `waves`). 174 + 6 = 180, so the brief's figure includes samples. Excluding samples, the count is 174.

Every file is well under every documented cap (see section 2). The whole set is about 1.4 MB.

## 2. Docs-sourced facts (Supabase Storage)

Pages fetched 2026-11-12. The official pages checked show **no publication or last-updated dates**, so dates are not stated.

| Fact | Value | Source |
|---|---|---|
| Free plan global file size limit | "For Free projects, the limit can't exceed 50 MB." | https://supabase.com/docs/guides/storage/uploads/file-limits |
| Paid (Pro and up) global file size limit | "On the Pro Plan and up, you can set this value to up to 500 GB." | same |
| Per-bucket limit rule | Cannot exceed the global limit. | same |
| Free plan storage quota | 1 GB, no over-usage charge (table row "Free \| 1 \| -"). | https://supabase.com/docs/guides/storage/pricing |
| Free plan egress quota | 5 GB uncached / 5 GB cached, no over-usage rate listed. | https://supabase.com/docs/guides/platform/manage-your-usage/egress |
| Cached vs uncached egress | Cached egress is served from the CDN on cache hits. Cached and uncached have independent quotas and pricing. | same |
| Exceeding Free egress | Notification and grace period, referring to a Fair Use Policy. | same |
| Public bucket URL pattern | `https://[project_id].supabase.co/storage/v1/object/public/[bucket]/[asset-name]`. Public-bucket files are CDN-cacheable. | https://supabase.com/docs/guides/storage/serving/downloads |

Items **not found in official docs** (fetch of the relevant pages returned no statement):
- CORS headers on Storage responses, or any bucket-level CORS setting.
- SVG / `image/svg+xml` Content-Type handling.
- Pro-plan egress rates. Search snippets quoted $0.03/GB cached and $0.09/GB uncached, but those were not verified on the fetched egress page. Treat as unverified.

Attempted and failed: `https://supabase.com/docs/guides/storage/uploads/limits` returned HTTP 404. The file-limits URL above is the correct page.

Secondary, non-official signals (indicative only):
- A Supabase blog post on self-hosting maps (https://supabase.com/blog/self-host-maps-storage-protomaps) says public buckets allow access from any origin and that bucket CORS settings could not be modified at that time. The post is roughly 2.4 years old, so this may be stale.
- A GitHub discussion (https://github.com/orgs/supabase/discussions/35343) reports no CORS configuration for hosted Storage. Community report, not official.
- A Supabase maintainer reply in https://github.com/orgs/supabase/discussions (SVG thread) says Supabase does not alter MIME type or file data, so the uploader's declared Content-Type is what gets served. Community thread, not an official doc.
- A security issue (https://github.com/DTour-git/DTour/issues/29) notes SVG/HTML on a public bucket is served from the `.supabase.co` origin and proposes restricting `allowed_mime_types` to exclude `image/svg+xml`. The author could not confirm the exact response headers. Not official.

## 3. CORS for SVG `fetch`

- Docs do not confirm that public objects send `Access-Control-Allow-Origin` by default. Secondary sources say public buckets allow any origin, which would match the need for a cross-origin `fetch`. **Unverified against official docs.**
- Docs do not confirm `Content-Type: image/svg+xml`. Secondary sources say the uploaded MIME type is preserved. **Unverified.**
- Any SVG served from the project origin should be treated as active content. Consider an explicit `allowed_mime_types` restriction only if SVGs are not needed as a served type, which they are here, so keep `image/svg+xml` and sanitize SVGs on ingest instead.

## 4. Blocker check

| Potential blocker | Limit | Project need | Blocker? |
|---|---|---|---|
| Per-object cap | 50 MB Free / 500 GB Pro | max 46 KB | No |
| Storage quota | 1 GB Free | about 1.4 MB | No |
| Egress (Free) | 5 GB uncached + 5 GB cached per cycle | 1.4 MB per full-catalog load, and most traffic is cache hits | No at current scale. Monitor if traffic grows, since Free egress is bounded. |
| CORS gap | not documented | `fetch` from app origin | Unverified, not a documented blocker |
| SVG Content-Type | not documented | 174 SVGs | Unverified, not a documented blocker |

Egress arithmetic: 1.42 MB per full-catalog download means the 5 GB uncached quota covers roughly 3,500 full-catalog downloads per billing cycle before any caching. Cache hits draw from the separate cached quota.

## 5. Fallbacks (R2 / S3)

Not compared. The brief limits fallback comparison to the case where a concrete blocker exists. No documented blocker was found; the two open items (CORS, Content-Type) are unverified rather than blocking. If the verification in section 6 fails, reopen this section and compare Cloudflare R2 (free tier, custom domain for CORS) against AWS S3 with CloudFront on CORS, public URLs, migration effort, and current pricing, with sourced figures.

## 6. Recommended verification before cutover

1. In an existing project, create a throwaway public bucket (no new account). Upload one SVG with `contentType: 'image/svg+xml'`.
2. From a browser at the app's origin, run `fetch(url)` and confirm the response reads without a CORS error. Check that `Access-Control-Allow-Origin` appears in response headers.
3. Confirm `Content-Type: image/svg+xml` on the response.
4. If either check fails, fall back to R2 or S3 per section 5.
5. Decide on SVG sanitization at ingest, since SVGs are served from the project origin.

Nothing above was executed; this is a plan.
