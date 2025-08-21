from app.chat.utils.schemas import SearchResults, EventSearchResults
import traceback


def parse_composio_event_search_results(composio_result: dict) -> dict:
    """Parse COMPOSIO_SEARCH_EVENT_SEARCH results into UnifiedSearchResponse format.

    Event search results have the same structure as news results, so we reuse the same parsing logic.
    """
    try:
        search_data = composio_result.get("data", {}).get("results", {})

        # Parse News Results as Organic Results
        events_data = search_data.get("event_results", [])
        events = []
        for event_item in events_data:
            event = EventSearchResults(
                title=event_item.get("title"),
                date="".join(event_item.get("date")),
                address="".join(event_item.get("address")),
                description=event_item.get("description"),
                image=event_item.get("image"),
                link=event_item.get("link"),
            )
            events.append(event)

        events_search_results = SearchResults(results=events)

        return events_search_results.model_dump()

    except Exception as e:
        print(traceback.format_exc())
        return {"error": f"Failed to parse COMPOSIO news search results: {str(e)}"}


def parse_google_calendar_events():
    pass
