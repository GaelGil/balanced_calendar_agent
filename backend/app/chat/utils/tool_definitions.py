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
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "analyze_events",
        "description": "Analyze the events in the users calendar and return a summary of the events.",
        "parameters": {
            "type": "object",
            "properties": {
                "events": {
                    "type": "string",
                    "description": "The users events",
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
    {
        "type": "function",
        "name": "create_event",
        "description": "Create a new event on the user's calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Title of the event."},
                "description": {
                    "type": "string",
                    "description": "Details about the event.",
                },
                "location": {"type": "string", "description": "Location of the event."},
                "start": {
                    "type": "object",
                    "properties": {
                        "dateTime": {
                            "type": "string",
                            "description": "ISO 8601 start datetime (e.g. 2025-08-27T17:00:00-07:00).",
                        },
                        "timeZone": {
                            "type": "string",
                            "description": "Timezone (e.g. America/Los_Angeles).",
                        },
                    },
                    "required": ["dateTime", "timeZone"],
                },
                "end": {
                    "type": "object",
                    "properties": {
                        "dateTime": {
                            "type": "string",
                            "description": "ISO 8601 end datetime.",
                        },
                        "timeZone": {"type": "string", "description": "Timezone."},
                    },
                    "required": ["dateTime", "timeZone"],
                },
                "attendees": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"email": {"type": "string"}},
                        "required": ["email"],
                    },
                    "description": "List of attendees with email addresses.",
                },
            },
            "required": ["summary", "start", "end"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "update_event",
        "description": "Update an existing event on the user's calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "The ID of the event to update.",
                },
                "event": {
                    "type": "object",
                    "description": "The updated event fields.",
                    "properties": {
                        "summary": {"type": "string"},
                        "description": {"type": "string"},
                        "location": {"type": "string"},
                        "start": {
                            "type": "object",
                            "properties": {
                                "dateTime": {"type": "string"},
                                "timeZone": {"type": "string"},
                            },
                            "required": ["dateTime", "timeZone"],
                        },
                        "end": {
                            "type": "object",
                            "properties": {
                                "dateTime": {"type": "string"},
                                "timeZone": {"type": "string"},
                            },
                            "required": ["dateTime", "timeZone"],
                        },
                        "attendees": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"email": {"type": "string"}},
                                "required": ["email"],
                            },
                        },
                    },
                },
            },
            "required": ["event_id", "event"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "delete_event",
        "description": "Delete an event from the user's calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "The Event ID of the event to delete.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
]
