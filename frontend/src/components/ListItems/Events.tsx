// in your React component
import { useEffect, useState } from "react";
import { fetchCalendarEvents } from "../../api/calendar";
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
    <div className="p-6 border rounded-lg bg-gray-100 shadow space-y-4 max-w-md mx-auto">
      {loading ? (
        <p className="text-center text-gray-600 font-semibold">Loading ...</p>
      ) : (
        <ul>
          {events.map((evt) => (
            <li className="mb-2" key={evt.id}>
              {evt.start.dateTime || evt.start.date} - {evt.summary}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
export default Events;
