// in your React component
import { useEffect, useState } from "react";
import { fetchCalendarEvents } from "../../api/calendar";
import Event from "../ListItems/Event";
const Events = () => {
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
        <Event events={events} />
      )}
    </>
  );
};
export default Events;
