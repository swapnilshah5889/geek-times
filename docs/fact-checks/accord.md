# Fact-check: "CEP-15: Fast General Purpose Transactions" (ACCORD whitepaper, Apache Cassandra wiki)

Source: Elliott Smith, Benedict; Zhang, Tony; Eggleston, Blake; Andreas, Scott (PDF p1, printed "Last, First"; the first author is Benedict Elliott Smith, so the story's "Elliott Smith and colleagues" matches the printed surname). Running header on every page: "Draft Whitepaper for CEP-15: General Purpose Transactions".
Venue/date as printed: none. No venue, no date, no publisher is printed. The story's `year: 2021` comes only from PDF metadata (CreationDate 15 Nov 2021), not visible text. The story text never states a date; the `year` field is the only place 2021 appears.
Canonical URL: https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-15%3A+General+Purpose+Transactions (CEP page, secondary).
Fetched URL: https://cwiki.apache.org/confluence/download/attachments/188744725/Accord.pdf (used for all links).
Archive: none captured.
Extraction: `pdftotext -layout`, 25 PDF pages (p1-p25), 96,806 characters. Quotes matched against the per-page text.
Checked on 2026-11-12.

**Location convention.** Links use `#page=N` (PDF page index; no printed page numbers). Section numbers are the paper's own: 1 Introduction (p1-2), 2 Predictable Leaderless Protocols (p2), 2.1 Flexible Fast-Path Quorums (p3), 2.1.1 Fast-Path Electorates (p3-4), 2.2 Timestamp Reorder Buffer (p4), 2.2.1 Clock Synchrony versus Latency (p4), 3 ACCORD Basic Protocol (p5), 3.1 Overview (p5), 3.2 Consensus (p5-7), 3.3 Execution (p7), 3.4 Safety (p8), 4 Recovery Protocol (p8-10), 5 Reconfiguring Electorates (p10-11), 6 Related Work (p11), Appendix (p12 on).

**Result key.** `pass` = in the paper or a plain restatement. `weakened` = wording went beyond the paper; fixed in the JSON. `scenario` = our invented picture, labelled illustration. `background` = not from the paper.

**What is in the paper:** the argument that leaderless fast paths stop working under fewer failures than tolerated; flexible fast-path electorates; the timestamp reorder buffer; the PreAccept/Accept/Commit/Execute/Apply protocol; recovery; reconfiguration; safety and liveness proofs.
**What is not in the paper:** any evaluation, benchmark or measured result; any statement that Cassandra has shipped or adopted ACCORD (it says only "We propose"); the words "desk", "captain", "waiting line" (metaphors); any printed date.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, authors | "CEP-15: Fast General Purpose Transactions" and the four-author list (PDF p1). The name ACCORD is in the abstract, not the title. | pass |
| 2 | Year 2021 | Not printed. PDF metadata CreationDate Mon Nov 15 2021 only. | background (metadata only; story text shows no date; owner to decide whether `year` should display) |
| 3 | Trust: meta.md suggests `preprint` | "Self-described draft whitepaper hosted on the Apache Cassandra wiki with no venue printed and no peer review evidence; not peer reviewed." Header: "Draft Whitepaper". No peer-review statement anywhere. | FLAG for owner: confirm trust level (preprint suggested; story JSON carries no trust field) |

## Summary, hook, lead

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 4 | Summary: draft proposal for Apache Cassandra | "Draft Whitepaper for CEP-15"; "We propose that this combination of features makes ACCORD uniquely suitable for implementing general purpose transactions in Apache Cassandra." | Header; Abstract, PDF p1 | model_design | pass |
| 5 | Summary: "not a shipped result" | The paper says nothing about whether Cassandra ships ACCORD | n/a | n/a | weakened: removed ", not a shipped result"; "draft proposal" stays |
| 6 | Summary: transactions across many machines without a leader | "a new distributed transaction protocol ACCORD"; "leaderless protocol" | Abstract p1; §1 p2 | model_design | pass |
| 7 | Summary: shrinks voters when machines break | "by modifying these quorums in response to failure, we can retain fast-path availability under any number of tolerated failures" | §1, PDF p2 | model_design | pass |
| 8 | Summary: holds each new job until a set time | "buffering it in a queue ordered by t0 until the computed Deadline" | §2.2, PDF p4 | model_design | pass |
| 9 | Summary: arguments and proofs, no benchmarks | No evaluation section; grep for evaluat/benchmark/experiment finds none; "Theorem 3.1 (Consistency)", "Theorem 4.1 (Liveness)" and appendix "Detailed Proof" | §3.4 p8; §4 p10; App. B | model_design | pass |
| 10 | Hook sticker "A proposal"; cta; `readMinutes` | Editorial | n/a | n/a | background |
| 11 | Hook teaser: "Can many machines agree on an order without a captain?" | Framing of "leaderless" | n/a | scenario | scenario |
| 12 | Hook frames: busy captain with a long line, far-away person waves; no-captain ring with a clock | "a scalability bottleneck"; "additional wide area round-trips for clients that are not co-located with the leader" | Abstract p1; §1 p1 | model_design | pass (pictures are ours) |
| 13 | Lead deck: "A draft proposal for Apache Cassandra, not something Cassandra ships" | Paper does not say what Cassandra ships | n/a | n/a | weakened: now "A draft proposal for Apache Cassandra: a way for many machines to agree..." |
| 14 | Lead deck: agree on order without one machine in charge | "leaderless" | Abstract p1 | model_design | pass |
| 15 | Fig. 1: many systems pick a leader; it can get busy; far-away clients wait | "Traditional SMR protocols ... rely on a stable leader"; "the single leader in these protocols is a bottleneck that limits throughput, and results in increased latency for remote clients" | §6, PDF p11 | model_design | pass |
| 16 | Fig. 2: "Any desk can start a job, and a clock decides the order." | "selects a nearby non-replica coordinator C"; "assigning them each a unique execution timestamp" | §3.1 p5; §3.2 p5 | model_design | weakened: a nearby coordinator (not any replica) starts the job. Now "A nearby helper can start a job, and timestamps decide the order." |

## Story chapters (provenance: illustration, evidence for ch. 4)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 17 | Ch.1: copies in many places so it survives breakage | "replicate and shard their state to achieve fault tolerance and scalable performance" | Abstract p1 | model_design | pass |
| 18 | Ch.1: databases get agreement with a leader, costing speed at scale or weaker guarantees | "leader-based techniques that entail trade-offs: either a scalability bottleneck or weaker isolation" | Abstract p1 | model_design | pass |
| 19 | Ch.1: leaderless systems exist but have not made it into real products | "Recent advances in leaderless protocols ... have not yet translated into production systems"; "these have not been used in real systems" | Abstract p1; §1 p1 | model_design | pass |
| 20 | Ch.1: grown-up words replication, shards, leader-based | "replicate and shard"; "leader-based techniques" | Abstract p1 | model_design | pass |
| 21 | Ch.2: quick path needs many answers; stops with fewer failures than tolerated overall; extra messages | "fast-path quorums that are disabled by fewer failures than are tolerated overall"; "remaining processes must exchange additional messages to reach slow-path consensus" | §1 p1; §2.1 p3 | model_design | pass |
| 22 | Ch.2: one plan allows at most one broken replica | "at most one replica may fail before its fast-path is unable to reach decisions" (Tempo) | §1 p1 | model_design | pass |
| 23 | Ch.2: grown-up words fast path, slow path, leaderless protocol | same sections | §1-2 | model_design | pass |
| 24 | Ch.3: "a proposal, not a shipped feature" | See row 5 | n/a | n/a | weakened: now "a proposal in a draft paper" |
| 25 | Ch.3: shrink the group whose votes count so the quick path still works | "in the case of the fast-path we may remove replicas in order to reduce the successful vote threshold" | §2.1.1 p3 | model_design | pass |
| 26 | Ch.3: desks hold new jobs until a set time so near and far jobs arrive in the same order everywhere | "if message processing time is derived from the transaction's proposed execution timestamp we are able to guarantee fast-path consensus"; "We assume that our bounds on message latency and clock synchrony are not breached"; "out-of-order transaction arrival does not result in any additional messages being exchanged" | §2.2 p4 | model_design | weakened: the guarantee is conditional on the assumed bounds and is about fast-path consensus without extra messages. Now "if the paper's clock and travel-time limits hold, jobs from near and far are handled in time order with no extra messages" |
| 27 | Ch.3: grown-up words electorate, timestamp reorder buffer, clock skew | "electorate"; "Timestamp Reorder Buffer"; "clock skew" | §2.1.1, §2.2 p3-4 | model_design | pass |
| 28 | Ch.4: no benchmark; reasons and proofs that every copy stays in the same order | "Theorem 3.1 (Consistency) ... γ will be applied before τ on all replicas in common" | §3.4 p8 | model_design | pass |
| 29 | Ch.4: recovery can finish stuck jobs | "Theorem 4.1 (Liveness). A transaction τ that is known by at least one healthy replica will always execute eventually" | §4 p10 | model_design | pass |
| 30 | Ch.4: performance claims, matching leader-based systems under contention and failure, are claims on paper | "ACCORD is the first protocol to achieve the same steady-state performance as leader-based protocols under important conditions such as contention and failure" | Abstract p1 | model_design | pass |
| 31 | Ch.4: "Real tests would still be needed." | Our inference from the absence of an evaluation | n/a | n/a | background (editorial, stated as ours) |
| 32 | Ch.4 link "See the safety section" `#page=8` | §3.4 Safety starts on PDF p8 | p8 | n/a | pass |

## Comic

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 33 | Deck/howTo: design as the paper proposes it; no measured results | See row 9 | n/a | model_design | pass |
| 34 | Strip 1 p1: person gives job to nearby helper (coordinator), who asks desks to vote on a time | "selects a nearby non-replica coordinator C"; "coordinator proposes a timestamp for execution" | §3.1 p5; §3.2 p6 | model_design | pass |
| 35 | Strip 1 p2: enough matching answers settle the job in one trip (fast path) | "If a fast-path quorum of replicas unanimously accept and record this timestamp ... it is decided immediately" | §3.2 p6 | model_design | pass |
| 36 | Strip 1 p3: disagreement, one more round, at most two trips | "consensus is reached in at most two round-trips" | §3 p5 | model_design | pass |
| 37 | Strip 1 grown-up words PreAccept, Accept, fast path, slow path | "PreAccept, Accept, Commit, Execute and Apply" | §3.1 p5 | model_design | pass |
| 38 | Strip 2 p1: nine desks, voting group starts at nine | "a replica set of r = 9 ... could choose an electorate of size 9, 7 or 5" | §2.1.1 p4 | model_design | pass |
| 39 | Strip 2 p2: shrinks to seven or five so fewer votes needed | "conferring fast-path quorums of 7, 6 and 5 respectively" | §2.1.1 p4 | model_design | pass |
| 40 | Strip 2 p3: at the maximum tolerated failures, quick and normal path use the same group, no extra messages | "all fast- and slow-path decisions would use the same quorum"; "no additional per-transaction messages must be exchanged" | §2.1.1 p4; §2.1 p3 | model_design | pass |
| 41 | Strip 2 grown-up words electorate, fast-path quorum | same | §2.1.1 p3 | model_design | pass |
| 42 | Strip 3 p1: two jobs at once in two far cities; near desks see their own first | "two transactions started at the same time but in different regions ... Those replicas closest to each coordinator will witness its corresponding transaction first" | §2.2 p4 | model_design | pass |
| 43 | Strip 3 p2: waiting line ordered by time until a deadline | "buffering it in a queue ordered by t0 until the computed Deadline" | §2.2 p4 | model_design | pass |
| 44 | Strip 3 p3: both jobs arrived by the deadline, same order everywhere | "We assume that our bounds on message latency and clock synchrony are not breached" | §2.2 p4 | model_design | weakened: conditional. Now "If the paper's clock and travel-time limits hold, ..." |
| 45 | Strip 3 grown-up words timestamp reorder buffer, clock skew | same | §2.2 p4 | model_design | pass |
| 46 | Strip 4 p1: waiting adds a delay as big as the gap between clocks | "an additional latency penalty equal to the bounds on clock synchrony" | §2.2.1 p4 | model_design | pass |
| 47 | Strip 4 p2: "good data centers keep clocks within less than a millisecond, so the delay is small next to long-distance travel" | "clock skew may be sub-millisecond [15], so that this penalty will likely be dwarfed by wide-area latency" | §2.2.1 p4 | model_design | weakened: "may be", "likely". Now "data centers with a good time source may keep clocks within a millisecond, so the delay will likely be small" |
| 48 | Strip 4 p3: each place has its own time source, a fixed cost not growing with distance | "each locale has its own time source and dissemination mechanism, so that accommodating clock skew represents a fixed global penalty" | §2.2.1 p4 | model_design | pass |
| 49 | Strip 4 grown-up words clock synchrony, GPS, NTP | "GPS ... NTP or PTP" | §2.2.1 p4 | model_design | pass |
| 50 | Strip 5 p1: helper starts a job then disappears | "Should the coordinator fail" (the picture is ours) | §3.1 p5 | scenario | scenario |
| 51 | Strip 5 p2: a desk that saw the job notices (rough failure detector) and takes over | "a weak failure detector invokes the recovery protocol on a replica that has witnessed the transaction, that then takes over the coordinator role" | §3.1 p5 | model_design | pass |
| 52 | Strip 5 p3: asks others what they saw, finishes in the same order | "contacts a recovery quorum"; "the same total order will be recovered" | §4 p8; §3.2 p6 | model_design | pass |
| 53 | Strip 6 p1: group of voters may change, e.g. a desk joins | "A configuration consists of ... the membership of all shards ρ and their fast-path electorates E"; "replicas that join the electorate" | §5 p10-11 | model_design | pass |
| 54 | Strip 6 p2: new desk first told every quick decision made before it joined | "until all fast-path decisions from the prior configuration are known to them" | §5 p11 | model_design | pass |
| 55 | Strip 6 p3: only then may it vote; keeps the move safe | "must not participate in any fast-path decision until ..."; "This ensures atomic migration from one configuration to another." | §5 p10-11 | model_design | pass |
| 56 | Strip 5/6 grown-up words recovery protocol, failure detector, reconfiguring electorates, epoch | "Recovery Protocol"; "weak failure detector"; "Reconfiguring Electorates"; "epoch identifier" | §4, §5 | model_design | pass |

## Facts (`facts[]`)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 57 | Fact 1 "1 trip": one round trip when it can, at most two; Caesar needs three. Link `#page=11` | "ACCORD has a worst case execution path of two wide area round-trips instead of Caesar's three"; Table 1 "ACCORD 1" | §6 p11; §1 p2 | model_design | pass |
| 58 | Fact 2 "at most 1": Tempo loses at most one replica; tolerates f overall; the problem ACCORD fixes. Link `#page=1` | "Tempo [11] tolerates f failures using 2f + 1 replicas, but at most one replica may fail before its fast-path is unable to reach decisions." | §1 p1 | model_design | pass |
| 59 | Fact 3 "9 to 5": nine desks shrink to seven or five; quorum 7, 6 or 5. Link `#page=4` | "an electorate of size 9, 7 or 5 conferring fast-path quorums of 7, 6 and 5 respectively" | §2.1.1 p4 | model_design | pass |
| 60 | Fact 4 "sub-ms": clock gaps under a millisecond, extra wait small; argued, not tested. Link `#page=4` | "clock skew may be sub-millisecond [15], so that this penalty will likely be dwarfed by wide-area latency" | §2.2.1 p4 | model_design | weakened: "would be small" now "would likely be small" |
| 61 | Fact 5 "5 phases": PreAccept, Accept, Commit, Execute, Apply; Accept skippable. Link `#page=5` | "PreAccept, Accept, Commit, Execute and Apply ... Only Accept may be skipped, if the fast path is taken." | §3.1 p5 | model_design | pass |
| 62 | Fact 6 "0 tests": no evaluation; arguments and proofs for safety and liveness; draft whitepaper for Cassandra. Link `#page=8` | "3.4 Safety"; "Theorem 4.1 (Liveness)" (p10); header "Draft Whitepaper"; no evaluation section | §3.4 p8; §4 p10 | model_design | pass (the link lands on §3.4; liveness is on p10) |

## Tag evidence (all `basis: paper`)

| # | Tag | Evidence link | Phrase | Result |
|---|---|---|---|---|
| 63 | field/computer-science, area/distributed-systems, area/databases | `#page=1` | "Modern applications replicate and shard their state ... modern databases address" | pass |
| 64 | technique/cassandra, technique/accord | `#page=1` | "uniquely suitable for implementing general purpose transactions in Apache Cassandra" | pass |
| 65 | concept/replication | `#page=1` | "replicate and shard their state" | pass |
| 66 | concept/quorum | `#page=2` | "Robustness. Fast-path quorums are said to be collectively robust..." | pass |
| 67 | concept/distributed-transactions | `#page=1` | "a new distributed transaction protocol ACCORD" | pass |
| 68 | concept/leaderless-consensus | `#page=2` | "Predictable Leaderless Protocols" | pass |

## Counts

68 rows: pass 54, weakened 8 (rows 5, 13, 16, 24, 26, 44, 47, 60), scenario 2, background 3 (rows 2, 10, 31), trust flag 1 (row 3).

## Open items for the owner

- Trust level: `preprint` suggested; confirm.
- `year: 2021` is PDF metadata only. The story text prints no date, but the `year` field will display 2021 if the UI shows it.
