# Fact-check: "Dynamo: Amazon's Highly Available Key-value Store" (DeCandia et al., SOSP 2007)

Source: Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall and Werner Vogels (Amazon.com), "Dynamo: Amazon's Highly Available Key-value Store". The title page prints "SOSP'07, October 14-17, 2007, Stevenson, Washington, USA" and "Copyright 2007 ACM". Author order above is the order on the title page (nine authors; the story says "DeCandia and colleagues").
Canonical file used: https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf (16 PDF pages; 879 KB). The story says "Venue: SOSP 2007" and `year: 2007`.
Checked on 2026-11-07. The PDF was downloaded and its text extracted with `pdftotext`; quotes were matched against that text. The fetch tool could not read the PDF directly (binary), so the extraction is the evidence.
Archive: not captured in this run (the paper is a PDF on the authors' site, not a post that can change; no archive link recorded).

**Location convention.** The PDF has no section anchors. Links use `#page=N` (PDF page index, not the printed ACM page number). Locations below give the paper's section number and heading, plus the PDF page. Section headings were confirmed by reading the extracted text; the two-column layout scrambles heading order in a raw dump, so the numbering follows the paper's own structure: 1 Introduction, 2 Background (2.1 System Assumptions, 2.2 SLA, 2.3 Design Considerations), 3 Related Work, 4 System Architecture (4.1 Interface, 4.2 Partitioning, 4.3 Replication, 4.4 Data Versioning, 4.5 get/put, 4.6 Hinted Handoff, 4.7 Replica synchronization, 4.8 Membership and Failure Detection, 4.9 Adding/Removing Nodes), 5 Implementation, 6 Experiences and Lessons Learned (6.1 Performance and Durability, 6.2 Uniform Load, 6.3 Divergent Versions, 6.4 Client- vs Server-driven, 6.5 Background vs Foreground, 6.6 Discussion).

**Result key.** `pass` = the claim as worded is in the paper, or is a plain restatement. `weakened` = the wording goes beyond the paper; the Result column says what was done. `scenario` = our invented example or metaphor, labelled illustration. `background` = not from the paper.

**What is in the paper:** the design of Dynamo: ring partitioning with virtual nodes, N/R/W replication, vector-clock versioning with application-side merge, sloppy quorum and hinted handoff, Merkle-tree replica sync, gossip membership, and measurements from Amazon's live system.
**What is not in the paper:** the sneaker and hat examples, the "houses on a round street", "neighbor holding your mail" and "sticky note" metaphors, the family-account scenario, and anything about Cassandra, Riak or DynamoDB (none is mentioned).

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Venue and year: SOSP 2007 | "SOSP'07, October 14-17, 2007, Stevenson, Washington, USA" (title page footer, PDF p1) | pass |
| 2 | `peer_reviewed` | The paper does not say "peer-reviewed". SOSP is a refereed ACM conference, which is background knowledge. The ACM proceedings page was not fetched in this run | weakened: kept `peer_reviewed` in the patch, flagged for the lead to confirm on the ACM Digital Library page before publishing |

## Facts (`facts[]`, hook, summary)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 3 | 3 copies; 2 must answer a save; 2 must answer a read (N, R, W) | "The common (N,R,W) configuration used by several instances of Dynamo is (3,2,2)." | §6.1, PDF p11 | model_design | pass |
| 4 | Usual promise: 99.9% of reads and writes finish within 300 ms | "99.9% of the read and write requests execute within 300ms" (also the §2.2 example: 300 ms for 99.9% at 500 requests per second) | §6.1 PDF p11; §2.2 PDF p3 | model_design | pass |
| 5 | 3 million+ checkouts in a single day; tens of millions of requests | "well over 3 million checkouts in a single day"; "served tens of millions requests" | §1, PDF p2 | measured_result | pass |
| 6 | Slowest 1 in 1,000 took about 200 ms in a 30-day look; about ten times the average | "the 99.9th percentile latencies are around 200 ms and are an order of magnitude higher than the averages"; Figure 4 covers "a period of 30 days" | §6.1, PDF p11 | measured_result | pass ("slowest 1 in 1,000" restates the 99.9th percentile) |
| 7 | 99.94% of cart requests saw exactly one version in 24 hours | "99.94% of requests saw exactly one version" | §6.3, PDF p13 | measured_result | pass |
| 8 | 99.9995% of requests got a successful reply without timing out; no data loss to date | "successful responses (without timing out) for 99.9995% of its requests and no data loss event has occurred to date" (over "the past two years") | §6.6, PDF p14 | measured_result | pass (hook stat "of requests answered" restates "successful responses") |
| 9 | Chapter 4: each of the 2-, 3- and 4-version cases was under 0.001% | 0.00057% (2 versions), 0.00047% (3), 0.00009% (4) | §6.3, PDF p13 | measured_result | weakened: first draft said "only a tiny sliver saw two or more". The listed cases sum to about 0.0011%, so 99.94% plus those leaves roughly 0.06% unaccounted for. Fixed in JSON to the per-case wording |
| 10 | Fact 7 text: "Splits are rare." | "This shows that divergent versions are created rarely." | §6.3, PDF p13 | measured_result | pass |

## Story text and comic (provenance: illustration)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 11 | Amazon runs tens of thousands of machines; some are always broken | "tens of thousands of servers"; "there are always a small but significant number of server and network components that are failing" | §1, PDF p2 | model_design | pass |
| 12 | The cart must always accept adds, even while machines fail | "customers should be able to view and add items to their shopping cart even if disks are failing" | §1, PDF p2 | model_design | pass |
| 13 | Lead: "It happens all the time, so the store plans for it" | "treats failure handling as the normal case" | §1, PDF p2 | model_design | pass |
| 14 | Lead picture: a server on fire, cart still full | Invented scene. The paper's own examples are failing disks, flapping network routes, and data centers destroyed by tornados | §1, PDF p2 | scenario | pass as scenario |
| 15 | A cart's name becomes a spot on a circle | "applies a MD5 hash on the key"; "treated as a fixed circular space or 'ring'" | §4.1 PDF p5; §4.2 PDF p5 | model_design | pass |
| 16 | Walk clockwise to the first machine | "walking the ring clockwise to find the first node with a position larger than the item's position" | §4.2, PDF p5 | model_design | pass |
| 17 | Copies go to the next machines along (N-1 successors) | "replicates these keys at the N-1 clockwise successor nodes in the ring" | §4.3, PDF p6 | model_design | pass |
| 18 | Each machine takes many spots; a new machine takes a little load from many neighbors | "each node gets assigned to multiple points in the ring"; "accepts a roughly equivalent amount of load from each of the other available nodes" | §4.2, PDF p6 | model_design | pass |
| 19 | Save needs 2 answers, read needs 2 answers; third copy catches up later | "R is the minimum number of nodes that must participate in a successful read operation. W is ... write" | §4.5, PDF p7 | model_design | pass ("catches up later" restates that R and W are usually less than N) |
| 20 | Two plus two is more than three, so a reader usually meets a machine that saw the last save | "Setting R and W such that R + W > N yields a quorum-like system." | §4.5, PDF p7 | model_design | weakened: kept the hedge "usually", because sloppy quorum (row 21) can place copies on stand-in machines and break the overlap |
| 21 | If a machine is down, the next healthy machine keeps the copy with a note naming the owner; it is handed back on recovery | "sloppy quorum"; "The replica sent to D will have a hint in its metadata that suggests which node was the intended recipient"; "D will attempt to deliver the replica to A" | §4.6, PDF p8 | model_design | pass |
| 22 | A strict rule would refuse the save | "If Dynamo used a traditional quorum approach it would be unavailable during server failures and network partitions" | §4.6, PDF p8 | model_design | pass |
| 23 | Each change adds a "note"; a vector clock is a list of (node, counter) pairs | "A vector clock is effectively a list of (node, counter) pairs." | §4.4, PDF p6 | model_design | pass ("sticky note" is a metaphor) |
| 24 | If one version is an update of the other, drop the old one; if they branched, keep both | "the first is an ancestor of the second and can be forgotten. Otherwise, the two changes are considered to be in conflict and require reconciliation." | §4.4, PDF p6 | model_design | pass |
| 25 | Two people change the same cart at once on two machines | Invented scenario. The paper says branches arise "in the presence of failures combined with concurrent updates" | §4.4, PDF p6 | scenario | pass as scenario |
| 26 | The cart service merges versions; an add is never lost | "an 'add to cart' operation is never lost" | §4.4, PDF p6 | model_design | pass |
| 27 | The application, not the store, decides how to merge | "the application that maintains customer shopping carts can choose to 'merge' the conflicting versions" | §2.3, PDF p4 | model_design | pass |
| 28 | A removed item can come back after a merge | "deleted items can resurface" | §4.4, PDF p6 | model_design | pass |
| 29 | Chapter 3 "the system does not guess" | The data store can use only simple policies such as "last write wins"; for carts the application merges | §2.3, PDF p4 | model_design | pass (the session service uses last-write-wins, §6; the story does not say all services merge) |
| 30 | Gossip: each second a random neighbor is contacted and membership news is swapped | "Each node contacts a peer chosen at random every second and the two nodes efficiently reconcile their persisted membership change histories." | §4.8.1, PDF p8 | model_design | pass |
| 31 | Compare one fingerprint of the whole shelf; same fingerprint means nothing to sync | "if the hash values of the root of two trees are equal, then the values of the leaf nodes in the tree are equal and the nodes require no synchronization" | §4.7, PDF p8 | model_design | pass ("fingerprint" = hash) |
| 32 | If they differ, compare halves, then smaller pieces, until the odd cart is found | "the nodes may exchange the hash values of children and the process continues until it reaches the leaves" | §4.7, PDF p8 | model_design | pass |
| 33 | Only the odd cart gets copied | "Merkle trees minimize the amount of data that needs to be transferred for synchronization" | §4.7, PDF p8 | model_design | pass (paraphrase) |
| 34 | Summary: copies around a ring; keep both versions when copies disagree and merge later; price is that a removed item can reappear | Rows 17, 24, 26 and 28 | §4.3, §4.4 | model_design | pass |
| 35 | Hook teaser: "A machine breaks while you shop. Why is your cart still full?" | Scenario question; the paper's design goal in rows 11 and 12 | §1 | scenario | pass as scenario |
| 36 | Metaphors: houses on a round street, neighbor holding your mail, sneaker and hat, family account | Not in the paper | n/a | scenario | pass as scenario |

**Counts (36 rows): 29 pass, 3 weakened, 4 scenario (our own invented examples and metaphors, labelled illustration), 0 rejected.** Weakened: rows 2, 9, 20. Scenarios: rows 14, 25, 35, 36.

Claim kinds in `facts[]`: `model_design` for rows 3 and 4 (a configuration and a service promise, not test findings); `measured_result` for rows 5-8 (numbers Amazon reports from its live system). Dynamo's numbers come from Amazon's own production system as the authors report them, not from independent tests; the story words these as "the paper reports".

## Required items from the brief

| Item | Where in paper | Result |
|---|---|---|
| Full title, author order, venue, year | Title page; footer of PDF p1 | pass |
| Consistent hashing and virtual nodes | §4.2, PDF p5-6 | pass |
| Vector clocks for conflicts | §4.4, PDF p6 | pass |
| Sloppy quorum and hinted handoff | §4.6, PDF p8 | pass |
| Merkle trees for anti-entropy | §4.7, PDF p8 ("Merkle trees for anti-entropy") | pass |
| Gossip-based membership and failure detection | §4.8.1 PDF p8 (membership); §4.8.3 PDF p9 (failure detection: the paper says early designs used a decentralized failure detector, later dropped for explicit join and leave plus local detection) | pass. Story uses gossip for membership only |
| 99.9th-percentile latency numbers | §6.1 PDF p11: SLA 300 ms at 99.9%; about 200 ms in 30-day look; write buffer lowered it "by a factor of 5" at peak (not used in the story) | pass |
| Use cases: shopping cart, session store | §1 PDF p2 (cart, session state); §6 PDF p10 (session service uses last-write-wins) | pass |
| Cluster size | §6.1 PDF p11: "a couple hundred nodes" for the measured system; §6.2 Figure 8 uses 30 nodes with N=3 as "the typical configuration deployed for majority of our services" | pass; not used as a fact card |
| Chord citation | §3.1 PDF p4 ("Systems like Pastry [16] and Chord [20]"); §4.2: Dynamo's consistent hashing is "similar to the one used in [10, 20]" (Karger et al. 1997 and Chord) | pass; used in the library patch |

## Paper-basis tags (spot-check)

All paper-basis tag evidence links point at the PDF with a `#page=N` fragment. The page for each was checked by extracting that page's text and searching for the supporting phrase.

| Tag | Evidence | Phrase | Result |
|---|---|---|---|
| `concept/consistent-hashing` | PDF p5 | "relies on consistent hashing" | pass |
| `concept/virtual-nodes` | PDF p6 | "virtual nodes" | pass |
| `concept/vector-clocks` | PDF p6 | "Dynamo uses vector clocks" | pass |
| `concept/eventual-consistency` | PDF p4 | "eventual consistency" (§2.3) | pass |
| `concept/quorum` | PDF p7 | "R + W > N yields a quorum-like system" | pass |
| `concept/hinted-handoff` | PDF p8 | "Handling Failures: Hinted Handoff" | pass |
| `concept/merkle-tree` | PDF p8 | "Dynamo uses Merkle trees for anti-entropy" | pass |
| `concept/gossip-protocol` | PDF p8 | "A gossip-based protocol propagates membership changes" | pass |
| `concept/conflict-resolution` | PDF p4 | "last write wins"; "merge" | pass |
| `concept/tail-latency` | PDF p3 | "99.9th percentile of the distribution" | pass |
| `concept/service-level-agreement` | PDF p3 | "Service Level Agreements (SLA)" | pass |
| `concept/replication` | PDF p6 | "replicates these keys at the N-1" | pass |
| `use/session-storage` | PDF p10 | "The service that maintains customer's session information" | pass |
| `venue/sosp-2007` | PDF p1 | "SOSP'07, October 14-17, 2007" | pass |
| `venue/sosp` | none (background) | parent of the venue tag | background |
| Other paper-basis tags (field, area, key-value, high availability, dynamo, shopping carts, Amazon, authors) | PDF p1 | Title, abstract and author block | pass |

34 of the 35 tags are proposed new tags (only `field/computer-science` exists in `data/seed/tags.json`). All carry `source: "ai"`, `status: "suggested"` until the owner approves them.
