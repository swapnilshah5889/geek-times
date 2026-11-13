# Fact-check: "How Discord Stores Billions of Messages" (Stanislav Vishnevskiy, Discord blog, 13 Jan 2017)

Source: Stanislav Vishnevskiy (Discord CTO & Co-Founder), "How Discord Stores Billions of Messages". Date as printed: "January 13, 2017". Venue: none printed (the page shows only the category label "Engineering & Developers").
Canonical = fetched URL: https://discord.com/blog/how-discord-stores-billions-of-messages
Archive: none captured.
Extraction: HTML, 22,495 chars of text, matched against `source.txt` and `raw.html`. The CQL schema block and chart images are not in the text.
Checked on 2026-11-12.

**Link convention.** The page has no heading ids (raw.html ids are only numbers and layout ids), so `#fragment` links are not usable. Links use text fragments `#:~:text=...`. Each was checked to hit the intended spot on first match. "The Future" alone would match "avoid them in the future for a channel" in The Big Surprise first, so the 12-node link uses `12%20node%20cluster` instead (fixed).

**Result key.** `pass` = in the post as worded. `weakened` = wording went past the post; fixed in the JSON. `scenario` = our metaphor or drawing. `background` = not from the post.

**Not in the post:** the folder, desk, whiteboard and ring metaphors; any outside test (every number is Discord's own report); the schema column list (image).

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | `company_reported`, organization Discord, published 2017-01-13 | Company engineering blog by its CTO; no refereed venue | pass. Owner decides: flag |

## Facts, hook, summary

| # | Claim as we state it | Exact phrase in source | Section | Kind | Result |
|---|---|---|---|---|---|
| 2 | Summary: outgrew MongoDB around 100 million | "Around November 2015, we reached 100 million stored messages ... the data and the index could no longer fit in RAM" | What we were doing | measured_result | pass |
| 3 | Summary: chose Cassandra, then oversized partitions, edit/delete races, tombstones, six-month surprise | "Cassandra was the only database that fulfilled all of our requirements"; sections Data Modeling, Eventual Consistency, The Big Surprise | various | n/a | pass |
| 4 | Hook stat: 100 million stored messages when MongoDB struggled | "reached 100 million stored messages ... latencies started to become unpredictable" | What we were doing | measured_result | pass |
| 5 | Fact 1: 100 million, Nov 2015, data and index no longer fit in RAM | same as row 2; link text `What we were doing` is the h2 | What we were doing | measured_result | pass |
| 6 | Fact 2: 100MB, warnings while importing into Cassandra | "When we started importing existing messages into Cassandra we immediately began to see warnings in the logs telling us that partitions were found over 100MB in size" | Data Modeling | measured_result | pass |
| 7 | Fact 3: 10 days per bucket so the largest channels stay under 100MB | "We looked at the largest channels on Discord and determined if we stored about 10 days of messages within a bucket that we could comfortably stay under 100MB" | Data Modeling | model_design | pass |
| 8 | Fact 4: 12 of 16 columns written as tombstones for no reason; 16 columns, average 4 set | "our entire message schema contains 16 columns, but the average message only has 4 values set. We were writing 12 tombstones into Cassandra most of the time for no reason" | Eventual Consistency | measured_result | weakened: draft dropped "most of the time". Added in JSON |
| 9 | Fact 5: tombstone life 10 days to 2 because nightly repairs | "We lowered the lifespan of tombstones from 10 days down to 2 days because we run Cassandra repairs (an anti-entropy process) every night on our message cluster" | The Big Surprise | model_design | pass |
| 10 | Fact 6: 12 nodes, replica factor 3 at the time of the post; nearly 1TB compressed per node | "We are currently running a 12 node cluster with a replica factor of 3" (The Future); "We currently store nearly 1TB of compressed data on each node" (Near term, an h3 under The Future) | The Future; Near term | measured_result | pass on content. Link fixed: `#:~:text=The%20Future` would land on "in the future for a channel" in The Big Surprise; now `#:~:text=12%20node%20cluster`, label "Post · The Future and Near term". Note: it is a stated configuration, not a benchmark; "measured_result" is acceptable as a company-reported figure. 1TB is "nearly", per node, and Discord hopes to raise it to 2TB |
| 11 | Hook: cta, sticker, `readMinutes` 4 | Editorial | n/a | n/a | background |

## Story text, lead and comic

| # | Claim as we state it | Exact phrase in source | Section | Result |
|---|---|---|---|---|
| 12 | Lead deck: Discord says it stores all chat history forever | "We decided early on to store all chat history forever" | Intro | pass |
| 13 | Fig. 1: by about 100 million messages its first database struggled | see row 2 | What we were doing | pass |
| 14 | Fig. 2: moved messages to Cassandra, which spreads data over many machines; ring of desks | "We can just add nodes to scale it"; "easy distribution around the cluster" | Choosing the Right Database | pass (ring of desks is a metaphor: scenario) |
| 15 | Ch. 1: MongoDB, one database for everything, Nov 2015, 100 million, no longer fit in RAM, unpredictable speed | "Everything on Discord was stored in a single MongoDB replica set"; "latencies started to become unpredictable" | What we were doing | pass |
| 16 | Ch. 2: needs: grow without hand-reshuffling, heal itself, low upkeep, steady speed; "the only database that met all of its requirements" | "Linear scalability — ... manually re-shard"; "Automatic failover"; "Low maintenance"; "Predictable performance" | Choosing the Right Database | pass |
| 17 | Ch. 3: one big folder, folders grew past 100MB, heavy pressure on Cassandra and data not spread; new folder about every 10 days | "Large partitions put a lot of GC pressure on Cassandra during compaction, cluster expansion"; "the data in it cannot be distributed around the cluster" | Data Modeling | pass |
| 18 | Ch. 3: later learned edits and deletes can collide; deletes leave tombstones | "a user edits a message at the same time as another user deletes"; "treating deletes as a form of write called a 'tombstone'" | Eventual Consistency | pass |
| 19 | Ch. 4: writes under 1 ms, reads under 5 ms in a week of testing; company's own numbers | "Writes were sub-millisecond and reads were under 5 milliseconds ... consistent during a week of testing" | Performance | pass |
| 20 | Ch. 4: surprise six months after launch; one channel with millions of deleted messages made Cassandra stall; link "The Big Surprise" | "about 6 months until that one day where Cassandra became unresponsive"; "they deleted millions of messages ... leaving only 1 message" | The Big Surprise | pass |
| 21 | Comic 1: MongoDB good for building fast; 100 million, no longer in RAM; speed unpredictable; time to move | "one of the best databases for iterating quickly"; "It was time to migrate to a database more suited to the task" | What we were doing | pass |
| 22 | Comic 2: wish list; steady response time without a helper cache; Cassandra only one meeting every item | "We also do not want to have to cache messages in Redis or Memcached" | Choosing the Right Database | pass |
| 23 | Comic 3: a channel's messages sit in one partition; warnings over 100MB; channel can grow for years; 10-day folder; newest folders first | "channel_id became the partition key"; "a single Discord channel can exist for years and perpetually grow in size"; "sequentially query partitions until enough messages are collected" | Data Modeling | pass |
| 24 | Comic 4: edit meets delete; every write a small update; row left with only a few pieces; fix: missing author means broken, delete | "all Cassandra writes are upserts"; "a row that was missing all the data except the primary key and the text"; "deleting the message if it was null" (author_id) | Eventual Consistency | pass |
| 25 | Comic 5: delete leaves a tombstone so other nodes hear; empty value same marker; 16 boxes, average 4 | "It has to replicate deletes to other nodes"; "Deleting a column and writing null to a column are the exact same thing" | Eventual Consistency | pass |
| 26 | Comic 5c: "So Discord was leaving 12 markers for no reason. The fix was simple: write only the boxes that have a value." | "12 tombstones ... most of the time for no reason"; "only write non-null values to Cassandra" | Eventual Consistency | weakened: now "So most of the time Discord was leaving 12 markers for no reason." Fixed in JSON |
| 27 | Comic 6: six months after switch Cassandra unresponsive, about 10 s pauses cleaning memory; millions of tombstones; 10 days to 2; track empty buckets | "10 second 'stop-the-world' GC constantly"; "scan millions of message tombstones (generating garbage faster than the JVM could collect it)"; "track empty buckets and avoid them" | The Big Surprise | pass |
| 28 | howTo: drawings made up; numbers company-reported | n/a | n/a | scenario |
| 29 | Chapter provenance (`model_design`, `evidence`) | Editorial labels | n/a | background |

## Tags (`basis: paper`, evidence = the post URL)

| # | Tag | Support | Result |
|---|---|---|---|
| 30 | field/computer-science, area/distributed-systems, area/databases | whole post | pass |
| 31 | technique/cassandra | "Cassandra was the only database that fulfilled all of our requirements" | pass |
| 32 | concept/eventual-consistency | "Since Cassandra is eventually consistent" | pass |
| 33 | concept/compaction | "permanently deleted during compaction" | pass |
| 34 | concept/replication | "replica factor of 3"; "replicate deletes to other nodes" (minor theme, relevance 0.4) | pass |
| 35 | organization/discord, author/stanislav-vishnevskiy (proposed) | byline and "Discord CTO & Co-Founder" | pass |
| 36 | use/chat-history, concept/tombstone, concept/garbage-collection (proposed) | "store all chat history forever"; "tombstone"; "stop-the-world GC" | pass |
| 37 | everyday/the-internet | `basis: editorial` | background |

Evidence links are the plain post URL (no fragment), which is valid.

## Counts

Pass 28, weakened 2 (rows 8 and 26) plus one link fix (row 10), scenario/background 5 (rows 11, 14 partly, 28, 29, 37). Storyline honesty: the post does say Cassandra is Discord's choice, so no unsupported mention.
