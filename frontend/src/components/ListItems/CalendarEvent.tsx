import React from "react";
import type { CalendarEventProps } from "../../types/Event";

const CalendarEvent: React.FC<CalendarEventProps> = ({ event }) => {
  return (
    <div
      className="w-20 h-20 bg-blue-500 rounded-sm flex items-center justify-center text-white text-xs"
      title={event.summary}
    >
      {event.summary}
      {event.start.dateTime || event.start.date}
    </div>
  );
};

export default CalendarEvent;
