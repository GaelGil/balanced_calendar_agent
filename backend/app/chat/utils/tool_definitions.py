tool_definitions = {
    "get_composio_search_results": {
        "name": "get_composio_search_results",
        "description": "Get search results from Composio.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
            },
            "required": ["query"],
        },
    },
}
