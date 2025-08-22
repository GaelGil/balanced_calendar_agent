from app.chat.utils.schemas import SearchResults, EventSearchResults
import traceback


def parse_composio_event_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_EVENT_SEARCH results into UnifiedSearchResponse format.

    Event search results have the same structure as news results, so we reuse the same parsing logic.
    """
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse News Results as Organic Results
        events_data = search_data.get("events_results", [])
        events = []
        for event_item in events_data:
            event = EventSearchResults(
                title=event_item.get("title", ""),
                date=f"{event_item.get('date', '').get('when', '')} {event_item.get('date', '').get('start_date', '')}",
                address="".join(event_item.get("address", "")),
                description=event_item.get("description", ""),
                image=event_item.get("image", ""),
                link=event_item.get("link", ""),
            )
            events.append(event)

        events_search_results = SearchResults(results=events)

        return events_search_results.model_dump()

    except Exception as e:
        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def format_events_to_markdown(events: list) -> str:
    """
    Convert Google Calendar events into a Markdown string.
    """
    if not events:
        return "### 📅 No events found."

    output = []
    for idx, event in enumerate(events, 1):
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        summary = event.get("summary", "No Title")
        description = event.get("description", "No Description")
        location = event.get("location", "No Location")

        entry = f"""### Event {idx}: {summary}

                - **Start:** {start}  
                - **End:** {end}  
                - **Location:** {location}  
                - **Description:** {description}  

                """
        output.append(entry.strip())

    return "\n\n".join(output)


def format_free_slots_to_markdown(free_slots: list) -> str:
    """
    Convert free time slots into a Markdown string.
    Each slot is a dict with 'start' and 'end' keys (ISO datetime strings).
    """
    if not free_slots:
        return "### ✅ No free slots available in this range."

    output = []
    for idx, slot in enumerate(free_slots, 1):
        start = slot.get("start")
        end = slot.get("end")

        entry = f"""### Free Slot {idx}
        - **Start:** {start}  
        - **End:** {end}  
"""
        output.append(entry.strip())

    return "\n\n".join(output)
