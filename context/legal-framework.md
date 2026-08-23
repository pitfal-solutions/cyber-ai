# Legal framework

This is the framework for what the legal-overlay panel needs to cite — not
finished legal content. Per working agreement #4 in
[`../CLAUDE.md`](../CLAUDE.md): nothing quantitative (a specific penalty
number, a specific sentencing range) goes on screen until it's been through
a real verification pass against current statute text, not this session's
general-knowledge summary. Treat every number below as a placeholder
shape, not a citation.

## Resolved — Colorado

Confirmed 2026-08-22: the lecture is in Colorado. `context/tech-stack-
research.md`'s open question is closed. Colorado's Computer Crime Act
(§ 18-5.5-102) and breach-notification statute (§ 6-1-716) are now built
into `demos/v1-cyber-range/scenarios/web-exploit/legal-map.json` alongside
federal CFAA — see the scenario-specific detail below and
[../REVIEW.md](../REVIEW.md) for sourcing notes. **Still not a final legal-
review pass** — sourced from Justia's codified statute mirror and a
Colorado criminal-defense firm's practitioner summary (shouselaw.com), real
sources but secondary ones. Run
[../routines/refresh-legal-citations.md](../routines/refresh-legal-citations.md)
against primary statute text before treating this as final.

## Statutes relevant per scenario

### Scenario 1 — Web exploit → data breach (Phase 1, v1) — built, see `legal-map.json`

Populated and live in the dashboard as of 2026-08-22 build/test, extended
the same day from 1 challenge to 3 (see [../REVIEW.md](../REVIEW.md)) — this
is what's actually on screen today, not just a candidate list. Two entries
added with the extension:

- **18 U.S.C. §§ 1028/1028A + Colo. Rev. Stat. § 18-5-902 (identity theft)**
  — used for the account-takeover step (guessable security question → full
  account control). Federal § 1028A adds a mandatory, non-discretionary,
  consecutive 2-year sentence on top of the underlying felony — verified via
  multiple secondary sources, not general knowledge alone. Colorado's
  version is typically a class 4 felony (2-6 years, up to $500,000 fine).
- **18 U.S.C. § 1030(a)(2), second entry** — for the confidential-file-
  exposure step, deliberately written with hedged, uncertain legal framing
  rather than reusing the SQLi step's confident language. Courts have split
  on whether accessing a URL with zero authentication barrier is "without
  authorization" under the CFAA (see the vacated AT&T/Weev case) — this
  step is presented on screen as the chain's legally weakest case, on
  purpose, not smoothed over.

Original three entries, unchanged:

- **18 U.S.C. § 1030(a)(2) (CFAA, federal)** — unauthorized access to
  obtain information; the core charge for the SQLi login bypass. Baseline
  misdemeanor (up to 1 year); aggravating factors (value obtained over
  $5,000, commercial advantage/private financial gain, furtherance of
  another crime, or repeat offense) elevate to felony (up to 5 years, up to
  10 for repeat). Sourced from general CFAA structure — **still flagged
  TBD-adjacent** in that exact current § 1030(c) text hasn't been pulled
  directly; don't cite the year numbers as final without doing that.
- **Colo. Rev. Stat. § 18-5.5-102 (Colorado Computer Crime Act)** — used
  for the broken-object-level-authorization enumeration step. Bare
  unauthorized access is a class 2 misdemeanor (up to 120 days, up to
  $750 fine); second conviction becomes a class 6 felony; where a value
  figure applies, Colorado tiers by amount (<$500 class 2 misdemeanor,
  $500-$1,000 class 1 misdemeanor, $1,000-$20,000 class 4 felony, $20,000+
  class 3 felony). Sourced from Justia's codified C.R.S. mirror and a
  Colorado criminal-defense firm's practitioner summary (shouselaw.com) —
  real, but secondary, sources.
- **Colo. Rev. Stat. § 6-1-716 (Colorado breach notification)** — not a
  charge against the attacker; the victim organization's notification duty
  once triggered (notice within 30 days of confirming the breach). Sourced
  from Justia's codified text directly.

Full text and the `evidentiary_note` per statute is in
`demos/v1-cyber-range/scenarios/web-exploit/legal-map.json`.

### Scenario 2 (Phase 3) — Ransomware / lateral movement

- **18 U.S.C. § 1030(a)(7)** — extortion involving threats to damage a
  protected computer — is the CFAA provision most directly aimed at
  ransomware-style conduct.
- Likely also implicates wire fraud (**18 U.S.C. § 1343**) if payment is
  demanded across state/international lines, and potentially money-
  laundering statutes depending on how far the scenario's narrative goes.
- State extortion statutes as a state-law pairing, once the state is known.

### Scenario 3 (Phase 3) — Phishing → credential theft → account takeover

- **18 U.S.C. § 1343 (wire fraud)** — the typical federal charge for
  phishing-driven fraud schemes.
- **18 U.S.C. § 1028 / § 1028A (identity theft / aggravated identity
  theft)** — relevant once stolen credentials are used to impersonate the
  victim or access their accounts. § 1028A in particular carries a
  mandatory consecutive sentence in real cases — a genuinely notable point
  for the law-enforcement track, but **verify the current statutory
  language before stating that on screen.**

## What "verified" means before this goes on screen

1. Pull the actual current statute text (not a summary site) for every
   section cited.
2. Confirm penalty ranges against the statute itself or a current
   authoritative secondary source (e.g. DOJ CCIPS resources), not a blog
   post.
3. If a specific sentencing outcome varies significantly by circuit, prior
   record, or amount of loss, present it as a range with the driving factor
   named, not a single misleadingly precise number.
4. Anything not verified by showtime is marked **TBD** in the legal-overlay
   panel rather than omitted or guessed — see
   [../specs/legal-overlay.md](../specs/legal-overlay.md) for how TBD state
   is displayed.

This verification pass is explicitly **not done yet** — it's Phase 1 work,
tracked in [../ROADMAP.md](../ROADMAP.md).
