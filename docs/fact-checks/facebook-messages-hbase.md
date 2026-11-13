# Fact-check: "The Underlying Technology of Messages" (Facebook Engineering blog, 2010)

Source: Kannan Muthukkaruppan (Facebook), "The Underlying Technology of Messages", Engineering at Meta (site suffix on the page title).
Date: 2010-11-15. Not printed in the visible text; taken from the page's `datePublished` metadata (2010-11-15T20:46:06+00:00).
Canonical and fetched URL: https://engineering.fb.com/2010/11/15/core-infra/the-underlying-technology-of-messages/
Archive: none captured.
Extraction: HTML stripped to text (6,202 characters, `source.txt`); quotes matched against it. The post is six short paragraphs, so locations are paragraph numbers (P1 intro, P2 data patterns and numbers, P3 storage choice, P4 HBase rationale, P5 app server, P6 close). The page has no heading ids, so links use the plain URL.
Checked on 2026-11-12.

**Result key.** `pass` = in the post as worded. `weakened` = wording went beyond the post; fixed in the JSON. `scenario` = our invented picture. `background` = not from the post.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | `blog.trust: company_reported`; organization Facebook Engineering | meta.md: company engineering blog post, not a paper; "Our Operations and Databases teams..." is the company's own account. No venue or review. Owner decides. | pass (flag for owner) |

## Headline claim: "gave away Cassandra"

Post (P3): "In 2008 we open-sourced Cassandra, an eventual-consistency key-value store that was already in production serving traffic for Inbox Search." and "We either had to move away from our investment in Cassandra or train our Operations teams to support a new, large system."
The post says Facebook open-sourced it and calls it an "investment". It does not say Facebook "gave it away", that this team built it, or that Facebook invented it. Also never says Cassandra is "Facebook's invention".

| # | Claim as we stated it | Result |
|---|---|---|
| 2 | pageTitle "The team that gave away Cassandra picked something else" | weakened: now "open-sourced" |
| 3 | Hook teaser "The company that built Cassandra" | weakened: now "open-sourced" |
| 4 | Lead headline "The inventor picked something else" | weakened: now "Facebook open-sourced Cassandra, then picked something else." |
| 5 | Lead deck "Facebook made Cassandra" | weakened: now "open-sourced" |
| 6 | Fig. 2 "one its own company had made and given away" | weakened: now "had open-sourced" |
| 7 | Ch. 2 "had built Cassandra itself" | weakened: now "had invested in Cassandra" |
| 8 | Comic 2 panel 2 "the company had made Cassandra itself" | weakened: now "open-sourced Cassandra and invested in it" |
| 9 | Summary "Facebook open-sourced Cassandra in 2008" | pass |

## Facts, hook, summary

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 10 | Summary: tested MySQL, Cassandra, HBase and others; chose HBase because of MySQL's long tail and Cassandra's eventual consistency | "evaluate clusters of MySQL, Apache Cassandra, Apache HBase, and a couple of other systems. We ultimately chose HBase. MySQL proved to not handle the long tail of data well"; "Cassandra's eventual consistency model to be a difficult pattern to reconcile" | P3 | model_design | pass (post also gives positive HBase reasons, P4) |
| 11 | Hook stat "15 billion / messages a month, Facebook says" | "handles over 350 million users sending over 15 billion person-to-person messages per month" | P2 | measured_result | pass (the post says "over"; the bare figure is the lower bound) |
| 12 | Hook cta, readMinutes | Editorial | n/a | n/a | background |
| 13 | Fact 1: 15 billion person-to-person messages per month, 350 million users | same quote; "The current Messages infrastructure handles" reads as observed usage | P2 | measured_result | weakened: text lacked "over"; now "over 15 billion". Kind stays measured_result (post presents it as current usage, company-reported) |
| 14 | Fact 2: 120 billion messages per month in chat, 300 million users | "Our chat service supports over 300 million users who send over 120 billion messages per month." | P2 | measured_result | weakened: text now "over 120 billion". Kind pass |
| 15 | Fact 3: 2008, open-sourced Cassandra, already serving Inbox Search | "In 2008 we open-sourced Cassandra ... already in production serving traffic for Inbox Search." | P3 | model_design | pass |
| 16 | Fact 4: a few weeks on a test framework for MySQL, Cassandra, HBase, a couple of others | "We spent a few weeks setting up a test framework to evaluate clusters of MySQL, Apache Cassandra, Apache HBase, and a couple of other systems." | P3 | model_design | pass |
| 17 | Fact 5: 20 new infrastructure services | "will launch over 20 new infrastructure services" | P6 | model_design | weakened: text now "over 20". A launch plan, not observed usage, so not measured_result |
| 18 | All fact source links (label "Post") | Plain URL, no fragment | n/a | n/a | pass |

## Story text (chapters, lead)

| # | Claim | Exact phrase | Loc | Result |
|---|---|---|---|---|
| 19 | Fig. 1: two piles, "small, busy pile of recent messages ... old ones" | "A short set of temporal data that tends to be volatile"; "An ever-growing set of data that rarely gets accessed" | P2 | weakened: the post says "data", not "messages", and "temporal" not "recent". Now "a small, busy pile of data and a huge pile that rarely gets opened" |
| 20 | Ch. 1 "short set of recent data that changes a lot" | same | P2 | weakened: now "time-related". The rest (ever-growing, rarely opened) pass |
| 21 | Ch. 1 desk and warehouse | our picture | n/a | scenario |
| 22 | Ch. 2 wanted an objective choice; few weeks; MySQL skills | "we wanted to take an objective approach"; "extensive knowledge in managing and running MySQL" | P3 | pass |
| 23 | Ch. 3 chose HBase; MySQL long tail; Cassandra consistency hard to fit; HBase simpler model; features; HDFS skills | "a simpler consistency model than Cassandra"; "most feature rich in terms of our requirements (auto load balancing and failover, compression support, multiple shards per server, etc.)"; "development and operational expertise in HDFS from data processing with Hadoop" | P3, P4 | pass |
| 24 | Ch. 4 company's own account, no benchmark numbers | The post gives no benchmark figures (checked; none) | n/a | pass |
| 25 | Ch. 4 350 million users, 15 billion messages | see row 11 | P2 | pass |
| 26 | Ch. 4 did a lot of work on HBase and sent changes back | "we've done a lot of work on HBase itself"; "committing our changes back to HBase itself" | P4 | pass |

## Comic

| # | Claim | Exact phrase | Loc | Result |
|---|---|---|---|---|
| 27 | Strip 1: volatile; ever-growing set that rarely gets accessed; objective way to choose | "tends to be volatile"; "An ever-growing set of data that rarely gets accessed"; "objective approach" | P2, P3 | pass; busy desk and warehouse are scenario; grownUpWords pass ("usage patterns", "workload") |
| 28 | Strip 2: tried MySQL, Cassandra, HBase and a couple of others; Ops and Databases teams knew MySQL | P3 quotes above | P3 | pass |
| 29 | Strip 2: either leave Cassandra work or train operations teams | "move away from our investment in Cassandra or train our Operations teams to support a new, large system" | P3 | pass |
| 30 | Strip 3: data and indexes grew, performance suffered; MySQL not good at long tail | "as indexes and data sets grew large, performance suffered" | P3 | pass; shelf panel scenario |
| 31 | Strip 4: Cassandra eventually consistent; hard to reconcile; HBase simpler model | "an eventual-consistency key-value store"; "a difficult pattern to reconcile"; "simpler consistency model" | P3, P4 | pass; "desks with different notes" and "one clear answer at a time" are our picture (scenario) |
| 32 | Strip 5: features; HDFS replication, checksums, rebalancing; teams knew HDFS; changes sent back | "replication, end-to-end checksums, and automatic rebalancing"; "committing our changes back to HBase" | P4 | pass; "copies, honesty checks and tidying" is gloss |

## Paper-basis tags

All point at the plain post URL (no fragment).

| Tag | Phrase | Result |
|---|---|---|
| `technique/cassandra` | "In 2008 we open-sourced Cassandra" | pass |
| `technique/hbase`, `technique/mysql`, `technique/hdfs` | "We ultimately chose HBase"; "MySQL proved to not handle"; "HDFS, the underlying filesystem used by HBase" | pass |
| `concept/eventual-consistency` | "an eventual-consistency key-value store" | pass |
| `organization/facebook`, `area/databases`, `field/computer-science` | author is "a software engineer at Facebook"; storage evaluation | pass |
| `area/distributed-systems` | "clusters", "auto load balancing and failover", "replication"; the post never says "distributed" | pass (classification, not a quote) |

## Storyline honesty

The post mentions Cassandra directly (open-sourced 2008, eventual consistency, evaluated and rejected). It does not say Facebook invented Cassandra, does not give benchmark numbers, and does not describe the test's results beyond the stated reasons. Story keeps all of that.
