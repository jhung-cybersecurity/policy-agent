from datetime import datetime, timezone
import httpx
THRESHOLD = 0.45
RAG_URL = "http://localhost:8000/ask"

SEARCH_POLICY_TOOL = {
    "name": "search_policy",
    "description": (
        "Search indexed insurance policy documents for text relevant to a question. "
        "Returns the matching text chunks, their source filenames, and top_score, "
        "which is the highest cosine similarity between the query and any retrieved "
        "chunk on a 0 to 1 scale. Use this whenever the user asks about coverage, "
        "exclusions, limits, or policy terms. A top_score below 0.45 means no chunk "
        "is a reliable match and the answer should NOT be drawn from those chunks. "
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The natural-language question to search policy documents for.",
            },
            "doc_filter": {
                "type": "string",
                "description": (
                    "NOT CURRENTLY SUPPORTED. Document filtering is not yet implemented on the "
                    "search backend, so this argument is ignored and all documents are always "
                    "searched. Do not rely on it to narrow results."
                ),
            },
        },
        "required": ["query"],
    },
}

def search_policy(query, doc_filter=None):
    response = httpx.post(
        RAG_URL,
        json={"question": query},
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()

    sources = data["sources"]
    top_score = data["top_score"]
    reliable = top_score >= THRESHOLD

    return {
        "answer": data["answer"],
        "chunks": [s["text"] for s in sources],
        "source_files": list({s["source"] for s in sources}),
        "top_score": top_score,
        "reliable": reliable,
    }

LIST_DOCUMENTS_TOOL = {
    "name": "list_documents",
    "description": (
        "List every insurance policy document currently indexed, with a one-line "
        "summary of what each one covers. Takes no input. Call this BEFORE searching "
        "when you do not know which documents exist "
        "and you want to retry against a single specific document. Returns a "
        "list of objects, each with a 'filename' and a 'summary'. Use the summaries to "
        "understand what is avaliable and to phrase follow-up searches using terms likely "
        "to appear in the relevant document. Filtering by document is not currently supported."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
    },
}

def list_documents():
    return {
        "documents": [
            {
                "filename": "sample_auto_policy.pdf",
                "summary": "Personal auto policy: liability, collision, comprehensive, "
                           "uninsured motorist, rental reimbursement.",
            },
            {
                "filename": "sample_renters_policy.pdf",
                "summary": "Renters policy: personal property, loss of use, personal "
                           "liability, medical payments to others.",
            },
        ],
    }

ESCALATE_TO_HUMAN_TOOL = {
    "name": "escalate_to_human",
    "description": (
        "Hand off to a human agent when you cannot produce a grounded answer. "
        "This is terminal: after calling it, do not call any other tool and do not attempt "
        "to answer from your own knowledge. Pass the users' original question and the reason "
        "the attempt failed. Call this only after the retry budget is exhausted or no reliable "
        "source was found. "

    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "list the question that the user asked",
            },
            "reason": {
                "type": "string",
                "enum": ["no_reliable_source", "retry_budget_exhausted"],
                "description": (
                    "use no_reliable_source when searches returned results but none met the reliability bar "
                    "use retry_budget_exhausted when the retry limit was reached without a reliable result "
                )
            },
        },
        "required": ["question", "reason"],
    },
}

def escalate_to_human(question, reason):
    return{
        "escalated": True, 
        "question": question,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


TOOLS = [SEARCH_POLICY_TOOL, LIST_DOCUMENTS_TOOL, ESCALATE_TO_HUMAN_TOOL]

def run_tool(name, tool_input):
    if name == "search_policy":
        return search_policy(**tool_input)
    if name == "list_documents":
        return list_documents(**tool_input)
    if name == "escalate_to_human":
        return escalate_to_human(**tool_input)
    return {"error": f"Unknown tool: {name}"}

