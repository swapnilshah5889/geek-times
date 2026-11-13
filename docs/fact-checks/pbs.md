# Fact-check: "Probabilistically Bounded Staleness for Practical Partial Quorums" (Bailis, Venkataraman, Franklin, Hellerstein, Stoica; PVLDB 5(8), VLDB 2012)

Source: Peter Bailis, Shivaram Venkataraman, Michael J. Franklin, Joseph M. Hellerstein, Ion Stoica (all University of California, Berkeley). Printed venue: "Proceedings of the VLDB Endowment, Vol. 5, No. 8"; "Copyright 2012 VLDB Endowment 2150-8097/12/04"; "Articles from this volume were invited to present their results at The 38th International Conference on Very Large Data Bases, August 27th - 31st 2012, Istanbul, Turkey." (PDF p1). No exact publication day is printed. The story says `year: 2012` and authors "Bailis and colleagues".
Canonical URL: https://vldb.org/pvldb/vol5/p776_peterbailis_vldb2012.pdf
Fetched URL: the same (HTTP 200, application/pdf, 12 pages).
Archive: none recorded (a Wayback snapshot exists at http://web.archive.org/web/20261014044058/https://vldb.org/pvldb/vol5/p776_peterbailis_vldb2012.pdf but the live PDF was used). An arXiv preprint (arXiv:1204.6082v1, 26 Apr 2012) was saved but not extracted.
Extraction: `pdftotext` per page (p1-p12), quotes matched against the per-page text.
Checked on 2026-11-12.

**Location convention.** `#page=N` is the PDF page index (the printed page number is N + 775: PDF p2 = 777). Sections as printed: 1 Introduction (1.1, 1.2), 2 Background (2.1-2.3), 3 PBS (3.1-3.5), 4 Dynamo-style t-visibility (4.1 WARS, 4.2, 4.3), 5 Evaluating (5.1 Experimental Validation, 5.2 Monte Carlo, 5.3 Write Latency, 5.4 Production Latency Distributions, 5.5 Model Fitting, 5.6 Observed t-visibility, 5.7 Quorum Sizing), Discussion (printed under a stray "5.8" heading, cross-referenced as Section 6), 7 Related Work, 8 Conclusion. Table 4 is on PDF p11.

**Result key.** `pass` = as worded in the paper. `weakened` = wording went beyond the paper; the fix is in the Result column and applied in the JSON. `scenario` = our invented example, labelled illustration. `background` = not from the paper.

**What is in the paper:** the PBS definitions (k-staleness, t-visibility), the closed form for k-staleness, the WARS model, a Monte Carlo simulator validated on Cassandra, and predictions fitted to latency summaries that LinkedIn (Voldemort) and Yammer (Riak) gave the authors, plus a synthetic WAN case.
**What is not in the paper:** the desks, notes, helper, runners and "Pizza at 6/7" scenario; any measurement of staleness on LinkedIn's or Yammer's live systems (the data were latency summaries, fitted to distributions, see §5.5); any claim that the LinkedIn or Yammer deployments ran Cassandra.

**Claim kinds.** The 1.85/45.5 ms, 43.9%, 97.4%, 1364/202 ms and 81.1% figures are model predictions (Monte Carlo over distributions fitted to the companies' latency data), so they are `model_design`. Only the 0.28% Cassandra validation error compares prediction against something measured (WARS latencies and staleness observed on Cassandra), so it stays `measured_result`.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, authors, year 2012 | Title page lists the five authors, Berkeley; "Copyright 2012 VLDB Endowment" (PDF p1) | pass |
| 2 | Trust: `journal_published` suggested | Venue quoted above. The PDF does not say "peer reviewed" or "refereed" | background: **owner decides**; do not upgrade to `peer_reviewed` without an external check (e.g. the VLDB 2012 call for papers) |
| 3 | Venue tags `venue/vldb`, `venue/vldb-2012` (`basis: background`) | "Proceedings of the VLDB Endowment, Vol. 5, No. 8"; "38th International Conference on Very Large Data Bases, August 27th - 31st 2012" (p1) | pass (as background) |

## Summary, hook, lead

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 4 | Summary: stores like Dynamo and Cassandra keep copies on several machines and answer fast by asking only some | "Quorum-replicated data stores such as Dynamo [20] and its open source descendants Apache Cassandra [41], Basho Riak [3], and Project Voldemort [24]"; "a data store waits for responses from a subset of replicas before answering a query" | Abstract p1; §1.1 p1 | model_design | pass |
| 5 | Summary: they promise "eventually" but never say how old a read can be | "these configurations provide only basic eventual consistency guarantees, with no limit to the recency of data returned" | Abstract, p1 | model_design | pass |
| 6 | Summary: a way to predict how likely a read is fresh and how long to wait | "providing the probability of reading a write t seconds after it returns (t-visibility ...)" | §1.2, p2 | model_design | pass |
| 7 | Summary: checked against Cassandra, fed real LinkedIn and Yammer latency numbers | "Our WARS predictions matched our empirical observations of Cassandra's behavior"; "we obtained production latency statistics from two internet-scale companies" | §5.1 p7; §5.4 p7 | model_design | pass (the data are summary statistics that were fitted, as chapter 4 and the facts say) |
| 8 | Hook sticker "How old is old?", teaser, cta "Meet the odds", `readMinutes: 4` | Framing and editorial | n/a | n/a | scenario / background |
| 9 | Hook stat "1.85 ms vs 45.5 ms: wait for 99.9% fresh reads, SSD vs disk" | "1.85ms versus 45.5ms wait time for a 99.9% probability of consistent reads"; Table 4 LNKD-SSD 1.85, LNKD-DISK 45.5 (R=W=1) | §1.2 p2; Table 4 p11 | model_design | weakened: stat read as a measurement. Now "predicted wait for 99.9% fresh reads". Fixed in JSON |
| 10 | Lead deck: databases keep several copies, promise "eventually", never say how old; "This paper measures it and predicts it, using real latency numbers" | "no limit to the recency of data returned" (p1). The paper measures staleness only on Cassandra under injected latencies (§5.1); everything else is simulated | Abstract p1; §5.1 p7 | model_design | weakened: draft said the paper "measures it ... using real latency numbers". Now "predicts it with a model, and feeds the model latency numbers from real systems". Fixed in JSON |
| 11 | Fig. 1 caption: a new note still on its way; a reader gets the old note | Our picture. The idea matches "reads are stale when all of the first R responses to the read request arrived at their replicas before the last (committed) write request" (§4.1 p5) | n/a | scenario | scenario |
| 12 | Fig. 2 caption: the paper works out how likely a fresh answer is, and how long to wait | "the probability of reading a write t seconds after it returns (t-visibility ...)" | §1.2 p2 | model_design | pass |

## Story chapters (provenance: illustration, evidence for chapter 4)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 13 | Ch. 1: copies on a few machines; answer after hearing from only some | "a data store waits for responses from a subset of replicas before answering a query, without guaranteeing that read and write replica sets intersect" | Abstract p1 | model_design | pass |
| 14 | Ch. 1: promise only that the latest version shows up "eventually" if no new writes come, no limit on age | "the system will 'eventually' return the most recent version in the absence of new writes" | §1, p1 | model_design | pass |
| 15 | Ch. 1: many operators use them anyway; the reason was mostly anecdotal | "operators frequently employ partial quorums"; "to date, this observation has been anecdotal" | §1.1, p1 | model_design | pass |
| 16 | Ch. 2: PBS answers how old in versions and how long in time | "t-visibility ... k-staleness" (versions) | §1.2 p2 | model_design | pass |
| 17 | Ch. 2: PBS does not change how stores work; a way to look at, predict, tune them | "PBS does not propose new mechanisms ...; instead, our goal is to provide a lens for analyzing, improving, and predicting the behavior of existing, widely deployed systems" | §1.2 p2 | model_design | pass |
| 18 | Ch. 3: a write goes to every copy, counts as done after W reply; a read asks every copy and takes the first R | "Coordinators send all requests to all replicas but consider only the first R (W) responses" | §2.2 p3 | model_design | pass (Voldemort sends reads to only R replicas, noted in §2.3; the story describes the Dynamo style) |
| 19 | Ch. 3: stale only when the first R answers come from replicas the write has not reached | "The read coordinator will return stale data if the first R responses received reached their replicas before the replicas received the latest version" | §4.1 p6 | model_design | pass |
| 20 | Ch. 3: four delays (write out, ack back, read out, answer back); the WARS model | "ack ... distribution W ... A ... R ... S" and "we introduce a model ... that, for convenience, we call WARS" | §4.1 p5-p6 | model_design | pass |
| 21 | Ch. 3: a formula for versions; a simulation of random delays for time | "closed-form solutions for PBS k-staleness and use Monte Carlo methods"; "draw N samples from W, A, R, and S" | §1.2 p2; §5.2 p7 | model_design | pass |
| 22 | Ch. 4: modified Cassandra on three servers, compared measured with predicted | "We modified Cassandra to profile WARS latencies, disabled read repair"; "Cassandra on three servers with 2.2GHz AMD Opteron 2214 ..."; "Our WARS predictions matched our empirical observations" | §5.1 p7 | measured_result | pass |
| 23 | Ch. 4: "average error ... 0.28%" | "Our average t-visibility prediction RMSE was 0.28% (std. dev. 0.05%, max. 0.53%)" | §5.1 p7 | measured_result | weakened: "average error" hides that it is a root-mean-square error of t-visibility. Now "average error (root-mean-square)". Fixed in JSON |
| 24 | Ch. 4: LinkedIn (Voldemort, disks and SSDs) and Yammer (Riak) gave the latency numbers; the authors built the WAN case; fitted models, not live Cassandra traffic | "LinkedIn provided two latency distributions, whose fits we denote LNKD-SSD and LNKD-DISK"; "Yammer ... uses Basho's Riak"; "We also considered a wide-area network replication scenario, denoted WAN" | §5.4 p8; §5.5 p8 | model_design | pass (traces are from Voldemort and Riak deployments; Cassandra was the validation target only. The story says so) |
| 25 | Ch. 4: with SSDs wait for 99.9% fresh reads 1.85 ms, 45.5 ms with disks; links Section 5.6 (`#page=9`) and Table 4 (`#page=11`) | Table 4 p11; §5.6 p9 discusses LNKD-SSD 1.85 ms | §5.6 p9; Table 4 p11 | model_design | pass (both pages correct) |

## Comic (provenance: illustration)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 26 | Deck / howTo: made-up drawings; Pizza at 6, then 7 | Our scenario | n/a | scenario | scenario |
| 27 | S1: copies keep the note safe if one desk breaks | "to provide high availability when components fail" | §1 p1 | model_design | pass |
| 28 | S1 panel 2: N is 3, "which the paper says is typical, between one and three" | "replication factors for data stores are low, typically between one and three" | §2.2 p3 | model_design | weakened: the paper says one to three is typical, not that 3 specifically is. Now "Here N is 3. The paper says the number of copies is low in practice, typically between one and three." Fixed in JSON |
| 29 | S1 panel 3: helper sends the new note to all three desks | "A coordinator node handles the client write and sends it to all N replicas" | Fig. 1, §2.2 p3 | model_design | pass |
| 30 | S2: first "got it", W=1 enough; others not yet reached | "The write call returns after the coordinator receives W acknowledgments"; "the write quorum size increases even after the operation returns, growing via anti-entropy" | Fig. 1 p3; §2.2 p3 | model_design | pass ("closest desk" is our picture) |
| 31 | S3: R=1 takes the first answer; old desk gives stale, lucky desk fresh | "only considered the first R responses"; "stale if READ arrives before WRITE" | §4.1 p6; Fig. 3 | model_design | pass |
| 32 | S4: R + W bigger than N is a strict quorum | "Dynamo-style systems guarantee consistency when R+W >N"; "strict quorum system ... any two quorums ... overlap" | §2.2 p3; §2.1 p2 | model_design | pass |
| 33 | S4: asking more desks means waiting for slower ones; fewer is quicker, a partial quorum | "partial quorums can lower latency by requiring fewer replicas to respond"; Table 4 (R=3 read latency 219 ms vs 5.6 ms at R=1 for YMMR) | §1.1 p1; Table 4 p11 | model_design | pass |
| 34 | S4 panel 3: Cassandra default N=3, R=1, W=1; Riak default R=2, W=2 | "Cassandra defaults to N =3, R=W =1"; "Riak defaults to N =3, R=W =2" | §2.3 p3 | model_design | pass |
| 35 | S5: a read is stale if its question reaches desks before the note; a race | "reads are stale when all of the first R responses to the read request arrived at their replicas before the last (committed) write request" | §4.1 p5 | model_design | pass |
| 36 | S5: the note keeps spreading after the writer is told it is done | "the write quorum size increases even after the operation returns, growing via anti-entropy" | §2.2 p3 | model_design | pass |
| 37 | S5: waiting makes a read fresher; the wait is t; how big t for 99.9% | "t-visibility is the probability that a read operation, starting t seconds after a write commits, will observe the latest value" | §3.4 p5 | model_design | pass |
| 38 | S6 panel 1: measure trip times on real machines; some quick, a few very slow | The authors profiled WARS latencies on Cassandra (§5.1 p7); the companies supplied round-trip summaries, which the authors turned into one-way fits (§5.5 p8) | §5.1, §5.5 | model_design | weakened: draft implied the authors measured every trip on real machines. Now "Get real trip times: the authors profiled Cassandra, and two companies shared their production latencies. Some trips are quick, a few are very slow." Fixed in JSON |
| 39 | S6 panel 2: replay many times, picking trip times at random from the measured ones | "draw N samples from W, A, R, and S at time t" (distributions, fitted in §5.5) | §5.2 p7 | model_design | weakened: samples come from fitted distributions. Now "from curves fitted to the real ones". Fixed in JSON |
| 40 | S6 panel 3: ran against Cassandra, counts matched; then tried other settings on paper | "Our WARS predictions matched our empirical observations of Cassandra's behavior"; "This validates our Monte Carlo simulator." | §5.1 p7 | measured_result | pass |
| 41 | S6 title "Replay the race a million times" | Table 4 caption: "(1M reads and writes)"; §5.6: "across 10M writes" for LNKD-SSD | Table 4 p11; §5.6 p9 | scenario | pass (a figure of speech; the paper's runs are 1M and 10M) |
| 42 | grownUpWords (replication, W, R, strict quorum, t-visibility, WARS, anti-entropy, Monte Carlo ...) | Terms all appear in the paper | §2-§5 | background | pass |

## Facts block

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 43 | Fact 1: 1.85 ms vs 45.5 ms, SSD vs disk, LinkedIn data; writes quicker and steadier on SSDs. Link `#page=2` | "1.85ms versus 45.5ms wait time for a 99.9% probability of consistent reads ... due to decreased write latency mean and variance" | §1.2 p2; Table 4 p11 | model_design | weakened: kind was `measured_result`; these are predictions from a model fitted to LinkedIn's data. Now `model_design`, text says "predicts" and names the Voldemort store. Fixed in JSON. Link correct |
| 44 | Fact 2: 43.9% fresh right after a write finished on disk data; 97.4% for SSD, above 99.999% after five ms. Link `#page=9` | "immediately after write commit, LNKD-DISK had only a 43.9% probability of consistent reads"; "LNKD-SSD had a 97.4% probability ... over a 99.999% probability ... after five milliseconds" | §5.6 p9 | model_design | weakened: kind `measured_result` and wording "was the chance". Now `model_design`, "the model's predicted chance", Voldemort data named. Fixed in JSON |
| 45 | Fact 3: 1364 ms for 99.9% fresh reads at R=1, W=1 on Yammer; R=2 brings it to 202 ms. Link `#page=9` | "R=W =1 results in low latency reads and writes (16.4ms) but high t-visibility (1364ms)"; "setting R=2 and W =1 reduces t-visibility to 202ms" | §5.6 p9; Table 4 p11 | model_design | weakened: same kind and wording issue. Now `model_design`, "the model's predicted wait", Yammer's Riak data named. Fixed in JSON |
| 46 | Fact 4: 0.28% average error vs Cassandra on three servers. Link `#page=7` | "Our average t-visibility prediction RMSE was 0.28%"; "Cassandra on three servers" | §5.1 p7 | measured_result | pass (stays `measured_result`: prediction against measured Cassandra behaviour; "average error" tweak is in row 23) |
| 47 | Fact 5: 81.1% lower combined latency at 99.9th pct (230 to 43.3 ms), for a 202 ms window, Yammer. Link `#page=2` | "we observe an 81.1% combined read and write latency improvement at the 99.9th percentile (230 to 43.3ms) for a 202ms window of inconsistency (99.9% probability consistent reads)"; §5.6: "lower than the fastest strict quorum (W =1, R=3)" | §1.2 p2; §5.6 p9 | model_design | weakened: kind and "reports for Yammer's data". Now `model_design`, "the paper's model predicts for Yammer's Riak data", and says "against the fastest strict quorum". Fixed in JSON |
| 48 | Fact 6: Cassandra default N=3, R=W=1; Riak N=3, R=W=2; most practitioner accounts never mention staleness. Link `#page=3` | "Cassandra defaults to N =3, R=W =1"; "Riak defaults to N =3, R=W =2"; "Most of these accounts did not discuss the possibility or occurrence of staleness" | §2.3 p3 | model_design | pass (a reported setting, not a measurement; kind kept) |

## Paper-basis tag evidence

| # | Tag | Evidence link | Check | Result |
|---|---|---|---|---|
| 49 | field/computer-science, area/distributed-systems, area/databases, concept/eventual-consistency, concept/replication, concept/staleness, organization/uc-berkeley, author/peter-bailis | `#page=1` | Title, authors, Berkeley and the abstract on p1 | pass |
| 50 | concept/quorum, technique/pbs | `#page=2` | "Quorum Foundations: Theory", "Probabilistically Bounded Staleness (PBS)" (p2) | pass |
| 51 | technique/dynamo, technique/riak, technique/voldemort | `#page=3` | §2.2 and §2.3 name Dynamo, Riak, Voldemort (p3) | pass |
| 52 | technique/cassandra, concept/monte-carlo-simulation | `#page=7` | §5.1 Cassandra validation, §5.2 Monte Carlo (p7) | pass |
| 53 | organization/linkedin, organization/yammer | was `#page=7`; now `#page=8` | p7 says only "two internet-scale companies"; LinkedIn and Yammer are named on p8 (§5.4) | weakened: evidence page moved to p8. Fixed in JSON |
| 54 | concept/tail-latency | `#page=9` | "YMMR's long tail hampered its t-visibility increase" (§5.6 p9) | pass |
| 55 | venue/vldb, venue/vldb-2012 (`basis: background`); everyday/keeping-copies-safe, everyday/teamwork (`basis: editorial`) | none | Printed venue on p1; editorial tags carry no paper claim | background |

## Counts

55 rows: pass 39, weakened 11 (rows 9, 10, 23, 28, 38, 39, 43, 44, 45, 47, 53; all fixed in the JSON), scenario 3 (rows 8, 11, 26), background 2 (rows 2, 55).

## JSON edits made (`data/seed/papers/pbs.json`)

- Hook stat text: "predicted wait for 99.9% fresh reads".
- Lead deck: "predicts it with a model, and feeds the model latency numbers from real systems" (was "measures it and predicts it, using real latency numbers").
- Chapter 4: "average error (root-mean-square)".
- Comic S1 panel 2: N is 3, the paper says copies are typically between one and three.
- Comic S6 panels 1 and 2: trip times from Cassandra profiling and company data; samples from fitted curves.
- Facts 1, 2, 3, 5: `claim` changed from `measured_result` to `model_design`; wording says "predicts" and names Voldemort or Riak; fact 5 adds "against the fastest strict quorum". Fact 4 (0.28%) stays `measured_result`.
- Tags `organization/linkedin` and `organization/yammer`: evidence `#page=7` changed to `#page=8`.
