# Local LLM agentic scenario (Phase 2)

Status: **designed, not yet built. Stretch goal — see working agreement #1
and the Phase 2 go/no-go rule in [../ROADMAP.md](../ROADMAP.md).**

## Goal

A genuinely non-deterministic scenario: one local LLM plays attacker
(chooses and executes actions via tool-calling against a constrained
toolset), a second plays defender/analyst (interprets alerts, responds),
both running fully offline via Ollama on the M4/48GB laptop.

## Why constrained, not open-ended

An unconstrained agent (free-form shell access, arbitrary tool choice) is
both a reliability risk for a live demo and unnecessary — the useful
signal for the audience is "the model chose this specific ATT&CK-mapped
technique," not "the model has root." Constrain the attacker's tool
surface to a fixed menu of scripted-but-parameterized actions (e.g. "attempt
SQLi against endpoint X with payload Y" as a callable tool, not raw shell
exec), mirroring how Caldera structures its ability library — see
[../context/tech-stack-research.md](../context/tech-stack-research.md).

## Model selection — not pinned yet

Per working agreement #7: don't commit to a specific model name from
research. Start from these *classes* and pick via a real memory/latency
check on the actual machine:

- Attacker/defender agent loop: a 7-14B-class tool-calling-capable model
  (e.g. try Llama 3.x or Qwen2.5/3 in that size range as starting points).
- Narration/commentary (if kept separate from the agent loop): a ~3B-class
  model, run concurrently.
- Budget check: both models resident simultaneously, plus the Wazuh stack
  (~6GB) and the rest of the demo infra, must fit comfortably under 48GB
  with real headroom — verify actual resident memory via `ollama ps` /
  Activity Monitor during a real run, not just parameter-count math.

## Reliability bar before this is ever presented live

Per the Phase 2 go/no-go rule in [../ROADMAP.md](../ROADMAP.md): **3
consecutive clean rehearsal runs with zero manual intervention**, on the
actual demo laptop, fully offline. If it doesn't hit that bar, Scenario 1
(scripted) is what gets presented — that's an acceptable, planned outcome,
not a failure state.

## Event stream + legal overlay

Same shared event shape as every other scenario (see
[architecture.md](architecture.md)) — the agent loop must emit
`attack_technique_id` / `legal_ref` per action it takes, meaning the
constrained tool menu should be defined with these tags attached to each
tool, not inferred after the fact.

## Open design questions (resolve if/when Phase 2 build actually starts)

- Does the defender model get the same constrained-tool treatment, or is it
  allowed more open-ended reasoning since it's not taking destructive
  action?
- How much of the agent's reasoning (chain-of-thought-style output) gets
  shown to the audience vs. just its chosen actions — showing some
  reasoning is likely more interesting for the cybersecurity track, but
  needs a legibility pass for a projector.
- Fallback behavior if a rehearsal run stalls mid-scenario (timeout →
  auto-abort to a "the AI got stuck, here's what real red-team engagements
  actually look like" narration beat, rather than dead air).
