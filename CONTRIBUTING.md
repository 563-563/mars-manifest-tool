# Contributing

This project's value is its discipline. The engines are simple; what makes the
tool worth trusting is that **every number traces to a source and every claim
survives a test**. Contributions are welcome — these are the rules that keep
it honest.

## The hierarchy of truth (highest wins)

1. **Verified external data.** The baseline always carries the best-verified
   number. Never keep a known-stale value and downgrade its confidence tier —
   when a source drifts, change the seed and let consequences propagate.
2. **Input data** (`inputs/` — split into program / assumptions / city /
   requirements / catalog; see `inputs/README.md`) — the catalog is the source
   of truth for component attributes; assumptions are injected, never
   hard-coded in engines.
3. **Engines** (`mars_manifest/`) — pure, deterministic, tested. Reports only
   render; no computation in the report layer.
4. **Generated documents** (`docs/REQUIREMENTS.md`, xlsx reports) —
   regenerate, never hand-edit.

## Changing a number

- Every input carries a confidence tier in `PROVENANCE.md`:
  **A** physical constant · **B** published spec/measurement ·
  **C** stated derivation from published figures · **D** notional estimate.
- To change a data value you need a **verifiable source** and a PROVENANCE
  entry (tier, link, and what the change does downstream). PRs that change
  seed values without a provenance entry will be asked to add one.
- Musk aspirational figures are documented precedent for *failing*
  verification (see PROVENANCE §8 and `docs/CITY_RAMP_RESEARCH.md` §4). They
  may be cited as aspirations, never used as load-bearing anchors.

## The regression contract

`tests/` pins two different things — don't confuse them:

- **Workbook-port fixtures** (`examples/precursor_2026*.yaml`,
  `campaign_4window.yaml`; target numbers originally recorded in HANDOFF.md
  §7): deliberately frozen
  historical inputs that verify the original workbook math was ported
  correctly. Do not "update" these to current data — that's the point of them.
- **Live-baseline tests** (program plan, ISRU chain, gates, loss tolerance,
  requirements): these assert current behavior and MUST move when verified
  data moves.

`pytest -q` must be green before any commit. If you change the program plan,
regenerate `docs/REQUIREMENTS.md` (`mars requirements inputs/program.json
--out docs/REQUIREMENTS.md`) in the same PR.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     POSIX: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Where to start

- `README.md` — CLI tour and document map.
- `HANDOFF.md` — the original spec (HISTORICAL; read for intent, not values).
- `CLAUDE.md` — the working agreement this file summarizes.
- `PROVENANCE.md` — every input, its source, its tier, and the verification log.
- Open questions and the forward roadmap live in `docs/CITY_RAMP_RESEARCH.md` §7.
