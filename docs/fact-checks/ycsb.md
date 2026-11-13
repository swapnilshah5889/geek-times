# Fact-check: "Benchmarking Cloud Serving Systems with YCSB" (Cooper, Silberstein, Tam, Ramakrishnan, Sears; Yahoo! Research; SoCC 2010)

Source: Brian F. Cooper, Adam Silberstein, Erwin Tam, Raghu Ramakrishnan, Russell Sears (Yahoo! Research), "Benchmarking Cloud Serving Systems with YCSB". Printed venue/date (PDF p1): "SoCC'10, June 10-11, 2010, Indianapolis, Indiana, USA." and "Copyright 2010 ACM 978-1-4503-0036-0/10/06 ...$10.00."
Canonical and fetched URL: https://courses.cs.duke.edu/fall13/cps296.4/838-CloudPapers/ycsb.pdf (a second Duke URL serves a byte-identical file, md5 b6707eff50f14091ed47a08c18f1b63a). Archive: none.
Extraction: pdftotext per page, 12 of 12 PDF pages (p1-p12), quotes matched against that text.
Checked on 2026-11-12.

**Location convention.** Links use `#page=N` (PDF page index). The paper's sections: 1 Introduction, 2 (background), 3 Benchmark Tiers, 4 Benchmark Workloads, 5 Details of the Tool, 6 Benchmark Results (6.1 Setup, 6.2 Workload A, 6.3 Workload B, 6.4 Workload E, 6.5 Other, 6.6 Scalability, 6.7 Elastic Speedup), 7 Future Work.

**Result key.** `pass` = in the paper as worded. `weakened` = wording went past the paper; fixed in the JSON. `scenario` = our invented picture or metaphor. `background` = editorial, not from the paper.

**What is not in the paper:** the shops, runners, clipboards, rulers, notebook and robot-arm pictures; the "Same race!" sticker.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Venue SoCC 2010 | "SoCC'10, June 10-11, 2010, Indianapolis, Indiana, USA." (p1) | pass |
| 2 | Trust suggestion `peer_reviewed` | The printed text gives the ACM conference but never says "refereed". meta.md suggests `peer_reviewed`. **Owner decides; flagged.** | owner check |

## Facts, hook, summary

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 3 | Summary: many new stores, nobody could compare fairly | "explosion in the number of systems"; "a lack of apples-to-apples performance comparisons" | Abstract p1 | model_design | pass |
| 4 | Summary: five workloads, run on Cassandra, HBase, PNUTS, sharded MySQL | "report results for four widely used systems: Cassandra, HBase, Yahoo!'s PNUTS, and a simple sharded MySQL"; Table 2 lists workloads A-E | Abstract p1; §4.2 p6 | measured_result | pass |
| 5 | Summary: highest throughput in update-heavy test, much worse scans | "Cassandra ... achieved the best throughput"; "Cassandra performs much worse" | §6.2 p8-9; §6.4 p9 | measured_result | pass |
| 6 | Summary: Cassandra 0.5.0 and six machines per store | "For most experiments, we used six server-class machines"; "Cassandra 0.5.0"; elastic test used "Cassandra 0.6.0-beta2" | §6.1 p8 | measured_result | weakened: "in most tests" added |
| 7 | Summary: newer versions may change results | "the performance may change and improve in the future" | §6 p8 | measured_result | pass |
| 8 | Hook stat: 11,978 operations a second, Cassandra peak, update-heavy | "peaking at 11978 operations/sec"; "Throughput ... represents total operations per second, including reads and writes" | §6.2 p9; Fig. 3 caption p8 | measured_result | pass |
| 9 | Hook sticker/teaser/cta, readMinutes 4 | Editorial framing | n/a | n/a | background |
| 10 | Fact 1: 11978 (A, half reads half updates); HBase 7904, MySQL 7283, PNUTS 7448 | "11978 operations/sec, compared to 7904 operations/sec for HBase, 7283 operations/sec for sharded MySQL, and 7448 operations/sec for PNUTS"; "50 percent reads and 50 percent updates" | §6.2 p8-9 (numbers on p9) | measured_result | pass; link p9 correct |
| 11 | Fact 2: "much worse" on short scans; HBase 1519, PNUTS 1440; new in 0.5.0, not heavily optimized | "1519 ops/sec for HBase, and 1440 ops/sec for PNUTS"; "Cassandra performs much worse. Cassandra's range scan support is relatively new in version 0.5.0, and is not yet heavily optimized" | §6.4 p9 | measured_result | pass |
| 12 | Fact 3: 5.5 hours; stopped so data could finish moving; known issue in 0.5.0, being optimized; test used 0.6.0-beta2 | "we had to stop the YCSB workload after 5.5 hours to allow the system to complete its repartitioning and quiesce. The high cost of repartitioning is a known issue with Cassandra 0.5.0 and is being optimized"; "For one experiment (elastic speedup), we used Cassandra 0.6.0-beta2" | §6.7 p10; §6.1 p8 | measured_result | pass (the paper itself names 0.5.0 for the issue and 0.6.0-beta2 for the test; the fact states both) |
| 13 | Fact 4: 120 GB, 120 million 1 KB records, six servers, about 20 GB each, more than fits in memory; replication off; no dedicated log disk | "120 million 1 KB records, for a total size of 120 GB. Each server thus had an average of 20 GB of data, more than it could cache entirely in RAM"; "We disabled replication"; "no dedicated log disk" | §6.1 p8 | model_design | weakened: "in most experiments" added to "six server machines" |
| 14 | Fact 5: 2 to 12 servers; read latency near constant for Cassandra and PNUTS, varied for HBase; read-heavy test | "varying the number of storage servers from 2 to 12"; "latency is nearly constant for Cassandra and PNUTS"; "HBase's performance varies a lot" (workload B) | §6.6 p10 | measured_result | pass |
| 15 | Fact 6: 95/5 in B; PNUTS and MySQL lower read latency; Cassandra, HBase better writes; extra disk reads dominate | "PNUTS and sharded MySQL are now able to provide lower latencies on reads than either Cassandra or HBase. Cassandra and HBase still perform better for writes. The extra disk I/Os being done by Cassandra to assemble records for reading dominates"; Table 2 Read 95% Update 5% | §6.3 p9; Table 2 p6 | measured_result | pass |

## Story text, lead and comic

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 16 | Lead deck: popping up fast, nobody could compare fairly; Yahoo! built a shared test and ran four stores | "lack of apples-to-apples performance comparisons"; four systems as row 4 | Abstract p1 | model_design | pass |
| 17 | Fig. 1 caption: nobody had a shared way to compare | same | p1 | model_design | pass; picture scenario |
| 18 | Fig. 2 caption: same workloads on every store | Sharded MySQL "does not support range scans", so workload E skipped it | §6.4 p9 | model_design | weakened: "on every store" became "on the stores" |
| 19 | Ch. 1: Cassandra, HBase, PNUTS among many; different choices; no apples-to-apples; teams could not tell which suited | Abstract list; Table 1 design decisions; "developers often have to download and manually evaluate multiple systems" | p1, p4 | model_design | pass |
| 20 | Ch. 2: same table of records, mixes (read, update, scan); open source, add a store or mix | "a table of records"; "available under an open source license ... new workloads and database interfaces" | §4 p4; §5 p5 | model_design | weakened: "every store" to "the stores" and noted MySQL skips scans |
| 21 | Ch. 3: six machines, same disks, replication off | "For most experiments, we used six server-class machines ... 6 disk RAID-10"; "We disabled replication" | §6.1 p8 | model_design | weakened: "for most tests" added |
| 22 | Ch. 3: developers of Cassandra, HBase, PNUTS helped tune; tuned as well as we knew how | "We configured and tuned each system as well as we knew how ... extensive tuning assistance from members of the development teams of the Cassandra, HBase and PNUTS systems" | §6.1 p8 | model_design | pass |
| 23 | Ch. 4: highest throughput update-heavy; scan much worse, new in 0.5.0; sixth server took many hours; 2010 versions, may change | "under load, it takes many hours for Cassandra to stabilize"; see rows 11, 12 | §6.2, 6.4, 6.7 p9-10 | measured_result | pass; link p9 correct |
| 24 | Comic howTo: all numbers from the paper | Checked below | n/a | n/a | pass |
| 25 | Strip 1: many stores; none measured same way; Yahoo! built one test | Abstract; "Our goal is to create a standard benchmark" | p1 | model_design | pass |
| 26 | Strip 2: ten fields of 100 bytes, about 1,000 bytes | "1,000 byte records by using F = 10 fields, each of L = 100 bytes" | §4 p4 | model_design | pass |
| 27 | Strip 2: insert, update, read, scan | "Insert ... Update ... Read ... Scan" | §4 p4-5 | model_design | pass |
| 28 | Strip 2: some records far more popular | "some records will be extremely popular (the head of the distribution)" (Zipfian) | §4.1 p5 | model_design | pass |
| 29 | Strip 3: A half reads half updates, session store | Table 2: "Read: 50% Update: 50%"; "Session store recording recent actions in a user session" | p6 | model_design | pass |
| 30 | Strip 3: B 95/5, photo tagging; C reads only; D newest | Table 2: "Read: 95% Update: 5%", "Photo tagging"; "Read: 100%"; "Read latest" | p6 | model_design | pass |
| 31 | Strip 3: E short scans, thread posts, a few inserts | Table 2: "Scan: 95% Insert: 5%"; "Threaded conversations, where each scan is for the posts in a given thread" | p6 | model_design | pass |
| 32 | Strip 4: 120 million records, 120 GB; same disks | §6.1 quote in row 13 | p8 | model_design | weakened: "Most tests used six machines per store" |
| 33 | Strip 4: replication off; developers helped tune | rows 21, 22 | p8 | model_design | pass |
| 34 | Strip 4: Cassandra 0.5.0, HBase 0.20.3, MySQL 5.1; newer may do better | "Cassandra 0.5.0, HBase 0.20.3, and MySQL 5.1.24 (for PNUTS) and 5.1.32"; "performance may change and improve" | §6.1 p8 | measured_result | weakened: elastic test version 0.6.0-beta2 added |
| 35 | Strip 5: A numbers 11978 / 7904 / 7283 / 7448 | row 10 | p9 | measured_result | pass |
| 36 | Strip 5: sequential disk, reads waited less for disk head | "Cassandra's efficient sequential use of disk for updates reduces contention for the disk head, meaning that read latency is lower than for the other systems" | §6.2 p9 | measured_result | pass |
| 37 | Strip 5: B, PNUTS and MySQL faster reads | row 15 | p9 | measured_result | pass |
| 38 | Strip 6: E, 1519 and 1440, Cassandra much worse; new in 0.5.0 | row 11 | p9 | measured_result | pass |
| 39 | Strip 6: sixth server, data moved, stopped after 5.5 hours | row 12 | p10 | measured_result | pass |
| 40 | Grown-up words (benchmark, workload, throughput, latency, Zipfian, replication, heap, RAID, update-heavy, sequential I/O, range scan, repartitioning) | All appear in the paper (heap, RAID-10 in §6.1; "repartitioning" §6.7) | p1-p10 | background | pass |
| 41 | Comic pictures and alt text | Our drawings | n/a | n/a | scenario |

## Tag evidence (`tags[]`)

| Tag | Link | Exact phrase | Result |
|---|---|---|---|
| field/computer-science, area/distributed-systems, area/databases, technique/ycsb, concept/benchmarking, organization/yahoo, author/brian-f-cooper, venue/socc, venue/socc-2010 | p1 | Title, author block, "Yahoo! Research", "SoCC'10", abstract | pass |
| technique/cassandra, technique/hbase, technique/pnuts, technique/mysql | p8 | "We ran Cassandra 0.5.0, HBase 0.20.3, and MySQL 5.1.24 (for PNUTS) and 5.1.32 (for sharded MySQL)" (§6.1) | pass |
| concept/elasticity | p10 | "good elastic scaling properties"; §6.7 "Elastic Speedup" | pass |
| concept/eventual-consistency | p7 | "Cassandra's is similar to Dynamo (e.g., using gossip and eventual consistency)" (§5.2.1); also p3 | pass (p3 is where the topic is introduced) |

## Summary

Rows 1-41 plus 14 tag rows. Pass: majority. Weakened (fixed in JSON): rows 6, 13, 18, 20, 21, 32, 34. Owner check: row 2 (trust). Scenario/background: rows 9, 17 (picture), 40, 41.
