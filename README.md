# policy-agent

This is an AI agent that wraps a document Q&A service as a callable tool. Rather than failed outputs, it rephrases and escalte to human agents.

## The problem

In the previous project, doc-qa-rag stops the system where as in policy-agent, the same similarity threshold starts the next action. Essentially it's brake versus trigger. RAG stops running the app when the top_score is <0.45 and the user cannot get more info. Same scenario, policy-agent calls `list_documents` to see what exists, then rephrases. If the policy-agent cannot find anything similar, it will escalate the question to a human agent. 


## Architecture
```
   user question
        |
        v
   agent.py  (loop: call tool -> read result -> decide)
        |
        +--> list_documents: list every policy documents currently indexed
        |
        +--> escalate_to_human: when no reliable sources are found and cannot produce a grounded answer, hand off to a human agent.
        |
        +--> search_policy
                 |
                 v
            HTTP POST /ask  (httpx)
                 |
                 v
            doc-qa-rag  (FastAPI, localhost:8000)
                 |
                 v
            ChromaDB + `BAAI/bge-small-en-v1.5` embeddings
```
**Note**: search_policy is the only tool that leaves the process. The other two (list_documents, escalate_to_human) are local and cannot fail on network. 

## Tools

| Tool | Input | Returns |
|---|---|---|
| `search_policy`| `query`, `doc_filter` (accepted, non-funcdtional) | `answer`, `chunks`, `source_files`, `top_score`, `reliable` |
| `list_documents` | none | list of objects, each with `filename`, `summary` |
| `escalate_to_human` | `question`, `reason (enum)` | `escalated`, `question`, `reason`, `timestamp` |

## Decision policy

| Condition | Action |
|---|---|
| `reliable=True` | Cite the sources |
| `reliable=False`, retries <2 | Rephrase the query, or call `list_documents` to see what is actually indexed. |
| `reliable=False`, retries =2 | Call `escalate_to_human` with the original question and the reason |
| iterations >= `MAX_ITERS` (6) | Runaway-loop guard. Cost control is a side benefit. |


## Sample runs
### Grounded answer
```
[iter 1] search_policy({'query': 'Is water damage covered under the policy?'})
   -> top_score=0.5923371734761808 reliable=True files=['sample_renters_policy.pdf', 'sample_auto_policy.pdf']
Here's what the policy documents say about water damage coverage:

**Renters Policy** — Water damage **is covered**, but only in specific situations. The policy covers "water damage from plumbing, heating, or air conditioning systems," as well as freezing of those systems (Source: *sample_renters_policy.pdf*).

However, there are important limitations:
- **Flood damage is explicitly excluded** — the policy does not cover loss resulting from flood, earthquake, or other earth movement (Source: *sample_renters_policy.pdf*).
- Only the specific water-related perils listed above are covered; any peril not listed is not covered.

**Auto Policy** — The retrieved documents did not contain specific information about water damage coverage for autos, so I can't confirm how that policy treats it.

If you let me know which policy you're asking about (and, for auto, the specific situation), I can search further for more detail.
```
**Note**: the exclusion language in this trace may be model inference rather than retrieved text. See Known Limitations.

### Refusal without escalation
```
[iter 1] search_policy({'query': 'inland marine cargo procedure'})
   -> top_score=0.4327958810367754 reliable=False files=[]
[iter 2] search_policy({'query': 'cargo in transit coverage claims filing steps and requirements'})
   -> top_score=0.5259117401004859 reliable=True files=['sample_auto_policy.pdf', 'sample_renters_policy.pdf']
[iter 2] list_documents({})
I searched the available policy documents but could not find any reliable information about an **inland marine cargo procedure**.

The documents currently available cover:
- **Auto insurance** (liability, collision, comprehensive, uninsured motorist, rental reimbursement)
- **Renters insurance** (personal property, loss of use, personal liability, medical payments to others)

Neither of these addresses inland marine or cargo coverage, so there is no reliable source I can draw from to answer your question.

If you have an inland marine or cargo policy, it would likely be a separate document not currently in this system. You may want to check with your insurance provider directly for the cargo procedure details. Is there anything about your auto or renters policy I can help with instead?
```
**Note**: On `iter 2` top+_scorew came back as 0.52 because of similar words that were used in sample_auto_policy.pdf. Therefore, policy-agent did not escalate this issue to a human. 

## Design decisions

- **[FILL IN: raw SDK choice]** [why]
- **[FILL IN: reliable computed in Python]** [why]
- **[FILL IN: structured escalation]** [why]
- **[FILL IN: escalated flag on the loop]** [why]

## Known limitations

- [fill]
- [fill]
- [fill]
- [fill]

## Setup

```

# 1. start doc-qa-rag first (the agent is useless without it)
#    ____________

# 2. clone and enter policy-agent
#    ____________

# 3. venv + install
#    ____________

# 4. create .env with ANTHROPIC_API_KEY
#    ____________

# 5. run
#    ____________

```