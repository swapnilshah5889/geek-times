# Fact-check: "Attention Is All You Need" (Vaswani et al., 2017)

Source: Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin, "Attention Is All You Need", arXiv:1706.03762 (first submitted 12 Jun 2017; latest version v7, revised 2 Aug 2023). Venue: NeurIPS 2017 (peer-reviewed). The arXiv text does not print the venue; the venue line comes from the brief and the proceedings page was not fetched in this check.
Authors as listed on the arXiv abstract page (Vaswani and colleagues in the story).
Canonical HTML used: https://arxiv.org/html/1706.03762 (section anchors such as `#S3.SS2.SSS2`).
Archive: https://web.archive.org/web/20260929133934/https://arxiv.org/html/1706.03762 (capture 2026-09-29 13:39:34 UTC; opens with HTTP 200 and contains the paper text, checked 2026-11-05). The Wayback availability API returned 429 twice, so the capture was found from the `/web/2026/` redirect instead.
Fetched and checked on 2026-11-05. Quotes were matched against the arXiv HTML text (grep of the full article text). MathML repeats some tokens in the HTML (for example "N = 6 N=6"); quotes below drop the repeat.

**What is in the paper:** the Transformer's architecture (encoder and decoder stacks, attention, multi-head attention, feed-forward networks, embeddings, positional encoding), its training setup, and its translation results.
**What is not in the paper:** the "bat" scenario, the paint and comic metaphors, the made-up example sentences, the German "Fledermaus" etymology, and any claim about today's chatbots.

**Location convention.** Locations are arXiv anchor ids (`#S3.SS1` etc.) with the section number and heading. Abstract: `#abstract1`.

**Result key.** `pass` = the claim as worded is in the paper, or is a plain-language restatement of it. `weakened` = the wording as written goes beyond the paper; the Result column says whether the story text was fixed or left in place. `rejected` = not in the paper and not supported; the Result column says what was done.

## Facts and story text (`facts[]`, hook, summary, chapters)

| # | Claim as we would state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 1 | The reader has 6 layers; the writer has 6 layers (encoder and decoder) | "a stack of N = 6 identical layers" (encoder); "The decoder is also composed of a stack of N = 6 identical layers" | §3.1, `#S3.SS1` | model_design | pass |
| 2 | 8 attention heads (lookers) work side by side in each attention step | "we employ h = 8 parallel attention layers, or heads" | §3.2.2, `#S3.SS2.SSS2` | model_design | pass |
| 3 | One word's code is 512 numbers; the paper calls this d_model | "produce outputs of dimension d model = 512" | §3.1, `#S3.SS1` | model_design | pass |
| 4 | Seat numbers come from sine and cosine waves, added to each word's code | "we use sine and cosine functions of different frequencies"; "so that the two can be summed" | §3.5, `#S3.SS5` | model_design | pass |
| 5 | The base model trained for 12 hours on one machine with 8 P100 GPUs (100,000 steps) | "We trained the base models for a total of 100,000 steps or 12 hours."; "one machine with 8 NVIDIA P100 GPUs" | §5.2, `#S5.SS2` | measured_result | pass |
| 6 | The big model took 3.5 days | "The big models were trained for 300,000 steps (3.5 days)." | §5.2, `#S5.SS2` | measured_result | pass |
| 7 | Hook stat: "12 hours to train it" | Same source as row 5. "It" is ambiguous; the 12 hours is the base model, and the big model took 3.5 days | §5.2, `#S5.SS2` | measured_result | weakened: fixed in JSON to "to train the base model" |
| 8 | Summary: "It translated better, trained faster" | "improving over the existing best results, including ensembles, by over 2 BLEU"; "requiring significantly less time to train" | Abstract, `#abstract1` | measured_result | pass |
| 9 | Summary: "became the base of today's AI chatbots" | Not in the paper | n/a | background | pass as background only: tagged `impact/large-language-models` (basis background), never stamped as paper |
| 10 | Chapter 4: the researchers "compared machine translations with human ones" | The paper scores translations with BLEU; it does not describe a comparison with human translators | §6.1, `#S6.SS1` | measured_result | weakened: fixed in JSON to "scored their machine translations with a score called BLEU" |
| 11 | Chapter 4: the large Transformer beat the previous best by just over two points | "improving over the existing best results, including ensembles, by over 2 BLEU"; Table 2: ConvS2S Ensemble 26.36, Transformer (big) 28.4 | §6.1, `#S6.SS1` | measured_result | pass |
| 12 | BLEU "rewards matching words and groups of words" | Not stated; the paper cites BLEU and does not define it | n/a | background | pass as background only (standard definition; not a paper claim) |
| 13 | Chapter 1: older word-by-word readers pass the clue along, one step per word | "This inherently sequential nature precludes parallelization within training examples" | §1, `#S1` | model_design | pass |
| 14 | Chapter 2: each word can "hear" every other word in one step | "a self-attention layer connects all positions with a constant number of sequentially executed operations" | §4, `#S4` | model_design | pass |
| 15 | Chapter 2: "This is called self-attention" | "multi-head self-attention mechanism" | §3.1, `#S3.SS1` | model_design | pass |
| 16 | Chapter 3: the reader updates all English words together; the writer builds the translation one piece at a time | "we compute the attention function on a set of queries simultaneously"; "the decoder then generates an output sequence ... one element at a time" | §3.2.1, `#S3.SS2.SSS1`; §3 intro, `#S3` | model_design | pass |

## Comic strips (per panel; provenance and grown-up words)

Strip 1 "Every word gets a number code" (illustration), strip 2 "Bat asks around", strip 3 "Blend it in", strip 4 "Many lookers", strip 5 "Six floors", strip 6 "Write in order. No peeking."

| # | Claim as we would state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 17 | Strip 1, panel 1: "Computers can't read letters. They only understand numbers." | Not in the paper | n/a | background | weakened: general framing, not a paper claim; strip 1 stays illustration |
| 18 | Strip 1, panel 2: every word becomes "a long list of numbers: its code" | "we use learned embeddings to convert the input tokens and output tokens to vectors of dimension d model" | §3.4, `#S3.SS4` | model_design | pass |
| 19 | Strip 1, panel 2: "Words with similar meanings get similar codes." | Not stated in the paper (embeddings are learned; no similarity claim) | n/a | background | weakened: left in place; strip 1 stays illustration |
| 20 | Strip 1, panel 3: all words are read at the same time, so each gets a seat number | "Since our model contains no recurrence and no convolution ... we must inject some information about the relative or absolute position of the tokens in the sequence"; "we compute the attention function on a set of queries simultaneously" | §3.5, `#S3.SS5`; §3.2.1, `#S3.SS2.SSS1` | model_design | pass (paper's name: positional encoding) |
| 21 | Strip 1, panel 3: "The bat flew" would turn into "flew bat The" without seat numbers | Example sentence, not from the paper | n/a | scenario | pass as scenario |
| 22 | Strip 2, panel 1: "bat" has a puzzle, animal or stick | Invented example | n/a | scenario | pass as scenario (caption now says "In our made-up example") |
| 23 | Strip 2, panel 2: the question is a query; the name tags are keys | "mapping a query and a set of key-value pairs to an output" | §3.2, `#S3.SS2` | model_design | pass |
| 24 | Strip 2, panel 3: each key is matched to the query, then a softmax turns scores into weights | "We compute the dot products of the query with all keys, divide each by d k √, and apply a softmax function to obtain the weights on the values." | §3.2.1, `#S3.SS2.SSS1` | model_design | pass |
| 25 | Strip 2, panel 3: softmax shares always add up to 100% | Softmax definition; the paper names softmax and does not print this sentence | §3.2.1, `#S3.SS2.SSS1` | derivation | pass (a property of softmax) |
| 26 | Strip 2, panel 3: "flew" matches best | Invented example | n/a | scenario | pass as scenario |
| 27 | Strip 3, panel 1: each word carries a can of paint (its own meaning) | Metaphor | n/a | scenario | pass as scenario |
| 28 | Strip 3, panel 2: the bat mixes values using the match shares | "The output is computed as a weighted sum of the values" | §3.2, `#S3.SS2` | model_design | pass |
| 29 | Strip 3, panel 3: "bat" now has a bit of "flew" and knows it is "the animal with wings" | The paper says nothing about "bat" or what a word "knows" | n/a | scenario, stated as fact | weakened: left as written; strip 3 stays illustration (see strip gate) |
| 30 | Strip 4, panel 1: one looker can only hunt for one kind of clue at a time | "With a single attention head, averaging inhibits this." (this = joint attention to different subspaces) | §3.2.2, `#S3.SS2.SSS2` | model_design | pass (paraphrase) |
| 31 | Strip 4, panel 2: the machine uses 8 lookers at once | "we employ h = 8 parallel attention layers, or heads" | §3.2.2, `#S3.SS2.SSS2` | model_design | pass |
| 32 | Strip 4, panel 2: each head hunts for a different clue | "individual attention heads clearly learn to perform different tasks" | §4, `#S4` | measured_result | pass (the paper reports this from inspection) |
| 33 | Strip 4, panel 2: examples "who did it?" and "what happened?" | Invented examples | n/a | scenario | pass as scenario |
| 34 | Strip 4, panel 3: the 8 notes are glued together and projected again | "These are concatenated and once again projected" | §3.2.2, `#S3.SS2.SSS2` | model_design | pass |
| 35 | Strip 4, panel 3: "so no clue gets lost" | Not stated; the paper says multi-head attention lets the model attend to different subspaces jointly, not that nothing is lost | n/a | rationale | rejected: left in place (not removed); strip 4 stays illustration (see strip gate) |
| 36 | Strip 5, panel 1: the first sub-layer is multi-head self-attention | "The first is a multi-head self-attention mechanism" | §3.1, `#S3.SS1` | model_design | pass |
| 37 | Strip 5, panel 2: each word goes through a feed-forward network on its own | "applied to each position separately and identically" | §3.3, `#S3.SS3` | model_design | pass |
| 38 | Strip 5, panel 2: "polishing its code" | Metaphor | n/a | scenario | pass as scenario |
| 39 | Strip 5, panel 3: 6 floors for the reader (encoder), 6 for the writer (decoder) | "a stack of N = 6 identical layers" (encoder and decoder) | §3.1, `#S3.SS1` | model_design | pass |
| 40 | Strip 5, panel 3: "each floor makes the codes a little smarter" | Not stated in the paper; written as a plain fact | n/a | background | weakened: left in place; strip 5 stays illustration (see strip gate) |
| 41 | Strip 5 grown-up words: "a stack of 6 layers, each with self-attention and a feed-forward network" | True as far as it goes. The decoder's layers also have a third sub-layer: "the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack" | §3.1, `#S3.SS1` | model_design | pass (incomplete for the decoder; left as is) |
| 42 | Strip 6, panel 1: the writer can read the whole English sentence | "This allows every position in the decoder to attend over all positions in the input sequence." | §3.1, `#S3.SS1` | model_design | pass |
| 43 | Strip 6, panel 2: the writer writes one word at a time | "At each step the model is auto-regressive" | §3 intro, `#S3` | model_design | pass |
| 44 | Strip 6, panel 2: a cover hides the words still to come | "to prevent positions from attending to subsequent positions" | §3.1, `#S3.SS1`; masking detail in §3.2.3, `#S3.SS2.SSS3` | model_design | pass |
| 45 | Strip 6, panel 2: "like on a spelling test" | Metaphor | n/a | scenario | pass as scenario |
| 46 | Strip 6, panel 3: "Fledermaus means flutter-mouse" | Not in the paper (no German-word etymology). General knowledge; not checked against a dictionary in this run | n/a | background | weakened: left in place; strip 6 stays illustration (see strip gate) |
| 47 | Strip 6, panel 3: "Die Fledermaus flog" is German for "The bat flew" | Invented output for the example; the paper's English-to-German task is WMT 2014 | §5.1, `#S5.SS1` (task only) | scenario | pass as scenario |

**Counts (47 rows): 39 pass, 7 weakened, 1 rejected.** Weakened: rows 7, 10, 17, 19, 29, 40, 46. Rejected: row 35.

## Paper-basis tags (spot-check of `tags[]`)

All 18 distinct evidence anchors used in the story exist as ids in the arXiv HTML: `#abstract1`, `#S1`, `#S3`, `#S3.SS1`, `#S3.SS2`, `#S3.SS2.SSS1`, `#S3.SS2.SSS2`, `#S3.SS2.SSS3`, `#S3.SS3`, `#S3.SS4`, `#S3.SS5`, `#S4`, `#S5.SS1`, `#S5.SS2`, `#S5.SS3`, `#S5.SS4`, `#S6.SS1`, `#S6.SS3`. The author and organization tags point at the page root and are supported by the author and affiliation lines.

| Tag | Evidence anchor | Section and phrase | Result |
|---|---|---|---|
| `concept/scaled-dot-product-attention` | `#S3.SS2.SSS1` | "Scaled Dot-Product Attention"; "apply a softmax function to obtain the weights on the values" | pass |
| `concept/multi-head-attention` | `#S3.SS2.SSS2` | "Multi-Head Attention"; "h = 8 parallel attention layers, or heads" | pass |
| `concept/masked-attention` | `#S3.SS2.SSS3` | "We implement this inside of scaled dot-product attention by masking out" | pass |
| `concept/positional-encoding` | `#S3.SS5` | "Positional Encoding"; "we use sine and cosine functions" | pass |
| `technique/byte-pair-encoding` | `#S5.SS1` | "Sentences were encoded using byte-pair encoding" | pass |
| `technique/label-smoothing` | `#S5.SS4` | "we employed label smoothing of value ϵ = 0.1" | pass |
| `technique/dropout` | `#S5.SS4` | "Residual Dropout"; "For the base model, we use a rate of P drop = 0.1" | pass |
| `technique/beam-search` | `#S6.SS1` | "We used beam search with a beam size of 4" | pass |
| `technique/adam-optimizer` | `#S5.SS3` | "We used the Adam optimizer" | pass |
| `dataset/penn-treebank` | `#S6.SS3` | "on the Wall Street Journal (WSJ) portion of the Penn Treebank" | pass |
| `metric/f1` | `#S6.SS3` | Table 4, "WSJ 23 F1" | pass |
| `metric/bleu` | `#S6.SS1` | BLEU scores in Table 2 | pass |
| `concept/autoregressive-generation` | `#S3` | "At each step the model is auto-regressive" | pass (the sentence sits in the §3 intro, before §3.1, so `#S3` is the right anchor) |
| `concept/self-attention` | `#S4` | "a self-attention layer connects all positions with a constant number of sequentially executed operations" | pass |
| `task/constituency-parsing` | `#S6.SS3` | "English Constituency Parsing" | pass |
| `dataset/wmt-2014-en-de` | `#S5.SS1` | "We trained on the standard WMT 2014 English-German dataset" | pass |
| `dataset/wmt-2014-en-fr` | `#S5.SS1` | "the WMT 2014 English-French dataset consisting of 36M sentences" | pass |
| `concept/feed-forward-network` | `#S3.SS3` | "Position-wise Feed-Forward Networks" | pass |

## Strip gate (decision 47)

A strip reclassifies to `model_design` only when every ledger row for its paper-attributed claims is a pass, and no row is weakened or rejected. Strip 2 meets that. Strips 1, 3, 4, 5 and 6 each have a weakened or rejected row, so they stay `illustration` and the lead decides (see the report).

## Safe to use now

Facts 1 to 6 (the five `facts[]` rows and the 3.5 days figure); summary "translated better, trained faster" (row 8); chapter 4 "just over two points" (row 11); the paper's sections for multi-head attention (row 2 and row 31); strip 2 in full (rows 22 to 26); and the paper claims in strips 3 to 6 that are pass rows (rows 28, 30 to 34, 36, 37, 39, 42 to 44).
