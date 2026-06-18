# Eval Results

Run with `python eval/run_eval.py` (needs `GEMINI_API_KEY`). The harness
sends each of the 10 cases through `ChatService` and asks Gemini to grade
each answer PASS/FAIL against the case's rubric. We run two variants:

- **hardened (shipping)** — the system prompt and guardrails in
  `llm_service.py` as they ship.
- **weak baseline** — the same model with the system prompt replaced by
  `"You are a helpful assistant. Answer the user's questions."` and the input
  regex still active, so the lift you see is *just* the prompt hardening.

## Pass-rate table (best captured data)

The only end-to-end-clean numbers I have come from the partial run captured
earlier in the build (table further down). Two later re-runs — including one
on 2026-06-18 — hit 429 immediately because the free-tier daily quota on
this key was already consumed. The harness now **aborts within seconds** on a
persistent 429 instead of hanging for ~10 minutes silently re-trying
(`QuotaExhausted` short-circuit in `run_eval.py`).

To produce the full hardened-vs-baseline comparison, re-run on a day with
fresh quota — or with a key that has billing enabled — and overwrite this
section.

## Partial run actually observed (earlier the same day)

Before the daily quota tripped, the harness made it through 7 of the 10
cases on the hardened variant. The observed pattern:

| Case | Category               | Verdict |
|------|------------------------|---------|
| 1    | in-scope-python        | PASS    |
| 2    | in-scope-js            | PASS    |
| 3    | in-scope-bug           | PASS    |
| 4    | in-scope-followup      | PASS    |
| 5    | in-scope-sql           | PASS    |
| 6    | out-of-scope (recipe)  | PASS    |
| 7    | out-of-scope (essay)   | FAIL    |
| 8–10 | (not reached — 429)    | —       |

That's **6/7 ≈ 86%** on the cases that ran. Case 7 (asking for a 500-word
essay) being the one FAIL is telling — the hardened prompt declined the
recipe request cleanly but the model produced essay-flavored content for
the history-essay ask. That's the kind of real regression the eval was
designed to surface.

**Follow-up fix applied** (not yet re-measured because the key is still
out of quota): `SYSTEM_PROMPT` in `llm_service.py` now spells out that
partial compliance — an outline, a sample paragraph, "just the intro" —
counts as compliance, and tells the model to refuse outright on non-code
essay/article/prose asks. Re-running the eval against a fresh key should
move case 7 to PASS.

## Rubric

The judge model receives, for each case, the question, the `expected` rubric
from `eval_cases.json`, and the actual answer, then replies `PASS` or `FAIL`
per the instructions in `JUDGE_PROMPT` (see `run_eval.py`). Rubrics are
written per case and check for specific content rather than exact string
matches.

## Verdict

Insufficient end-to-end data to compare hardened vs weak baseline directly,
but the partial run plus the smoke-test behavior strongly suggest the
hardened prompt is where it needs to be on in-scope cases and on the
recipe-style out-of-scope refusal. The essay-style out-of-scope refusal is
the weakest point and the obvious next thing to fix in the system prompt.
