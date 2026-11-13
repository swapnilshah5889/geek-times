# Fact-check: "Cassandra at Twitter Today" (Twitter Engineering blog, 2010)

Source: Twitter Engineering blog post "Cassandra at Twitter Today". No author is printed on the archived page (no byline in raw.html); the story names none.
Date as printed: "Saturday, 10 July 2010". Venue: none (company blog).
Canonical URL: https://blog.twitter.com/engineering/en_us/a/2010/cassandra-at-twitter-today (live page redirects to blog.x.com and returns HTTP 403 to curl).
Fetched copy: http://web.archive.org/web/20231205014529/https://blog.twitter.com/engineering/en_us/a/2010/cassandra-at-twitter-today
Archive URL (in JSON, https form of the same capture): https://web.archive.org/web/20231205014529/https://blog.twitter.com/engineering/en_us/a/2010/cassandra-at-twitter-today
Extraction: HTML tags stripped to `source.txt` (1,831 characters). Short, but the text runs to the last paragraph, so it is complete, not blocked. The cookie banner was dropped.
Checked on 2026-11-12. Every quote below was matched against `source.txt`.

**Location convention.** The post has one heading and four body paragraphs: P1 "In the past year...", P2 "We're using Cassandra in production...", P3 "For now, we're not working on...", P4 "We're investing in Cassandra every day...". `raw.html` has no ids that mark the content (ids found: analytics-settings, component-wrapper, twBearerToken, twAuthenticationFlag, twGeoLocationRegion, u12, u12b), so no `#fragment` links are used; every link is the plain URL.

**Result key.** `pass` = the claim as worded is in the post. `weakened` = wording went past the post; fixed in the JSON. `scenario` = our invented picture or metaphor. `background` = not from the post.

**What is not in the post:** any number other than the date and "past year"; any speed test; any reason beyond "this isn't the time to make large scale migration"; any author name; any detail of how Cassandra is used (schema, cluster size).

## Trust level

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | `trust: company_reported`, organization "Twitter Engineering" | meta.md: "trust_suggestion: company_reported. Twitter Engineering blog post, so it is the company's own account of its decisions." venue_evidence: "none printed (company blog)". The organization name comes from the blog URL path and title, not from text in the post. **Owner decides; flagged.** | pass (owner to confirm) |
| 2 | Title and date 2010-07-10 | "Cassandra at Twitter Today"; "Saturday, 10 July 2010" | pass |

## Facts (`facts[]`, hook, summary, lead)

| # | Claim as we state it | Exact phrase in source | Location | Kind | Result |
|---|---|---|---|---|---|
| 3 | Fact "Not for tweets": for now not working on Cassandra as a store for tweets; calls it a change in strategy | "For now, we're not working on using Cassandra as a store for Tweets. This is a change in strategy." | P3 | model_design | pass |
| 4 | Fact "MySQL": will continue to maintain existing MySQL-based storage | "Instead we're going to continue to maintain our existing Mysql-based storage." | P3 | model_design | pass |
| 5 | Fact "3 uses": three examples | Post lists: geo team "store and query their database of places of interest"; research team "store the results of data mining"; analytics/operations/infrastructure teams "are working on a system that uses cassandra for large-scale real time analytics". Plain count of listed items = 3 ("A few examples:"). Old text said "use in production" for all three; the third is a system being worked on | P2 | model_design | weakened: now "Three examples the post lists: ..." |
| 6 | Fact "Every day": invests every day; use will only grow | "We're investing in Cassandra every day. It'll be with us for a long time and our usage of it will only grow." | P4 | model_design | pass |
| 7 | Fact source labels "Post · paragraph 3 / 2 / last paragraph" and links | Labels match P3, P2, P4. Links are the plain canonical URL | n/a | n/a | pass |
| 8 | Summary: used Cassandra in production for places, research and analytics | "We're using Cassandra in production for a bunch of things"; analytics is "working on a system" | P2 | n/a | weakened: now "in production for places and research, was building an analytics system on it" |
| 9 | Summary: would not move tweet storage "for now"; not the time for a large-scale migration; kept MySQL-based storage | P3 quotes above; "We believe that this isn't the time to make large scale migration to a new technology." | P3 | n/a | pass |
| 10 | Hook: sticker "Not for tweets!", teaser "Twitter used Cassandra. So why did it keep tweets on MySQL?", cta "Read the decision" | P2 (uses Cassandra), P3 (keeps MySQL-based storage, gives its reason). `readMinutes: 4` is an editorial estimate, not from the post | P2, P3 | n/a | pass |
| 11 | Lead headline "Why tweets stayed on MySQL." | P3 | P3 | n/a | pass |
| 12 | Lead deck: used Cassandra "for new jobs" but, for now, did not move tweet storage; not the time for a large-scale move | The post's geo and research uses are described as current, not new; "new projects" is only the future focus (P3) | P2, P3 | n/a | weakened: now "for other jobs" |
| 13 | Fig. 1 and Fig. 2 captions (tweets stay on the old shelf; team says it is not the time for a big move) | P3 | P3 | n/a | pass (picture is scenario) |
| 14 | Lead slide alt text and hook frame alts (shelves, moving box, "not now" sign) | Drawings | n/a | n/a | scenario |

## Story text and comic

| # | Claim as we state it | Exact phrase in source | Location | Provenance | Result |
|---|---|---|---|---|---|
| 15 | Ch.1 "In 2010 Twitter had been working with Cassandra for a year" | "In the past year, we've been working with the Apache Cassandra open source distributed database." | P1 | illustration | pass |
| 16 | Ch.1 work done in the open; lately less involved in the community; created misunderstandings | "Much of our work there has been out in the open"; "lately we've been less involved in the community because of more pressing concerns and have created some misunderstandings." | P1 | illustration | pass |
| 17 | Ch.1 "So it wrote this post to say where things stand." | The post states no purpose for itself | n/a | illustration | weakened: now "The post then says where things stand." |
| 18 | Ch.2 title "Use it for new jobs" | see row 12 | P2 | model_design | weakened: now "Use it for other jobs" |
| 19 | Ch.2 already uses Cassandra in production for a bunch of things; geo stores places of interest; research stores data-mining results; a third system for real-time analytics was being built | P2 quotes (rows 5, 8) | P2 | model_design | pass |
| 20 | Ch.3 not working on Cassandra as a store for tweets; "a change in strategy"; keep maintaining MySQL-based storage; reason: not the time for large-scale move to new technology | P3 quotes | P3 | model_design | pass |
| 21 | Ch.4 "short company post, so there are no speed tests or charts in it, and the reasons are the team's own" | Post has no figures or tests (meta.md key_numbers: none) | whole post | evidence | pass |
| 22 | Ch.4 Cassandra work goes to new projects that could not ship without a large-scale data store; use will grow | "We will focus our Cassandra work on new projects that we wouldn't be able to ship without a large-scale data store."; "our usage of it will only grow." | P3, P4 | evidence | pass |
| 23 | Ch.4 link "Read the post" | plain canonical URL | n/a | n/a | pass |
| 24 | Strip 1 title/panel 1: uses Cassandra in production for a bunch of things; three examples. grownUpWords "production use, geo data, data mining, real-time analytics" | "We're using Cassandra in production for a bunch of things"; the words geo, data mining, real time analytics all appear | P2 | illustration | pass |
| 25 | Strip 1 panel 2: geo team keeps places of interest; research team keeps data-mining results that feed things like @toptweets and local trends | "Those results then feed into things like @toptweets and local trends." | P2 | illustration | pass |
| 26 | Strip 1 panel 3: analytics, operations and infrastructure teams building a system on Cassandra for large-scale real-time analytics, inside and outside Twitter | "for use both internally and externally" | P2 | illustration | pass |
| 27 | Strip 2 panel 1: "A pile of tweets lives in an old, trusted store. The post says it is MySQL-based." | "old, trusted" is not in the post; "existing Mysql-based storage" is | P3 | illustration | weakened: now "in its existing store" |
| 28 | Strip 2 panel 2: "for now, no. It calls this a change in strategy." grownUpWords "MySQL, storage, migration" | P3 | P3 | illustration | pass |
| 29 | Strip 2 panel 3: team will continue to maintain its existing MySQL-based storage | P3 | P3 | illustration | pass |
| 30 | Strip 3 panel 1: "Moving everything is a big job, like moving a whole house." | Not in post | n/a | model_design | scenario (our metaphor, drawn as a house) |
| 31 | Strip 3 panel 2: team believes this isn't the time to make a large-scale migration to a new technology | "We believe that this isn't the time to make large scale migration to a new technology." | P3 | model_design | pass |
| 32 | Strip 3 panel 3: post gives no other reason and no test results | Only reason given is the sentence above; no tests | whole post | model_design | pass |
| 33 | Strip 4 panel 1: aims its Cassandra work at new projects. grownUpWords "new projects, large-scale data store" | "We will focus our Cassandra work on new projects" | P3 | model_design | pass |
| 34 | Strip 4 panel 2: projects it wouldn't be able to ship without a large-scale data store | "new projects that we wouldn't be able to ship without a large-scale data store" | P3 | model_design | pass |
| 35 | Strip 4 panel 3: invests every day; around a long time; use will only grow | P4 quote (row 6) | P4 | model_design | pass |
| 36 | Strip/chapter titles, kickers, howTo ("drawings are made up", "The post has no numbers or tests. It is the team's own account.") | No numbers other than date and "past year"; company's own account | n/a | n/a | pass |
| 37 | All drawings and alt texts (shelves, truck, house, plant, bridge) | Not claims | n/a | n/a | scenario |

Storyline honesty: the post does mention Cassandra by name throughout and says Twitter used it for non-tweet work and chose not to use it for tweets, so the story's angle (adopted for some jobs, not for tweets) is supported. The story does not say why MySQL is better, and does not claim Twitter left Cassandra: the post says "our usage of it will only grow".

## Paper-basis tags (spot-check)

All eight tags use `basis: paper` and the plain canonical URL as evidence (a blog has no fragments, so none is expected).

| Tag | Phrase | Result |
|---|---|---|
| `field/computer-science`, `area/distributed-systems` | "Apache Cassandra open source distributed database" (P1) | pass |
| `area/databases` | "distributed database"; "existing Mysql-based storage" | pass |
| `technique/cassandra` | "We're using Cassandra in production" (P2) | pass |
| `technique/mysql` (proposed) | "existing Mysql-based storage" (P3) | pass |
| `concept/data-migration` (proposed) | "large scale migration to a new technology" (P3) | pass |
| `use/real-time-analytics` (proposed) | "large-scale real time analytics" (P2) | pass (the system was being built) |
| `organization/twitter` (proposed) | "Cassandra at Twitter Today"; "at Twitter" (P2) | pass |

## Summary of results

Rows 1-37. Pass: 28. Weakened: 6 (rows 5, 8, 12, 17, 18, 27), all fixed in the JSON. Scenario: 3 (rows 14, 30, 37). Background: 0. Needs owner: trust row 1.
