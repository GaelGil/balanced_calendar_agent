import { useState } from "react";

interface Event {
  id: string;
  summary?: string;
  start?: { dateTime?: string; date?: string };
  end?: { dateTime?: string; date?: string };
}

const GoogleCalendar = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = () => {
    // Redirect to Flask backend OAuth start endpoint
    window.location.href = "http://localhost:5000/auth/google";
  };

  const fetchEvents = async () => {
    try {
      const res = await fetch("http://localhost:5000/calendar/events", {
        credentials: "include", // important to send cookies/session
      });
      if (!res.ok) {
        throw new Error("Not authenticated");
      }
      const data = await res.json();
      setEvents(data.items || []);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div>
      <button onClick={handleLogin}>Login with Google</button>
      <button onClick={fetchEvents}>Load Events</button>

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <ul>
        {events.map((event) => (
          <li key={event.id}>
            {event.summary} -{" "}
            {event.start?.dateTime || event.start?.date || "No start date"}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GoogleCalendar;
