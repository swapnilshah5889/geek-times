# Fact-check: "Jepsen: Cassandra" (Kyle Kingsbury / Aphyr, aphyr.com, 2013-09-24)

Source: "Jepsen: Cassandra", blog post on aphyr.com. The page prints the site name "Aphyr", no per-post byline (footer: "Copyright © 2026 Kyle Kingsbury"), and the date 2013-09-24. Tags on the page: Software, Network, Distributed Systems, Jepsen, Cassandra. Story `blog.organization` is "Jepsen (Kyle Kingsbury)".
Canonical URL: https://aphyr.com/posts/294-call-me-maybe-cassandra (HTTP 200; https://aphyr.com/posts/294-jepsen-cassandra gives the same page). Fetched: the canonical URL, directly. Archive: none captured in this run.
Extraction: HTML fetched with curl, tags stripped to `source.txt` (about 36 KB; includes reader comments, which were not used as evidence). Checked on 2026-11-12; every quote was matched against `source.txt` and every `#fragment` against ids in `raw.html`.

**Location convention.** The post has six heading ids: `some-write-loses`, `cql-and-crdts`, `counters`, `isolation`, `lightweight-transactions`, `final-thoughts`. The intro (before the first heading) has no id; it is cited as "intro" and linked by the plain URL. All fragments used in the story exist as ids in `raw.html`. No guessed anchors remain.

**Result key.** `pass` = the claim is in the post or a plain restatement. `weakened` = the wording went beyond the post; the Result column says the fix (applied in the JSON). `scenario` = our invented picture, labelled illustration. `background` = not from the post.

**What is in the post:** Cassandra described as a Dynamo-style system with N replicas on different nodes and "a pure last-write-wins approach"; four Jepsen results (lock test 285 of 1009 lost; CQL set adds 2000 of 2000; counters drifting up to 50% under a partition; isolation test 58 of 10000 corrupt rows); lightweight transactions in "Cassandra 2.0.0" (naive Paxos, four round trips, deadlock bugs #6029 and #5985 fixed, then 3 of 829 lost on a patched build, with #6012 and #6013 reported); and a closing section crediting the Cassandra team.
**What is not in the post:** an exact Cassandra build for any test (it names Cassandra 1.0, 1.1, 1.2, 2.0 and 2.0.0 only in discussion, and 2.0.0 for lightweight transactions); how the Jepsen tool works (the post assumes earlier Jepsen posts); any later release. A reader comment (not the post) says DataStax later reported no new issues in 2.1 and 2.2; this is outside the post and is not used in the story.
**Fairness notes.** (1) The post says the team "fixed the bugs I've found so quickly", credits the maintainers, and calls Cassandra "a capable AP datastore"; the story keeps "the team fixed several bugs". (2) The 3-of-829 lightweight-transaction run used patched builds ("You start building patched versions of Cassandra"), so it is not a release result; the story now says so. (3) Author says "there's nothing technically wrong with many of the behaviors I've discussed above"; the story presents the safe cases (set adds, immutable data) as the post does. (4) These are the author's runs in 2013 on versions he does not pin.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, date, author | "Jepsen: Cassandra"; "2013-09-24"; footer "Copyright © 2026 Kyle Kingsbury"; no byline printed | pass |
| 2 | `blog.trust: company_reported` | meta.md: independent tester's personal blog (Jepsen series), "not a company blog"; no refereed venue; not a preprint. The label `company_reported` (used for company blogs) does not fit well | FLAG for owner: trust level needs a decision (independent tester's blog; suggestion in meta.md was "needs owner check"). JSON left unchanged |

## Facts (`facts[]`, hook, summary)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 3 | Summary: outside tester Kyle Kingsbury ran Jepsen on Cassandra in 2013 | "Jepsen: Cassandra"; "2013-09-24"; "Here's a Jepsen test which mutates the same cell repeatedly" | Title, date; Some Write Loses | measured_result | pass |
| 4 | Summary: last-write-wins lost acknowledged writes in some tests | "285 acknowledged writes lost!"; "Cassandra eschews vector clocks in favor of a pure last-write-wins approach" | Some Write Loses | measured_result | pass |
| 5 | Summary: counters and row isolation fell short of what the documentation suggested | Counters: "Cassandra counters will over- or under-count by a wide range during a network partition" (no documentation claim made about counters). Isolation: DataStax docs "writes to a row are isolated to the client performing the write"; "Cassandra row isolation is probabilistic at best" | Counters; Isolation | measured_result | weakened: the documentation contrast is made only for isolation (the post also says "the Cassandra documentation can be less than accurate" about the lock test). Now "counters could drift during a network split, that row isolation fell short of what DataStax's documentation said". Fixed in JSON |
| 6 | Summary: the team fixed several bugs he reported | "they've fixed the bugs I've found so quickly"; "they manage to reproduce and fix the bug: #6029 ... and #5985" | Final thoughts; Lightweight Transactions | measured_result | pass |
| 7 | Hook stat: 285 of 1009 acknowledged writes lost in one run | "1009 acknowledged"; "285 acknowledged writes lost!" | Some Write Loses | measured_result | pass |
| 8 | Hook: sticker "Stamped, then gone?", teaser "A database said 'got it.' Was the data still there later?", cta "Count the lost notes"; `readMinutes: 4` | Editorial framing | n/a | scenario | scenario / background |
| 9 | Hook frame tags "Test it!" and "Lost!"; frame alts (person with clipboard at a ring of six desks; clerk keeps later clock stamp) | Pictures are ours; "keeps N replicas of each chunk on different nodes" (the six desks is invented) | Intro | n/a | scenario |
| 10 | Fact 1: 285 of 1009 lost in the lock test; Cassandra, QUORUM, synced clocks, lock service; 2000 writes tried; loss rate 0.2824579, about 28% | "using perfectly synchronized clocks, QUORUM consistency, and a perfect lock service"; "2000 total / 1009 acknowledged / 724 survivors / 285 acknowledged writes lost!"; "0.2824579 loss rate"; "Losing 28% of your supposedly committed data" | Some Write Loses | measured_result | pass. Link `#some-write-loses` exists |
| 11 | Fact 2: 2000 of 2000 survived when adding items to a CQL set; never-overwrite writes were safe in this test | "2000 total / 2000 acknowledged / 2000 survivors / All 2000 writes succeeded"; "adding elements to a CQL set"; "writing immutable data is safe" | CQL and CRDTs | measured_result | pass. Link `#cql-and-crdts` exists |
| 12 | Fact 3: up to 50% counter drift when partitioned for about half of the run | "If partitioned for about half of the test run, I found counters could drift by up to 50% of the expected value." | Counters | measured_result | pass. Link `#counters` exists |
| 13 | Fact 4: 1 in 200 rows corrupt, 58 of 10000; traced to milliseconds padded with zeroes somewhere in the stack | "58 acknowledged writes lost!"; "10000 total"; "Roughly 1 in 200 rows were corrupt!"; "somewhere in this maze of software, either Cassandra, the DataStax Java driver, or Cassaforte is taking the current time in milliseconds and tacking on three zeroes"; "'writes lost' here means corrupted rows" | Isolation | measured_result | pass (hedged correctly: "somewhere in the software stack"). Link `#isolation` exists |
| 14 | Fact 5: 3 of 829 acknowledged lightweight-transaction writes lost in a 2000-write test at a slowed rate; 1-5% depending on throughput | "2000 total / 829 acknowledged / 827 survivors / 3 acknowledged writes lost!"; "Let's slow down the test to 5 transactions/sec"; "Depending on throughput, they may drop anywhere from 1-5% of acknowledged writes" | Lightweight Transactions | measured_result | weakened: the run was on patched builds ("You start building patched versions of Cassandra ... paxos-fixed-hopefully"); not stated before. Now "run on builds patched for the deadlock bugs". Fixed in JSON. Link `#lightweight-transactions` exists |
| 15 | Fact 6: 4 round trips per write, naive Paxos; performance can be improved | "The implementation is based on naive Paxos–requiring four round trips for each write–but the performance can be improved with time." | Lightweight Transactions | model_design | weakened: draft said "The post expects performance to improve". Now "The post says the performance can be improved with time". Fixed in JSON |

## Story text and comic

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 16 | Lead deck: database says it got your data; a tester in 2013 checked it was still there later | "supposedly committed data"; "acknowledged" (used throughout the tests) | Some Write Loses | measured_result | pass |
| 17 | Fig. 1: outside tester at a ring of desks checking acknowledged notes still exist | Picture is ours | n/a | scenario | scenario |
| 18 | Fig. 2: two clients rewrite the same note; desk keeps only the later time stamp | "Because the register is last-write-wins, it preserves whichever arrives with the highest timestamp." | Some Write Loses | model_design | pass |
| 19 | Ch. 1: people expect a done write to stay; Kingsbury tested Cassandra in 2013 with Jepsen | "Jepsen: Cassandra", 2013-09-24; "my Jepsen tests" | Lightweight Transactions | measured_result | pass (the "people expect" line is framing) |
| 20 | Ch. 1: "Jepsen, a tool he wrote that breaks networks and checks what survives" | The post says "Jepsen tests" and "doesn't even require a network partition"; it does not say he wrote the tool or describe how it works | n/a | n/a | weakened: now "with his Jepsen tests, which check what survives". Fixed in JSON |
| 21 | Ch. 1: several copies of each piece of data on different machines; pure last-write-wins | "keeps N replicas of each chunk on different nodes"; "a pure last-write-wins approach" | Intro | model_design | pass |
| 22 | Ch. 2: each value carries a time stamp, highest kept | "it preserves whichever arrives with the highest timestamp" | Some Write Loses | model_design | pass |
| 23 | Ch. 2: chose this over vector clocks for speed; one round trip instead of two | "Cassandra chose not to implement vector clocks for performance reasons"; "cut the number of round trips required for a write from 2 to 1" | Some Write Loses | model_design | pass |
| 24 | Ch. 2: no safe way to change a cell that holds a value | "The downside is that there is no safe way to modify a Cassandra cell." | Some Write Loses | model_design | pass |
| 25 | Ch. 3: adding items to a CQL set was safe in its test, every write survived; data that never changes is safe | "All 2000 writes succeeded"; "writing immutable data is safe" | CQL and CRDTs | measured_result | pass |
| 26 | Ch. 3: risky parts are changing a cell, counters in a split, row isolation, lightweight transactions | "no safe way to modify a Cassandra cell"; counters "over- or under-count ... during a network partition"; "row isolation is probabilistic at best"; "Cassandra lightweight transactions are not even close to correct" | Some Write Loses; Counters; Isolation; Lightweight Transactions | measured_result | pass |
| 27 | Ch. 3: after the bugs he reported, the team fixed several | "they've fixed the bugs I've found so quickly"; "reproduce and fix the bug: #6029 ... #5985" | Final thoughts; Lightweight Transactions | measured_result | pass |
| 28 | Ch. 4: lock test, 2000 tried with QUORUM, synced clocks, lock service; 1009 acknowledged, 285 lost, "28%"; one tester's runs; post names no exact build per test; link "See the test in the post" | As row 10; builds: only "Cassandra 2.0.0" is named, for lightweight transactions | Some Write Loses | evidence | pass. Link `#some-write-loses` exists |
| 29 | Comic deck/howTo: our story is a desk that stamps notes; drawings made up; post is one tester's report, no exact build | Pictures ours; builds not named | n/a | scenario | scenario / pass |
| 30 | Strip 1 p1: two people read the same note a; one adds b, the other adds c | "The left client adds a, which is read by both clients. One client adds b, constructing the set [a b]. The other adds c, constructing the set [a c]." | Some Write Loses | model_design | pass |
| 31 | Strip 1 p2: both send back, each note has a clock stamp | "Both write their values back"; "highest timestamp" | Some Write Loses | model_design | pass |
| 32 | Strip 1 p3: clerk keeps only the later stamp; the other change is gone, nobody told | "it's as if the write from the client on the left never even happened"; "silently ignored" | Some Write Loses | model_design | pass |
| 33 | Strip 1 grown-up words: LWW, timestamp, register | "LWW register"; "timestamp" | Some Write Loses | model_design | pass |
| 34 | Strip 2 p1: reading first then writing is two trips; vector clocks usually need the read | "Vclocks (typically) require a read before each write"; "from 2 to 1" | Some Write Loses | model_design | pass |
| 35 | Strip 2 p2: Cassandra skips the read, keeps later stamp; one trip; big speedup | "By using last-write-wins in all cases ... Cassandra can cut the number of round trips ... and obtain a significant speedup" | Some Write Loses | model_design | pass |
| 36 | Strip 2 p3: no safe way to change an existing note | "no safe way to modify a Cassandra cell" | Some Write Loses | model_design | pass |
| 37 | Strip 3 p1: clocks in sync, QUORUM (majority of desks), lock | "perfectly synchronized clocks, QUORUM consistency, and a perfect lock service" | Some Write Loses | measured_result | pass ("majority" is our gloss of QUORUM, not in the post) |
| 38 | Strip 3 p2: changed the same cell repeatedly; counted every write the cluster said it had saved | "a Jepsen test which mutates the same cell repeatedly"; "1009 acknowledged" | Some Write Loses | measured_result | pass |
| 39 | Strip 3 p3: 1009 acknowledged, 285 lost, "28% of committed data" | "285 acknowledged writes lost!"; "Losing 28% of your supposedly committed data" | Some Write Loses | measured_result | pass |
| 40 | Strip 4 p1: adding items to a CQL set worked; each add gets its own slot | "you write each distinct change to its own UUID-keyed cell" | CQL and CRDTs | model_design | pass |
| 41 | Strip 4 p2: 2000 adds acknowledged and survived | "2000 acknowledged / 2000 survivors" | CQL and CRDTs | measured_result | pass |
| 42 | Strip 4 p3: read the rules per operation; build your own safe merge on wide rows | "Read the specs carefully ... you can always write your own CRDTs on top of wide rows yourself" | CQL and CRDTs | model_design | pass |
| 43 | Strip 4 grown-up words: immutable data, CQL set, CRDT | same words in the section | CQL and CRDTs | model_design | pass |
| 44 | Strip 5 p1: docs said a change to one row is isolated; Cassandra can still mix two writes made at once | "writes to a row are isolated to the client performing the write"; "Cassandra allows P0" (dirty write) | Isolation | measured_result | pass |
| 45 | Strip 5 p2: same stamp, picks the bigger value, cell by cell; 2 from one write and minus 1 from the other | "It picks the lexicographically bigger value"; "we might write [1 -1] and [2 -2] ... The result? [2 -1]" | Isolation | model_design | pass |
| 46 | Strip 5 p3: about 1 in 200 rows corrupt; "traced this to time stamps in milliseconds with three zeroes added" | "Roughly 1 in 200 rows were corrupt!"; "somewhere in this maze of software, either Cassandra, the DataStax Java driver, or Cassaforte" | Isolation | measured_result | weakened: the post does not locate the fault; wording now "The post says the cause is somewhere in the software stack: time stamps in milliseconds with three zeroes added." Fixed in JSON |
| 47 | Strip 5 grown-up words: isolation, atomic, timestamp collision | "isolation", "atomic", "two timestamps to collide" | Isolation | model_design | pass |
| 48 | Strip 6 p1: Cassandra 2.0.0 added lightweight transactions (change only if old value matches); Paxos, four round trips | "In Cassandra 2.0.0, Lightweight Transactions offer linearizable consistency for compare-and-set operations"; "naive Paxos–requiring four round trips for each write" | Lightweight Transactions | model_design | pass |
| 49 | Strip 6 p2: first deadlocks, team fixed it; then a slowed test at 5 transactions per second | "the cluster would go unresponsive after the first 10 or so transactions"; "they manage to reproduce and fix the bug"; "slow down the test to 5 transactions/sec" | Lightweight Transactions | measured_result | weakened: "the post hit deadlocks" read oddly; now "the tester hit deadlocks". Fixed in JSON |
| 50 | Strip 6 p3: 829 acknowledged, 3 lost; 1-5%; team fixed several bugs it found | "829 acknowledged"; "3 acknowledged writes lost!"; "Depending on throughput, they may drop anywhere from 1-5% of acknowledged writes"; "#6012 ... #6013"; "fixed the bugs I've found so quickly" | Lightweight Transactions; Final thoughts | measured_result | weakened: run was on patched builds. Now "Result, on builds patched for the deadlock bugs". Fixed in JSON |
| 51 | Strip 6 grown-up words: compare-and-set, Paxos, linearizable | same words in the section | Lightweight Transactions | model_design | pass |
| 52 | Provenance labels: ch.1 illustration, ch.2 and 3 model_design, ch.4 evidence | n/a | n/a | n/a | pass |

## Paper-basis tag evidence links

| # | Tag | Link and phrase | Result |
|---|---|---|---|
| 53 | field/computer-science, area/distributed-systems, technique/cassandra, concept/replication, technique/jepsen, author/kyle-kingsbury | Plain URL; intro: "Cassandra is a Dynamo system ... keeps N replicas of each chunk on different nodes"; tags "Distributed Systems Jepsen Cassandra" | pass |
| 54 | concept/eventual-consistency | Was `#cql-and-crdts`, which does not use the phrase. Counters section: "incremented and decremented in an eventually consistent way". Evidence link now `#counters` | weakened: link fixed in JSON |
| 55 | concept/quorum | `#some-write-loses`: "QUORUM consistency" (the post also names "tunable quorums" in the intro) | pass |
| 56 | concept/conflict-resolution, concept/last-write-wins, concept/vector-clocks | `#some-write-loses`: "pure last-write-wins"; "Vector clocks avoid this problem by identifying conflicting writes" | pass |
| 57 | concept/linearizability, concept/lightweight-transactions | `#lightweight-transactions`: "offer linearizable consistency for compare-and-set operations" | pass |
| 58 | organization/datastax | `#final-thoughts`: "DataStax and the open-source community around Cassandra" | pass |
| 59 | everyday/keeping-copies-safe | Editorial tag, no evidence link | background |

## Summary

59 rows: pass 45, weakened 8 (rows 5, 14, 15, 20, 46, 49, 50, 54), scenario 4, background 1, flag 1 (row 2, trust). All edits are applied in `data/seed/papers/jepsen-cassandra.json`.
