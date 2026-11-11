# Einstein 1905 special-relativity story — intake draft

**Status:** editorial intake; not a published story and not approved for live release.

## Source identity

- Albert Einstein, “Zur Elektrodynamik bewegter Körper” / “On the Electrodynamics of Moving Bodies.”
- Annalen der Physik 17 (1905), 891–921. The original-paper DOI is <https://doi.org/10.1002/andp.19053221004>; Wiley also exposes a later republication record at <https://doi.org/10.1002/andp.2005517S113>.
- Accessible English text: <https://fourmilab.ch/etexts/einstein/specrel/www/>. This is a 1923 translation of the 1905 German paper; the edition notes changed notation and later corrections. Treat it as a translation, not the original wording. Its section anchors are `#SECTION11` (I.1), `#SECTION12` (I.2), `#SECTION13` (I.3), `#SECTION14` (I.4), and `#SECTION15` (I.5).
- Trust: `journal_published`, not `peer_reviewed`. Historical accounts state the 1905 Annalen papers were accepted without external peer review. The paper is theoretical, so its claims below are `model_design`, not measurements.
- Scope guard: this is special relativity applied to electrodynamics and uniformly moving coordinate systems. Do not say it is general relativity, a theory of gravity, or the source of `E=mc²`.

## Story direction

**Working headline:** When clocks disagree, whose time is it?

**Accent:** Einstein’s 1905 puzzle

**Working dek:** A clock tells you when something happens beside it. But how can two far-away clocks agree? Einstein used light signals to build a rule—and found that moving observers can disagree about which far-apart events happened at the same time.

**Hook question:** Can two careful observers both be right about what happened at the same time?

**One-line takeaway:** In Einstein’s model, time and distance measurements depend on the motion of the measuring system, while each inertial system measures light in empty space at the same speed.

**Desk/field:** Physics / space and time; existing database field `physics`.

## Four-chapter arc

1. **The magnet and the wire.** The paper opens with a puzzle: the same relative motion can produce the same current, though the old account describes a moving magnet and a moving wire differently. Einstein asks whether the laws need a special “absolute rest” frame.
2. **How do distant clocks agree?** A clock can tell time where it sits. For far-apart events, Einstein defines how separated clocks can be synchronized using a light signal that travels out and back.
3. **Same time depends on the frame.** Starting with the relativity principle and constant light speed, Einstein derives how coordinates and time relate between uniformly moving systems. The paper says events simultaneous in one system need not be simultaneous in another.
4. **Light keeps its speed.** The transformation also changes how lengths, moving clocks, and combined velocities are described. Close on the surprising rule: combining two sub-light speeds still does not produce a speed greater than light.

## Candidate evidence cards

All cards below are derivations or definitions from the paper (`model_design`), not experimental measurements.

| Candidate card | Source location | Wording constraint |
|---|---|---|
| **Two principles** — the same physical laws apply in uniformly moving systems; light in empty space has a fixed speed independent of the emitter’s motion. | Introduction, paragraph beginning “They suggest rather…”; stable URL: base paper link. | These are postulates the paper adopts, not new measurements. |
| **One clock rule** — Einstein defines distant clocks as synchronized when the light signal’s outward and return travel times match. | §1, “Definition of Simultaneity”; [`#SECTION11`](https://fourmilab.ch/etexts/einstein/specrel/www/#SECTION11). | This is his operational definition; do not claim the translation settles modern discussions of synchronization conventions. |
| **One surprising consequence** — events simultaneous in one coordinate system need not be simultaneous in a system moving relative to it. | §1 and §2; [`#SECTION11`](https://fourmilab.ch/etexts/einstein/specrel/www/#SECTION11) and [`#SECTION12`](https://fourmilab.ch/etexts/einstein/specrel/www/#SECTION12). | Keep the claim about coordinate systems and distant events; avoid saying people “see time differently.” |
| **One transformation** — the paper derives equations connecting position and time in uniformly moving systems. | §3, “Theory of the Transformation…”; [`#SECTION13`](https://fourmilab.ch/etexts/einstein/specrel/www/#SECTION13). | Calling these the Lorentz transformation is explanatory naming; historical attribution needs a separate source. |
| **One speed rule** — §5 derives a composition rule under which combining speeds below `c` does not produce a result above `c`. | §5, “The Composition of Velocities”; [`#SECTION15`](https://fourmilab.ch/etexts/einstein/specrel/www/#SECTION15). | Do not use the equation from the 1923 translation until checked against the German original; that edition notes a translation error in the equation. |

## Attribution and content cautions

- Do not attribute the train-and-lightning thought experiment to this paper. The paper uses clocks, light signals, rods, and a train-arrival example for a local clock reading; the well-known lightning-at-both-ends train scene is not in this text.
- Do not put “Einstein proved time is an illusion” or imply a person’s awareness changes reality. The paper discusses measurements made in coordinate systems equipped with clocks and rulers.
- Avoid claiming the paper reports an experiment. It is a theoretical argument and derivation.
- Don’t state that Einstein created relativity from nothing. Keep historical-credit claims within what the paper and authoritative history sources establish.
- The English text is a 1923 translation. Use the original German publication record for bibliographic metadata and be cautious with close quotations or wording about clock synchronization.

## Tag and graph notes

- Existing approved broad tags confirmed so far: `field/physics`, `area/physics`.
- No approved relativity-specific tag was found in the seed vocabulary. Do not add one or tag it as approved without the owner’s vocabulary decision.
- The seed contains a separate Einstein 1915 general-relativity node. Do not reuse it as this 1905 story or imply a verified relation between the papers.
- No graph relation is proposed in this intake.

## Visual checkpoint

No production media has been created. A private two-option design board is ready for the owner to choose: [Geeky Times 1905 Artwork Board](https://claude.ai/artifact/G2q4ordMMPrrSgUHaepTNA). Option A uses the magnet-and-wire opening puzzle; Option B shows the out-and-back light synchronization rule. The board was revised to remove the unsupported bulb-brightness analogy and to show the return light signal. Build the chosen direction into lead, chapter and comic SVGs only after the owner picks it.
