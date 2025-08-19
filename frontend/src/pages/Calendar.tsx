// in your React component
import { useEffect, useState } from "react";
import Events from "../components/Lists/Events";
import { PROJECT_NAME } from "../data/ProjectName";
import { calendarConnectionStatus } from "../api/calendar";
import CalendarEvents from "../components/Lists/CalendarEvents";

type Event = {
  id: string;
  title: string;
  time?: string;
};

const CalendarPage = () => {
  // const [events, setEvents] = useState<any[]>([]);
  const [balance, setBalance] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const year = new Date().getFullYear();
  const month = new Date().getMonth();

  const events = {
    "2025-08-10": [
      { id: "1", title: "Meeting with team", time: "10:00" },
      { id: "2", title: "Doctor appointment", time: "15:00" },
    ],
    "2025-08-15": [{ id: "3", title: "Birthday Party" }],
  };

  useEffect(() => {
    const getConnectionStastus = async () => {
      try {
        const status = await calendarConnectionStatus();
        setIsConnected(status);
      } catch (err) {
        console.error("Failed to load events", err);
      } finally {
        setLoading(false);
      }
    };
    getConnectionStastus();
  }, []);
  const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0 = Sunday
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Generate calendar days including leading empty days
  const days: (number | null)[] = [];
  for (let i = 0; i < firstDayOfMonth; i++) days.push(null);
  for (let d = 1; d <= daysInMonth; d++) days.push(d);

  const formatDate = (day: number) =>
    `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(
      2,
      "0"
    )}`;

  // TODO: on click of balance calendar send a request to balance agent to get a plan and execute
  // TODO: recieve pland and tasks and print them for user to see
  // TODO: Once done load events

  const connectGoogleCalendar = () => {
    window.location.href = "http://localhost:5000/calendar/authorize";
  };
  return (
    <div className="p-10 flex flex-col items-center justify-center">
      <h1>{PROJECT_NAME}</h1>

      {!isConnected ? (
        <button
          className="bg-blue-600 text-white font-semibold py-6 px-6 rounded-md hover:bg-blue-700 transition"
          onClick={connectGoogleCalendar}
        >
          Connect Google Calendar
        </button>
      ) : (
        <>
          <CalendarEvents />
          {!balance ? (
            <button
              className="bg-blue-600 text-white font-semibold py-6 px-6 rounded-md hover:bg-blue-700 transition"
              onClick={() => setBalance(true)}
            >
              Balance Calendar
            </button>
          ) : (
            <Events />
          )}
        </>
      )}
    </div>
  );
};
export default CalendarPage;
