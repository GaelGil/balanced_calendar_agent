tool_definitions = [
    {
        "type": "function",
        "name": "COMPOSIO_SEARCH_EVENT_SEARCH",
        "description": "The eventsearch class enables scraping of google events search queries. it conducts an event search using the composio events search api, retrieving information on events such as concerts, festivals, and other activities based on the provided query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for the Composio Events Search API, specifying the event topic.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_events_in_month",
        "description": "Get user's calendar events for the current month.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The credentials for the Google Calendar API.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "analyze_events",
        "description": "Analyze the events in the users calendar and return a summary of the events.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Get user's calendar events for the current month.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "calendar_availability",
        "description": "Find available time slots on the user's calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for the Composio Events Search API, specifying the event topic.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]
