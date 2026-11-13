# Fact-check: "Bigtable: A Distributed Storage System for Structured Data" (Chang and colleagues, Google; OSDI 2006)

Source: Fay Chang, Jeffrey Dean, Sanjay Ghemawat, Wilson C. Hsieh, Deborah A. Wallach, Mike Burrows, Tushar Chandra, Andrew Fikes, Robert E. Gruber (Google, Inc.). Venue as printed: "To appear in OSDI 2006" (Google copy, every page footer) and "OSDI '06: 7th USENIX Symposium on Operating Systems Design and Implementation" (USENIX copy, p1). No day or month printed; the story says `year: 2006`.
Canonical URL: https://www.usenix.org/legacy/event/osdi06/tech/chang/chang.pdf
Fetched URL (used as the story's link): https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf (14 pages; the pre-publication draft, "To appear in OSDI 2006"). The USENIX copy (also 14 pages) was used for venue evidence only.
Archive: none captured.
Extraction: PDF text per page (`source.txt` with `=== PAGE N ===` markers, plus p1-p14); every quote below was matched against that text. Checked on 2026-11-12.

**Location convention.** Links use `#page=N`, the PDF page index of the Google copy (it has no separate printed page numbers). Each `#page=N` was checked against the `=== PAGE N ===` markers. Paper sections: 1 Introduction (p1), 2 Data Model (p1-p3), 3 API (p3), 4 Building Blocks (p3-p4), 5 Implementation (p4), 5.1 Tablet Location (p4), 5.2 Tablet Assignment (p5), 5.3 Tablet Serving (p6), 5.4 Compactions (p6), 6 Refinements (p6-p7), 7 Performance Evaluation (p8), 8 Real Applications (p10), 11 Conclusions (p13).

**Result key.** `pass` = the claim as worded is in the paper or is a plain restatement. `weakened` = wording went beyond the paper; the Result says the fix (done in the JSON). `scenario` = our invented picture or metaphor, labelled illustration. `background` = not from the paper.

**Cassandra.** The paper never mentions Cassandra (0 hits). The story text does not mention it either (0 hits in the JSON).

**What is not in the paper:** the words "notebook", "whiteboard", "folder", "doorman", "zip", the desk/scissors/manager pictures, and the dictionary simile; these are our metaphors (provenance `illustration`). The paper's own terms are used under "grown-up words". The paper says Bloom filters tell whether an SSTable "might contain" data; the "definitely not here" half is the standard reading plus the paper's line that most lookups for non-existent rows "do not need to touch disk".

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | Title, authors, year 2006 | Title block PDF p1; nine authors, story says "Chang and colleagues" (first author Fay Chang) | pass |
| 2 | Venue OSDI 2006 (`venue/osdi`, `venue/osdi-2006`, tags `basis: background`) | "To appear in OSDI 2006" (Google copy, p1 and footers); USENIX copy p1: "OSDI '06: 7th USENIX Symposium on Operating Systems Design and Implementation", "USENIX Association" | pass (venue not in story text) |
| 3 | Trust suggestion `peer_reviewed` (owner decides; FLAG) | meta.md: printed venue is a refereed systems symposium. The printed text does not itself say "refereed" or "peer reviewed", so the owner should confirm if strict. The linked Google copy is the pre-publication draft, not the USENIX published copy | flag for owner |

## Facts (`facts[]`, hook, summary)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 1 | Fact 1: 24,500 tablet servers in 388 non-test clusters, August 2006; link `#page=10` | "As of August 2006, there are 388 non-test Bigtable clusters running in various Google machine clusters, with a combined total of about 24,500 tablet servers." | §8, PDF p10 | measured_result | pass (company's own report; text says "as the paper reports it") |
| 2 | Fact 2: more than 1.2 million requests/second, 14 busy clusters, 8069 tablet servers; link `#page=10` | "One group of 14 busy clusters with 8069 total tablet servers saw an aggregate volume of more than 1.2 million requests per second" | §8, PDF p10 | measured_result | pass |
| 3 | Fact 3: 100-200 MB default tablet size, "the row range that moves between servers"; link `#page=4` | "As a table grows, it is automatically split into multiple tablets, each approximately 100-200 MB in size by default."; "Each row range is called a tablet, which is the unit of distribution and load balancing" (p2) | §5 PDF p4; §2 PDF p2 | model_design | pass |
| 4 | Fact 4: 10-to-1 space reduction on web page contents, helped by keeping pages from one host together; Gzip 3-to-1 or 4-to-1; link `#page=7` | "The scheme achieved a 10-to-1 reduction in space. This is much better than typical Gzip reductions of 3-to-1 or 4-to-1 on HTML pages because of the way Webtable rows are laid out: all pages from a single host are stored close to each other." ("In one experiment") | §6 Compression, PDF p7 | measured_result | pass |
| 5 | Fact 5: 200 TB raw click table, one row per end-user session; link `#page=10` | "The raw click table (~200 TB) maintains a row for each end-user session." | §8.1, PDF p10 | measured_result | pass (paper uses "~", text says "200 TB" as the table's size, close enough; owner may prefer "about") |
| 6 | Fact 6: 0.0047% of server hours had some data unavailable because Chubby was down or unreachable, across 14 clusters; link `#page=4` | "We recently measured this effect in 14 Bigtable clusters spanning 11 Chubby instances. The average percentage of Bigtable server hours during which some data stored in Bigtable was not available due to Chubby unavailability (caused by either Chubby outages or network issues) was 0.0047%." | §4, PDF p4 | measured_result | pass |
| 7 | Hook stat: 24,500 "tablet servers in August 2006" | Same phrase as fact 1 | §8, PDF p10 | measured_result | pass |
| 8 | Hook teaser, stickers "One huge table!", "Sorted!", "Cut up!" | Teaser is a question; stickers are labels for the sorted map and tablets (p1-p2) | n/a | n/a | scenario |
| 9 | Summary: Google had data of very different sizes; a giant sorted table found by row, column and time; cut into tablets on thousands of ordinary machines | "data size (from URLs to web pages to satellite imagery)"; "a sparse, distributed, persistent multidimensional sorted map. The map is indexed by a row key, column key, and a timestamp"; "petabytes of data across thousands of commodity servers" | Abstract p1; §2 p1 | model_design | pass |
| 10 | Summary: each write goes to a notebook and a whiteboard, then sorted folders zipped together later | "A valid mutation is written to the commit log... its contents are inserted into the memtable" (p6); "converted to an SSTable" (p6); "merging compaction in the background" (p6) | §5.3-5.4, PDF p6 | model_design | pass (metaphors named; "The paper describes its own design and Google's use of it" is accurate) |

## Story text and comic (provenance: illustration, evidence for chapter 4)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 11 | Lead deck: data of every size, from web addresses to satellite pictures; one huge sorted table cut into pieces on thousands of ordinary machines | "data size (from URLs to web pages to satellite imagery)"; "petabytes of data across thousands of commodity servers" | Abstract, PDF p1 | model_design | pass |
| 12 | Fig. 1: rows kept in order "like a dictionary"; every box found by row, column and time | "Bigtable maintains data in lexicographic order by row key" (p2); "indexed by a row key, column key, and a timestamp" (p1) | §2, PDF p1-p2 | model_design | pass (dictionary is our simile, `scenario`) |
| 13 | Fig. 2: table cut into row ranges, each piece on one machine, a lightly busy manager hands out pieces | "Each tablet is assigned to one tablet server at a time" (p5); "the master is lightly loaded in practice" (p4); master "responsible for assigning tablets" (p4) | §5, §5.2, PDF p4-p5 | model_design | pass |
| 14 | Ch. 1: more than sixty products, web indexing to Google Earth | "Bigtable is used by more than sixty Google products and projects"; "web indexing, Google Earth, and Google Finance" | §1 and Abstract, PDF p1 | model_design | pass |
| 15 | Ch. 1: some want fast answers for people waiting, others chew huge piles in the background | "throughput-oriented batch-processing jobs to latency-sensitive serving of data to end users" | §1, PDF p1 | model_design | pass |
| 16 | Ch. 1: goal was petabytes over thousands of ordinary machines | "designed to scale to a very large size: petabytes of data across thousands of commodity servers" | Abstract, PDF p1 | model_design | pass |
| 17 | Ch. 2: not a full relational database; a sorted map found by row, column, time | "Bigtable does not support a full relational data model" (p2); "sorted map" (p1) | §1-§2, PDF p1-p2 | model_design | pass |
| 18 | Ch. 2: rows in alphabetical order; neighbors "close together on disk" | Paper: "reads of short row ranges are efficient and typically require communication with only a small number of machines"; "Storing pages from the same domain near each other makes some host and domain analyses more efficient"; clients "reason about the locality properties of the data" | §2, PDF p1-p2 | model_design | weakened: "close together on disk" is not stated. Reworded to "kept together, and reading a short range of rows is efficient". Fixed in JSON |
| 19 | Ch. 2: tablets each about 100 to 200 MB by default, each served by one machine at a time | "approximately 100-200 MB in size by default" (p4); "assigned to one tablet server at a time" (p5) | §5, §5.2, PDF p4-p5 | model_design | pass |
| 20 | Ch. 2: grown-up words column families, tablets | "column families" (p2), "tablet" (p2) | §2, PDF p2 | model_design | pass |
| 21 | Ch. 3: write goes at the end of a notebook on disk, then onto a sorted whiteboard in memory | "Updates are committed to a commit log that stores redo records... the recently committed ones are stored in memory in a sorted buffer called a memtable"; "we append mutations to a single commit log per tablet server" (p7) | §5.3, PDF p6; §6, PDF p7 | model_design | pass (the log is stored in GFS, "on disk" is a fair simplification) |
| 22 | Ch. 3: full whiteboard saved as a sorted, never-edited folder; fresh whiteboard starts | "the memtable is frozen, a new memtable is created, and the frozen memtable is converted to an SSTable and written to GFS"; "ordered immutable map" (p3) | §5.4, PDF p6; §4, PDF p3 | model_design | pass |
| 23 | Ch. 3: folders pile up, so the machine zips a few together in the background | "we bound the number of such files by periodically executing a merging compaction in the background. A merging compaction reads the contents of a few SSTables and the memtable, and writes out a new SSTable." | §5.4, PDF p6 | model_design | pass |
| 24 | Ch. 3: a read looks at the whiteboard and all folders together | "executed on a merged view of the sequence of SSTables and the memtable" | §5.3, PDF p6 | model_design | pass |
| 25 | Ch. 3: a doorman can say "not in this folder" without opening it | "A Bloom filter allows us to ask whether an SSTable might contain any data for a specified row/column pair"; "most lookups for non-existent rows or columns do not need to touch disk" | §6 Bloom filters, PDF p7 | model_design | pass (doorman is our metaphor; see note above) |
| 26 | Ch. 3: grown-up words commit log, memtable, SSTable, compaction, Bloom filter | All five terms appear (p6, p7) | §5.3-5.4, §6 | model_design | pass |
| 27 | Ch. 4: 388 clusters, about 24,500 tablet servers; 14 busy clusters, 8069 servers, more than 1.2 million requests/s; "Google's own reported numbers"; link `#page=10` | Same as facts 1-2 | §8, PDF p10 | measured_result | pass |
| 28 | Comic strip 1 (data model): address = row, column, time; grown-up words row key, column family, timestamp | "indexed by a row key, column key, and a timestamp" (p1); "column families" (p2) | §2, PDF p1-p2 | model_design | pass |
| 29 | Strip 1: rows alphabetical; web addresses flipped so pages from one site sit side by side | "lexicographic order by row key"; "pages in the same domain are grouped together into contiguous rows by reversing the hostname components of the URLs" | §2, PDF p2 | model_design | pass |
| 30 | Strip 1: older versions kept, newest first; page table keeps the last three | "Different versions of a cell are stored in decreasing timestamp order, so that the most recent versions can be read first"; "lets us keep only the most recent three versions of every page" | §2, PDF p2-p3 | model_design | pass |
| 31 | Strip 2: tablets roughly 100 to 200 MB; one machine at a time; a machine holds many tablets | "100-200 MB" (p4); "assigned to one tablet server at a time" (p5); "somewhere between ten to a thousand tablets per tablet server" (p4) | §5, PDF p4-p5 | model_design | pass |
| 32 | Strip 2: master hands out tablets, people ask machines directly, so master lightly busy; grown-up words tablet, tablet server, master | "clients communicate directly with tablet servers for reads and writes... most clients never communicate with the master. As a result, the master is lightly loaded in practice." | §5, PDF p4 | model_design | pass |
| 33 | Strip 3: write goes at end of notebook; "Adding at the end is quick, and it survives a crash" | Paper: updates "committed to a commit log"; the tablet server "reapply the mutations for that tablet from the commit log" after a death (p7). It does not say appending is quick | §5.3 p6; §6 p7 | model_design | weakened: reworded to "The notebook is what lets a machine rebuild after a crash." Fixed in JSON |
| 34 | Strip 3: then onto a sorted whiteboard in memory | "its contents are inserted into the memtable"; "sorted buffer called a memtable" | §5.3, PDF p6 | model_design | pass |
| 35 | Strip 3: one notebook shared by all tablets on the machine | "we append mutations to a single commit log per tablet server, co-mingling mutations for different tablets in the same physical log file" | §6, PDF p7 | model_design | pass |
| 36 | Strip 4: whiteboard frozen at a limit, fresh one takes writes; copied out as sorted never-edited file; reads/writes continue; fewer notebook lines replayed after a crash | "When the memtable size reaches a threshold, the memtable is frozen, a new memtable is created, and the frozen memtable is converted to an SSTable"; "reduces the amount of data that has to be read from the commit log during recovery"; "Incoming read and write operations can continue while compactions occur" | §5.4, PDF p6 | model_design | pass |
| 37 | Strip 5: every freeze makes another folder, too many means slow reads; a few zipped into one, old thrown away; zipping all is a major compaction; deleted notes gone for good | "Every minor compaction creates a new SSTable... read operations might need to merge updates from an arbitrary number of SSTables"; "input SSTables and memtable can be discarded"; "rewrites all SSTables into exactly one SSTable is called a major compaction... contains no deletion information or deleted data" | §5.4, PDF p6 | model_design | pass |
| 38 | Strip 6: merged view of whiteboard and folders, "all are sorted, so this is quick" | "Since the SSTables and the memtable are lexicographically sorted data structures, the merged view can be formed efficiently." | §5.3, PDF p6 | model_design | pass |
| 39 | Strip 6: doorman says "might have it" or "not here"; saves disk trips | "might contain"; "drastically reduces the number of disk seeks"; "most lookups for non-existent rows or columns do not need to touch disk" | §6, PDF p7 | model_design | pass |
| 40 | Strip 6: if a machine dies, another replays the notebook to rebuild the whiteboard; grown-up words merged view, Bloom filter, redo points | "To recover a tablet... reconstructs the memtable by applying all of the updates that have committed since the redo points" (p6); tablets "moved to a large number of other tablet servers" which reapply the log (p7) | §5.3, PDF p6; §6, PDF p7 | model_design | pass |
| 41 | Comic howTo and deck: drawings made up; "grown-up words" are the paper's; the write is a small note about a web page | Framing text, labelled illustration | n/a | n/a | scenario |

## Paper-basis tag evidence links

| Tag | Link | What is on that page | Result |
|---|---|---|---|
| field/computer-science, area/distributed-systems, area/databases, concept/high-availability, organization/google, technique/bigtable, author/fay-chang | `#page=1` | Title block, "distributed storage system", Google, authors, "high availability" among the goals | pass |
| concept/key-value-store | `#page=1` | "sparse, distributed, persistent multidimensional sorted map"; the paper does not use the term "key-value store" | pass (loosely; tag is a classification) |
| concept/column-family, concept/tablet | `#page=2` | "column families" and "Each row range is called a tablet" | pass |
| concept/sstable | `#page=3` | "The Google SSTable file format is used internally to store Bigtable data" | pass |
| concept/commit-log, concept/compaction, concept/memtable | `#page=6` | §5.3 commit log and memtable; §5.4 compactions | pass |
| concept/bloom-filter | `#page=7` | "Bloom filters" under §6 Refinements | pass |
| everyday/finding-things | none (editorial) | Editorial tag, no evidence link needed | n/a |
| venue/osdi, venue/osdi-2006 | none (background) | Venue printed on the paper (row 2) | n/a |

## Summary

Rows checked: 3 trust, 10 facts, 31 story/comic, 8 tag groups (every claim and link covered).
Results: pass 38 (+8 tag groups), weakened 2 (rows 18 and 33, both fixed in the JSON), scenario 3, background 1, flag 1 (trust).

JSON edits to `data/seed/papers/bigtable.json` (keys and media paths unchanged; JSON validated):
- Chapter 2 caption: "neighbors in the list are close together on disk" became "neighbors in the list are kept together, and reading a short range of rows is efficient".
- Comic strip 3, panel 1: "Adding at the end is quick, and it survives a crash." became "The notebook is what lets a machine rebuild after a crash."

Owner flags: `peer_reviewed` (row 3) is inferred from the OSDI venue, and the linked copy is the pre-publication draft; the fact 5 text says "200 TB" where the paper prints "~200 TB".
