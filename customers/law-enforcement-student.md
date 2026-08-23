# Law enforcement / criminal justice student

## Who they are

Studying law enforcement or criminal justice, not necessarily technical.
May have little to no background in networking, exploits, or how a "SQL
injection" actually works mechanically.

## What they want from this demo

- To follow **what happened** without needing to parse technical detail —
  "the attacker sent a crafted request that tricked the login into letting
  them in as someone else" is the right altitude, not the raw payload.
- To know **what crime just occurred**, in real legal terms: which statute,
  what the elements of the offense are, whether it's federal or state,
  misdemeanor or felony.
- To see the **evidentiary trail** — what the defense's alert/log actually
  captured, since that's the kind of artifact this track will deal with in
  their careers (what would investigators actually have to work with here).
- A real, cited penalty range — not a vague "this is illegal" statement.

## What loses them

- A demo that's 100% technical with the legal content bolted on as an
  afterthought slide at the end.
- Legal claims that sound authoritative but aren't cited to an actual
  statute — this audience is being trained to care about exactly that
  distinction.
- Jargon-dense narration with no plain-language translation.

## Design implication

The legal-overlay panel (see
[../specs/legal-overlay.md](../specs/legal-overlay.md)) needs to update in
sync with the attack timeline, in plain language, with a real statute
citation and evidentiary note per step — not a single legal summary shown
once at the end. See [../context/legal-framework.md](../context/legal-framework.md)
for the statutes this needs to cite, and working agreement #4 in
[../CLAUDE.md](../CLAUDE.md) for why nothing unverified reaches this panel.
