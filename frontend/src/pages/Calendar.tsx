// in your React component
import { useEffect, useState } from "react";
import Events from "../components/Lists/Events";
import { PROJECT_NAME } from "../data/ProjectName";
import { calendarConnectionStatus } from "../api/calendar";
import CalendarEvents from "../components/Lists/CalendarEvents";

const CalendarPage = () => {
  // const [events, setEvents] = useState<any[]>([]);
  const [balance, setBalance] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [isConnected, setIsConnected] = useState<boolean>(false);

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
