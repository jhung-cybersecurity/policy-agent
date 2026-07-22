# policy-agent

Agentic layer over doc-qa-rag. Wraps the existing RAG service as a callable tool.

## Problem

doc-qa-rag currently answers one question against a fixed corpus with a
similarity-threshold gate. When retrieval confidence falls below 0.45, the
request terminates as `blocked=True`.

The limitation: `blocked` is a terminal state. The system has no way to try
a different phrasing or a different document, so a retrievable answer is
lost whenever the user's wording diverges from the source text.

## Tools

| Tool | Input | Returns |
|---|---|---|
| `list_documents` | none | filenames + one-line summaries |
| `search_policy` | `query`, optional `doc_filter` | chunks + `top_score` |
| `escalate_to_human` | `question`, `reason` | halts the loop |

## Decision policy

| Condition | Action |
|---|---|
| `top_score >= 0.45` | Answer, grounded, cite chunks |
| `top_score < 0.45`, retries < 2 | Rephrase or narrow to a different doc, search again |
| `top_score < 0.45`, retries = 2 | `escalate_to_human("no grounded source found")` |
| iterations >= 6 | `escalate_to_human("iteration budget exhausted")` |

Iteration cap exists because: the loop has no guaranteed natural exit. Without
a hard cap an agent that never reaches a stopping condition runs indefinitely,
burning tokens and growing the append-only message history until it exceeds
the context window.

## Framework decision

Hand-written agentic loop on the raw Anthropic SDK.

Rejected: LangChain `create_agent`, Anthropic Tool Runner.

Reason: The loop mechanics are the skill this project exists to demonstrate. Tool Runner is beta and LangChain's agent API churned through v1, so the raw SDK is the more stable surface.

## Open question (resolve before build starts)

Does the agent decide when to rephrase the query, or is the rephrase rule
coded deterministically?

My answer: The agent decides. A coded rephrase rule would make this a
branching workflow, not an agent, and query reformulation is the judgment
call I actually want the model making.

Tradeoff accepted: rephrasing becomes nondeterministic, so eval cannot assert
on exact query strings. Same constraint I hit with prompt-level refusals in
doc-qa-rag. Eval will assert on outcomes (did it escalate, how many iterations)
rather than on the intermediate queries.

## Status

Scoped. Not started.