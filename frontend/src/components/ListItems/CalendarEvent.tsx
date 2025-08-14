import React from "react";
import type { CalendarEventProps } from "../../types/Event";

const CalendarEvent: React.FC<CalendarEventProps> = ({ event }) => {
  return (
    <div className="flex flex-col items-center justify-center bg-gray-100">
      <div className="bg-white shadow-lg rounded-2xl p-6 w-80 text-center">
        <h2 className="text-xl font-bold">{event.summary}</h2>
        <p className="text-gray-500 mt-2">
          {event.start.dateTime || event.start.date} —{" "}
          {event.end.dateTime || event.end.date}
        </p>
      </div>
    </div>
  );
};

export default CalendarEvent;
