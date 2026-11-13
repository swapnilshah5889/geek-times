# Fact-check: "How Discord Stores Trillions of Messages" (Bo Ingram, Discord engineering blog)

Source: Bo Ingram (Senior Staff Software Engineer, Discord), "How Discord Stores Trillions of Messages". Printed date: March 6, 2023. Printed category: "Engineering & Developers". No venue.
Canonical = fetched URL: https://discord.com/blog/how-discord-stores-trillions-of-messages
Archive: none captured.
Extraction: HTML stripped to text (23,456 chars, all five sections). Not captured: the CQL schema block. Checked on 2026-11-12 against that text.

**Location convention.** Links are the plain post URL (allowed). Locations give the post's section heading: Our Cassandra Troubles (CT), Changing Our Architecture (CA), Data Services Serving Data (DS), A Very Big Migration (VBM), Several Months Later (SML). The page has numeric ids ("1"..."10") but no heading anchors, so no `#fragment` is used.

**Result key.** pass = in the post as worded. weakened = wording went past the post (fixed in JSON). scenario = our invented picture or example. background = general explanation not in the post.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | `trust: company_reported`, published 2023-03-06, organization Discord | meta.md: engineering blog post by a Senior Staff Software Engineer at Discord; no venue printed; not refereed. Date printed "March 6, 2023" | pass (owner decides; flagged) |

## Hook, summary, lead

| # | Claim as we state it | Exact phrase in source | Section | Kind | Result |
|---|---|---|---|---|---|
| 2 | Summary: grew from 12 Cassandra machines to 177; busy spots, slow tidying, long pauses | "In 2017, we ran 12 Cassandra nodes"; "At the beginning of 2022, it had 177 nodes"; hot partition, "falling behind on compactions", "super long consecutive GC pauses" | CT, CA | measured_result | pass |
| 3 | Summary: Discord reports it moved to ScyllaDB in May 2022 and now runs 72 machines | "We switched our messages database over in May 2022"; "going from running 177 Cassandra nodes to just 72 ScyllaDB nodes" | SML | measured_result | pass (attributed to Discord; "now" = as of the post) |
| 4 | Hook stat "177 to 72", "database machines, as Discord reports" | "we're going from running 177 Cassandra nodes to just 72 ScyllaDB nodes" | SML | measured_result | pass (checked: 177 is the start-of-2022 count, 72 the post-switch count; both Discord's own) |
| 5 | Hook teaser: why move trillions of messages off a database used for years | Framing question; Cassandra since the 2017 post ("migrated our data to Cassandra") | intro | scenario | scenario |
| 6 | Hook cta, sticker, readMinutes 4, frames | Editorial | n/a | n/a | background |
| 7 | Lead deck: messages database got harder to look after as it grew; why the team says it left Cassandra | "required increasing amounts of effort to just maintain, not improve" | intro | model_design | pass |
| 8 | Fig. 1: 12 machines in 2017 to 177 at start of 2022; more machines meant more work | Same quotes as row 2; "increasing amounts of effort" | CT | measured_result | pass |
| 9 | Fig. 2: after the move Discord reports "72 machines for the same job. Each one holds more." | 72 nodes, 9 TB vs 4 TB (SML). The post does not say the load was unchanged | SML | measured_result | weakened: "for the same job" removed; now "runs its messages database on 72 machines". Fixed in JSON |

## Story chapters

| # | Claim | Exact phrase | Section | Provenance | Result |
|---|---|---|---|---|---|
| 10 | Ch1: 12 machines/billions (2017), 177/trillions (2022); on-call paged often, latency unpredictable, maintenance cut back as too costly | "our on-call team was frequently paged"; "latency was unpredictable"; "cut down on maintenance operations that became too expensive to run" | CT | was model_design | pass for content; provenance changed to illustration: the chapter reports scale and operating pain, not how the system was designed |
| 11 | Ch2: busy spot from uneven traffic; tidying falls behind; Java engine pauses | "a server with just a small group of friends tends to send orders of magnitude fewer messages"; "prone to falling behind on compactions"; "GC pauses would cause significant latency spikes" | CT | model_design | pass (design consequences of partitioning by channel and bucket; kept) |
| 12 | Ch2: "The team says it chose ScyllaDB, a Cassandra-compatible database with no such cleaner" | "ScyllaDB, a Cassandra-compatible database written in C++"; "it is void of a garbage collector" | CA | model_design | pass (attributed to the team) |
| 13 | Ch2: also built a front desk to calm the traffic | "we wrote what we refer to as data services — intermediary services that sit between our API monolith and our database clusters" | DS | model_design | pass |
| 14 | Ch3: front desk is a "small Rust service" | "a language we've been using more and more at Discord: Rust!"; no size given | DS | model_design | weakened: "small" dropped. Fixed in JSON |
| 15 | Ch3: same row at once, ask the database one time, share the answer | "If multiple users are requesting the same row at the same time, we'll only query the database once." | DS | model_design | pass |
| 16 | Ch3: requests for one channel go to the same desk | "consistent hash-based routing ... For messages, this is a channel ID, so all requests for the same channel go to the same instance" | DS | model_design | pass |
| 17 | Ch3: first tool three-month estimate | "we have an estimated time to completion: three months" | VBM | model_design | pass |
| 18 | Ch3: new mover "written in Rust in an afternoon", nine days | "In an afternoon, we extended our data service library to perform large-scale data migrations"; "a new estimate: nine days!" | VBM | model_design | weakened: it extended an existing Rust library. Now "built in Rust in an afternoon on its data-service library". Fixed in JSON. Migration plan is process, not system design; ch3 kept as model_design because it mainly describes the data-services design (owner may prefer illustration) |
| 19 | Ch3 grown-up words: request coalescing, data services, dual-write | "request coalescing"; "data services"; "dual-writing new data" | DS, VBM | n/a | pass |
| 20 | Ch4: switched May 2022; 72 vs 177; 9 TB vs about 4 | "May 2022"; "9 TB ... up from the average of 4 TB per Cassandra node" | SML | evidence | pass |
| 21 | Ch4: fetch old messages 40-125 ms to 15 ms "at the slow end"; save 5-70 ms to a steady 5 ms | "fetching historical messages had a p99 of between 40-125ms on Cassandra ... 15ms p99"; "5-70ms p99 on Cassandra, to a steady 5ms p99" | SML | evidence | pass (p99 = slow end) |
| 22 | Ch4: "Discord's own numbers about its own system, not an outside test"; link to "Several Months Later" | Post is Discord's own report; plain post URL | SML | evidence | pass |

## Comic (provenance: illustration)

| # | Claim | Exact phrase | Section | Result |
|---|---|---|---|---|
| 23 | S1p1: filed by channel and time window; copies on three machines | "all messages for a given channel and bucket will be stored together and replicated across three nodes (or whatever you've set the replication factor)" | CT | pass |
| 24 | S1p2: huge server sends far more; busy drawer | "orders of magnitude fewer messages than a server with hundreds of thousands of people" | CT | pass |
| 25 | S1p3: one busy drawer slowed the whole database; every read waits for several machines | "frequently affected latency across our entire database cluster"; "we perform reads and writes with quorum consistency level, all queries to the nodes that serve the hot partition suffer latency increases" | CT | weakened: "every read" overstated and writes omitted. Now "Reads and writes wait for several machines to agree, so a slow machine holds up the queries that use it." Fixed in JSON |
| 26 | S1 grown-up words: partition, hot partition, quorum, replica | "hot partition"; "quorum consistency level"; "replication factor" | CT | pass |
| 27 | S2p1: new notes pile up in many small files; merge into tidy ones (compaction) | "compact SSTables on disk for more performant reads"; "many small files" not stated | CT | background (general explanation; picture is ours) |
| 28 | S2p2: kept falling behind on tidying; reads slower; delay spread | "falling behind on compactions ... our reads then more expensive, ... cascading latency" | CT | pass |
| 29 | S2p3: "gossip dance": take node out, bring back, repeat | "take a node out of rotation to let it compact without taking traffic, bring it back in to pick up hints ..., and then repeat until the compaction backlog was empty" | CT | pass |
| 30 | S3p1: Cassandra is Java; Java has a built-in cleaner | "the JVM's garbage collector"; "written in C++ rather than Java" (about ScyllaDB) | CT, CA | pass (Cassandra-on-Java implied; sweeper image is background) |
| 31 | S3p2: pauses cause speed spikes; much tuning | "spent a large amount of time tuning the JVM's garbage collector and heap settings, because GC pauses would cause significant latency spikes" | CT | pass |
| 32 | S3p3: back-to-back pauses, manual restart; ScyllaDB is C++ with no cleaner | "super long consecutive GC pauses that got so bad that an operator would have to manually reboot and babysit the node" | CA | weakened (attribution): C++ claim now "Discord says ScyllaDB is written in C++, which has no such cleaner." Fixed in JSON |
| 33 | S4p1: Rust service between app and database; one doorway per question | "intermediary services that sit between our API monolith and our database clusters"; "roughly one gRPC endpoint per database query" | DS | weakened: "small" dropped. Fixed in JSON |
| 34 | S4p2: first request wakes a helper, others join; database asked one time | "The first user that makes a request causes a worker task to spin up ... Subsequent requests will check for the existence of that task and subscribe to it." | DS | pass |
| 35 | S4p3: same channel to same desk; "@everyone message no longer swamps the database as it used to" | "we're able to significantly reduce traffic spikes"; "We're still seeing hot partitions ... just not quite as frequently". The @everyone case is a hypothetical ("Let's imagine") | DS | weakened: now "traffic spikes, such as a big @everyone message, now hit the database much less." Fixed in JSON |
| 36 | S4 grown-up words: request coalescing, consistent hashing, routing key | "request coalescing"; "consistent hash-based routing"; "we provide a routing key" | DS | pass |
| 37 | S5p1: trillions, no downtime; dual-write | "migrate trillions of messages with no downtime"; "dual-writing new data to Cassandra and ScyllaDB" | VBM | pass |
| 38 | S5p2: "first moving tool was set up for months" | "once we get it set up, we have an estimated time to completion: three months" (an estimate, not months of setup) | VBM | weakened: now "The first moving tool estimated three months." Fixed in JSON |
| 39 | S5p2: own mover in Rust in an afternoon; checkpoints | "reads token ranges from a database, checkpoints them locally via SQLite" | VBM | weakened: "wrote" changed to "built" (extended its library, row 18) |
| 40 | S5p3: skip two-step plan, switch at once; up to 3.2 million messages a second | "forget our complicated time-based approach and instead flip the switch for everything at once"; "speeds of up to 3.2 million per second" | VBM | pass |
| 41 | S6p1: several days; stuck just short; huge piles of never-cleaned deleted-message markers | "stuck at 99.9999% complete"; "gigantic ranges of tombstones that were never compacted away" | VBM | pass ("deleted-message markers" is our gloss of tombstones) |
| 42 | S6p2: tidy last pile, seconds later complete; small share of reads to both | "We compact that token range, and seconds later, the migration is complete!"; "sending a small percentage of reads to both databases and comparing results" | VBM | pass |
| 43 | S6p3: new database handled full traffic while Cassandra struggled; May 2022 switch; cake | "The cluster held up well with full production traffic, whereas Cassandra was suffering increasingly frequent latency issues"; "ate celebratory cake"; "May 2022" | VBM, SML | pass |
| 44 | S6 grown-up words: tombstone, validation, cutover | "tombstones"; "automated data validation"; "cutover time" | VBM | pass |
| 45 | Comic deck and howTo: pictures follow Discord's own account; ScyllaDB is Discord's report only | Honest labelling of made-up drawings | n/a | pass |
| 46 | Titles, metaphors (drawers, desks, sweeper, front desk, truck, cake picture) | Not in the post | n/a | scenario |

## Facts (`facts[]`)

| # | Claim | Exact phrase | Section | Kind | Result |
|---|---|---|---|---|---|
| 47 | 12 to 177 machines; trillions by then | "12 Cassandra nodes"; "177 nodes with trillions of messages" | CT | measured_result | pass (Discord's own count, worded "as Discord reports it") |
| 48 | 3 months to 9 days, Spark tool then Rust mover, estimates | "ScyllaDB's Spark migrator"; "three months"; "nine days!" | VBM | measured_result | pass (estimates, worded so) |
| 49 | 3.2 million messages per second, top speed | "speeds of up to 3.2 million per second" | VBM | measured_result | pass |
| 50 | 177 to 72 machines after May 2022 switch; 9 TB vs 4 TB | quotes in rows 3 and 20 | SML | measured_result | weakened: text lacked attribution. Now "as Discord reports it". Fixed in JSON |
| 51 | p99 fetch 40-125 ms to 15 ms; definition of p99 | "p99 of between 40-125ms on Cassandra ... 15ms p99" | SML | measured_result | pass |
| 52 | p99 insert 5-70 ms to steady 5 ms | "5-70ms p99 on Cassandra, to a steady 5ms p99 on ScyllaDB" | SML | measured_result | pass |

Source labels ("Post · Our Cassandra Troubles", "A Very Big Migration", "Several Months Later") match the headings (VBM label drops nothing; SML heading has a trailing ellipsis). All fact links are the plain post URL.

## Paper-basis tags

All 17 paper-basis tags carry the plain post URL as evidence; each concept appears in the post. ScyllaDB claims read as Discord's report throughout (summary, hook stat, Fig. 2, ch2, ch4, comic howTo, S3p3, facts 4-6).

| Tag | Phrase in post | Result |
|---|---|---|
| field/computer-science, area/distributed-systems, area/databases | cluster, nodes, replication, "database" | pass |
| technique/cassandra, technique/scylladb | "cassandra-messages"; "ScyllaDB, a Cassandra-compatible database" | pass |
| concept/hot-partition, concept/garbage-collection, concept/compaction | "hot partition"; "garbage collector"; "falling behind on compactions" | pass |
| concept/tail-latency | "Our tail latencies have also improved drastically" | pass |
| concept/quorum (0.4), concept/consistent-hashing (0.4) | "quorum consistency level"; "consistent hash-based routing" | pass (minor topics) |
| concept/request-coalescing, concept/data-migration, technique/rust | "request coalescing"; "A Very Big Migration"; "Rust" | pass |
| use/chat-messaging, organization/discord, author/bo-ingram | messages, "Discord"; "Bo Ingram" | pass |
| everyday/chatting-online | Editorial (`basis: editorial`) | background |

**Counts (52 rows): 37 pass, 11 weakened (rows 9, 10, 14, 18, 25, 32, 33, 35, 38, 39, 50; all fixed in the JSON, row 10 is a provenance change), 2 scenario (rows 5, 46), 2 background (rows 6, 27).** The trust level (row 1) is a pass but flagged for the owner.
