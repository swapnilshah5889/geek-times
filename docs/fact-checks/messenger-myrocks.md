# Fact-check: "Migrating Messenger storage to optimize performance" (Xiang Li, Thomas Georgiou; Facebook Engineering, 2018)

Source: Xiang Li and Thomas Georgiou, "Migrating Messenger storage to optimize performance", Engineering at Meta (Facebook Engineering blog). Printed byline "By Xiang Li, Thomas Georgiou". The date is not in the body text; it is page metadata `article:published_time 2018-06-26T02:24:52+00:00` and the URL path `2018/06/26`. No venue is printed (page title suffix "- Engineering at Meta").
Canonical = fetched URL: https://engineering.fb.com/2018/06/26/core-infra/migrating-messenger-storage-to-optimize-performance/
Archive: none captured.
Extraction: HTML, 14,331 characters of text (`source.txt`; `raw.html` 96,406 bytes). Cookie banner and share/nav text dropped.
Checked on 2026-11-12. Every quote below was matched against `source.txt`.

**Location convention.** The post has numbered headings only as `<h2>` text; `raw.html` has no `id` on any of them, so `#fragment` links like `#benefits-of-the-new-system` do not exist. Links now use text fragments `#:~:text=<exact words>`. Locations name the section heading (the opening paragraphs are "Intro").

**Result key.** `pass` = in the post as worded. `weakened` = wording went beyond the post; fixed in the JSON. `scenario` = our invented picture, labelled illustration. `background` = not from the post.

**What is in the post:** HBase to MyRocks on flash (Lightning servers), the normal and buffered migration flows, Iris queue, Bistro, the 90 percent / 6-to-3 / 50x / 99.9 percent numbers.
**What is not in the post:** any mention of Apache Cassandra (it names HBase as the old system), the words "shelf", "library", "holding room", any independent measurement of the numbers, and any storage or latency figure beyond the percentages and ratios above.

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, organization "Facebook Engineering", published 2018-06-26, trust `company_reported` | meta.md: "Company engineering blog post, not a refereed publication; all numbers are the company's own claims." Date from page metadata | pass; trust flagged for owner decision (company_reported suggested by evidence) |

## Facts (`facts[]`, hook, summary)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 2 | Summary: moved Messenger's stored messages from HBase to MyRocks, a MySQL-based database, without downtime | "We moved from HBase ... to MyRocks, Facebook's open source database project that integrates RocksDB as a MySQL storage engine"; "did not cause any disruption or downtime" | Intro | company-reported | pass |
| 3 | Summary: 90 percent less storage | "decreased storage consumption by 90 percent" | Intro | measured_result | pass |
| 4 | Summary: "reads became 50 times faster" | "Read latency is now 50 times lower than in the previous system." | Benefits | measured_result | weakened: the post says latency, not speed. Now "read latency is 50 times lower". Fixed in JSON |
| 5 | Hook teaser, headline: "a billion chat histories" | "keeping Messenger up and running for more than 1 billion accounts" | Handling the challenge | scenario | pass (framing; the post counts accounts) |
| 6 | Hook stat 90% "less storage, as Facebook reports" | "reduced storage consumption by 90 percent without data loss" | Benefits | measured_result | pass |
| 7 | Hook cta, `readMinutes: 4` | Editorial | n/a | n/a | background |
| 8 | Lead deck: messages lived in HBase; moved to MyRocks while the app stayed open | "HBase had been our database since 2010"; "did not cause any disruption or downtime" | Handling; Intro | company-reported | pass |
| 9 | Fig. 1: old shelf many copies, new shelf fewer | "reduce the replication factor from six to three" | Benefits | model_design | pass (shelf is a metaphor) |
| 10 | Fig. 2: 90 percent less storage after the move | as row 3 | Benefits | company-reported | pass |

## Story text (chapters)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 11 | Ch. 1: started like email; now live chat; more than a billion people use it | "primarily intended to be a direct messaging product similar to email, with messages waiting in your inbox"; "More than a billion people now use Facebook Messenger"; "mobile-first, real-time communications system" | Intro | company-reported | pass |
| 12 | Ch. 1: app could not close; some businesses keep chats open all day and night | "business users often have many Messenger chat windows active simultaneously around the clock" | Handling | company-reported | pass |
| 13 | Ch. 2: team had used HBase since 2010 | "HBase had been our database since 2010" | Handling | company-reported | pass |
| 14 | Ch. 2: MyRocks puts RocksDB inside MySQL; spinning disks to flash | "integrates RocksDB as a MySQL storage engine"; "moved from storing the database on spinning disks to flash" | Intro | company-reported | pass |
| 15 | Ch. 2: MySQL's way of making copies fits its data centers, so fewer copies | "the replication topology for MySQL is more compatible with the way Facebook data centers operate in production, enabling us to reduce the number of physical replicas" | Handling | company-reported | pass |
| 16 | Ch. 3: normal way: quiet moment, copy, check nothing changed, double-write and compare | "no data is written to the account during migration"; "we check whether the data position moved"; "double-writing state"; "confirm that the data we have in HBase matches the data in MyRocks" | Normal migration | model_design | pass |
| 17 | Ch. 3: busy accounts: snapshot into a holding area; new messages wait in Iris; new system catches up | "take a snapshot of the account's data"; "copy the snapshot to a buffer tier"; "write traffic ... is queueing up in Iris"; "drains the queue and catches up" | Buffered | model_design | pass |
| 18 | Ch. 4: 99.9 percent in two weeks normal flow, the rest two weeks later; 90 percent less without data loss; latency 50 times lower | "we migrated 99.9 percent of accounts via the normal migration flow in two weeks, and finished the remaining via the buffered migration flow two weeks after"; "without data loss"; "50 times lower" | Benefits | measured_result | pass |
| 19 | Ch. 4 link "See 'Benefits of the new system'" used no valid anchor | `raw.html` has no `id` on the heading | Benefits | n/a | weakened: link now `#:~:text=Benefits%20of%20the%20new%20system`. Fixed in JSON |

## Comic

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 20 | 1a: HBase served the team well from 2010 | "HBase had been our database since 2010 and it served us well" | Handling | company-reported | pass |
| 21 | 1b (old): "reading old history on HBase kept the disks busy ... that made some features hard" | "extensive reading across all historical data on HBase clusters, which are I/O operations bound"; mobile search: "Because it is I/O bound, it would require an equivalent read-heavy job" | Handling; Benefits | company-reported | weakened: the I/O-bound point is about migration reads and index building, not everyday history reads. Now "The post says HBase work is bound by disk reads. The team says that made some features hard, like searching messages on a phone." Fixed in JSON |
| 22 | 1c: MyRocks made phone search possible | "launch message content search on mobile"; "It was hard to implement mobile message search using HBase" | Benefits | company-reported | pass |
| 23 | 2a: spinning disks to flash | "spinning disks to flash on our new Lightning Server SKU" | Intro | company-reported | pass |
| 24 | 2b: smaller on disk; Zstandard saved more | "The simplified data schema directly reduced the size of data on disk. We saved additional space in MyRocks by applying Zstandard" | Benefits | company-reported | pass |
| 25 | 2c: three copies instead of six; 90 percent less | "reduce the replication factor from six to three"; "reduced storage consumption by 90 percent" | Benefits | measured_result | pass |
| 26 | 3a: three states; nobody writes while moving | "not-migrated, double-writing, or done"; "no data is written to the account during migration" | Normal | model_design | pass |
| 27 | 3b: copy, check, on change fail, wipe, retry later | "classify this account migration as failed, clean up the data in MyRocks, and let a future migration job try ... again" | Normal | model_design | pass |
| 28 | 3c: double-write, compare, roll back | "there is a complete revert plan that can roll back an account to the not-migrated state" | Normal | model_design | pass |
| 29 | 4a: business bot, no quiet moment | "a large business may run a Messenger bot ... there is no window of time to perform the migration" | Buffered | company-reported | pass |
| 30 | 4b: snapshot at cutoff, copy takes about a tenth of the migration time | "usually takes about 10 percent of the migration time" | Buffered | company-reported | pass |
| 31 | 4c: queue Iris holds messages for weeks | "Iris was designed to be able to queue messages for weeks" | Buffered | company-reported | pass |
| 32 | 5a: Bistro, another Facebook open source project; can throttle | "Bistro framework, another Facebook open source project"; "throttle jobs if issues arise" | Migrate at scale | company-reported | pass |
| 33 | 5b: new accounts only on new system; stop writing to HBase one cluster at a time | "all new Messenger accounts are then created on the new system only. We gradually stop writing traffic to HBase, one cluster at a time" | Migrate at scale | company-reported | pass |
| 34 | 5c: accounting job; old system offline | "accounting job"; "we finally took the old system offline" | Handling; Migrate | company-reported | pass |
| 35 | 6a: scrolling back through old messages is faster | "much faster to scroll back though old messages" | Benefits | company-reported | pass |
| 36 | 6b: much faster data-center switching, no manual steps | "no longer need to involve human supervisors and perform manual operations ... orders of magnitude faster" | Benefits | company-reported | pass |
| 37 | 6c: reuse Facebook search built on MySQL; search on phone | "directly adopted the established Facebook search infrastructure built on top of MySQL" | Benefits | company-reported | pass |
| 38 | grownUpWords (HBase, MyRocks, key-value store, MySQL storage engine, flash storage, replication factor, compression, Zstandard, state machine, double-writing, validation, revert plan, buffer tier, Iris, queue, snapshot, accounting job, Bistro, latency, search, resilience) | all appear in the post (e.g. "state machine", "buffer tier", "replication factor", "resilient") | various | n/a | pass |

## Fact cards (`facts[]`)

| # | Claim | Exact phrase | Location | Kind | Link before / after | Result |
|---|---|---|---|---|---|---|
| 39 | 90 percent, "made flash practical" | "reduced storage consumption by 90 percent without data loss, thereby making it practical to use flash storage" | Benefits | measured_result | `#benefits-of-the-new-system` (no such id) / `#:~:text=reduced%20storage%20consumption%20by%2090%20percent` | weakened: link fixed |
| 40 | 6 to 3 copies, "thanks to differences between HBase and MyRocks" | "reduce the replication factor from six to three, thanks to differences between the HBase and MyRocks architectures" | Benefits | measured_result | same / `#:~:text=reduce%20the%20replication%20factor%20from%20six%20to%20three` | weakened: link fixed |
| 41 | 50x lower read latency | "Read latency is now 50 times lower than in the previous system." | Benefits | measured_result | same / `#:~:text=Read%20latency%20is%20now%2050%20times%20lower` | weakened: link fixed |
| 42 | 99.9% by normal flow in two weeks; rest two weeks after | "we migrated 99.9 percent of accounts via the normal migration flow in two weeks" | Benefits | measured_result | same / `#:~:text=we%20migrated%2099.9%20percent%20of%20accounts` | weakened: link fixed |
| 43 | 10% of migration time for snapshot copy | "usually takes about 10 percent of the migration time" | Buffered migration flow | model_design | `#buffered-migration-flow` (no id) / `#:~:text=usually%20takes%20about%2010%20percent` | weakened: link fixed. Kind is `model_design` though this is a company-reported figure; left as is, text already says "the post says" |
| 44 | 2010: HBase became Messenger's database | "HBase had been our database since 2010" | Handling the challenge | model_design | `#handling-the-challenge-of-migrating-at-scale` (no id) / `#:~:text=HBase%20had%20been%20our%20database%20since%202010` | weakened: link fixed |

All fact labels ("Post · Benefits of the new system" etc.) name real section headings.

## Paper-basis tags (spot-check)

All paper-basis tags point at the plain post URL (valid, no fragment).

| Tag | Phrase | Result |
|---|---|---|
| `field/computer-science`, `area/distributed-systems`, `area/databases` | "open source distributed key-value store based on HDFS"; database migration | pass |
| `concept/replication` | "reduce the replication factor from six to three" | pass |
| `use/message-search` | "launch message content search on mobile" | pass |
| `organization/facebook` | "Facebook's open source database project"; Facebook Engineering | pass |
| `technique/myrocks` (proposed) | "MyRocks, Facebook's open source database project" | pass |
| `technique/hbase` (proposed) | "HBase, an open source distributed key-value store based on HDFS" | pass |
| `concept/data-migration` (proposed) | whole post | pass |
| `concept/flash-storage` (proposed) | "spinning disks to flash"; "SSDs" | pass |
| `author/xiang-li`, `author/thomas-georgiou` (proposed) | "By Xiang Li, Thomas Georgiou" | pass |
| `everyday/keeping-copies-safe` | editorial | background |

## Storyline honesty

The post never mentions Apache Cassandra. The JSON makes no Cassandra claim (it names HBase and MyRocks only). Any storyline link to Cassandra is the lead's editorial relation, not the post's.

JSON edits made in `data/seed/papers/messenger-myrocks.json`: summary wording (row 4), comic 1b caption (row 21), chapter 4 link (row 19), six fact source links (rows 39-44). Keys and media paths unchanged; JSON validated.
