# Cassandra storyline: source ledger

The source list for the Cassandra storyline, checked on 2026-11-12 by the stage A workers (`skills/batch-storyline`).
Every row was opened and its text extracted. Titles, dates and venue lines below are what each source prints. "Angle"
says how the source relates to Cassandra, using only the source's own words.

| Year | Slug | Source | Kind | Trust (suggested) | Angle |
|---|---|---|---|---|---|
| 2006 | `bigtable` | Bigtable: A Distributed Storage System for Structured Data (Chang et al., OSDI '06) | paper | peer_reviewed? (venue printed) | Ancestor: column families, commit log → memtable → SSTables, compaction, Bloom filters. Never mentions Cassandra |
| 2007 | `dynamo` | Dynamo (DeCandia et al., SOSP 2007), **live** | paper | preprint (owner's conservative call) | Ancestor: the ring, replication, gossip |
| 2009 | `cassandra` | Cassandra - A Decentralized Structured Storage System (Lakshman & Malik, LADIS 2009), **live** | paper | peer_reviewed (LADIS CFP) | The origin |
| 2010 | `ycsb` | Benchmarking Cloud Serving Systems with YCSB (Cooper et al., SoCC '10) | paper | peer_reviewed? (venue printed) | Measured: Cassandra 0.5.0 vs HBase, PNUTS, sharded MySQL |
| 2010 | `twitter-cassandra-2010` | Cassandra at Twitter Today (Twitter Engineering, 10 Jul 2010; read from Wayback) | blog | company_reported | Kept tweets on MySQL; Cassandra for places, research, analytics |
| 2010 | `facebook-messages-hbase` | The Underlying Technology of Messages (Muthukkaruppan, Facebook, 15 Nov 2010) | blog | company_reported | Left: chose HBase; Cassandra's eventual consistency "difficult" for Messages |
| 2011 | `hadoop-realtime-facebook` | Apache Hadoop Goes Realtime at Facebook (Borthakur et al., SIGMOD '11) | paper | peer_reviewed? (venue printed) | Left: one abstract sentence names Cassandra; requirements give the reasons |
| 2011 | `netflix-cassandra-benchmark` | Benchmarking Cassandra Scalability on AWS — Over a million writes per second (Netflix, 2 Nov 2011) | blog | company_reported | Adopted: linear scaling test |
| 2012 | `pbs` | Probabilistically Bounded Staleness for Practical Partial Quorums (Bailis et al., PVLDB 5(8)) | paper | journal_published | Measured: how stale eventual reads are |
| 2013 | `jepsen-cassandra` | Jepsen: Cassandra (Kingsbury, 24 Sep 2013) | blog | needs owner call (independent tester) | Measured: lost acknowledged writes, counters, LWT issues |
| 2017 | `discord-billions` | How Discord Stores Billions of Messages (Vishnevskiy, 13 Jan 2017) | blog | company_reported | Adopted: MongoDB → Cassandra |
| 2018 | `instagram-rocksandra` | Open-sourcing a 10x reduction in Apache Cassandra tail latency (Instagram, 5 Mar 2018) | blog | company_reported | Improved: RocksDB storage engine. Headline "10x" is a benchmark; production P99 went 60 → 20 ms |
| 2018 | `messenger-myrocks` | Migrating Messenger storage to optimize performance (Li & Georgiou, Facebook, 26 Jun 2018) | blog | company_reported | Facebook's next step: HBase → MyRocks. Never mentions Cassandra |
| 2021 | `accord` | CEP-15: Fast General Purpose Transactions (Elliott Smith et al., draft whitepaper) | paper | preprint | Improved (proposed): transactions for Cassandra. No date printed (PDF metadata Nov 2021), no benchmarks |
| 2023 | `discord-trillions` | How Discord Stores Trillions of Messages (Ingram, 6 Mar 2023) | blog | company_reported | Left: Cassandra → ScyllaDB |

## Owner decisions

- **Conference trust.** Bigtable, YCSB and the SIGMOD paper print their venue but not a refereeing statement. Dynamo,
  in the same position, was labelled `preprint`. Choose one rule for all four (`peer_reviewed` or the conservative label).
- **Jepsen.** The schema has no "independent" trust value. The draft uses `company_reported` (self-published blog).
- **Accord.** `preprint` (draft whitepaper). The year 2021 comes from PDF metadata, not printed text.

## Source notes

- Twitter: live site blocks automated reads (403); text read from the Wayback snapshot. No byline is printed.
- Netflix: read from a Wayback snapshot of the Netflix Tech Blog URL; originally published on techblog.netflix.com.
- Instagram: read from a Wayback snapshot; the live site did not respond.
- Messenger 2018 and Bigtable never mention Cassandra. Their stories must not claim they do; the storyline places them.
