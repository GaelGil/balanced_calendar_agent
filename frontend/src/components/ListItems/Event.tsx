import React, { useState } from "react";
import type { EventProps } from "../../types/Event";

const EventTinder: React.FC<EventProps> = ({ events }) => {
  const [index, setIndex] = useState(0);

  if (events.length === 0) {
    return <p>No events found</p>;
  }

  const currentEvent = events[index];

  const handleAccept = () => {
    console.log("Accepted:", currentEvent);
    nextEvent();
  };

  const handleReject = () => {
    console.log("Rejected:", currentEvent);
    nextEvent();
  };

  const nextEvent = () => {
    if (index < events.length - 1) {
      setIndex(index + 1);
    } else {
      console.log("No more events");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="bg-white shadow-lg rounded-2xl p-6 w-80 text-center">
        <h2 className="text-xl font-bold">{currentEvent.summary}</h2>
        <p className="text-gray-500 mt-2">
          {currentEvent.start.dateTime || currentEvent.start.date} —{" "}
          {currentEvent.end.dateTime || currentEvent.end.date}
        </p>
      </div>

      <div className="flex gap-4 mt-6">
        <button
          className="bg-red-500 text-white px-6 py-2 rounded-full shadow-md hover:bg-red-600"
          onClick={handleReject}
        >
          ❌ Reject
        </button>
        <button
          className="bg-green-500 text-white px-6 py-2 rounded-full shadow-md hover:bg-green-600"
          onClick={handleAccept}
        >
          ✅ Accept
        </button>
      </div>
    </div>
  );
};

export default EventTinder;
