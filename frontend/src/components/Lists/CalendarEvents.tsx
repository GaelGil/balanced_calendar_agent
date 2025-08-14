// in your React component
import { useEffect, useState } from "react";
import { fetchCalendarEvents } from "../../api/calendar";
import CalendarEvent from "../ListItems/CalendarEvent";

const CalendarEvents = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const events = await fetchCalendarEvents();
        setEvents(events);
      } catch (err) {
        console.error("Failed to load events", err);
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, []);

  return (
    <>
      {loading ? (
        <p className="text-center text-gray-600 font-semibold">Loading ...</p>
      ) : (
        events.map((event) => <CalendarEvent key={event.id} event={event} />)
      )}
    </>
  );
};
export default CalendarEvents;
