# Glimpses — Open Technology Decisions & Working Notes

**What this file is:** the working space where technology decisions get made. Options, tradeoffs, and unresolved questions live here — the technology-phase counterpart of `PRD.md`.

**What this file is not:** the answer. Once a question is ruled, the decision moves to **`LOCKED_TECH_DECISIONS.md`** as a tight, reference-grade entry, and the concepts and reasoning behind it are written up in **`TECH_EXPLANATIONS.md`**. Read `LOCKED_TECH_DECISIONS.md` first if you want to know what Glimpses runs on; read `TECH_EXPLANATIONS.md` if you want to know why and how.

**How we work:** AI presents options with real tradeoffs — using named concrete scenarios and a scorecard, the same method that ruled all 100 product decisions — and the user rules. Nothing gets decided by default or by implementation drift. **Technology never re-rules product**: if an option here would make a `P-nn` awkward or expensive, that is surfaced as a product revision request, not resolved here.

**Status:** 0 ruled · 0 open *(register opened 2026-08-06)*

**Ids:** `T-nn`, stable and never reused or renumbered. A question closed without a technology choice attached (because product made it moot, or because it dissolved into another question) is marked **DISSOLVED**, not deleted.

---

## How to read the register

Each question has a stable `T-nn` id. Questions are grouped by the agenda area in `SESSION_HANDOFF.md`'s "The technology phase" table. The **Product inputs** column names which `P-nn` rulings constrain the answer — check these before proposing options, since they are not negotiable inputs to the decision, only the decision itself is open.

---

## Agenda area 1 — Runtime and language

*(No rows yet — first decision to be worked.)*

---

## Agenda area 2 — Ingestion orchestration

---

## Agenda area 3 — API shape

---

## Agenda area 4 — Data model

---

## Agenda area 5 — Rekognition collection lifecycle

---

## Agenda area 6 — Terraform state and naming

---

## Agenda area 7 — Observability, IAM granularity, CORS, secrets

---

## Agenda area 8 — Testing approach and CI/CD

---

## Decision log

| Date | `T-nn` | What happened |
|---|---|---|
