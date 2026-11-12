# Dynamo library patch (for the lead to apply)

Status: spec only, prepared 2026-11-07 on `v1`. `data/seed/library.json` and `data/seed/tags.json` were **not** edited. Nothing was published and no npm script was run.
Files delivered: `data/seed/papers/dynamo.json`, `docs/fact-checks/dynamo.md`, 30 placeholder SVGs under `public/media/dynamo/`.

## Notes before applying

- **Field.** `library.json` already has a `sw` field ("Software & systems"); the H3 story uses it. Use `"sw"` for both the story and the node. No new field is needed (the brief guessed `cs`, which does not exist in this library).
- **Cluster overlap.** The `sw` cluster (cx 620, cy 460) overlaps the `physics` cluster (cx 600, cy 460), and the `weinberg` (560, 450) and `higgs` (620, 430) nodes sit inside it. The x/y below stay clear of those two nodes, but the clusters themselves overlap; the lead may want to move `sw`.
- **Tags.** `data/seed/tags.json` has no distributed-systems vocabulary, so 34 of the story's 35 tags are proposals. Only `field/computer-science` exists. The story's tags are all `source: "ai"`, `status: "suggested"`; approve them by setting `status: "approved"` in `dynamo.json` after the tags land.
- **Trust.** `peer_reviewed` is set on the strength of the SOSP 2007 venue line printed on the paper. The paper itself does not say "peer-reviewed", and the ACM proceedings page was not fetched. Confirm before publishing (fact-check row 2).
- **Top-level `cover`.** Omitted on purpose: `attention-is-all-you-need.json` has none, and `types.ts` says the lead block is used when it is absent. The hook's frames reuse the lead art.
- **Per-fact `trust`.** Not in the `Fact` type; trust comes from the library entry's `trust` (the publisher copies it onto fact moments). It is not written on the facts.
- **Media.** All SVGs are grey placeholders with the caption inline. Final art needs the canvas step first (skills/convert-paper step 4).
- `site.json` is not in `data/seed` scope of this task. `convert-paper` step 6.1 says to add `{slug, title, dataUrl}` to `papers` in `site.json`; check whether `data/seed/site.json` still needs the entry.

## 1. `stories[]` entry

Append to `stories` in `data/seed/library.json`:

```json
{
  "id": "dynamo",
  "real": true,
  "sample": false,
  "headline": "The cart that",
  "accent": "never disappears.",
  "dek": "A machine breaks while you shop, and your cart is still there. Amazon's Dynamo keeps copies on a ring of servers and merges them when they disagree.",
  "desk": "Computer science  /  Distributed systems",
  "fields": [
    "sw"
  ],
  "role": "feature",
  "kind": "paper",
  "title": "Dynamo: Amazon’s Highly Available Key-value Store",
  "authors": "DeCandia and colleagues",
  "year": 2007,
  "trust": "peer_reviewed",
  "minutes": 4
}
```

`front`/`issues`: not placed. The owner decides.

## 2. `nodes[]` entries

The brief says `slug`; existing nodes use `id`, so the node below uses `id`.

```json
{
  "id": "dynamo",
  "title": "Dynamo: Amazon’s Highly Available Key-value Store",
  "authors": "DeCandia and colleagues",
  "year": 2007,
  "field": "sw",
  "type": "paper",
  "x": 680,
  "y": 490,
  "story": "dynamo",
  "short": "Amazon's Dynamo",
  "blurb": "Amazon's shopping-cart store. Copies of each cart sit on a ring of servers, and when copies disagree the cart code merges them so an added item is never lost."
}
```

Optional ancestor nodes (neither exists in the library; add them only if the lead wants the edges in section 3). They carry no `story`, like the other background nodes.

```json
{
  "id": "chord",
  "title": "Chord: a scalable peer-to-peer lookup service",
  "authors": "Stoica and colleagues",
  "year": 2001,
  "field": "sw",
  "type": "paper",
  "x": 590,
  "y": 505
}
```

```json
{
  "id": "karger-hashing",
  "title": "Consistent hashing and random trees",
  "authors": "Karger and colleagues",
  "year": 1997,
  "field": "sw",
  "type": "paper",
  "x": 545,
  "y": 480
}
```

## 3. `relations[]` edges

Relations point from the earlier idea to the later one.

```json
[
  {
    "from": "karger-hashing",
    "to": "dynamo",
    "kind": "uses_method",
    "note": "Dynamo places carts and machines on a ring using consistent hashing.",
    "cited": true
  },
  {
    "from": "chord",
    "to": "dynamo",
    "kind": "builds_on",
    "note": "Dynamo uses a ring like Chord's but lets every machine know where each cart lives, so there are no extra hops.",
    "cited": true
  }
]
```

- **Chord to Dynamo (`builds_on`)**: citable from this paper. §3.1 (PDF p4) names Chord [20] among structured P2P systems, and §4.2 (PDF p6) says Dynamo's variant of consistent hashing is "similar to the one used in [10, 20]". The paper also says Dynamo avoids Chord-style multi-hop routing, because extra hops add latency variation (§3.3 Discussion), which is what the note says. `cited: true` is justified by that text.
- **Karger et al. to Dynamo (`uses_method`)**: reference [10] is "Consistent hashing and random trees", and §4.2 cites it as the source of consistent hashing. Also citable.
- **Descendants: none proposed.** The paper does not mention Cassandra, Riak, Voldemort or DynamoDB, so edges to them are **unverified and not included**. Add them only with a cited outside source (and the nodes would need to exist). One for the lead's awareness: Avinash Lakshman is an author of this paper; his later work is not in the paper.
- Use `kind: "builds_on"` or `"uses_method"` only; the validator accepts `builds_on | improves_on | uses_method`.

## 4. Proposed new tags

Append to `tags` in `data/seed/tags.json`. Exact shape (`id`, `facet`, `label`, optional `parent`, optional `aliases`). Parents must exist: `concept/consistent-hashing` and `venue/sosp` are both in this list, so add parents before children.

```json
[
  {
    "id": "area/distributed-systems",
    "facet": "area",
    "label": "Distributed systems",
    "aliases": [
      "distributed computing"
    ]
  },
  {
    "id": "area/databases",
    "facet": "area",
    "label": "Databases",
    "aliases": [
      "data stores",
      "storage systems"
    ]
  },
  {
    "id": "concept/key-value-store",
    "facet": "concept",
    "label": "Key-value stores",
    "aliases": [
      "key value store",
      "kv store"
    ]
  },
  {
    "id": "concept/consistent-hashing",
    "facet": "concept",
    "label": "Consistent hashing"
  },
  {
    "id": "concept/virtual-nodes",
    "facet": "concept",
    "label": "Virtual nodes",
    "parent": "concept/consistent-hashing",
    "aliases": [
      "vnodes",
      "tokens"
    ]
  },
  {
    "id": "concept/vector-clocks",
    "facet": "concept",
    "label": "Vector clocks",
    "aliases": [
      "version vectors"
    ]
  },
  {
    "id": "concept/eventual-consistency",
    "facet": "concept",
    "label": "Eventual consistency"
  },
  {
    "id": "concept/high-availability",
    "facet": "concept",
    "label": "High availability",
    "aliases": [
      "always-on",
      "uptime"
    ]
  },
  {
    "id": "concept/replication",
    "facet": "concept",
    "label": "Replication",
    "aliases": [
      "replicas",
      "copies"
    ]
  },
  {
    "id": "concept/quorum",
    "facet": "concept",
    "label": "Quorums",
    "aliases": [
      "sloppy quorum",
      "read quorum",
      "write quorum"
    ]
  },
  {
    "id": "concept/hinted-handoff",
    "facet": "concept",
    "label": "Hinted handoff"
  },
  {
    "id": "concept/merkle-tree",
    "facet": "concept",
    "label": "Merkle trees",
    "aliases": [
      "hash tree",
      "anti-entropy"
    ]
  },
  {
    "id": "concept/gossip-protocol",
    "facet": "concept",
    "label": "Gossip protocols",
    "aliases": [
      "gossip"
    ]
  },
  {
    "id": "concept/conflict-resolution",
    "facet": "concept",
    "label": "Conflict resolution",
    "aliases": [
      "reconciliation",
      "last write wins"
    ]
  },
  {
    "id": "concept/tail-latency",
    "facet": "concept",
    "label": "Tail latency",
    "aliases": [
      "99.9th percentile",
      "percentile latency"
    ]
  },
  {
    "id": "concept/service-level-agreement",
    "facet": "concept",
    "label": "Service level agreements",
    "aliases": [
      "SLA"
    ]
  },
  {
    "id": "technique/dynamo",
    "facet": "technique",
    "label": "Dynamo"
  },
  {
    "id": "use/shopping-carts",
    "facet": "use",
    "label": "Shopping carts",
    "aliases": [
      "online shopping carts"
    ]
  },
  {
    "id": "use/session-storage",
    "facet": "use",
    "label": "Session storage",
    "aliases": [
      "session state"
    ]
  },
  {
    "id": "organization/amazon",
    "facet": "organization",
    "label": "Amazon",
    "aliases": [
      "Amazon.com"
    ]
  },
  {
    "id": "venue/sosp",
    "facet": "venue",
    "label": "SOSP",
    "aliases": [
      "Symposium on Operating Systems Principles"
    ]
  },
  {
    "id": "venue/sosp-2007",
    "facet": "venue",
    "label": "SOSP 2007",
    "parent": "venue/sosp"
  },
  {
    "id": "author/giuseppe-decandia",
    "facet": "author",
    "label": "Giuseppe DeCandia"
  },
  {
    "id": "author/deniz-hastorun",
    "facet": "author",
    "label": "Deniz Hastorun"
  },
  {
    "id": "author/madan-jampani",
    "facet": "author",
    "label": "Madan Jampani"
  },
  {
    "id": "author/gunavardhan-kakulapati",
    "facet": "author",
    "label": "Gunavardhan Kakulapati"
  },
  {
    "id": "author/avinash-lakshman",
    "facet": "author",
    "label": "Avinash Lakshman"
  },
  {
    "id": "author/alex-pilchin",
    "facet": "author",
    "label": "Alex Pilchin"
  },
  {
    "id": "author/swaminathan-sivasubramanian",
    "facet": "author",
    "label": "Swaminathan Sivasubramanian"
  },
  {
    "id": "author/peter-vosshall",
    "facet": "author",
    "label": "Peter Vosshall"
  },
  {
    "id": "author/werner-vogels",
    "facet": "author",
    "label": "Werner Vogels"
  },
  {
    "id": "everyday/online-shopping",
    "facet": "everyday",
    "label": "Online shopping"
  },
  {
    "id": "everyday/keeping-copies-safe",
    "facet": "everyday",
    "label": "Keeping copies safe",
    "aliases": [
      "backups"
    ]
  },
  {
    "id": "everyday/neighbors",
    "facet": "everyday",
    "label": "Neighbors and mail"
  }
]
```

Facets used exist already (`area`, `concept`, `technique`, `use`, `organization`, `venue`, `author`, `everyday`). No `impact` tags are proposed, because the paper makes no claim about what Dynamo led to.
