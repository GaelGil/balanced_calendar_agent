// in your React component
import { useEffect, useState } from "react";
import { fetchCalendarEvents } from "../api/calendar";
import { useLocation } from "react-router-dom";
const CalendarPage = () => {
  const [events, setEvents] = useState<any[]>([]);
  const location = useLocation();

  useEffect(() => {
    console.log(events);
    const params = new URLSearchParams(location.search);
    if (params.get("connected") === "true") {
      // Fetch events immediately
      fetch("http://localhost:5000/calendar/events", {
        credentials: "include", // if using session cookies
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("Events:", data);
          fetchCalendarEvents().then(setEvents).catch(console.error);
        });
    }
  }, [location]);

  useEffect(() => {}, []);

  const connectGoogleCalendar = () => {
    window.location.href = "http://localhost:5000/calendar/authorize";
  };
  return (
    <div className="p-6 border rounded-lg bg-gray-100 shadow space-y-4 max-w-md mx-auto">
      <h1>Calendar</h1>
      {events ? (
        <></>
      ) : (
        <button
          className="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 transition"
          onClick={connectGoogleCalendar}
        >
          Connect Google Calendar
        </button>
      )}

      <ul>
        {events.map((evt) => (
          <li key={evt.id}>
            {evt.start.dateTime || evt.start.date} – {evt.summary}
          </li>
        ))}
      </ul>
    </div>
  );
};
export default CalendarPage;
