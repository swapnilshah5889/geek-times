# Fact-check: "Open-sourcing a 10x reduction in Apache Cassandra tail latency" (Instagram Engineering, 2018)

Source: Instagram Engineering blog post on Medium, "Open-sourcing a 10x reduction in Apache Cassandra tail latency". Date as printed: "Mar 5, 2018" (metadata 2018-03-05). No venue printed (company engineering blog).
Author: no byline in the captured text. The closing line reads "Dikang Gu is an infrastructure engineer at Instagram." The page's metadata author is the account "Instagram Engineering".
Canonical URL: https://instagram-engineering.com/open-sourcing-a-10x-reduction-in-apache-cassandra-tail-latency-d64f86b43589
Fetched / archive URL: https://web.archive.org/web/20190403015202/https://instagram-engineering.com/open-sourcing-a-10x-reduction-in-apache-cassandra-tail-latency-d64f86b43589?gi=ec2643f1aee4 (live site gave no response; Wayback capture of 2019-04-03 used).
Extraction: HTML (135,420 bytes) to `source.txt` (7,362 chars). Graphs are images; only their captions and text were read, so no figure value was taken from a picture.
Checked on 2026-11-12.

**Location convention.** Locations name the post's section (Motivation, Solution, Challenges, Performance metrics, Future work). Links use the heading ids that exist in `raw.html`: `#d01d` Motivation, `#87af` Solution, `#cb1c` Challenges, `#a1f4` Performance metrics, `#d343` Future work.

**Result key.** `pass` = in the post as worded. `weakened` = wording went beyond the post; fix noted and applied in the JSON. `scenario` = our invented picture. `background` = not from the post.

**Where "10x" is allowed.** The post attaches "10X" to exactly two things: GC stalls on one production cluster (2.5% to 0.3%, "a 10X reduction!"; arithmetic is about 8.3x) and read throughput in the 3-node AWS test (300K/s vs 30K/s at similar P99 of 2 ms). It does NOT attach it to the production P99 (60 to 20 ms, about 3x), although its own title says "10x reduction in ... tail latency". Every "10X" in the story was checked against this (rows 5, 12, 13, 22, 25, 33). None sits on the production P99. The post title appears in `blog.title` as printed.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, organization Instagram Engineering, published 2018-03-05 | "Mar 5, 2018"; collection "Instagram Engineering" | pass |
| 2 | `trust: company_reported` | meta.md: "Instagram Engineering company blog post; numbers are the company's own production and self-run benchmark figures." Production numbers come from Instagram's own clusters; the AWS test is run by Instagram with NDBench, no outside party | pass; owner decides, flagged |

## Summary, hook, lead

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 3 | Instagram kept Cassandra but changed the engine inside | "decided to develop a C++ storage engine to replace existing ones" | Solution | model_design | pass |
| 4 | Team says the Java storage engine made the GC freeze servers and slow the slowest reads | "the JVM garbage collector (GC) contributed a lot to the latency spikes"; "components in the storage engine ... created a lot of objects in the Java heap" | Motivation, Solution | model_design | pass (attributed to the team) |
| 5 | Built Rocksandra in C++ on RocksDB; in one production cluster P99 fell 60 ms to 20 ms | "a project ... which we call Rocksandra"; "In one of our production clusters, the P99 read latency dropped from 60ms to 20ms." | Intro, Performance metrics | measured_result | pass (no 10x attached) |
| 6 | Hook sticker "Same database, new engine" and teaser "What if the slow reads come from the cleanup crew, not the database?" | Framing; the post blames GC for "a lot" of the spikes, not all | Motivation | scenario | scenario |
| 7 | Hook stat "60 → 20 ms, P99 read latency, one production cluster" | as row 5 | Performance metrics | measured_result | pass |
| 8 | Hook cta, `readMinutes: 4` | Editorial (page metadata says reading time 5.2 min; not a claim about content) | n/a | n/a | background |
| 9 | Hook frames "Freeze!" / "Swap!" | Pictures; stop-the-world GC and engine replacement are in the post | Motivation, Solution | scenario | scenario |
| 10 | Lead deck: kept Cassandra, changed engine so slowest reads stop waiting on the cleanup crew | rows 3, 4 | Solution | model_design | pass |
| 11 | Fig. 1: servers sometimes stop serving requests while a Java cleanup crew works | "stop-the-world GC (Young Gen GC) and could not serve client requests" | Motivation | model_design | pass |
| 12 | Fig. 2: kept Cassandra, swapped the engine for one on RocksDB in C++ | "build the new storage engine on top of RocksDB"; "RocksDB ... It's written in C++" | Solution | model_design | pass |

## Story chapters

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 13 | Ch. 1: general key-value store; most requests online | "use Apache Cassandra heavily as a general key value storage service. The majority of Instagram's Cassandra requests are online" | Motivation | measured_result | pass |
| 14 | Ch. 1: P99 is the time 99 of 100 reads beat | Post does not define P99; standard definition | n/a | background | background |
| 15 | Ch. 1: one production cluster, average 5 ms, P99 25 to 60 ms | "average read latency (5ms) ... P99 read latency (in the range of 25ms to 60ms ...)" | Motivation | measured_result | pass |
| 16 | Ch. 1: GC "a big cause" of the spikes | "contributed a lot to the latency spikes" | Motivation | model_design | pass |
| 17 | Ch. 2: Java engine creates lots of objects, work on the GC; chose C++; did not build from scratch; RocksDB open source embedded key-value database; name Rocksandra | "created a lot of objects in the Java heap"; "did not want to build a new storage engine from scratch"; "open source, high-performance embedded database for key-value data" | Solution, Intro | model_design | pass |
| 18 | Ch. 3: no plug-in slot, new engine interface; translate rich tables to keys and values; rebuilt streaming | "Cassandra does not have a pluggable storage engine architecture yet"; "defined a new storage engine API"; "encoding/decoding algorithms"; "re-implement the streaming using RocksDB APIs" | Challenges | model_design | pass |
| 19 | Ch. 4: new engine in several production clusters | "successfully rolled it into several production Cassandra clusters" | Performance metrics | measured_result | pass |
| 20 | Ch. 4: in one, P99 60 to 20 ms and GC stalls 2.5% to 0.3% | "dropped from 60ms to 20ms"; "GC stalls on that cluster dropped from 2.5% to 0.3%" | Performance metrics | measured_result | pass |
| 21 | Ch. 4: post calls the stall drop a 10X reduction | "which was a 10X reduction!" | Performance metrics | measured_result | pass (attached to GC stalls only) |
| 22 | Ch. 4: separate 10X throughput figure from a 3-machine AWS test at P99 2 ms; company's own numbers | "10X higher read throughput"; "three i3.8 xlarge EC2 instances" | Performance metrics | measured_result | pass |
| 23 | Ch. 4 link "See Performance metrics in the post" | Heading id `a1f4` exists in raw.html | Performance metrics | n/a | weakened: link was the bare URL; now `#a1f4`. Fixed in JSON |

## Comic strips

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 24 | Strip 1 (tail, P99): most reads quick, a few slow; Instagram watches P99 because app users wait live | "actively monitor the throughput and latency ..., especially the P99 read latency"; "majority ... requests are online" | Motivation | illustration | pass (line and counter are our picture) |
| 25 | Strip 2: janitor stops the server; stop-the-world pause; GC stall percentage up to 2.5% at busy times | "stop-the-world GC"; "could be as high as 2.5% during peak hours" | Motivation | model_design | pass (post's "1.25% at lowest traffic" omitted, not contradicted) |
| 26 | Strip 3: storage engine keeps the data; Java one made many objects; C++ engine to cut GC load; built on RocksDB | rows 4, 17 | Solution | model_design | pass. Grown-up word "memtable" and "compaction" are named in the post |
| 27 | Strip 4: engine glued to Cassandra, new interface; table-to-key-value rules; streaming into temp files then bulk load | "existing storage engine is coupled together with other components"; "stream data into temp sst files first, and then use the RocksDB ingest file API to bulk load" | Challenges | model_design | pass |
| 28 | Strip 5a: "tried it away from its own data centers" | Post says only "public cloud environment" and AWS; it does not say "away from its own data centers" | Performance metrics | evidence | weakened: now "Instagram also tried it in a public cloud." Fixed in JSON |
| 29 | Strip 5b: filled with data, ran NDBench against old Cassandra and Rocksandra | "We used NDBench for the benchmark"; "(300K/s for Rocksandra vs. 30K/s for C* 3.0)" | Performance metrics | evidence | pass |
| 30 | Strip 5c: at about the same P99 of 2 ms, Rocksandra served 10X the reads; tail times lower and steadier for reads and writes | "at similar P99 read latency (2ms), Rocksandra could provide 10X higher read throughput"; "much lower and consistent tail read/write latency" | Performance metrics | evidence | pass (10X attached to throughput only) |
| 31 | Strip 6: open-sourced code and benchmark tool; adding secondary indexes, repair; plug-in slot to Apache Cassandra | "open sourced our Rocksandra code base and benchmark framework"; "secondary indexes, repair"; "pluggable storage engine architecture to contribute our work back" | Future work | illustration | pass |
| 32 | howTo: "numbers ... are Instagram's own" | Post reports all numbers itself | n/a | n/a | pass |

## Facts (`facts[]`)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 33 | 60 → 20 ms, one production cluster; "several" clusters | row 20 | Performance metrics, `#a1f4` | measured_result | pass (link fragment added) |
| 34 | 2.5% → 0.3% GC stall, same cluster; post calls it 10X | row 20, 21. Note: 2.5/0.3 is about 8.3x, the post rounds to 10X; the story attributes the word to the post | Performance metrics, `#a1f4` | measured_result | pass |
| 35 | 5 ms average, P99 25 to 60 ms in one cluster, "before the change" | The caption gives the numbers for "one production Cassandra cluster"; the post does not say it is the same cluster as the 60 to 20 ms one, nor label it "before" | Motivation, `#d01d` | measured_result | weakened: now "Average read time and the P99 range on the client side of one production cluster, as the post's Motivation graph caption gives them." Fixed in JSON |
| 36 | 10X read throughput, 3-machine AWS test, P99 2 ms, 300K vs 30K reads/s, Cassandra 3.0, benchmark not production | "at similar P99 read latency (2ms), Rocksandra could provide 10X higher read throughput (300K/s for Rocksandra vs. 30K/s for C* 3.0)" | Performance metrics, `#a1f4` | measured_result | pass |
| 37 | 250M rows of 6KB, about 500GB per server, three servers, 128 readers and writers | "250M 6KB rows"; "each server stores about 500GB"; "128 readers and 128 writers" | Performance metrics, `#a1f4` | measured_result | pass |
| 38 | About a year of development and testing before the first version reached production | "After about a year of development and testing, we have finished a first version ... rolled it into several production Cassandra clusters" | Performance metrics, `#a1f4` | model_design | pass (claim kind is a stated duration, not a measurement; left as is) |
| 39 | Fact source links | Fragments `#a1f4` and `#d01d` exist as heading ids in raw.html | n/a | n/a | weakened: all were the bare URL; fragments added. Fixed in JSON |

## Tags (`basis: paper`)

| Tag | Evidence | Result |
|---|---|---|
| `field/computer-science`, `area/distributed-systems`, `area/databases` | Post is about a distributed database | pass |
| `technique/cassandra` | "Apache Cassandra" throughout | pass |
| `concept/tail-latency` | "P99 read latency", title "tail latency" | pass |
| `concept/compaction` (0.4) | "memtable, compaction, read/write path" named once | pass (minor mention, low relevance) |
| `organization/facebook` (0.3) | "migrated them over to Facebook's infrastructure" | pass (minor mention) |
| `organization/instagram` | Publisher and subject | pass (proposed) |
| `technique/rocksdb`, `concept/garbage-collection`, `concept/storage-engine` | All three are central terms in Solution and Motivation | pass (proposed) |
| `author/dikang-gu` (0.4) | Only the closing line "Dikang Gu is an infrastructure engineer at Instagram." The post says "I will describe the motivation", so the writer is the person in that bio; no byline is printed and the page metadata author is "Instagram Engineering" | pass, rests on printed text only; low relevance and proposed status suit it. Evidence link changed to a text fragment on that line. Fixed in JSON |
| `everyday/the-internet` | `basis: editorial` | background |

All tag evidence links are the post URL (no fragment except the author tag).

## JSON edits made

1. All 6 fact source links now carry `#a1f4` (Performance metrics) or `#d01d` (Motivation); chapter 4 link to `#a1f4`.
2. Comic strip 5 panel 1: "away from its own data centers" replaced with "in a public cloud".
3. Fact "5 ms, 25 to 60 ms": dropped "before the change", now cites the Motivation graph caption.
4. `author/dikang-gu` evidence: text fragment on the bio line.

## Open items for the owner

- Trust level (`company_reported`) is a judgment call; flagged.
- The post's headline claims a 10x tail-latency reduction; its own body shows about 3x on production P99. The story keeps the title as printed and never repeats "10x" for P99.
- The production cluster of the 25 to 60 ms graph and the cluster with the 60 to 20 ms result may not be the same; the story no longer implies it.
