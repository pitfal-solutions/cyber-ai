# Talk-track — legal reference + (superseded) slide script

> **Status (2026-08-29):** the deck was restructured into two parts —
> *"Attack, Autonomy & Accountability"* (Part I: human-directed / TeamPCP;
> Part II: autonomous agents, with the legal + policy material folded in).
> The **slide-by-slide script below predates that restructure** — the
> authoritative, current speaker notes now live *inside the deck* (press
> `N`). What remains fully valid and worth keeping here is the **Legal
> Reference Pack** further down (statutes, sentencing ranges, the five
> anchor cases, and the demo-step → law → case cheat sheet), which still
> matches the deck and the dashboard `legal-map.json` files.

---

## (Superseded) original three-act script — "Who Goes to Prison When the AI Did It?"

**Runtime:** 45 min · **Room:** dual-track (cybersecurity + criminal justice)
**Deliverable after approval:** HTML click-through deck + presenter run-sheet
**Speaker framing:** programmer (12 yrs) → intel analyst, narcotics/cybercrime → national-security sector (employer stays vague)

Alt titles: "No Cat, No Culprit" · "The Attribution Ladder"

Time budget: Cold open 3.5 · Act 1 ~13 · Act 2 ~19 · Act 3 ~7 · buffer/Q&A ~2.5

---

## COLD OPEN (~3.5 min)

### SLIDE 0 — "Caught by their own data" [REMOVABLE — personal hook] (~60s)
- **On screen:** a blurred phone photo + a map pin. No employer, no unit name.
- **Say:** First person, de-identified. In the narcotics/cybercrime world, the people we caught rarely got caught by brilliant detective work. They got caught because they *leaked themselves* — e.g., dealers photographing product with GPS quietly baked into the image's EXIF. (Real pattern: 229 dealers deanonymized off un-stripped photo metadata.)
- **Land line:** "Nobody outsmarted them. They handed us the evidence — because they're human."
- **Isolation note:** self-contained. If cut, open on Slide 1; the theme still lands.

### SLIDE 1 — The cat (TeamPCP) (~90s)
- **On screen:** the cat avatar → arrow chain (handle → Steam → TikTok → real name → Perth).
- **Say:** TeamPCP / UNC6780 — prolific software-supply-chain attacker. Undone by a **reused cat avatar**: same picture on a Steam profile linked from TikTok, matching the avatar fronting their Telegram. Thread by thread → real identity → **two arrested in Australia this month (Aug 2026).**
- **Land line:** Same lesson, bigger stage. Sophisticated attacker, caught by ego and reuse — by being human.

### SLIDE 2 — The pivot / title (~45s)
- **Say:** "Catching attackers is really *attribution*, and attribution runs on human mistakes. So here's tonight's question:"
- **On screen (title card):** **WHO GOES TO PRISON WHEN THE AI DID IT?**
- **Say:** "We'll answer it by watching two crimes. The first one, I commit — and you'll see exactly how I'd get caught and charged. The second, no human commits at all. Then you decide."

---

## ACT 1 — The human in the chair (you) (~13 min)

**Thesis of the act:** for a human attacker we have BOTH halves — the *crime* (statutes) and the *culprit* (attribution). Someone goes to prison. This is the easy case.

### SLIDE 3 — "I'm the hacker" setup (~1 min)
- **Say:** Fully isolated lab, offline, a deliberately-vulnerable practice app (OWASP Juice Shop). Everything you see is a real request against a real running app — no theater. The dashboard shows two synchronized views: **left = the technique (MITRE ATT&CK); right = the law it breaks (real statute + penalty).** Cyber folks watch the left, CJ folks watch the right.

### SLIDE 4 — LIVE DEMO: scripted web-exploit (~6–7 min)
- **Cue:** run `./run.sh web-exploit`, then `./scenarios/web-exploit/run-attack.sh`. Narrate each beat as it lands (charge cited per step — full detail in the Legal Reference Pack):
  1. **Recon** — T1595. "Casing the building." No charge yet.
  2. **Exposed confidential file** (`/ftp/acquisitions.md`) — T1213. Fed **§1030(a)(2)** / Colo. **§18-5.5-102** — *but flagged as the chain's weakest case on purpose*: no control was defeated because there wasn't one (the **weev / *Auernheimer*** problem). **Plant the seed** — we come back to this in the debate.
  3. **SQLi login bypass** — T1190. Logged in as admin with no password. Fed **§1030(a)(2)**, Colo. **§18-5.5-102**. This is a classic "**gate** defeated" — squarely inside CFAA even after *Van Buren*.
  4. **Broken access control** — enumerate other users' records. Fed **§1030(a)(2)**, Colo. **§18-5.5-102**. ***Van Buren* controls**: these were off-limits files/areas, so it's a CFAA violation even under the narrowed rule.
  5. **Account takeover** — guessable security question resets a real user's password. **Identity theft**: Fed **§1028A** (mandatory **+2 yrs, consecutive**), Colo. **§18-5-902** (**class 4 felony, 2–6 yrs**). Note *Flores-Figueroa*: §1028A needs proof you *knew* it was a real person's identity — easy here (you targeted a named user), the crux later when an AI picks the victim.
- **Detector fires live** — a separate piece of code that never saw the attack script catches it off real traffic. "This is the evidence trail."
- **Fallback:** if anything hangs, `reset.sh` + narrate from the recorded run.

### SLIDE 5 — "So how do *I* get caught?" (attribution) (~3 min)
- **Say:** The exploit is only half a case. The other half is *me*. Same lesson as the cold open — humans leak themselves:
  - TeamPCP: reused avatar/handle → identity.
  - Ochoa / "w0rmer" (CabinCr3w): posted a taunt photo of his girlfriend; the iPhone's EXIF GPS pinned the location → FBI arrest.
- **On screen:** the attribution ladder — alias → reuse → metadata → real name → cuffs.

### SLIDE 6 — The full case against me (~2.5 min)
- **On screen:** two columns — **the crime** (the statutes that lit up in the demo) and **the culprit** (the attribution ladder).
- **Concrete stack against "me" (say the numbers out loud — they land):** federal CFAA up to **5 years** (the SQLi/enum steps were for private gain / in furtherance of the takeover), **plus a mandatory consecutive 2 years** for aggravated identity theft under §1028A, **plus** Colorado's own **class 4 felony** identity-theft charge (2–6 yrs) — state and federal can both prosecute. And the breached org now owes **30-day breach notice** under §6-1-716.
- **Say:** For a human we have both halves. Mens rea is easy — *I* chose every step, *I* knew Jim was a real person. Prosecutors can name the defendant and stack the charges. Someone goes to prison. Hold onto how clean this is.

---

## ACT 2 — Pull the human out (~19 min)

**Thesis of the act:** the same crime happens with no human choosing it — and every rung of the ladder we just used disappears.

### SLIDE 7 — Setup: same crime, no hands on keys (~1.5 min)
- **Say:** Now two local AI models — one attacker, one defender — fight over a small real network. Real tools (nmap, hydra, smbclient), real hosts, real detection. I am not choosing the exploit path; the model is.

### SLIDE 8 — LIVE DEMO: AI vs AI (network-intrusion hero) (~6 min)
- **Cue:** `./run.sh network-intrusion` → `./run-network-intrusion.sh`. Narrate: sweep → find hosts → brute SSH / trigger the vsftpd backdoor / anonymous SMB → **the attacker writes a real "ATTACKER WON" marker to disk** and reads it back. Defender earns a block off real alerts; whether it lands is an on-screen, labeled coin flip (honest: shown as chance, not dressed up as a technical result).
- **Freeze** at the marker-write. "A real intrusion just happened. Real data read, real file written. Now —"
- **Fallback:** freeze on the agentic Juice Shop run, or the recorded clean run.

### SLIDE 9 — THE QUESTION (~1 min)
- **On screen:** **Same crime. Who do you charge?**
- **Say:** The AI has no ego. No reused cat avatar. No girlfriend's photo. No EXIF. **The entire ladder we climbed in Act 1 has no rungs.** So who's on the hook?

### SLIDE 10 — The lineup (facilitated debate) (~7 min)
- **On screen:** four suspects — **Developer → Deployer → Operator → End-user** — plus "the AI itself?" and "the state that sheltered it."
- **Run it as a real discussion.** Prompts for the room:
  - Can the AI be a defendant? (No prosecutable mens rea — dead end. Why the law needs a *human's* intent.)
  - Whose intent counts — the person who typed the goal, or the one who built/deployed the tool?
  - Does "it acted autonomously" get anyone off the hook?
- **Scaffolding to reveal as they argue — four real cases, each doing one job (CJ track carries this; full cites in the Reference Pack):**
  - **Autonomy anchor — *United States v. Morris*, 928 F.2d 504 (2d Cir. 1991):** first CFAA conviction (the Morris Worm). Held the government need only prove intent to **access** — not intent to cause the **damage** that followed. → The human who *launches* autonomous code is liable for the access even when the program runs past what he intended. Direct ammunition for "the deployer is on the hook."
  - **Authorization line — *Van Buren v. United States*, 141 S. Ct. 1648 (2021):** "exceeds authorized access" reaches only the files/areas that are off-limits to you (the "gates-up-or-down" test). → What is an AI agent ever "authorized" to reach? The whole fight moves to *scope*.
  - **Mens rea crux — *Flores-Figueroa v. United States*, 556 U.S. 646 (2009):** aggravated ID theft requires proof the defendant *knew* the identity was a real person's. → If the **AI** chose the victim, which human "knew"? The §1028A stack from Act 1 may not attach at all.
  - **The escape hatch, closed — *Global-Tech v. SEB*, 563 U.S. 754 (2011):** willful blindness = subjectively believing a fact is highly probable and deliberately avoiding confirming it. → A developer/deployer who ignored a known attack risk can't hide behind "I didn't know."
  - **Statutory backstops now forming:** **California** — can't dodge liability *solely* because the AI "acted autonomously"; **June 2, 2026 EO** — directs prosecutors to apply CFAA to intrusion "carried out with AI."
- **Callback:** the Act-1 exposed-file step we flagged — was that even "unauthorized access"? (weev / *Auernheimer*, vacated on venue, merits never resolved.) Now imagine an **AI** wandering into it with no human intent behind the click. CJ students argue prosecution vs. defense.

### SLIDE 11 — The real-world data point: GTG-1002 (~2.5 min)
- **Say:** This isn't hypothetical. Nov 2025: the first reported AI-orchestrated espionage campaign — a state group jailbroke Claude Code into running ~80–90% of an operation against ~30 targets. The current answer: **charge the humans who jailbroke it.** But note what that requires — findable humans, inside a reachable jurisdiction. Take either away and the ladder's gone again.
- **On screen:** honest bar — *there is no settled case law that cleanly resolves the no-human case yet. That's the point.*

---

## ACT 3 — The state's answer: privateers (~7 min)

### SLIDE 12 — If you can't always catch them… (~2 min)
- **Say:** So what does a government do when attribution and liability get this hard, and the worst actors sit where your subpoena can't? One answer landed **Aug 12, 2026.**

### SLIDE 13 — The hack-back memo (~3 min)
- **On screen:** NSPM "Expanding Capabilities to Combat Transnational Cyber-Enabled Crime."
- **Say:** For the first time, vetted **private** U.S. firms may run offensive "cyber effects" ops against foreign criminal orgs — DOJ/DHS sign-off per operation, $1M escrow forfeited for breaking the rules. Experts openly call it the cyber equivalent of **letters of marque** — the state licensing private force.
- **The legal inversion to name explicitly:** everything a private firm does under this memo — the SSH break-in, the backdoor shell, the data destruction you watched the AI do in Act 2 — is *exactly* the conduct CFAA §1030 makes a federal crime. The memo doesn't repeal §1030; it creates a **government-authorization carve-out** for vetted firms, per-operation DOJ/DHS sign-off, $1M escrow. That's the whole legal novelty: the same act is a felony or a licensed operation depending only on who blessed it.
- **Both tracks:** cyber — who's actually capable and trustworthy to do this? CJ — oversight, liability, collateral damage, and what happens when a licensed private strike hits the wrong box (and who's charged then).

### SLIDE 14 — Close: back to the cat (~2 min)
- **Say:** We started with a cat avatar and a metadata slip — humans caught because they can't stop being human. We end with attackers that have no cat to give them away, and a government handing offense to private hands because catching them the old way no longer scales.
- **Final line:** "Humans get caught by their humanity. AI doesn't have any — and that's the problem this whole field is now racing to solve. So: who *should* go to prison when the AI did it?"

### SLIDE 15 — Q&A / buffer (~2.5 min)

---

## Dual-track balance check
- **Cyber track** gets: real exploits, MITRE IDs, live detection, real tools, AI-vs-AI.
- **CJ track** gets: statutes per step, the attribution ladder, mens rea/willful-blindness/precedent, the privateering policy debate.
- Every act hands both tracks something to hold.

## Decision rule for the personal hook (Slide 0)
Keep it if you can land it in ~60s and it feels like *you*. Cut it the moment it needs setup or context to make sense — open cold on the cat, and Slide 5's Ochoa/EXIF beat still carries the "humans leak themselves" theme. Nothing else changes either way.

## Open items before build
- Confirm the ATT&CK IDs / statutes I list match the current dashboard `legal-map.json` (verified 2026-08-28 — they match; the dashboard's own `_note` still flags a final primary-source pass).
- Slide 11: keep the honest "Anthropic-authored report" framing on GTG-1002.

---

# LEGAL REFERENCE PACK
*Concrete data to speak from. Verified 2026-08-28 against the sources cited at the bottom. Two honesty caveats kept from the project's own bar: (a) exact fine caps for CO misdemeanors and the precise §6-1-716 notice-trigger wording rest on secondary sources — cite the jail/prison ranges confidently, hedge the dollar caps; (b) §1030(a)(5) is deliberately NOT asserted for the AI marker-write without a primary pass.*

## A. Federal statutes

**18 U.S.C. § 1030(a)(2) — CFAA, core charge.**
Elements: (1) intentionally accesses a computer, (2) without authorization or exceeding authorized access, (3) and thereby obtains information from a protected computer.
Penalty ladder (§1030(c)(2)): **misdemeanor, ≤1 year** baseline → **felony, ≤5 years** if the offense was **for commercial advantage or private financial gain**, **in furtherance of any criminal or tortious act**, OR **the value obtained exceeds $5,000** → **≤10 years** on a repeat offense.

**18 U.S.C. § 1030(a)(5) — the "damage" provision.** Knowingly causing transmission that intentionally damages a protected computer. This is what the Act-2 AI marker-*write* (altering the disk) would implicate. It has its own loss thresholds (generally ≥$5,000 aggregated harm). *We flag it, we don't assert it as charged* — no primary-source pass yet.

**18 U.S.C. § 1028A — Aggravated Identity Theft.** A **mandatory 2-year sentence, served consecutively** to the underlying felony — a judge cannot suspend it, reduce it, or run it concurrently. Requires (per *Flores-Figueroa*) that the defendant **knew** the identification belonged to a real person. (§ 1028 is the broader identity-fraud statute it sits on top of.)

**18 U.S.C. § 1343 — Wire Fraud** (backup / policy framing). ≤20 years; ≤30 if it affects a financial institution or federally declared disaster. The usual federal hook for phishing/extortion — useful in the hack-back discussion.

## B. Colorado statutes

**C.R.S. § 18-5.5-102 — Computer Crime.**
- Bare unauthorized access → **class 2 misdemeanor (≤120 days)**; **class 6 felony** on a prior conviction under this section.
- Value/loss tiers: **<$500** = class 2 misdemeanor · **$500–<$1,000** = **class 1 misdemeanor** · **$1,000–<$20,000** = **class 4 felony** · **$20,000+** = **class 3 felony**.
- Why it matters: Colorado prosecutes computer crime under *this*, far more often than the feds run a CFAA case. State and federal charges can both be brought.

**C.R.S. § 18-5-902 — Identity Theft.** **Class 4 felony** → **2–6 years** prison, **3 years mandatory parole**, fine **$2,000–$500,000**. Prison is **mandatory** on a qualifying prior.

**C.R.S. § 6-1-716 — Breach Notification** (civil duty on the *victim org*, not a charge on the attacker). Notify affected Colorado residents in the most expedient time possible and **no later than 30 days** after determining a breach occurred — among the strictest deadlines in the country. Notice to consumer reporting agencies if **>1,000** residents affected; AG notification duty also applies.

**Colorado sentencing quick-table (post-SB21-271, current 2026):**
| Class | Prison | Mand. parole | Fine |
|---|---|---|---|
| F3 | 4–12 yrs | 3 yrs | $3,000–$750,000 |
| F4 | 2–6 yrs | 3 yrs | $2,000–$500,000 |
| F5 | 1–3 yrs | 2 yrs | $1,000–$100,000 |
| F6 | 1–1.5 yrs | 1 yr | — |
| M1 | ≤364 days | — | — |
| M2 | ≤120 days | — | — |

## C. Case law (the five that carry the whole talk)

| Case | Cite | One-line holding | Where it fires in the talk |
|---|---|---|---|
| **United States v. Morris** | 928 F.2d 504 (2d Cir. 1991) | First CFAA conviction; government need only prove intent to **access**, not intent to cause the **damage** that followed. | Act 2 anchor — the human who launches autonomous code owns the access it makes. |
| **Van Buren v. United States** | 141 S. Ct. 1648 (2021) | "Exceeds authorized access" = reaching files/areas **off-limits** to you; not misusing data you may see ("gates-up-or-down"). | Act 1 Step 4 (clearly inside CFAA); Act 2 reframes it as "what is an AI authorized to reach?" |
| **Flores-Figueroa v. United States** | 556 U.S. 646 (2009) | §1028A "knowingly…of another person" requires the defendant **knew** the ID was a **real** person's. | Act 1 Step 5 (easy: you targeted Jim); Act 2 crux (who "knew" when the AI chose?). |
| **United States v. Auernheimer (weev)** | 748 F.3d 525 (3d Cir. 2014) | Conviction for scraping AT&T's exposed iPad emails via public URLs **vacated on venue** — merits never resolved. | Act 1 Step 2 + Act 2 callback — is an unprotected resource even "unauthorized"? |
| **Global-Tech Appliances v. SEB** | 563 U.S. 754 (2011) | Willful blindness = believing a fact highly probable **and** deliberately avoiding confirming it. | Act 2 — closes the developer/deployer "I didn't know it would attack" defense. |

## D. Demo step → law → case (the cheat sheet)
| Demo step | Federal | Colorado | Governing case |
|---|---|---|---|
| Exposed confidential file | §1030(a)(2) *(contested)* | §18-5.5-102 *(contested)* | *Auernheimer* (weev) |
| SQLi login bypass | §1030(a)(2) | §18-5.5-102 | *Van Buren* (a real gate defeated) |
| Broken-access enumeration | §1030(a)(2) | §18-5.5-102 | *Van Buren* (off-limits areas) |
| Account takeover | §1028 / §1028A (**+2 yrs**) | §18-5-902 (**F4**) | *Flores-Figueroa* |
| AI marker-write (Act 2) | §1030(a)(2); §1030(a)(5) *argued, not asserted* | §18-5.5-102 | *Morris* (intent-to-access) |
| Breach aftermath | — | §6-1-716 (30-day notice) | — |

## E. The AI-accountability answer, doctrinally (Act 2 close)
1. **You can't charge the AI** — no prosecutable mens rea. So you climb a ladder of humans: **user → operator → deployer → developer.**
2. **Morris** puts the *launcher* on the hook for the access, even past his intent.
3. **Flores-Figueroa** is the wall: "knowing" charges (like §1028A) need a *human* who knew the target was real — hard when the model chose it.
4. **Global-Tech** closes the "I didn't know it'd attack" exit if a known risk was ignored.
5. **Backstops still forming:** California's "autonomy is no defense" statute; the June 2, 2026 EO applying CFAA to AI-run intrusion.
6. **Real-world answer so far (GTG-1002):** charge the humans who directed/jailbroke it — which only works when such humans exist *and* sit in a reachable jurisdiction. Remove either and the ladder has no bottom rung. **That is the open question the room leaves with.**

## Sources (for your own confidence / the deck's footnotes)
- CFAA text & penalties: [18 U.S.C. §1030 (House OLRC)](https://uscode.house.gov/view.xhtml?req=%28title%3A18+section%3A1030+edition%3Aprelim%29); [USSC 2021 Computer Crimes Primer](https://www.ussc.gov/sites/default/files/pdf/training/primers/2021_Primer_Computer_Crimes.pdf)
- CO computer crime: [C.R.S. §18-5.5-102 (FindLaw)](https://codes.findlaw.com/co/title-18-criminal-code/co-rev-st-sect-18-5-5-102/)
- CO identity theft: [C.R.S. §18-5-902 (FindLaw)](https://codes.findlaw.com/co/title-18-criminal-code/co-rev-st-sect-18-5-902/)
- CO sentencing (post-SB21-271): [Colorado Sentencing Chart 2026](https://bacharach.law/colorado-sentencing-chart/); [C.R.S. §18-1.3-401](https://law.justia.com/codes/colorado/title-18/article-1-3/part-4/section-18-1-3-401)
- *Van Buren*: [Slip opinion (SCOTUS)](https://www.supremecourt.gov/opinions/20pdf/19-783_k53l.pdf)
- *Flores-Figueroa*: [556 U.S. 646 (Justia)](https://supreme.justia.com/cases/federal/us/556/646/)
- AI-liability framing: [Alston & Bird — rogue AI agent](https://www.alston.com/en/insights/publications/2026/07/autonomous-hacking-rogue-ai-agent-planning); [Security Boulevard](https://securityboulevard.com/2026/08/when-the-ai-goes-rogue-who-goes-to-jail-and-who-pays/)
- GTG-1002: [Anthropic report (PDF)](https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf); [MITRE C0062](https://attack.mitre.org/campaigns/C0062/)
- Aug 12 hack-back NSPM: [Help Net Security](https://www.helpnetsecurity.com/2026/08/13/usa-private-companies-offensive-cyber-operations/); [Federal News Network](https://federalnewsnetwork.com/cybersecurity/2026/08/trumps-move-to-unleash-private-sector-hackers-raises-novel-oversight-liability-questions/)
