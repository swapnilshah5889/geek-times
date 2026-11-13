# Fact-check: "Apache Hadoop Goes Realtime at Facebook" (Borthakur et al., Facebook; SIGMOD 2011)

Source: Dhruba Borthakur, Joydeep Sen Sarma, Jonathan Gray, Kannan Muthukkaruppan, Nicolas Spiegelberg, Hairong Kuang, Karthik Ranganathan, Dmytro Molkov, Aravind Menon, Samuel Rash, Rodrigo Schmidt, Amitanand Aiyer (all Facebook). The story says authors "Borthakur and colleagues", `year: 2011`.
Venue as printed (PDF p1): "SIGMOD '11, June 12-16, 2011, Athens, Greece." and "Copyright 2011 ACM 978-1-4503-0661-4/11/06...$10.00." No separate publication date is printed.
Canonical = fetched URL: https://borthakur.com/ftp/RealtimeHadoopSigmod2011.pdf (10 PDF pages). Archive URL: none captured.
Extraction: `pdftotext` per page (p1-p10, 57,990 chars), quotes matched against that text.
Checked on 2026-11-12.

**Location convention.** Links use `#page=N` (PDF page index; pages carry no printed numbers). Paper sections: 1 Introduction, 2 Workload Types (2.1 Messaging, 2.2 Insights, 2.3 ODS), 3 Why Hadoop and HBase, 4 Realtime HDFS, 5 Production HBase, 6 Deployment and Operational Experiences, 7 Future Work. Section 2.1 starts on p2; the Introduction (with the 500 million line) is on p1.

**Result key.** `pass` = in the paper as worded or a plain restatement. `weakened` = wording went beyond the paper; fixed in the JSON. `scenario` = our invented picture or metaphor. `background` = not from the paper.

**Cassandra.** The word appears exactly once in the paper: the abstract ("reasons why Facebook chose Hadoop and HBase over other systems such as Apache Cassandra and Voldemort"). The body has no comparison and no Cassandra-specific reason. The story repeats only the abstract line and says so ("It never compares them one by one").

**What is not in the paper:** the notebook, whiteboard, folders, zipping, doorman, boss, diary and signpost metaphors; the bell icon; the claim that mismatched screens make people lose trust.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, authors, year 2011 | Title block and 12-author block, PDF p1; "SIGMOD '11, June 12-16, 2011" | pass |
| 2 | Venue SIGMOD 2011 (`venue/sigmod`, `venue/sigmod-2011`) | Printed on PDF p1 (above) | pass; tags were `basis: background` with no evidence, now `basis: paper`, evidence `#page=1` (fixed in JSON) |
| 3 | Trust label `peer_reviewed` (owner decides) | meta.md: ACM SIGMOD conference paper with ACM copyright line; the word "refereed" is not printed in the PDF, and no review process is stated | **flag for owner**: suggested `peer_reviewed` on venue evidence; not confirmed from the paper |

## Facts (`facts[]`, hook, summary)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 4 | Summary: Messages needed unread count and inbox to agree, with huge numbers of writes | "'unread' message counts displayed on the home page and the messages shown in the inbox page view should be consistent with respect to each other"; "High write throughput" | §3 item 3, PDF p3; §2.1.1 p2 | model_design | pass |
| 5 | Summary: needs "led by" strong consistency and write throughput | "(in no particular order)" | §3, PDF p3 | model_design | weakened: "led by" implied a ranking. Now "in no particular order, including ..." |
| 6 | Summary: explains why Facebook chose HBase on Hadoop | "we chose Hadoop and HBase as the foundational storage technology" | §3, PDF p4 | model_design | pass |
| 7 | Summary: abstract names Cassandra and Voldemort as systems it chose HBase over | "why Facebook chose Hadoop and HBase over other systems such as Apache Cassandra and Voldemort" | Abstract, PDF p1 | background | pass (abstract only; no comparison implied) |
| 8 | Hook stat: 500 million, "people at launch" | "suited for production use by more than 500 million people immediately after launch" | §1, PDF p1 | model_design | weakened: it is a design target, not users; text now "people to serve at launch" |
| 9 | Hook teaser: two screens show unread messages; must always agree | as row 4 | §3, PDF p3 | model_design | pass |
| 10 | Lead deck: same unread count "everywhere" | the paper names two views: home page and inbox page | §3, PDF p3 | model_design | weakened: now "on the home page and the inbox page" |
| 11 | Lead Fig. 1: home page three unread, inbox three; "If they disagree, people lose trust" | "This requirement often arises directly from user expectations" | §3, PDF p3 | model_design | weakened: the number 3 and trust claim are ours. Now "The paper says this need comes from what users expect." (three is illustration) |
| 12 | Lead Fig. 2: each person served from one data center; machines can "all agree quickly" | "a particular user could be served entirely out of a single data center making strong consistency within a single data center a critical requirement"; "each user will be sticky to a single data center" | §3 PDF p3; §2.1 PDF p2 | model_design | weakened: "agree quickly" not stated. Now "so strong consistency inside that one data center is enough" |
| 13 | Ch. 1: Messages brings messages, email, chat, SMS into one inbox | "combines existing Facebook messages with e-mail, chat, and SMS"; "integrates the display of all e-mail, SMS and chat messages" | §2.1 PDF p2; §1 PDF p1 | model_design | pass |
| 14 | Ch. 1: more than 500 million people right after launch | as row 8 | §1, PDF p1 | model_design | pass |
| 15 | Ch. 1: millions of messages and billions of chat messages every day; a message written several times | "millions of messages and billions of instant messages every day"; "each message could be written several times" | §2.1.1, PDF p2 | model_design | pass ("chat" for "instant messages") |
| 16 | Ch. 1: MySQL good at reading, typically weak at heavy random writing | "MySQL storage engines are proven and have very good random read performance, but typically suffer from low random write throughput" | §1, PDF p1 | model_design | pass |
| 17 | Ch. 2: list has eight items, in no particular order | "(in no particular order)"; items 1-8 | §3, PDF p3 | model_design | pass |
| 18 | Ch. 2: strong consistency inside a data center; unread count and inbox must agree | rows 4 and 12 | §3, PDF p3 | model_design | pass |
| 19 | Ch. 2: names things not needed, e.g. surviving a network split inside one data center | "Tolerance of network partitions within a single data center" (non-requirement 1) | §3, PDF p3-p4 | model_design | pass |
| 20 | Ch. 2: grown-up words strong consistency, write throughput | "strong consistency"; "High write throughput" | §3, PDF p3 | model_design | pass |
| 21 | Ch. 3: chose HDFS with HBase on top; HBase already highly consistent and fast at writes | "HBase already provided a highly consistent, high write-throughput key-value store." | §3, PDF p3 | model_design | pass |
| 22 | Ch. 3: note goes in a notebook, then a whiteboard, then sorted folders; HDFS keeps copies | "first gets written to a commit log and then applied to an in-memory cache called MemStore ... written out as an HFile ... sorted order"; "two other replicas exist" | §5.3 PDF p7; §5.1.2 PDF p6 | model_design | pass (metaphor) |
| 23 | Ch. 3: team fixed gaps itself, e.g. single boss machine in HDFS | "The HDFS NameNode stood out as a central point of failure, but we were confident that our HDFS team could build a highly-available NameNode"; AvatarNode | §3 PDF p3-p4; §4.1 PDF p4 | model_design | pass |
| 24 | Ch. 3: abstract says chose this over Cassandra and Voldemort; never compares them one by one; reasons are the needs list | Only mention is the abstract line (row 7); `grep` finds no other hit | Abstract, PDF p1 | background | pass |
| 25 | Ch. 3: grown-up words HBase, HDFS, commit log | "commit log" | §5.3, PDF p7 | model_design | pass |
| 26 | Ch. 4: after launching to employees, very high write delays | "After launching to employees, we noticed that our put and sync latencies were very high." | §5.3.1, PDF p7 | measured_result | pass |
| 27 | Ch. 4: a big file kept re-copied with tiny ones | "a 1 GB file would be regularly compacted with three 5 MB files" | §5.3.1, PDF p7 | measured_result | pass |
| 28 | Ch. 4: put latency fell from 25 ms to 3 ms | "our put latency dropped from 25 milliseconds to 3 milliseconds" | §5.3.1, PDF p7 | measured_result | pass |
| 29 | Ch. 4: weekly instead of daily big-file merging cut network traffic 40% | "40% network IO reduction by simply increasing our major compaction interval from every day to every week" | §6.9, PDF p9 | measured_result | pass |
| 30 | Ch. 4: "the team's own production reports" | Row 28 follows employee launch; row 29 follows "running in production for a couple months" | §5.3.1 p7; §6.9 p9 | n/a | weakened: now "the team's own reports" |
| 31 | Ch. 4 link "See the paper's §5.3.1" `#page=7` | §5.3.1 is on PDF p7 | PDF p7 | n/a | pass |
| 32 | Fact 1 (500 million): "were expected to use ... which is why it needed very high uptime and size"; link §2.1 `#page=2` | "had to be suited for production use by more than 500 million people immediately after launch and needed to scale to many petabytes of data with stringent uptime requirements" | §1, PDF p1 | model_design | weakened: wrong section and page; "expected ... which is why" was ours. Reworded, label "Paper §1", link `#page=1` |
| 33 | Fact 2 (8 needs; two are write throughput and strong consistency) | rows 17-18 | §3, PDF p3 | model_design | pass |
| 34 | Fact 3 (25 to 3 ms) | row 28 | §5.3.1, PDF p7 | measured_result | pass |
| 35 | Fact 4 (40%) | row 29; link `#page=9` | §6.9, PDF p9 | measured_result | pass |
| 36 | Fact 5 (10 to thousands): "the test cluster grew ... from 10 machines to many clusters of thousands" | "In the past year, we have gone from running a small HBase test cluster with 10 nodes to many clusters running thousands of nodes." | §6, PDF p7 | measured_result | weakened: one test cluster did not itself grow; now "Facebook's HBase use grew ... from a small 10-machine test cluster to many clusters running thousands of machines" |
| 37 | Fact 6 (20 min): failover with standard backup boss could take 20 min | "the failover times for the BackupNode solution can be as high as 20 minutes" | §4.1.1, PDF p4 | measured_result | pass ("as high as", added "the paper says") |
| 38 | Fact 6: hot standby "aims for" well under a minute | "can become Active in well under a minute"; separate goal "failover within seconds" | §4.1.1, PDF p4 | model_design | weakened: now "can take over in well under a minute" |

## Comic (provenance: illustration)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 39 | howTo: drawings made up; grown-up words are the paper's or usual names | Terms used in paper: strong consistency, federate, denormalized, commit log, HLog, MemStore, HFile, compaction, bloom filter, NameNode, AvatarNode, ZooKeeper, checksum. "Consistent view" and "failover" are usual names ("failover" appears in §4.1) | various | n/a | pass |
| 40 | Strip 1 p1: home page bell with unread count; inbox page lists messages | "'unread' message counts displayed on the home page and the messages shown in the inbox page" | §3, PDF p3 | scenario | pass (bell is a drawing) |
| 41 | Strip 1 p2: mismatch "feels broken" | Not in paper | n/a | scenario | scenario |
| 42 | Strip 1 p3: user expectations drove the need for strong consistency; "everyone sees the same answer" | "This requirement often arises directly from user expectations" | §3, PDF p3 | model_design | weakened: "everyone" overstated; now "the two screens give the same answer" |
| 43 | Strip 2 p1: a data center is a big building of machines | Background definition | n/a | background | background |
| 44 | Strip 2 p2: each person served from one data center; easy to split up | "Messages was easy to federate so that a particular user could be served entirely out of a single data center" | §3, PDF p3 | model_design | pass |
| 45 | Strip 2 p3: machines in that building only need to agree with each other; agreeing worldwide practically impossible | "While a globally distributed strongly consistent system is practically impossible, a system that could at least provide strong consistency within a data center would make it possible to provide a good user experience" | §3, PDF p3 | model_design | pass |
| 46 | Strip 2 grown-up words: data center, federation | "federate" / "federated" | §3, PDF p3 | model_design | pass |
| 47 | Strip 3 p1: every message saved; nothing deleted unless the person does | "messages would not be deleted unless explicitly done so by the user" | §2.1.2, PDF p2 | model_design | pass |
| 48 | Strip 3 p2: one message written several times so each person's view is ready | "messages to be stored for each participating user"; "each message could be written several times" | §2.1, §2.1.1, PDF p2 | model_design | pass |
| 49 | Strip 3 p3: old setup slows for random writes as tables grow | "write performance will typically degrade in a system like MySQL as the number of rows in the table increases" | §2.1.2, PDF p2 | model_design | pass |
| 50 | Strip 3 grown-up words: write throughput, denormalization | "denormalized requirement" | §2.1.1, PDF p2 | model_design | pass |
| 51 | Strip 4 p1: write first goes to a notebook so a crash cannot lose it | "A data transaction first gets written to a commit log"; "the HLog (write ahead log) on HDFS provided sufficient durability" | §5.3 PDF p7; §5.1 PDF p6 | model_design | weakened: "cannot lose" absolute; now "so it can be recovered after a crash" |
| 52 | Strip 4 p2: then on a whiteboard in memory; when full copied to a sorted folder | "applied to an in-memory cache called MemStore. When the MemStore reaches a certain threshold it is written out as an HFile. HFiles are immutable HDFS files containing key/value pairs in sorted order." | §5.3, PDF p7 | model_design | pass |
| 53 | Strip 4 p3: folders pile up, merged now and then | "these HFiles need to be periodically compacted, or merged together, to avoid degrading read performance" | §5.3, PDF p7 | model_design | pass |
| 54 | Strip 4 p3: doorman at each folder says "not here" to skip needless looks | "a check of the cached bloom filter for each HFile can allow some files to be completely skipped" | §5.3.2, PDF p7 | model_design | pass (doorman is a metaphor) |
| 55 | Strip 4 grown-up words | "commit log", "HLog", "MemStore", "HFile", "compaction", "bloom filters" | §5.3, §5.3.2, PDF p7 | model_design | pass |
| 56 | Strip 5 p1: HDFS keeps copies of every block; a write goes down a line of machines | "HDFS sets up a pipeline connection to each replica"; "two other replicas exist for this data" | §5.1.2, PDF p6 | model_design | pass |
| 57 | Strip 5 p2: HBase waits for every copy to say got it; on a failed copy, starts a fresh notebook | "all replicas must ACK any data sent to them. HBase will not continue until it gets a response or failure notification"; "HBase will immediately roll the log and obtain new blocks if it detects that even a single HDFS replica has failed to write data" | §5.1.2, PDF p6 | model_design | pass (applies to the log, which the notebook is) |
| 58 | Strip 5 p3: checksum checked on read; damaged copy discarded, others remain | "checksum validation is performed and the entire block is discarded upon a checksum failure. Data discard is rarely problematic because two other replicas exist" | §5.1.2, PDF p6 | model_design | pass |
| 59 | Strip 6 p1: HDFS has one boss that knows where every block is; if it stops the cluster stops | "The design of HDFS has a single master - the NameNode. Whenever the master is down, the HDFS cluster is unusable" | §4.1, PDF p4 | model_design | pass |
| 60 | Strip 6 p2: standby listens to the same diary and keeps up | "the Standby opens the same transaction log for reading ... keeping its namespace as close to the primary as possible" | §4.1.1, PDF p4 | model_design | pass |
| 61 | Strip 6 p3: signpost in a shared service points everyone to new boss; well under a minute | "ZooKeeper holds a zNode with the physical address of the Primary AvatarNode"; "can become Active in well under a minute" | §4.1.3 PDF p5; §4.1.1 PDF p4 | model_design | pass |
| 62 | Strip 6 grown-up words: NameNode, AvatarNode, ZooKeeper, failover | same sections | §4.1, PDF p4-p5 | model_design | pass |

## Paper-basis tags

| Tag | Evidence (PDF page) | Phrase | Result |
|---|---|---|---|
| `field/computer-science`, `area/distributed-systems`, `area/databases` | p1 | "Apache HBase is a database-like layer built on Hadoop"; keywords "distributed systems" | pass |
| `technique/hbase`, `use/facebook-messages`, `organization/facebook`, `author/dhruba-borthakur` | p1 | Abstract; author block | pass |
| `technique/hdfs` | p4 | "4. REALTIME HDFS" | pass |
| `technique/cassandra` (relevance 0.3) | p1 | Abstract line only (row 7) | pass |
| `concept/strong-consistency` | p3 | "strong consistency semantics within a data center" | pass |
| `concept/high-availability` | p3 | "High Availability and Disaster Recovery" | pass |
| `concept/replication` | p6 | "HDFS provides replication for HBase" (§5.1.2) | pass |
| `concept/commit-log` | p7 | "first gets written to a commit log" | pass |
| `concept/compaction` | p7 | "periodically compacted, or merged together" | pass |
| `concept/bloom-filter` | p7 | "Bloom filters provide a space-efficient and constant-time method" (§5.3.2) | pass |
| `venue/sigmod`, `venue/sigmod-2011` | p1 | "SIGMOD '11, June 12-16, 2011" | weakened: basis was `background` with no evidence; now `paper`, `#page=1` |
| `everyday/*` | none | Editorial | background |

## Counts

62 rows: pass 48, weakened 12 (rows 2, 5, 8, 10, 11, 12, 30, 32, 36, 38, 42, 51; the venue tags are the same fix as row 2), scenario 1 (row 41), background 1 (row 43). All JSON edits validated with `json.load`.
