# Fact-check: "Benchmarking Cassandra Scalability on AWS — Over a million writes per second" (Netflix Technology Blog, 2011)

Source: Adrian Cockcroft and Denis Sheahan (byline "by Adrian Cockcroft and Denis Sheahan"; page author "Netflix Technology Blog"), Netflix TechBlog. Printed date: "Nov 2, 2011" and "Originally published at techblog.netflix.com on November 2, 2011." No venue is printed; the post only says "Adrian presented these results at the High Performance Transaction Systems workshop last week" (a talk, not a venue for this write-up).
Canonical URL: https://netflixtechblog.com/benchmarking-cassandra-scalability-on-aws-over-a-million-writes-per-second-39f45f066c9e
Fetched / archive URL: http://web.archive.org/web/20261021060254/https://netflixtechblog.com/benchmarking-cassandra-scalability-on-aws-over-a-million-writes-per-second-39f45f066c9e (the live canonical URL and the original blogspot URL returned 403 / redirect to 403; the Wayback snapshot of the canonical URL was read).
Extraction: HTML from the Wayback snapshot, tags stripped (source.txt, 21,335 chars); Medium chrome dropped, article body complete. The charts and tables in the post are images; their contents were not readable, so no claim here rests on them.
Checked on 2026-11-12.

**Location convention.** Blog, no PDF pages. The post's own headings are used: the unlabeled intro (before the first heading), TL;DR, EC2 Configuration, Netflix Automation for Cassandra, Scale-Up Linearity, Per-Instance Activity, Costs of Running This Benchmark, Detailed Cassandra Configuration, Data Flows Latency and Durability, Next Steps, Takeaway. The page has only opaque Medium ids; all links in the story are the plain URL, which is fine (no fragment is used).

**Result key.** `pass` = as worded is in the post. `weakened` = wording went beyond the post; fixed in the JSON. `scenario` = our framing or invented picture. `background` = not from the post.

**Linear claim.** "Linear" appears only as Netflix's own statement ("the throughput scaled linearly", "The scalability is linear as shown in the chart below", "Cassandra scales linearly far beyond our current capacity requirements"). Every use in the story is attributed ("the team says", "the post says", "Netflix's own view", "Netflix reports"). Caveat noted: one run per configuration, CPU "a little higher for the largest cluster", and the chart is not independently checked.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | `trust: company_reported` | Company engineering blog, by two Netflix staff; no peer review, no venue. "Adrian presented these results at the High Performance Transaction Systems workshop" is a talk mention only. | pass (owner decides; flagged: self-reported benchmark, results not independently reproduced here) |
| 2 | Title, org, date 2011-11-02 | Page title, "Nov 2, 2011" | pass |

## Summary, hook, lead

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 3 | Summary: tested whether Cassandra on Amazon's cloud gets faster in a straight line as machines are added | "validate our tooling and automation scalability as well as the performance characteristics of Cassandra"; "the throughput scaled linearly as we increased the number of instances" | intro | measured_result | pass (stated as the test question, result attributed) |
| 4 | Summary: 1.1 million client writes a second on a 288-machine ring, 3.3 million with three copies | "288 medium sized instances"; "1.1 million client writes per second"; "making a total of 3.3 million writes per second across the cluster" | intro | measured_result | pass |
| 5 | Hook sticker "Over a million!" | Title "Over a million writes per second" | title | measured_result | pass |
| 6 | Hook stat 1.1 million writes a second, Netflix reports | "a workload of 1.1 million client writes per second" | intro | measured_result | pass |
| 7 | Hook teaser question; cta "Watch the ring grow"; readMinutes 4 | Framing question; editorial (page shows "13 min read" for the post, 4 is our story) | n/a | n/a | scenario / background |
| 8 | Hook frames: "Many desks!", "Straight line!" (alt: four dots on one line) | Drawings of the intro/Scale-Up Linearity claim; same picture as Fig. 2, which is attributed | n/a | n/a | scenario (illustration; attribution is on Fig. 2 and the stat) |
| 9 | Lead headline "Add a machine, get a bit more speed." | Not a number claim; the post says throughput "scaled linearly" | n/a | n/a | pass (understates rather than overstates) |
| 10 | Lead deck: tested Cassandra on rented machines; "This is Netflix's own benchmark." | "these EC2 instances were only in existence for the duration of the test"; "As part of our benchmarking we recently decided to run a test" | intro | measured_result | pass |
| 11 | Fig. 1: 288-machine ring, then writes sent at it | "288 medium sized instances"; "60 instances as clients running the stress program" | intro | measured_result | pass |
| 12 | Fig. 2: team says speed grew in a straight line: 48, 96, 144, 288 | "the same test was run with 48, 96, 144 and 288 instances ... the throughput scaled linearly" | intro | measured_result | pass (attributed) |

## Story chapters

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 13 | Ch.1: rolling out Cassandra about six months; clusters held 6 to 48 machines | "rolling out the Apache Cassandra NoSQL data store for production use over the last six months"; "many application specific Cassandra clusters from 6 to 48 instances" | intro | measured_result | pass |
| 14 | Ch.1: "Before going bigger, the team wanted to know: if we keep adding machines, does the cluster keep getting faster? And would its tools cope" | Post gives the aim as "validate our tooling and automation scalability as well as the performance characteristics"; it does not say the test came before a plan to go bigger | intro | model_design | weakened: dropped "Before going bigger," (now "The team wanted to know: ..."). Fixed in JSON |
| 15 | Ch.2: machines rented from AWS only for the test; set up in about an hour; split evenly over three availability zones | "about an hour to go from nothing to a very large Cassandra cluster"; "96 instances in each of three EC2 availability zones"; "only in existence for the duration of the test" | intro | model_design | pass |
| 16 | Ch.2: every write copied three times, once per zone; writes sent from a separate crowd of client machines | "Data was automatically replicated across all three zones"; "an additional 60 instances as clients" | intro | model_design | pass |
| 17 | Ch.3: ran four times with 48/96/144/288 machines and 10/20/30/60 clients; similar load per machine; straight line; 60 clients sent 1.1 million writes a second | "the same test was run with 48, 96, 144 and 288 instances, with 10, 20, 30 and 60 clients respectively. The load on each instance was very similar in all cases"; "1.1 million client writes per second" with 60 clients | intro | measured_result | pass (attributed with "The team says"; 60 x about 17,500 requests per client ~ 1.05M is consistent) |
| 18 | Ch.4: Netflix's own test, ran each size once, Cassandra 0.8.6 | "using our standard production configuration of Cassandra 0.8.6"; "a random fluctuation in the test, which we only ran once" | intro; Per-Instance Activity | measured_result | pass (post says "the test ... only ran once"; reading it as once per size is natural but is an inference) |
| 19 | Ch.4: 3.3 million total because each write kept three times; two hours and a few hundred dollars | "3.3 million writes per second across the cluster"; "within two hours with a total cost of a few hundred dollars" | intro | measured_result | pass |
| 20 | Ch.4 link "intro and Scale-Up Linearity sections" | Plain post URL, no fragment | n/a | n/a | pass |

## Comic strips and grownUpWords

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 21 | Strip 1a: a few clicks, about an hour to a very large ring | "a few clicks on a web page and about an hour to go from nothing to a very large Cassandra cluster" | intro | model_design | pass |
| 22 | Strip 1b: three buildings called availability zones, about one millisecond apart, same number of machines each | "three ASGs ... one in each availability zone, which are separate data-centers separated by about one millisecond of network latency"; "96 instances in each" | EC2 Configuration; intro | model_design | pass (equal split is stated for the 288 case; 48/96/144 are all divisible by 3) |
| 23 | Strip 1c: dead machine is replaced, ring keeps going | "If an instance dies for any reason, the ASG automatically creates a replacement instance" | EC2 Configuration | model_design | pass |
| 24 | Strip 1 grownUpWords: auto-scaling group, availability zone | "auto-scale group (ASG)"; "availability zone" | EC2 Configuration | n/a | pass |
| 25 | Strip 2a: client sends to any machine, which becomes helper | "they pick a node at random which then acts as a coordinator" | Data Flows | model_design | pass |
| 26 | Strip 2b: helper passes it on, three copies, one per building | "send replicas of the data to the correct nodes"; "replicated across all three zones"; "three replicas which is specified in the keyspace" | Data Flows; intro; Stress command | model_design | pass |
| 27 | Strip 2c: thumbs-up when one desk has it; fastest option | "requests use consistency level 'ONE' which means that they are acknowledged when one node has acknowledged"; "For the fastest writes a single node has to acknowledge the write" | Detailed Cassandra Configuration; Data Flows | model_design | pass |
| 28 | Strip 2 grownUpWords: replication factor 3, consistency level ONE | "consistency level 'ONE'"; replicas 3 | as above | n/a | pass |
| 29 | Strip 3a: writes push a data store all the way to the disks | "Writes stress a data store all the way to the disks" | intro (2nd paragraph) | model_design | pass |
| 30 | Strip 3b: reading can sometimes be answered from memory | "read benchmarks may only exercise the in-memory cache" | intro (2nd paragraph) | model_design | pass |
| 31 | Strip 3c: write jotted in a notebook (commit log) first, takes a tiny moment | "just the few microseconds it takes to queue the data to the commit log writer" | Data Flows | model_design | pass |
| 32 | Strip 3 grownUpWords: commit log, write-oriented benchmark | "write oriented benchmark"; "commit log" | intro; Data Flows | n/a | pass |
| 33 | Strip 4a-c: 48/10, 96/20, 144/30, then 288/60; load per machine very similar; straight line (post says) | "48, 96, 144 and 288 instances, with 10, 20, 30 and 60 clients respectively"; "very similar in all cases" | intro | measured_result | pass |
| 34 | Strip 4 grownUpWords: scalability, throughput, client threads | "throughput scaled"; "Each client ran 200 threads" | intro; Scale-Up Linearity | n/a | pass |
| 35 | Strip 5a: machines existed only while the test ran; no buying, no waiting for a room | "only in existence for the duration of the test. There was no setup time, no discussions with IT operations about datacenter space" | intro | model_design | pass |
| 36 | Strip 5b: two hours, a few hundred dollars | "within two hours with a total cost of a few hundred dollars" | intro | measured_result | pass |
| 37 | Strip 5c: copying between buildings was costly; Amazon charges for cross-zone traffic | "AWS charges $0.01 per gigabyte for cross zone traffic"; "it actually cost more per hour than the instances" | Costs of Running This Benchmark | measured_result | pass |
| 38 | Strip 5 grownUpWords: spot pricing, cloud billing | "This cost could be further reduced by using spot pricing"; costs given "at the normal list price" | Costs | n/a | pass (note: the test was not run on spot pricing; the term is vocabulary only, the strip does not say it was used) |
| 39 | Strip 6a: only one test of each size; largest cluster's CPU a little higher | "The CPU load is a little higher for the largest cluster ... the test, which we only ran once" | Per-Instance Activity | measured_result | pass (same once-per-size inference as row 18) |
| 40 | Strip 6b: "planned to test Cassandra 1.0 next, and to try more than one region" | "we are currently working to characterize the performance of Cassandra 1.0 and multi-region performance for both reads and writes"; the post also says "in our multi-region testing we have found" (already under way) | Next Steps; Detailed Cassandra Configuration | model_design | weakened: "planned ... next" implied the future; now "was now working on testing Cassandra 1.0, and on tests across more than one region". Fixed in JSON |
| 41 | Strip 6c: post ends by saying Cassandra scaled linearly far beyond current needs; Netflix's own view | "Cassandra scales linearly far beyond our current capacity requirements" | Takeaway | measured_result | pass (attributed; a hiring pitch follows, but this is the last claim) |
| 42 | Comic howTo: numbers come from Netflix's own post | Figures all trace to the post (rows above) | n/a | n/a | pass |
| 43 | Strip 6 grownUpWords: Cassandra 1.0, multi-region | "Cassandra 1.0 and multi-region performance" | Next Steps | n/a | pass |

## Facts (`facts[]`)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 44 | 288 machines, 96 in each of three zones; sixty more as clients | "288 medium sized instances, with 96 instances in each of three EC2 availability zones"; "an additional 60 instances as clients" | intro | measured_result | pass |
| 45 | 1.1 million client writes a second; 3.3 million across the cluster | "1.1 million client writes per second"; "3.3 million writes per second across the cluster" | intro | measured_result | pass |
| 46 | 48 to 288 machines, 10/20/30/60 clients; post says linear | "48, 96, 144 and 288 instances, with 10, 20, 30 and 60 clients"; "scaled linearly"; "The scalability is linear as shown in the chart below" | intro; Scale-Up Linearity | measured_result | pass (attributed; chart image not read) |
| 47 | 6 to 48 machines existing; glad to see linear scale to six times the largest | "from 6 to 48 instances, so we were very happy to see linear scale to six times the size of our current largest deployment" | intro | measured_result | pass (288 / 48 = 6) |
| 48 | About 11 ms client response time, about 1.2 ms network; server side a small fraction of a millisecond | "The response time measured at the client was about 11ms, with about 1.2ms due to network latency"; "The write latency measured at each Cassandra server is a small fraction of a millisecond" | Per-Instance Activity | measured_result | pass |
| 49 | 2 hours, few hundred dollars; 66 minutes to get ring ready, about 15 minutes waiting for Amazon | "within two hours with a total cost of a few hundred dollars"; "about 15 minutes out of our total of 66 minutes" | intro | measured_result | pass (the 66 minutes covers creating, booting and joining the ring, per the post) |

All fact source links are the plain post URL. Labels ("Post · intro", "Post · Per-Instance Activity", "Post · intro and Scale-Up Linearity") match the sections used.

## Paper-basis tags (spot-check)

All 13 paper-basis tags carry the plain post URL as evidence.

| Tag | Phrase | Result |
|---|---|---|
| `field/computer-science`, `area/distributed-systems` | "globally distributed streaming product"; "availability zones"; "gossip protocol" | pass |
| `area/databases` | "Apache Cassandra NoSQL data store" | pass |
| `technique/cassandra` | Title | pass |
| `concept/replication` | "Data was automatically replicated across all three zones" | pass |
| `concept/high-availability` | "this configuration is very highly available" | pass |
| `concept/quorum` (0.3) | "To get immediately consistent writes with Cassandra we use a quorum write" | pass |
| `concept/linear-scalability` | "the throughput scaled linearly" (Netflix's claim) | pass |
| `concept/benchmarking` | Title; "Benchmarking can take a lot of time and money" | pass |
| `concept/cloud-computing` | "running on Amazon EC2 instances" | pass |
| `organization/netflix`, `author/adrian-cockcroft`, `author/denis-sheahan` | Byline "by Adrian Cockcroft and Denis Sheahan"; "Netflix Technology Blog" | pass |
| `everyday/streaming-video` | none (`basis: editorial`); post says "globally distributed streaming product" | background |

Status flags (`proposed`) on the new tags were left as is.

## Summary

49 rows: pass 45, weakened 2 (rows 14, 40), scenario/background 2 (rows 7, 8), plus the tag table (12 pass, 1 background). JSON edits: ch. 1 caption and strip 6b caption. Trust flag: `company_reported` is right; owner to confirm.
