THRESHOLD = 0.45

SEARCH_POLICY_TOOL = {
    "name": "search_policy",
    "description": (
        "Search indexed insurance policy documents for text relevant to a question. "
        "Returns the matching text chunks, their source filenames, and top_score, "
        "which is the highest cosine similarity between the query and any retrieved "
        "chunk on a 0 to 1 scale. Use this whenever the user asks about coverage, "
        "exclusions, limits, or policy terms. A top_score below 0.45 means no chunk "
        "is a reliable match and the answer should NOT be drawn from those chunks. "
        "This tool does not tell you which documents exist; call list_documents first "
        "if you need to narrow the search with doc_filter."
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
                    "Optional. An exact filename to restrict the search to a single document, "
                    "e.g. 'sample_renters_policy.pdf'. Get valid filenames from list_documents. "
                    "If omitted, all documents are searched."
                ),
            },
        },
        "required": ["query"],
    },
}

def search_policy(query, doc_filter=None):
    top_score = 0.72
    reliable = top_score >= THRESHOLD
    return {
        "chunks": ["Water damage from sudden pipe bursts is covered under Section 4."],
        "source_files": ["sample_renters_policy.pdf"],
        "top_score": top_score,
        "reliable": reliable
    }

LIST_DOCUMENTS_TOOL = {
    "name": "list_documents",
    "description": (
        "List every insurance policy document currently indexed, with a one-line "
        "summary of what each one covers. Takes no input. Call this BEFORE searching "
        "when you do not know which documents exist, or after a search returned a low "
        "top_score and you want to retry against a single specific document. Returns a "
        "list of objects, each with a 'filename' and a 'summary'. Use the summaries to "
        "decide which document is most likely to answer the question, then pass that "
        "exact filename as the doc_filter argument to search_policy."
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

TOOLS = [SEARCH_POLICY_TOOL, LIST_DOCUMENTS_TOOL]

def run_tool(name, tool_input):
    if name == "search_policy":
        return search_policy(**tool_input)
    if name == "list_documents":
        return list_documents(**tool_input)
    return {"error": f"Unknown tool: {name}"}

